# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import os
import time
import re
from os import path

import requests

from nicos import session
from nicos.core import MASTER, Override, Param, absolute_path
from nicos.core.data import DataManager
from nicos.devices.experiment import Experiment as CoreExperiment
from nicos.core.errors import InvalidValueError
from nicos.utils import readFile, writeFile

SERVICE_EXP = 'Service'

class Experiment(CoreExperiment):
    """Base experiment for SINQ

    Compared to `CoreExperiment`, this class adds the following features:
    - If a proposal ID is given, the "Query DB" button reads experiment metadata
    from DUO and populates the corresponding fields of the "Experiment" class.
    - If no proposal ID is given, the "Query DB" button reads the last proposal
    for the instrument from DUO.
    - At experiment start, it is verified if the given proposal ID exists in DUO
    and is valid (i.e. exists and is not refused, in review or currently being
    edited). If the proposal is not valid, starting an experiment is prevented.
    """

    parameter_overrides = {
        'propprefix': Override(default=''),
        'serviceexp': Override(
            default=SERVICE_EXP, internal=True, settable=False),
        'sendmail': Override(default=False),
        'zipdata': Override(default=False),
        'elog': Override(default=False),
        'title': Override(settable=True),
        'users': Override(settable=True),
    }

    parameters = {
        'scriptpath': Param('Path to script files',
                            type=absolute_path, settable=True),
        'proposal_title': Param('Title for the proposal',
                                type=str, settable=True,
                                category='experiment'),
        'user_email': Param('User email', type=str, settable=True,
                            category='experiment'),
        'duo_url': Param('Duo url', type=str,
            default='https://duo.psi.ch/duo/api.php'),
        'persistent_environment': Param(
            'environment devices to be added if present',
            type=list, settable=True, userparam=False, default=[])
    }

    def proposalpath_of(self, proposal):
        if self.proposalpath:
            return self.proposalpath
        proposal = proposal.replace(' ', '')
        return path.join(self.dataroot, 'proposals', time.strftime('%Y'),
                         proposal)

    def _getDuoapikey(self):
        try:
            apikeypath = path.join(path.expanduser('~'), '.duoapikey')
            return readFile(apikeypath)[0]
        except FileNotFoundError:
            return None

    @property
    def datapath(self):
        if self.proposal:
            prop = self.proposal.replace(' ', '')
        else:
            prop = self.serviceexp
        return path.join(self.dataroot, 'data', time.strftime('%Y'), prop)

    def doWriteTitle(self, title):
        self.update(title=title)

    def doWriteUsers(self, users):
        self.update(users=users)

    def _newPropertiesHook(self, proposal, kwds):
        if 'proposal_title' in kwds:
            self.proposal_title = kwds['proposal_title']
        # Set proposal in case this isn't already set
        # Case when Duo is down and we just want to start experiment
        if not 'proposal' in kwds:
            kwds['proposal'] = proposal
        return kwds

    def _newSetupHook(self):
        envlist = [k for k in self.persistent_environment if k in session.devices]
        if envlist:
            self.setEnvironment(envlist)
            self.log.info('reset environment to %r', envlist)

    def newSample(self, parameters):
        # Do not try to create unwanted directories as
        # in nicos/devices/experiment
        pass

    def doReadTitle(self):
        return self.propinfo.get('title', SERVICE_EXP)

    def doFinish(self):
        """
        This method mainly creates or touches a scicat sync file.
        This file is used to signal that this proposal is to be archived
        by a separate process.
        """
        # Check if data path exists
        if not self.datapath:
            return

        # The interface relies solely on the file system.
        # Construct sync file name path
        syncpathname = path.join(self.datapath, '.scicatsync')

        # Check if modification time is older than 5 minutes,
        # throttle just as a security measure
        if path.exists(syncpathname):
            last_sync = (time.time() - os.path.getmtime(syncpathname))
        else:
            last_sync = float('inf')

        if last_sync > 300:
            # Touch file to modify timestamp
            with open(syncpathname, 'w+', encoding='utf-8') as syncfile:
                syncfile.write('')

    def _requestDuoProposal(self, proposal=None):
        """ Request proposal from duo.
        Returns a dictionary with duoinfo if succesful.
        If response is 404 it raises an exception.
        Anything else returns None.
        """
        if key := self._getDuoapikey():
            headers = {'accept': '*/*','X-API-SECRET': key}
        else:
            self.log.error("No duoapikey present")
            return None

        try:
            if proposal:
                # Query number
                self.log.debug('Query proposal %s', proposal)
                response = requests.get(
                    url=self.duo_url + '/v1/ProposalInfos/details/sinq/',
                    params={'propid': proposal},
                    headers=headers,
                    timeout=2.0
                )
            else:
                # Query Schedule
                # Deduct instrument name, we should name our instrument the same as in Duo.
                # However Duo does seem to accept multiple names,
                # e.g. it accepts both SANS and SANS-I
                # Read the instrument name from the setup and remove the SINQ prefix
                beamline = re.sub("sinq", "", session.instrument.instrument,
                flags=re.IGNORECASE).strip()
                self.log.debug('Query proposal based on schedule for %s', beamline)
                response = requests.get(
                    url=self.duo_url + '/CalendarInfos/scheduled/sinq/?beamline='
                    + beamline,
                    headers=headers,
                    timeout=2.0
                )
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            # If duo for some reason is offline or unreachable
            # we will be permissive
            self.log.error("Failed to reach Duo: %s", str(e))
            return None

        if response.status_code == 200:
            duoinfo = response.json()
            # List that has elements take the first
            if isinstance(duoinfo, list) and duoinfo:
                duoinfo = duoinfo[0]
            # Return duoinfo dictionary
            return duoinfo

        if response.status_code == 404:
            # Don't allow unknown proposals, return list of errors
            self.log.debug('Duo responded with %s', response)
            raise InvalidValueError(
                    f'Failed to find proposal {proposal} in duo')

        if response.status_code == 403:
            # This is likely an authentication issue, is the apikey correct?
            self.log.warning('Duo responded with %s. '
                    'There is likely a problem with authentication. '
                    'You can go on manually, but please notify LIN-Controls.'
                    , response)
            return None

        # Something went wrong but we don't know what.
        # Let's not block, but log an error message.
        self.log.error('Unhandled error, Duo responded with %s '
                'when querying proposal %s. '
                'You can go on manually, but please notify LIN-Controls.',
                response, proposal)
        return None

    def _proposalIsAllowed(self, duoinfo):
        """ Check if a proposal is allowed based on dict returned by duo
        Return error string if allowed, if not return None.
        """
        proposal = duoinfo['proposal']
        if 'type' in duoinfo and duoinfo['type'] == "Proprietary":
            # This is ok, we just don't know more so we need to return
            self.log.debug(" proprietary proposal %s", proposal)
            return None
        proposal_status = duoinfo.get('proposal_status', None)
        if proposal_status is None:
            # let's be permissive here, this shouldn't happen
            # but if it does we allow it
            self.log.warning("This proposal has no status: %s", proposal)
            return None
        if proposal_status == "Accepted":
            self.log.debug("Proposal %s is accepted.", proposal)
            return None
        if proposal_status == "Finished":
            # Tolerate finished experiments, but generate a warning
            self.log.warning("Proposal %s is finished according to duo.", proposal)
            return None
        if proposal_status == "Refused":
            errstr = f'Failure, proposal {proposal} is refused according to duo.'
            self.log.error(errstr)
            return errstr
        if proposal_status == "In Review":
            errstr = f'Failure, proposal {proposal} is in review according to duo.'
            self.log.error(errstr)
            return errstr
        if proposal_status == "Editing":
            errstr = f'Failure, proposal {proposal} is in editing according to duo.'
            self.log.error(errstr)
            return errstr
        # We are now in an unforeseen case, let's be permissive
        self.log.warning("Unknown proposal status: %s", duoinfo)
        return None

    def _canQueryProposals(self):
        can_query = bool(self._getDuoapikey()) and bool(session.instrument.instrument)
        self.log.debug('Can query proposals: %d', can_query)
        return can_query

    def _newCheckHook(self, proptype, proposal):
        """Check if it's allowed to start experiment on this proposal
        """
        if proposal == self.serviceexp:
            return

        # check proposal number syntax
        if not (len(proposal) == 8 and proposal.isdigit()):
            # This is not a proposal number
            raise InvalidValueError('Please check that the format is digits only '
                'on the following format: YYYYNNNN. E.g. 20250123')

        if not self._canQueryProposals():
            # The preconditions of querying are not met
            return
        duoinfo = self._requestDuoProposal(proposal)
        if duoinfo is None:
            # Not ok, but neither connection error nor 404
            # So let's be permissive
            return
        # Check if it's allowed to collect data on this proposal
        error = self._proposalIsAllowed(duoinfo)
        if error:
            raise InvalidValueError(error)
        return

    def _queryProposals(self, proposal=None, kwds=None):
        # The instrument name at SINQ is usally given as "SINQ <INST>". Hence,
        # the string is split and only the last part is taken.
        self.log.debug('Query proposal %s \n %s', proposal, kwds)

        if not isinstance(kwds, dict):
            kwds = {}

        if proposal in (None, self.serviceexp):
            self.log.debug('Query proposal based on schedule')
            try:
                duoinfo = self._requestDuoProposal()
                self.log.debug('Duoinfo based on schedule %s', duoinfo)
            except InvalidValueError:
                duoinfo = None
            if duoinfo is None:
                kwds['errors'] = [
                        'Failed to fetch schedule. Try to search for proposal number.' ]
                return [ kwds ]
        else:
            self.log.debug('Query proposal %s ', proposal)
            try:
                duoinfo = self._requestDuoProposal(proposal)
            except InvalidValueError:
                kwds['errors'] = [
                        f'Could not find proposal {proposal}, it may not exist '
                        'or be wrongly entered. Check that format is digits '
                        'only YYYYNNNN. E.g. 20250123'
                        ]
                return [ kwds ]
            if not duoinfo:
                kwds['errors'] = [
                        'Something went wrong when querying Duo. '
                        'Check logs for further info. You should still be able '
                        'to start an experiment by manually filling in the details.'
                        ]
                return [ kwds ]

        self.log.debug('Received the following %s', duoinfo)

        # We have to check here for proprietary, if yes return without more info
        if 'type' in duoinfo and duoinfo['type'] == "Proprietary":
            kwds.update({
                'proposal': duoinfo['proposal'],
                'title': 'Proprietary proposal ' + duoinfo['proposal'],
                })
            return [ kwds ]

        error = self._proposalIsAllowed(duoinfo)
        if error:
            kwds['errors'] = [error]
            return [ kwds ]

        propinfo = {
            'users': [{
                'name': ' '.join([duoinfo['pi_firstname'], duoinfo['pi_lastname']]),
                'email': duoinfo['pi_email'],
                }],
            'proposal': duoinfo['proposal'],
            'title': duoinfo['title'],
            'localcontacts': [],
        }

        for period in duoinfo['schedule']:
            if localcontact := period.get('localcontact', None):
                contactinfo = {
                    'name': ' '.join([localcontact['firstname'], localcontact['lastname']]),
                    'email': localcontact['email'],
                }
                if contactinfo not in propinfo['localcontacts']:
                    propinfo['localcontacts'].append(contactinfo)

        self.log.debug('kwds %s', kwds)
        # Docstring of Experiment._queryProposals: This function must return
        # a list of dictionaries where each dictionary represents a proposal
        kwds.update(propinfo)
        return [ kwds ]

