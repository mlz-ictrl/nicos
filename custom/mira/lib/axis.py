#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Airpad axis for MIRA."""

from time import sleep

from nicos.core import Attach, Moveable, Param, anytype, tupleof
from nicos.devices.generic.axis import Axis


class HoveringAxis(Axis):
    """An axis that also controls air for airpads."""

    attached_devices = {
        'switch': Attach('The device used for switching air on and off',
                         Moveable),
    }

    parameters = {
        'startdelay':   Param('Delay after switching on air', type=float,
                              mandatory=True, unit='s'),
        'stopdelay':    Param('Delay before switching off air', type=float,
                              mandatory=True, unit='s'),
        'switchvalues': Param('(off, on) values to write to switch device',
                              type=tupleof(anytype, anytype), default=(0, 1)),
    }

    def doTime(self, start, end):
        return Axis.doTime(self, start, end) + self.startdelay + self.stopdelay

    def _preMoveAction(self):
        self._adevs['switch'].maw(self.switchvalues[1])
        sleep(self.startdelay)

    def _postMoveAction(self):
        sleep(self.stopdelay)
        self._adevs['switch'].maw(self.switchvalues[0])
