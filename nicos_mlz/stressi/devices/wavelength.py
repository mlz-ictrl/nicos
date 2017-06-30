#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""Wave length device for STRESS-SPEC diffractometer."""

from math import asin, pi, sin

from nicos.core import Attach, HasLimits, HasPrecision, Moveable, Override, \
    Param, SIMULATION, status
from nicos.core.errors import ConfigurationError, PositionError
from nicos.devices.generic import Switcher

from nicos_mlz.stressi.devices.mixins import TransformMove


class TransformedMoveable(HasPrecision, TransformMove, Moveable):
    """Moveable transforming the data from and to a Moveable."""

    valuetype = float

    hardware_access = True


class Wavelength(HasLimits, Moveable):
    """Device for adjusting initial/final wavelength."""

    parameters = {
        'crystal': Param('Used crystal',
                         type=str, unit='', settable=True, volatile=True,
                         category='instrument'),
        'plane': Param('Used scattering plane of the crystal', type=str,
                       unit='', mandatory=True, settable=True,
                       category='instrument'),
    }

    parameter_overrides = {
        'unit': Override(volatile=True),
    }

    attached_devices = {
        'omgm': Attach('Monochromator table', Moveable),
        'base': Attach('Device to move', Moveable),
        'crystal': Attach('The crystal switcher', Switcher),
    }

    valuetype = float

    hardware_access = False

    _lut = {'Ge': {'311': [1.7058, 9.45, 0.65],
                   '511': [1.08879, 0.0, 0.65],
                   '711': [0.79221, -4.37, 0.65]},
            # 511, 400, 311
            'Si': {'511': [1.0452, 15.79, 0.45],
                   '400': [1.35773, 0.0, 0.45],
                   '311': [1.6376, 25.24, 0.45]},
            # 400, 200, 600
            'PG': {'400': [1.6771, 0.0, 0.0],
                   '200': [3.3542, 0.0, 0.0],
                   '600': [1.11807, 0.0, 0.0]},
            }

    def _crystal(self):
        return self._lut[self.crystal] if self.crystal in self._lut else None

    def _d(self, maxage=0):
        crystal = self._crystal()
        if crystal:
            p = crystal.get(self.plane, None)
            if p:
                return p[0]
            raise ConfigurationError('No plane of the crystal set.')
        raise ConfigurationError('No crystal set.')

    def doInit(self, mode):
        crystal = self._crystal()
        if crystal:
            if not self.plane:
                self._params['plane'] = p = sorted(crystal.keys())[0]
                if self._mode != SIMULATION:
                    self._cache.put(self, 'plane', p)

    def doStatus(self, maxage=0):
        for dev in (self._attached_base, self._attached_omgm,
                    self._attached_crystal):
            ok, why = dev.status(maxage)
            if ok != status.OK:
                return ok, '%s: %s' % (dev, why)
        try:
            self._d(maxage)
            return status.OK, 'idle'
        except ConfigurationError as e:
            return status.ERROR, e.message

    def doRead(self, maxage=0):
        try:
            mono = self._attached_base.read(maxage)
            return 2 * self._d(maxage) * sin(mono * pi / (2 * 180.))
        except ConfigurationError:
            return None

    def doStart(self, target):
        crystal = self._crystal()
        if not crystal:
            raise ConfigurationError(self, 'Not valid setup')
        plane = crystal.get(self.plane, None)
        if not plane:
            raise ConfigurationError(self, 'No valid mono configuration')
        tthm = asin(target / (2 * self._d())) / pi * 360.
        omgm = tthm / 2.0 + plane[1] + plane[2]
        self.log.debug(self._attached_base, 'will be moved to %.3f' % tthm)
        self.log.debug(self._attached_omgm, 'will be moved to %.3f' % omgm)
        if self._attached_base.isAllowed(tthm) and \
           self._attached_omgm.isAllowed(omgm):
            self._attached_base.start(tthm)
            self._attached_omgm.start(omgm)

    def doReadUnit(self):
        return 'AA'

    def doReadCrystal(self):
        try:
            crystal = self._attached_crystal.read(0)
            return crystal if crystal in self._lut else None
        except PositionError:
            return None

    def doWriteCrystal(self, value):
        self._attached_crystal.move(value)
        return value

    def doWritePlane(self, target):
        crystal = self._crystal()
        if crystal:
            if not crystal.get(target, None):
                raise ValueError('The "%s" plane is not allowed for "%s" '
                                 'crystal' % (target, crystal))
        else:
            raise ConfigurationError('No valid setup of the monochromator')
        return target
