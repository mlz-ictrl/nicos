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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************

"""Focus class for PUMA."""

from nicos.core import Param
from nicos.devices.generic.axis import Axis


class FocusAxis(Axis):
    """Special Axis for the monochromator and analyser focus."""

    parameters = {
        'uplimit': Param('The upper limit',
                         type=float, unit='deg', settable=False),
        'lowlimit': Param('The upper limit',
                          type=float, unit='deg', settable=False),
        'startpos': Param('The backlash position',
                          type=float, unit='deg', settable=False),
        'flatpos': Param('The flat position',
                         type=float, unit='deg', settable=False),
    }

    def doStart(self, target):
        if target == 0:
            target = self.flatpos
        elif target > self.uplimit:
            target = self.uplimit
        elif target < self.lowlimit:
            target = self.lowlimit
        if self.target != target:
            self._setROParam('target', target)

        # This is the calculation of a dynamic changing backlash
        # If a blacklash is needed, it should start from the 'startpos' value
        curpos = self.read(0)
        direct = (target - curpos) * (curpos - self.startpos)
        if direct < 0:
            self.backlash = self.startpos - target
        else:
            self.backlash = 0
        self.log.debug('backlash is now: %.3f', self.backlash)
        Axis.doStart(self, target)
