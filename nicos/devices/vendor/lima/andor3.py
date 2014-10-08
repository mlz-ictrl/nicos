# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import status, HasLimits, HasPrecision, Moveable
from nicos.devices.tango import PyTangoDevice
from .optional import LimaCooler


class Andor3TemperatureController(PyTangoDevice,
                                  HasLimits, HasPrecision, LimaCooler, Moveable):
    """
    This devices provides access to the cooling feature of Andor3 cameras.
    """

    COOLER_STATUS_MAP = {
        'Fault' : status.ERROR,
        'Drift' : status.ERROR,
        'Cooler Off' : status.OK,
        'Stabilised' : status.OK,
        'Cooling' : status.BUSY,
        'Not Stabilised' : status.BUSY
    }

    def doRead(self, maxage=0):
        return self._dev.temperature

    def doStatus(self, maxage=0):  #pylint: disable=W0221
        coolerState = self._dev.cooling_status
        nicosState = self.COOLER_STATUS_MAP.get(coolerState, status.UNKNOWN)

        return (nicosState, coolerState)

    def doStart(self, value):
        self._dev.temperature_sp = value
        self.doWriteCooleron(True)

