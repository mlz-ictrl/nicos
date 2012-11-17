#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS PANDA Experiment."""

from __future__ import with_statement

__version__ = "$Revision$"

import time
from os import path

from nicos.core import Override, UsageError
from nicos.frm2.experiment import Experiment


class PandaExperiment(Experiment):

    parameter_overrides = {
        'propprefix':    Override(default='p'),
        'templatedir':   Override(default='exp/template'),
        'servicescript': Override(default='start_service.py'),
    }

    def _getProposalDir(self, proposal):
        return path.join(self.dataroot, 'exp', proposal)

    def _getProposalSymlink(self, proposal):
        return path.join(self.dataroot, 'exp', 'current')

    def _getDatapath(self, proposal):
        return [
            path.join(self.dataroot, 'exp', proposal, 'data'),
            path.join(self.dataroot, time.strftime('%Y'),
                      'cycle_%s' % self.cycle),
        ]

    def _getProposalType(self, proposal):
        if proposal in ('template', 'current'):
            raise UsageError(self, 'The proposal names "template" and "current"'
                             ' are reserved and cannot be used')
        return Experiment._getProposalType(self, proposal)
