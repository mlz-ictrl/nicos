# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
from os import path

from nicos import session
from nicos.core import MASTER, Override, Param, absolute_path
from nicos.core.data import DataManager
from nicos.devices.experiment import Experiment
from nicos.utils import readFile, writeFile


class SinqDataManager(DataManager):
    """
    A SINQ special DataManager which handles the SINQ file
    numbering scheme
    """

    _pointcounter = 1

    def incrementCounters(self, countertype):
        result = []
        exp = session.experiment
        if countertype == 'scan':
            val = exp.sicscounter
            exp.updateSicsCounterFile(val+1)
            result.append((countertype, val))
            result.append(('counter', val))
            self._pointcounter = 1
        elif countertype == 'point':
            result.append((countertype, self._pointcounter))
            result.append(('counter', self._pointcounter))
            self._pointcounter += 1
        return result


class SinqExperiment(Experiment):
    """Follow the current file structure used in SINQ"""

    parameter_overrides = {
        'propprefix': Override(default=''),
        'serviceexp': Override(default='Service'),
        'sendmail': Override(default=False),
        'zipdata': Override(default=False),
        'title': Override(settable=True, volatile=False),
        'users': Override(settable=True, volatile=False),
        'elog': Override(default=False),
    }

    parameters = {
        'scriptpath': Param('Path to script files',
                            type=absolute_path, settable=True),
        'proposal_title': Param('Title for the proposal',
                                type=str, settable=True,
                                category='experiment'),
        'user_email': Param('User email', type=str, settable=True,
                            category='experiment'),
    }
    datamanager_class = SinqDataManager

    def proposalpath_of(self, proposal):
        if self.proposalpath:
            return self.proposalpath
        proposal = proposal.replace(' ', '')
        return path.join(self.dataroot, 'proposals', time.strftime('%Y'),
                         proposal)

    @property
    def datapath(self):
        if self.proposal:
            prop = self.proposal.replace(' ', '')
        else:
            prop = 'unknown_proposal'
        return path.join(self.dataroot, 'data', time.strftime('%Y'), prop)

    def getProposalType(self, proposal):
        proposalstr = proposal
        if not isinstance(proposalstr, str):
            proposalstr = str(proposal)

        year = time.strftime('%Y')
        if proposalstr.startswith(year):
            return 'user'

        return Experiment.getProposalType(self, proposal)

    #
    # Following configurations make SICS and NICOS have same counters.
    #

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
        lines.append('You\'ll risk eternal damnation and a reincarnation '
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

    def doWriteScriptpath(self, scriptpath):
        if not os.path.isdir(scriptpath):
            raise ValueError('%s is not a directory' % scriptpath)
        if not os.access(scriptpath, os.R_OK | os.W_OK | os.X_OK):
            raise ValueError('Cannot access scriptpath %s' % scriptpath)
        # param set in device.py

    def _newPropertiesHook(self, proposal, kwds):
        if 'proposal_title' in kwds:
            self.proposal_title = kwds['proposal_title']
        return kwds


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
