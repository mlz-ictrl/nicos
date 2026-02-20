# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
from nicos.core.device import Attach, Moveable, Param
from nicos.devices.abstract import TransformedMoveable


class SANSWL(TransformedMoveable):
    """
    Class for calculating and running the velocity selector wavelength.
    The formula is:
        wl = a  + b/rpm

    where a and b are constants.
    """

    hardware_access = False

    parameters = {
        'a': Param('Additive constant for the wavelength calculation',
                   type=float, settable=False),
        'b': Param('Constant numerator for the wavelength equation',
                   type=float, settable=False),
        'fwhm': Param('FWHM of the wavelength', type=float, default=11.6),
    }

    attached_devices = {
        'speed': Attach('Device which controls the VS speed',
                        Moveable),
    }

    def _startRaw(self, target):
        self._attached_speed.start(target)

    def _mapTargetValue(self, target):
        return 1./((target - self.a)/self.b)

    def doStatus(self, maxage=0):
        return self._attached_speed.status(maxage)

    def _readRaw(self, maxage=0):
        return self._attached_speed.read(maxage)

    def _mapReadValue(self, value):
        return self.a + self.b/value
