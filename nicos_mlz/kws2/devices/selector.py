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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Special class for KWS 2 selector, which can be tilted."""

from nicos.core import Moveable, Readable, Attach, Param, Override, dictof, \
    dictwith, tupleof
from nicos_mlz.kws1.devices.selector import SelectorSwitcher as \
    KWS1SelectorSwitcher


class SelectorLambda(Moveable):
    """
    Control selector wavelength directly, converting between speed and
    wavelength.

    This uses not the default conversion from the Astrium selector classes,
    since the selector is tilted against the beam, and it is easier to use
    the constant determined by wavelength calibration.

    This class allows two calibration settings, determined by the current
    value of a (manually moved) "tilt" device.
    """

    parameters = {
        'constants': Param('Conversion constants: '
                           'lam[Ang] = constant/speed[Hz] + offset',
                           type=tupleof(float, float),
                           mandatory=True, unit='Ang Hz'),
        'offsets':   Param('Conversion offsets: '
                           'lam[Ang] = constant/speed[Hz] + offset',
                           type=tupleof(float, float),
                           mandatory=True, unit='Ang'),
    }

    attached_devices = {
        'seldev':  Attach('The selector speed device', Moveable),
        'tiltdev': Attach('The tilt device', Readable),
    }

    hardware_access = False

    def doRead(self, maxage=0):
        tilted = bool(self._attached_tiltdev.read(maxage))
        speed = self._attached_seldev.read(maxage)
        return (60 * self.constants[tilted] / speed) + self.offsets[tilted] \
            if speed else -1

    def doIsAllowed(self, value):
        if value == 0:
            return False, 'zero wavelength not allowed'
        tilted = bool(self._attached_tiltdev.read(0))
        speed = int(round(60 * self.constants[tilted] /
                    (value - self.offsets[tilted])))
        return self._attached_seldev.isAllowed(speed)

    def doStart(self, value):
        tilted = bool(self._attached_tiltdev.read(0))
        speed = int(round(60 * self.constants[tilted] /
                    (value - self.offsets[tilted])))
        self.log.debug('moving selector to %f rpm', speed)
        self._attached_seldev.start(speed)


class SelectorSwitcher(KWS1SelectorSwitcher):
    """Switcher whose mapping is determined by a list of presets."""

    parameter_overrides = {
        'presets':  Override(type=dictof(str, dictwith(lam=float, speed=float,
                                                       spread=float, tilted=bool))),
    }
