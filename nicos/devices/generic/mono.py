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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************
"""
Base monochromator class
"""

import sys
from math import asin, degrees, pi, radians, sin, sqrt

from nicos.core import MASTER, SIMULATION, Attach, ComputationError, \
    HasLimits, Moveable, Override, Param, ProgrammingError, oneof, status
from nicos.core.errors import ConfigurationError
from nicos.core.params import floatrange, tupleof
from nicos.core.utils import multiStatus

THZ2MEV = 4.1356675
ANG2MEV = 81.804165
SPEED_1A = 3956.03401207


def from_k(value, unit):
    try:
        if unit == 'A-1':
            return value
        elif unit == 'A':
            return 2.0 * pi / value
        elif unit == 'meV':
            return ANG2MEV * value ** 2 / (2 * pi) ** 2
        elif unit == 'THz':
            return ANG2MEV / THZ2MEV * value ** 2 / (2 * pi) ** 2
        elif unit == 'm/s':  # not useful for TAS but for TOF
            return SPEED_1A * value / (2 * pi)
        else:
            raise ProgrammingError('unknown energy unit %r' % unit)
    except (ArithmeticError, ValueError) as err:
        raise ComputationError(
            'cannot convert %s A-1 to %s: %s' % (value, unit, err)) from None


def to_k(value, unit):
    try:
        if unit == 'A-1':
            return value
        elif unit == 'A':
            return 2.0 * pi / value
        elif unit == 'meV':
            return 2.0 * pi * sqrt(value / ANG2MEV)
        elif unit == 'THz':
            return 2.0 * pi * sqrt(value * THZ2MEV / ANG2MEV)
        elif unit == 'm/s':
            return 2.0 * pi * value / SPEED_1A
        else:
            raise ProgrammingError('unknown energy unit %r' % unit)
    except (ArithmeticError, ValueError) as err:
        raise ComputationError(
            'cannot convert %s A-1 to %s: %s' % (value, unit, err)) from None


class Monochromator(Moveable):
    """General monochromator device.

    It supports setting the `unit` parameter to different values.

    * "A-1" -- wavevector in inverse Angstrom
    * "A" -- wavelength in Angstrom
    * "meV" -- energy in meV
    * "THz" -- energy in THz

    """

    hardware_access = False

    parameter_overrides = {
        'unit': Override(default='A-1', type=oneof('A-1', 'A', 'meV', 'THz'),
                         chatty=True),
        'fmtstr': Override(default='%.3f'),
    }

    def doInit(self, mode):
        if ('target' not in self._params or not self.target or
           self.target == 'unknown'):
            self._setROParam('target', from_k(to_k(0.73, 'A'), self.unit))

    def doStart(self, target):
        self._sim_setValue(target)

    def doIsAllowed(self, pos):
        return True, ''

    def doRead(self, maxage=0):
        return self.target

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doReadPrecision(self):
        return 0

    def doWriteUnit(self, value):
        if self._cache:
            self._cache.invalidate(self, 'value')

    def doUpdateUnit(self, value):
        if 'unit' not in self._params:
            # this is the initial update
            return
        if self._mode not in (MASTER, SIMULATION):
            # change limits only from the master copy, or in simulation mode
            return
        if 'target' in self._params and self.target and self.target != 'unknown':
            # this should be still within the limits
            self._setROParam(
                'target', from_k(to_k(self.target, self.unit), value))
        self.read(0)


# This dict contains the possible used reflections of a monochromator material
# For each of the reflection the distance of the scattering planes is given
# in Angstroem as first element of the corresponding list. The other parameters
# of the list are unused at the moment.

crystals = {
    'CoFe': {
    },
    'Cu': {
        (1, 1, 1): [2.08717, 0.0, 0.0],
        (2, 2, 0): [1.278, 0.0, 0.0],
        (4, 2, 0): [0.8072, 0.0, 0.0],
        (4, 2, 2): [0.7375, 0.0, 0.0],
    },
    'Diamond': {
    },
    'Fe3Si': {
    },
    'Ge': {
        (3, 1, 1): [1.7058, 9.45, 0.65],
        (3, 3, 1): [1.299194, 9.45, 0.65],
        (4, 2, 2): [1.140, 0.0, 0.0],
        (5, 1, 1): [1.08879, 0.0, 0.65],
        (5, 3, 3): [0.855, 0.0, 0.0],
        (5, 5, 1): [0.792778, 0.0, 0.65],
        (7, 1, 1): [0.79221, -4.37, 0.65],
        (7, 7, 1): [0.568937, -4.37, 0.65],
    },
    'Heusler': {
        (1, 1, 1): [3.355, 0.0, 0.0],
    },
    'Multilayer': {
    },
    'PG': {
        (0, 0, 2): [3.3542, 0.0, 0.0],
        (0, 0, 4): [1.6771, 0.0, 0.0],
        (0, 0, 6): [1.11807, 0.0, 0.0],
    },
    'Si': {
        (1, 1, 1): [3.13, 0.0, 0.0],
        (3, 1, 1): [1.6376, 25.24, 0.45],
        (4, 0, 0): [1.35773, 0.0, 0.45],
        (5, 1, 1): [1.0452, 15.79, 0.45],
    },
}


