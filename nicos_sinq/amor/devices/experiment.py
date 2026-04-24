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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

import subprocess
import time
from os import path

from nicos.core import Override, Param, absolute_path
from nicos.core.data import DataManager
from nicos.core.errors import InvalidValueError
from nicos.core.params import none_or
from nicos_sinq.devices.experiment import SinqExperiment

class AmorExperiment(SinqExperiment):
    """Additional experiment parameters for AMOR"""

    parameter_overrides = {
        'elog': Override(default=False),
    }

    parameters = {
        'scriptroot': Param('Root for script files',
                            type=absolute_path, userparam=False),
        'scriptpath': Param('Path to script files',
                            type=absolute_path, settable=True),
        'datadir_amordr': Param('Path to raw data on amor-dr.psi.ch',
                                 type=none_or(absolute_path), settable=False, default=None),
        'pi_user': Param('Principal investigator', type=str, settable=True,
                                  category='experiment'),
        'pi_email': Param('Principal investigator', type=str, settable=True,
                                  category='experiment'),
        'pi_affiliation': Param('PI user affiliation', type=str, settable=True,
                                  category='experiment'),
    }
    datamanager_class = DataManager

    def _newCheckHook(self, proptype, proposal):
        SinqExperiment._newCheckHook(self, proptype, proposal)
        try:
            duoinfo = self._requestDuoProposal(proposal)
        except InvalidValueError:
            return

        self.pi_user =  ' '.join([duoinfo['pi_firstname'], duoinfo['pi_lastname']])
        self.pi_email = duoinfo['pi_email']

        pi_affil = duoinfo['pi_affiliation']
        name = pi_affil['name']
        if department := pi_affil.get('department', None):
            name = ' '.join([name, department])
        if country := pi_affil.get('country', None):
            name = ', '.join([name, country])
        self.pi_affiliation = name

    @property
    def allpaths(self):
        """Return a list of all autocreated paths.

        Needed to keep track of directory structure upon proposal change.
        """
        return [self.proposalpath, self.datapath, self.elogpath] + list(self.extrapaths)

    @property
    def datapath(self):
        if self.proposal:
            prop = self.proposal.replace(' ', '')
        else:
            prop = self.serviceexp
        return path.join(self.dataroot, 'amor', 'data', time.strftime('%Y'), prop)

    def getProposalType(self, proposal):
        proposalstr = proposal
        if not isinstance(proposalstr, str):
            proposalstr = str(proposal)

        year = time.strftime('%Y')
        if proposalstr.startswith(year):
            return 'user'

        return SinqExperiment.getProposalType(self, proposal)

    def doWriteScriptpath(self, scriptpath):
        """
        Do not perform script path check for AMOR, as the AMOR script paths are actually
        created on the machine amor-dr.psi.ch (daemon is running on amor.psi.ch).
        """

    def createUserPaths(self, scriptdir):
        self._setROParam('datadir_amordr', scriptdir.replace('scripts', 'raw'))
        result = subprocess.run(
            ["ssh", "sinquser@amor-dr", f"mkdir -p {scriptdir} && mkdir -p {self.datadir_amordr}"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            self.log.error('Creating user paths failed: %s', result.stderr)

    def doFinish(self):
        SinqExperiment.doFinish(self)
        self._setROParam('datadir_amordr', '/home/sinquser/service/raw')
        self._setROParam('scriptpath', '/home/sinquser/service/scripts')