class SicsDataManager(DataManager):
    """
    A SINQ special DataManager which handles the SICS file
    numbering scheme
    """

    _pointcounter = 1

    def incrementCounters(self, countertype):
        result = []
        exp = session.experiment
        if countertype == 'scan':
            val = exp.sicscounter + 1
            exp.updateSicsCounterFile(val)
            result.append((countertype, val))
            result.append(('counter', val))
            self._pointcounter = 1
        elif countertype == 'point':
            result.append((countertype, self._pointcounter))
            result.append(('counter', self._pointcounter))
            self._pointcounter += 1
        return result


class SinqExperiment(Experiment):
    """Legacy SINQ experiment, with number schema from Sics.
    """

    datamanager_class = SicsDataManager

    @property
    def sicscounterfile(self):
        return path.join(self.dataroot, 'data', time.strftime('%Y'),
                         'DataNumber')

    def updateSicsCounterFile(self, value):
        """Update the counter file."""
        counterpath = self.sicscounterfile
        if not path.isdir(path.dirname(counterpath)):
            os.makedirs(path.dirname(counterpath))
        lines = ['%3s\n' % value]
        lines.append('NEVER, EVER modify or delete this file\n')
        lines.append("You'll risk eternal damnation and a reincarnation "
                     'as a cockroach!')
        writeFile(counterpath, lines)

    @property
    def sicscounter(self):
        try:
            lines = readFile(self.sicscounterfile)
        except OSError:
            self.updateSicsCounterFile(0)
            return 0
        if lines:
            return int(lines[0].strip())

        # the counter is not yet in the file
        return 0



class TomoSinqExperiment(SinqExperiment):
    """
    This only adds a parameter to store the dictionary of
    tomography parameters for the tomography commands in
    iconcommands.py
    """

    parameters = {
        'tomo_params': Param('Dictionary of tomography parameters',
                             type=dict,
                             internal=True,
                             settable=True),
    }

    def doInit(self, mode):
        if mode == MASTER:
            self.tomo_params = {'status': 'reset'}
