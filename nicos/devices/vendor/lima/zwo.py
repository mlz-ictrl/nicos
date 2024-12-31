# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************
"""Special classes for ZWO cameras."""

from nicos.core import HasLimits, HasPrecision, Moveable, status
from nicos.devices.tango import PyTangoDevice

from .optional import LimaCooler


class ZwoTC(PyTangoDevice, HasLimits, HasPrecision, LimaCooler, Moveable):
    """This device controls the cooling of Zwo cameras."""

    def doRead(self, maxage=0):
        return self._dev.temperature

    def doStatus(self, maxage=0):
        coolerState = self._dev.cooler
        temperature = self.doRead()
        sp = self._dev.temperature_sp

        nicosState = status.UNKNOWN

        if self.doReadCooleron():
            if abs(temperature - sp) < self.precision:
                nicosState = status.OK
            else:
                nicosState = status.BUSY
        else:
            if temperature > 10:
                nicosState = status.OK
            else:
                nicosState = status.BUSY

        return (nicosState, coolerState)

    def doStart(self, target):
        if target > 10:
            self.cooler = 'OFF'
        else:
            self._dev.temperature_sp = target
            self.cooler = 'ON'

    def doVersion(self):
        return [(self.tangodevice,
                 f'tango {self._dev.get_tango_lib_version() / 100:.02f}')]
