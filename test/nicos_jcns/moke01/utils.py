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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

from nicos.core import Param
from nicos.devices.generic import VirtualMotor


class VirtualSensor(VirtualMotor):

    parameters = {
        'testqueue': Param(
            'Values for tests',
            type=list, settable=True, default=[],
        ),
        'simulate': Param(
            'Flag for being tested',
            type=bool, settable=True, default=False,
        ),
    }

    def doInit(self, mode):
        VirtualMotor.doInit(self, mode)
        self._i = -1

    def doRead(self, maxage=0):
        if self.simulate:
            self._i += 1
            return self.testqueue[self._i] or VirtualMotor.doRead(self, maxage)
        else:
            return VirtualMotor.doRead(self, maxage)

    def readStd(self, _):
        return 0


class VirtualPS(VirtualMotor):

    def doStart(self, target):
        self.ramp = 0
        VirtualMotor.doStart(self, target)

    def doStop(self):
        self.ramp = 0
        VirtualMotor.doStop(self)

    def doReadRamp(self):
        return 400.0
