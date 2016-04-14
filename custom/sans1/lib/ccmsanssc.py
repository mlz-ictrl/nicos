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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Axis with brake control for SANS-1 sample changer sword."""

from time import sleep

from nicos.core import Attach, Moveable, Param, anytype, tupleof, status
from nicos.devices.generic.axis import Axis


class SwordAxis(Axis):

    attached_devices = {
        'switch': Attach('The device used for switching the brake', Moveable),
    }

    parameters = {
        'startdelay':   Param('Delay after switching on brake', type=float,
                              mandatory=True, unit='s'),
        'stopdelay':    Param('Delay before switching off brake', type=float,
                              mandatory=True, unit='s'),
        'switchvalues': Param('(on, off) values to write to brake switch',
                              type=tupleof(anytype, anytype), default=(2, 1)),
    }

    def doStatus(self, maxage=0):
        stval, ststr = Axis.doStatus(self, maxage)
        # special case: the Phytron server correctly returns an error if the
        # enable bit is not set, but since this is always the case we want to
        # present it as just a WARN state
        if stval == status.ERROR and ststr == 'motor halted, ENABLE not set':
            return status.WARN, ststr
        return stval, ststr

    def doTime(self, start, end):
        return Axis.doTime(self, start, end) + self.startdelay + self.stopdelay

    def _preMoveAction(self):
        self._adevs['switch'].maw(self.switchvalues[1])
        sleep(self.startdelay)

    def _postMoveAction(self):
        sleep(self.stopdelay)
        self._adevs['switch'].maw(self.switchvalues[0])
