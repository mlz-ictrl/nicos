#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

import time
import os
from os import path

from nicos.devices.experiment import Experiment
from nicos.utils import readFile, writeFile


class AmorExperiment(Experiment):
    """Follow the current file structure used in AMOR"""

    def proposalpath_of(self, proposal):
        return path.join(self.dataroot, 'nicos', time.strftime('%Y'), proposal)

    @property
    def samplepath(self):
        if self.sampledir:
            return path.join(self.proposalpath, self.sampledir)
        return self.proposalpath

    @property
    def scriptpath(self):
        return path.join(self.dataroot, 'nicos', 'scripts')

    @property
    def datapath(self):
        return path.join(self.dataroot, 'data', time.strftime('%Y'))

    #
    # Following configurations make SICS and NICOS have same counters.
    #

    @property
    def sicscounterfile(self):
        return path.join(self.datapath, 'DataNumber')

    def updateSicsCounterFile(self, value):
        """Update the amor counter file."""
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
        except IOError:
            self.updateSicsCounterFile(0)
            return 0
        if lines:
            return int(lines[0].strip())

        # the counter is not yet in the file
        return 0
