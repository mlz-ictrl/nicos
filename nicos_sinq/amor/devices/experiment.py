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

from nicos.core import Param, absolute_path
from nicos.core.data.manager import DataManager
from nicos.core.params import none_or
from nicos_sinq.devices.experiment import SinqExperiment

class AmorExperiment(SinqExperiment):
    """Additional experiment parameters for AMOR"""

    parameters = {
        'datadir_amordr': Param('Path to raw data on amor-dr.psi.ch',
                                 type=none_or(absolute_path), settable=False, default=None),
    }

    # To be removed in SD27, when AMOR will be switched to the same counting
    # mechanism as the other experiment (sicscounter). Until then, the base data
    # manager is used to avoid enumeration issues in operation.
    datamanager_class = DataManager

    @property
    def allpaths(self):
        """Return a list of all autocreated paths.

        Needed to keep track of directory structure upon proposal change.
        Compared to the overwritten method of nicos_sinq.devices.experiment.Experiment,
        self.scriptpath is not included in the list, as it is not created on the
        local machine and therefore the existence check would fail. The script
        path is created on the machine amor-dr.psi.ch.
        """
        return [self.proposalpath, self.datapath, self.elogpath] + list(self.extrapaths)

    def doWriteScriptpath(self, scriptpath):
        """
        Do not perform script path check for AMOR, as the AMOR script paths are actually
        created on the machine amor-dr.psi.ch (daemon is running on amor.psi.ch).
        """

    def createUserPaths(self, scriptdir):
        """
        This method is called from the GUI to create the user paths on
        amor-dr.psi.ch. It uses ssh to create the directories on the remote
        machine.
        """
        self._setROParam('datadir_amordr', scriptdir.replace('scripts', 'raw'))
        result = subprocess.run(
            ["ssh", "sinquser@amor-dr", f"mkdir -p {scriptdir} && mkdir -p {self.datadir_amordr}"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            self.log.error('Creating user paths failed: %s', result.stderr)

    def doFinish(self):
        """
        Overridden to set the datadir_amordr and scriptpath parameters to the
        AMOR-specific default paths.
        """
        SinqExperiment.doFinish(self)
        self._setROParam('datadir_amordr', '/home/sinquser/service/raw')
        self._setROParam('scriptpath', '/home/sinquser/service/scripts')
