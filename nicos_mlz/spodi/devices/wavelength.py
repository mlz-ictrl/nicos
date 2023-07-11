# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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

"""Wave length device for SPODI diffractometer."""

from math import asin, degrees, radians, sin

from nicos.core import SIMULATION, Attach, HasLimits, Moveable, Override, \
    Param, status
from nicos.core.errors import ConfigurationError, PositionError
from nicos.core.utils import multiStatus


class Wavelength(HasLimits, Moveable):
    """Device for adjusting initial/final wavelength."""

    parameters = {
        'crystal': Param('Used crystal',
                         type=str, unit='', settable=False, volatile=True,
                         category='instrument'),
        'plane': Param('Used scattering plane of the crystal', type=str,
                       unit='', mandatory=True, settable=True,
                       category='instrument'),
    }

    parameter_overrides = {
        'unit': Override(volatile=True),
    }

    attached_devices = {
        'tthm': Attach('Monochromator 2 theta', Moveable),
        'omgm': Attach('Monochromator table', Moveable),
        'crystal': Attach('The crystal switcher', Moveable),
    }

    valuetype = float

    hardware_access = False

    _lut = {
        'Ge': {
            '331': [1.299194, 9.45, 0.65],
            '551': [0.792778, 0.0, 0.65],
            '771': [0.568937, -4.37, 0.65]
        },
    }

    def _crystal(self, maxage=0):
        return self._lut.get(self._attached_crystal.read(maxage), {})

    def _d(self, maxage=0):
        p = self._crystal(maxage).get(self.plane, [])
        if p:
            return p[0]
        raise PositionError('No valid setup of the monochromator')

    def doInit(self, mode):
        crystal = self._crystal(0)
        if crystal:
            if 'plane' not in self._params:
                self._params['plane'] = p = crystal.values()[1]
                if self._mode != SIMULATION:
                    self._cache.put(self, 'plane', p)

    def doStatus(self, maxage=0):
        state = multiStatus(self._adevs, maxage)
        if state[0] != status.OK:
            return state
        try:
            self._d(maxage)
            return status.OK, 'idle'
        except PositionError as e:
            return status.ERROR, str(e)

    def doRead(self, maxage=0):
        mono = self._attached_tthm.read(maxage)
        return 2 * self._d(maxage) * sin(radians(mono / 2))

    def doStart(self, target):
        crystal = self._crystal(0)
        plane = crystal.get(self.plane, None)
        if not plane:
            raise ConfigurationError(self, 'No valid mono configuration')
        tthm = degrees(asin(target / (2 * self._d(0))))
        omgm = tthm / 2.0 + plane[1] + plane[2]
        self.log.debug('%s will be moved to %.3f', self._attached_tthm, tthm)
        self.log.debug('%s will be moved to %.3f', self._attached_omgm, omgm)
        if self._attached_tthm.isAllowed(tthm) and \
           self._attached_omgm.isAllowed(omgm):
            self._attached_tthm.start(tthm)
            self._attached_omgm.start(omgm)

    def doReadUnit(self):
        return 'AA'

    def doReadCrystal(self):
        crystal = self._attached_crystal.read(0)
        if crystal in self._lut:
            return crystal
        return None

    def doWritePlane(self, target):
        crystal = self._crystal(0)
        if not crystal.get(target):
            raise ValueError(
                'The "%s" plane is not allowed for "%s" crystal' % (
                    target, self.crystal))
        return target