class CrystalMonochromator(HasLimits, Monochromator):
    """Device to adjust wavelength using Bragg reflection via a crystal."""

    valuetype = float

    hardware_access = False

    parameters = {
        'material': Param('Used crystal',
                          type=oneof(*crystals), unit='', settable=True,
                          category='instrument'),
        'reflection': Param('Used hkl parameter of the reflection',
                            type=tupleof(int, int, int), unit='',
                            mandatory=True, settable=True,
                            category='instrument'),
        'd': Param('d value of the used reflection',
                   type=floatrange(0), volatile=True, userparam=True,
                   category='instrument'),
    }

    parameter_overrides = {
        'unit': Override(default='A', type=oneof('A', 'AA'), mandatory=False),
        'abslimits': Override(volatile=True, mandatory=False),
    }

    attached_devices = {
        'theta': Attach('Monochromator rocking angle', Moveable),
        'twotheta': Attach('Monochromator scattering angle', Moveable),
    }

    @property
    def theta(self):
        return self._attached_theta

    @property
    def ttheta(self):
        return self._attached_twotheta

    def _crystal(self, maxage=0):
        # maxage is foreseen for a device with changing the crystal hardware
        return crystals.get(self.material)

    def doReadD(self):
        if crystal := self._crystal(0):
            if p := crystal.get(self.reflection):
                return p[0]
            raise ConfigurationError('No plane of the crystal set.')
        raise ConfigurationError('No crystal set.')

    def doStatus(self, maxage=0):
        ok, why = multiStatus(self._adevs, maxage)
        if ok != status.OK:
            return ok, why
        try:
            _ = self.d  # check simply the crystal configuration
            return status.OK, 'idle'
        except ConfigurationError as e:
            return status.ERROR, str(e)

    def doRead(self, maxage=0):
        try:
            mono = self.ttheta.read(maxage)
            return 2 * self.d * sin(radians(mono / 2))
        except ConfigurationError:
            return None

    def _calc_angles(self, target):
        th = degrees(asin(target / (2 * self.d)))
        tt = 2 * th  # + plane[1] + plane[2]
        return tt, th

    def doIsAllowed(self, pos):
        tt, th = self._calc_angles(pos)
        for d, t in zip([self.ttheta, self.theta], [tt, th]):
            ok, why = d.isAllowed(t)
            if not ok:
                return ok, f'{d} to {t}: {why}'
        return True, ''

    def doStart(self, target):
        tt, th = self._calc_angles(target)
        self.log.debug('%s will be moved to %.3f', self.theta, th)
        self.log.debug('%s will be moved to %.3f', self.ttheta, tt)
        self.ttheta.start(tt)
        self.theta.start(th)

    def doWriteMaterial(self, value):
        # The simple way so set the reflection is not working due to the
        # doWriteReflection method which requires the change of the crystal
        # first
        self._params['reflection'] = next(iter(crystals[value]))

    def doWriteReflection(self, target):
        if crystal := self._crystal():
            if crystal.get(target) is None:
                raise ValueError('The "%s" plane is not allowed for "%s" '
                                 'crystal' % (target, self.material))
            return target
        raise ConfigurationError('No valid setup of the monochromator')

    def doReadAbslimits(self):
        deflimits = (0, sys.float_info.max)
        th_limits = self.theta.userlimits if isinstance(self.theta, HasLimits) else deflimits
        tt_limits = self.ttheta.userlimits if isinstance(self.ttheta, HasLimits) else deflimits
        th_limits = tuple(2 * self.d * sin(radians(t)) for t in th_limits)
        tt_limits = tuple(2 * self.d * sin(radians(t / 2)) for t in tt_limits)
        self.log.debug(
            'theta limits: %s two theta limits: %s', th_limits, tt_limits)
        return (max(th_limits[0], tt_limits[0]),
                min(th_limits[1], tt_limits[1]))
