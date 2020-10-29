#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@tum.de>
#
# *****************************************************************************

"""LASCON pyrometer temperature devices."""

from nicos.core import HasLimits, HasWindowTimeout, Moveable, MoveError, \
    Param, PositionError, Readable, oneof, status
from nicos.devices.tango import StringIO


class TemperatureSensor(StringIO, Readable):
    """LASCON pyrometer temperature sensor device."""

    def doRead(self, maxage=0):
        return float(self.communicate('GetTemp 1').split()[3])


class TemperatureController(HasWindowTimeout, HasLimits, StringIO, Moveable):
    """LASCON pyrometer temperature controller device."""

    parameters = {
        'setpoint': Param('Current temperature setpoint', unit='main',
                          category='general'),
        'timeoutaction': Param('What to do when a timeout occurs',
                               type=oneof('continue', 'raise'), settable=True),
    }

    @property
    def errorstates(self):
        return {status.ERROR: MoveError, status.NOTREACHED: PositionError} \
            if self.timeoutaction == 'raise' else {status.ERROR: MoveError}

    def doStart(self, target):
        self.writeLine('SetSTemp 1 0 %f' % target)

    def doPoll(self, n, maxage):
        self._pollParam('setpoint', 1)

    def doTime(self, oldvalue, newvalue):
        return self.window

    def doRead(self, maxage=0):
        return float(self.communicate('GetTemp 1 0').split()[3])

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doStop(self):
        self.start(self.doRead(0))

    def doReadSetpoint(self):
        return float(self.communicate('GetSTemp 1').split()[3])
