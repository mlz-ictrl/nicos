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

from __future__ import absolute_import, division, print_function

import os
import time
from os import path

from nicos.core import Override
from nicos.devices.experiment import Experiment
from nicos.pycompat import string_types
from nicos.utils import readFile, writeFile


class SinqExperiment(Experiment):
    """Follow the current file structure used in SINQ"""

    parameter_overrides = {
        'propprefix': Override(default=''),
        'reporttemplate': Override(default=''),
        'serviceexp': Override(default='Service'),
        'sendmail': Override(default=False),
        'zipdata': Override(default=False),
    }

    def proposalpath_of(self, proposal):
        if self.proposalpath:
            return self.proposalpath
        proposal = proposal.replace(' ', '')
        return path.join(self.dataroot, 'proposals', time.strftime('%Y'),
                         proposal)

    @property
    def datapath(self):
        return path.join(self.dataroot, 'data', time.strftime('%Y'))

    def getProposalType(self, proposal):
        proposalstr = proposal
        if not isinstance(proposalstr, string_types):
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
        return path.join(self.datapath, 'DataNumber')

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
        except IOError:
            self.updateSicsCounterFile(0)
            return 0
        if lines:
            return int(lines[0].strip())

        # the counter is not yet in the file
        return 0
