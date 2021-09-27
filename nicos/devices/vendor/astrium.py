#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Astrium selector device."""

from math import atan, pi, radians, tan

from nicos.core import Attach, Moveable, Param, Readable, status
from nicos.core.mixins import HasPrecision


class SelectorLambda(HasPrecision, Moveable):
    """
    Control selector wavelength directly, converting between speed and
    wavelength.
    """

    parameters = {
        'twistangle': Param('Blade twist angle', mandatory=True, unit='deg'),
        'length':     Param('Selector length', mandatory=True, unit='m'),
        'beamcenter': Param('Beam center position', mandatory=True, unit='m'),
        'maxspeed':   Param('Max selector speed', mandatory=True, unit='rpm'),
    }

    attached_devices = {
        'seldev':  Attach('The selector speed device', Moveable),
        'tiltdev': Attach('The tilt angle motor, if present', Moveable,
                          optional=True),
    }

    hardware_access = False

    def _get_tilt(self, maxage):
        if self._attached_tiltdev:
            return self._attached_tiltdev.read(maxage)
        return 0

    def _constant(self, tiltang=0):
        """Calculate the inverse proportional constant between speed (in rpm)
        and wavelength (in A), depending on the tilt angle (in degrees).

        Formula adapted from Astrium NVS C++ source code.
        """
        v0 = 3955.98
        lambda0 = self.twistangle * 60 * v0 / (360 * self.length * self.maxspeed)
        A = 2 * self.beamcenter * pi / (60 * v0)
        return (tan(radians(tiltang)) + (A * self.maxspeed * lambda0)) / \
            (-A**2 * self.maxspeed * lambda0 * tan(radians(tiltang)) + A)

    def doRead(self, maxage=0):
        spd = self._attached_seldev.read(maxage)
        return self._constant(self._get_tilt(maxage)) / spd if spd else -1

    def doIsAllowed(self, value):
        if value == 0:
            return False, 'zero wavelength not allowed'
        speed = int(self._constant(self._get_tilt(0)) / value)
        allowed, why = self._attached_seldev.isAllowed(speed)
        if not allowed:
            why = 'requested %d rpm, %s' % (speed, why)
        return allowed, why

    def doStart(self, target):
        if self.isAtTarget(target=target):
            return
        speed = int(self._constant(self._get_tilt(0)) / target)
        self.log.debug('moving selector to %d rpm', speed)
        self._attached_seldev.start(speed)


class SelectorLambdaSpread(Readable):
    """
    Returns the calculated wavelength spread.
    """

    parameters = {
        'n_lamellae': Param('Number of lamellae', mandatory=True, unit=''),
        'd_lamellae': Param('Thickness of a lamella', mandatory=True,
                            unit='mm'),
        'diameter':   Param('Rotor diameter', mandatory=True, unit='m'),
    }

    attached_devices = {
        'lamdev': Attach('The wavelength device', SelectorLambda),
    }

    def doRead(self, maxage=0):
        lamdev = self._attached_lamdev
        tilt = lamdev._get_tilt(maxage)
        eff_twistangle = lamdev.twistangle + \
            tilt * lamdev.length / lamdev.beamcenter
        spread = atan((2*pi / self.n_lamellae) -
                      (2 * self.d_lamellae / self.diameter)) / eff_twistangle
        return 100 * spread

    def doStatus(self, maxage=0):
        return status.OK, ''
