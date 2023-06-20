#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
"""ESS Experiment device."""

import time
from os import path

from yuos_query.exceptions import BaseYuosException
from yuos_query.yuos_client import YuosCacheClient

from nicos import session
from nicos.core import SIMULATION, Override, Param, UsageError, \
    absolute_path, listof, mailaddress
from nicos.devices.experiment import Experiment
from nicos.utils import createThread


class EssExperiment(Experiment):
    parameters = {
        'cache_filepath':
            Param('Path to the proposal cache',
                  type=str,
                  category='experiment',
                  mandatory=True,
                  userparam=False),
        'filewriter_root':
            Param('Root data path on the file writer server under which all '
                  'proposal specific paths exist.', mandatory=True,
                  type=absolute_path),
        'update_interval':
            Param('Time interval (in hrs.) for cache updates',
                  default=1.0,
                  type=float,
                  userparam=False)
    }

    parameter_overrides = {
        'propprefix': Override(default=''),
        'proptype': Override(settable=True),
        'serviceexp': Override(default='Service'),
        'sendmail': Override(default=False, settable=False),
        'zipdata': Override(default=False, settable=False),
        'users': Override(default=[], type=listof(dict)),
        'localcontact': Override(default=[], type=listof(dict)),
        'title': Override(settable=True),
        'elog': Override(default=False, settable=False),
    }

    def doInit(self, mode):
        Experiment.doInit(self, mode)
        self._client = None
        self._update_cache_worker = createThread('update_cache',
                                                 self._update_cache,
                                                 start=False)
        try:
            self._client = YuosCacheClient.create(self.cache_filepath)
            self._update_cache_worker.start()
        except Exception as error:
            self.log.warn('proposal look-up not available: %s', error)

    def doReadTitle(self):
        return self.propinfo.get('title', '')

    def doReadUsers(self):
        return self.propinfo.get('users', [])

    def doReadLocalcontact(self):
        return self.propinfo.get('localcontacts', [])

    def new(self, proposal, title=None, localcontact=None, user=None, **kwds):
        if self._mode == SIMULATION:
            raise UsageError('Simulating switching experiments is not '
                             'supported!')

        proposal = str(proposal)

        if not proposal.isnumeric():
            raise UsageError('Proposal ID must be numeric')

        # Handle back compatibility
        users = user if user else kwds.get('users', [])
        localcontacts = localcontact if localcontact \
            else kwds.get('localcontacts', [])

        self._check_users(users)
        self._check_local_contacts(localcontacts)

        # combine all arguments into the keywords dict
        kwds['proposal'] = proposal
        kwds['title'] = str(title) if title else ''
        kwds['localcontacts'] = localcontacts
        kwds['users'] = users

        # give an opportunity to check proposal database etc.
        propinfo = self._newPropertiesHook(proposal, kwds)
        self._setROParam('propinfo', propinfo)
        self._setROParam('proposal', proposal)
        self.proptype = 'service' if proposal == '0' else 'user'

        # Update cached values of the volatile parameters
        self._pollParam('title')
        self._pollParam('localcontact')
        self._pollParam('users')
        self._newSetupHook()
        session.experimentCallback(self.proposal, None)

    def update(self, title=None, users=None, localcontacts=None):
        self._check_users(users)
        self._check_local_contacts(localcontacts)
        title = str(title) if title else ''
        Experiment.update(self, title, users, localcontacts)

    def proposalpath_of(self, proposal):
        return path.join(self.filewriter_root, time.strftime('%Y'), proposal)

    def _check_users(self, users):
        if not users:
            return
        if not isinstance(users, list):
            raise UsageError('users must be supplied as a list')

        for user in users:
            if not user.get('name'):
                raise KeyError('user name must be supplied')
            mailaddress(user.get('email', ''))

    def _check_local_contacts(self, contacts):
        if not contacts:
            return
        if not isinstance(contacts, list):
            raise UsageError('local contacts must be supplied as a list')
        for contact in contacts:
            if not contact.get('name'):
                raise KeyError('local contact name must be supplied')
            mailaddress(contact.get('email', ''))

    def finish(self):
        self.new(0, 'Service mode')
        self.sample.set_samples({})

    def _canQueryProposals(self):
        if self._client:
            return True
        return False

    def _update_cache(self):
        while True:
            self._client.update_cache()
            time.sleep(self.update_interval * 3600)

    def _queryProposals(self, proposal=None, kwds=None):
        if not kwds:
            return []
        if kwds.get('admin', False):
            results = self._get_all_proposals()
        else:
            results = self._query_by_fed_id(kwds.get('fed_id', ''))

        return [{
            'proposal': str(prop.id),
            'title': prop.title,
            'users': self._extract_users(prop),
            'localcontacts': [],
            'samples': self._extract_samples(prop),
            'dataemails': [],
            'notif_emails': [],
            'errors': [],
            'warnings': [],
        } for prop in results]

    def _query_by_fed_id(self, name):
        try:
            return self._client.proposals_for_user(name)
        except BaseYuosException as error:
            self.log.error('%s', error)
            raise

    def _get_all_proposals(self):
        try:
            return self._client.all_proposals()
        except BaseYuosException as error:
            self.log.error('%s', error)
            raise

    def _extract_samples(self, query_result):
        samples = []
        for sample in query_result.samples:
            mass = f'{sample.mass_or_volume[0]} {sample.mass_or_volume[1]}'.strip(
            )
            density = f'{sample.density[0]} {sample.density[1]}'.strip()
            samples.append({
                'name': sample.name,
                'formula': sample.formula,
                'number_of': sample.number,
                'mass_volume': mass,
                'density': density
            })
        return samples

    def _extract_users(self, query_result):
        users = []
        for first, last, fed_id, org in query_result.users:
            users.append(self._create_user(f'{first} {last}', '', org, fed_id))
        if query_result.proposer:
            first, last, fed_id, org = query_result.proposer
            users.append(self._create_user(f'{first} {last}', '', org, fed_id))
        return users

    def _create_user(self, name, email, affiliation, fed_id):
        return {
            'name': name,
            'email': email,
            'affiliation': affiliation,
            'facility_user_id': fed_id
        }

    def get_samples(self):
        return [dict(x) for x in self.sample.samples.values()]
