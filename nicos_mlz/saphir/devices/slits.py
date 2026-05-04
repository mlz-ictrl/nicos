# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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

from math import cos, radians, sin

from nicos.core.errors import InvalidValueError
from nicos.core.mixins import HasPrecision
from nicos.core.params import Attach, Override, Param, Value, floatrange, \
    oneof, tupleof
from nicos.core.utils import multiStatus
from nicos.devices.generic.slit import CenterXSlitAxis, CenterYSlitAxis, Gap, \
    HeightSlitAxis, WidthSlitAxis


class LSlit(Gap):
    """A rectangular slit consisting of 2 L shaped blades.

    The movement devices are on a virtual axis, which goes through the center
    of the opening.  This axis is going under a certain angle against the x
    direction.

    All instances have attributes controlling single dimensions that can be
    used as devices, for example in scans.  These attributes are:

    * `width`, `height` -- aliases for the horizontal and vertical slits
    * `centerx`, `centery` -- aliases for the origin axes

    Example usage::

        >>> scan(slit.width, 0, 1, 6)  # scan over slit width from 0 to 5 mm

    .. automethod:: doRead
    """

    attached_devices = {
        'm1': Attach('Bottom motor', HasPrecision),
        'm2': Attach('Upper motor', HasPrecision),
    }

    parameters = {
        'angle': Param('Angle of the axes for L shaped blades',
                       type=floatrange(0, 90), default=45,
                       )
    }

    parameter_overrides = {
        'fmtstr_map': Override(default={
                                'centered': '%.2f x %.2f',
                                'offcentered': '(%.2f, %.2f) %.2f x %.2f'
                                }),
        'unit': Override(mandatory=False),
        'opmode': Override(type=oneof('centered', 'offcentered'),
                           default='centered'),
        'coordinates': Override(default='opposite'),
    }

    valuetype = tupleof(float, float, float, float)

    hardware_access = False

    def _init_adevs(self):
        self._autodevs = [
            ('centerx', CenterXSlitAxis),
            ('width', WidthSlitAxis),
            ('centery', CenterYSlitAxis),
            ('height', HeightSlitAxis),
        ]
        self._axes = [self._attached_m1, self._attached_m2]
        self._axnames = ['m1', 'm2']

    def _isAllowedSlitOpening(self, positions):
        """Check if the opening, given by the axes positions, is valid."""
        for opening in positions[-2:]:
            if opening < self.min_opening:
                if self.min_opening > 0:
                    return False, 'opening is too small'
                if self.min_opening == 0:
                    return False, 'opening is negative'
                return False, 'overlap is too big'
        return True, ''

    def _doIsAllowedPositions(self, positions):
        for ax, axname, pos in zip(self._axes, self._axnames, positions):
            ok, why = ax.isAllowed(pos)
            if not ok:
                return ok, f'[{axname} slit]: {why}'
        return True, ''

    def doIsAllowed(self, target):
        positions = self._getPositions(target)
        ok, why = self._isAllowedSlitOpening(target)
        if not ok:
            return ok, why
        return self._doIsAllowedPositions(positions)

    def doRead(self, maxage=0):
        """Read the current value according to the operation mode.

        The method calls:

        .. automethod:: _doReadPositions
        """
        positions = self._doReadPositions(maxage)
        l, r, b, t = positions
        if self.opmode == 'centered':
            if abs((l + r) / 2) > self._attached_m1.precision or \
               abs((t + b) / 2) > self._attached_m2.precision:
                self.log.warning('slit seems to be off-centered, but is '
                                 'set to "centered" mode')
            return [r - l, t - b]
        return [(l + r) / 2, (t + b) / 2, r - l, t - b]

    def _doStartPositions(self, positions):
        m1, m2 = positions
        self._attached_m1.move(m1)
        self._attached_m2.move(m2)

    def _getPositions(self, target):
        if self.opmode == 'centered':
            if len(target) != 2:
                raise InvalidValueError(self, 'arguments required for '
                                        'centered mode: [width, height]')
            w, _h = target
            m1 = m2 = w / (2 * cos(radians(self.angle)))
        else:
            if len(target) != 4:
                raise InvalidValueError(self, 'arguments required for off-'
                                        'centered mode: [xcenter, ycenter, '
                                        'width, height]')
            x, _y, w, _h = target
            m1 = (w / 2 - x) / cos(radians(self.angle))
            m2 = (w / 2 + x) / cos(radians(self.angle))
        return [m1, m2]

    def _doReadPositions(self, maxage):
        m1 = self._attached_m1.read(maxage)
        cl = m1 * cos(radians(self.angle))
        cb = m1 * sin(radians(self.angle))
        m2 = self._attached_m2.read(maxage)
        cr = m2 * cos(radians(self.angle))
        ct = m2 * sin(radians(self.angle))
        if self.coordinates == 'opposite':
            cl *= -1
            cb *= -1
        return [cl, cr, cb, ct]

    def valueInfo(self):
        vnames = []
        if self.opmode.startswith('off'):
            vnames += [center[0] for center in self._autodevs[::2]]
        vnames += [size[0] for size in self._autodevs[1::2]]
        return tuple(Value(f'{self}.{vn}', unit=self.unit, fmtstr='%.2f')
                     for vn in vnames)

    def doStatus(self, maxage=0):
        return multiStatus(list(zip(self._axnames, self._axes)))

    def doReadUnit(self):
        return self._attached_m1.unit

    def doUpdateOpmode(self, value):
        if value == 'centered':
            self.valuetype = tupleof(float, float)
        else:
            self.valuetype = tupleof(float, float, float, float)
