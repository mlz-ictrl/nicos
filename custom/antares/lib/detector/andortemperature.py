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

from nicos.core import HasLimits, HasPrecision, Moveable, status, \
    waitForStatus

from nicos.antares.detector.pytangodevice import PyTangoDevice


class AndorTemperature(PyTangoDevice, HasLimits, HasPrecision, Moveable):

    def doRead(self, maxage=0):
        return self._tangoGetAttrGuard('temperature')

    def doStatus(self, maxage=0):
        coolerState = self._tangoGetAttrGuard('cooler')
        temperature = self.doRead()
        sp = self._tangoGetAttrGuard('temperature_sp')

        nicosState = status.UNKNOWN

        if coolerState == 'ON':
            if abs(temperature - sp) < self.precision:
                nicosState = status.OK
            else:
                nicosState = status.BUSY
        else:
            if temperature > -10:
                nicosState = status.OK
            else:
                nicosState = status.BUSY

        return (nicosState, coolerState)

    def doStart(self, value):

        if value > -10:
            self._tangoSetAttrGuard('cooler', 'OFF')
        else:
            self._tangoSetAttrGuard('temperature_sp', value)
            self._tangoSetAttrGuard('cooler', 'ON')

    def doStop(self):
        temperature = self.doRead()

        if temperature < -10:
            self.doStart(temperature)
        else:
            self._tangoSetAttrGuard('cooler', 'OFF')

    def doWait(self):
        waitForStatus(self)
