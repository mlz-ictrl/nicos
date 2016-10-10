#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

from math import pi, sin, asin

from nicos.core import Attach, HasLimits, Moveable, Override, Param, \
    PositionError, status
from nicos.core.params import floatrange
from nicos.devices.generic import Switcher


class Wavelength(HasLimits, Moveable):
    """Device for adjusting initial/final wavelength."""

    parameters = {
        'precision': Param('Precision of the device value (allowed deviation '
                           'of stable values from target)', unit='deg',
                           type=floatrange(0), default=0.005,
                           settable=True, category='precisions'),
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

    # Since the real tthm value differs from the displayed value at the PLC the
    # value must be corrected via:
    # y = m * x + n
    # we use the following values for m and n:
    _m = 1.0 / 0.959
    _n = -11.5 / 0.956

    _lut = {
            # the combinations are the 311, 511, 711
            'Ge': [(48.01841, 1.7058), (38.56841, 1.08879),
                   (34.19841, 0.79221)],
            # 511, 400, 311
            'Si': [(54.15841, 1.0452), (38.36841, 1.35773),
                   (63.60841, 1.6376)],
            # The PG monochromator gives all 3 reflexes at a single position
            # we prefer the value for the (400)
            # 400, 200, 600
            'PG': [(38.56841, 1.6771), (38.56841, 3.3542),
                   (38.56841, 1.11807)],
            }

    def _isAt(self, target, value):
        self.log.debug('%f - %f : %f' % (target, value, self.precision))
        ret = abs(target - value) <= self.precision
        self.log.debug('%r' % ret)
        return ret

    def _d(self, maxage=0):
        self._crystal = self._attached_crystal.read(maxage)
        self._omgm = self._attached_omgm.read(maxage)
        if self._crystal in self._lut:
            for omg, d in self._lut[self._crystal]:
                if self._isAt(omg, self._omgm):
                    return d
        raise PositionError('No valid setup of the monochromator')

    def _getWaiters(self):
        return [self._attached_base]

    def doStatus(self, maxage=0):
        for dev in (self._attached_base, self._attached_omgm,
                    self._attached_crystal):
            state = dev.status(maxage)
            if state[0] != status.OK:
                return state
        try:
            self._d(maxage)
            return status.OK, 'idle'
        except PositionError as e:
            return status.ERROR, e.message

    def doRead(self, maxage=0):
        try:
            mono = self._m * self._attached_base.read(maxage) + self._n
            return 2 * self._d(maxage) * sin(mono * pi / (2 * 180.))
        except PositionError:
            return None

    def doStart(self, target):
        mono = (asin(target / (2 * self._d(0))) / pi * 360. - self._n) / self._m
        self.log.info(self._attached_base, 'would be moved to %.3f' % mono)
        # self._attached_base.start(mono)

    def doStop(self):
        # self._attached_base.stop()
        pass

    def doReadUnit(self):
        return 'AA'
