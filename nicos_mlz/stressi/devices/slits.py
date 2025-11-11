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

"""STRESS-SPEC specific slit devices."""

from nicos.core.errors import InvalidValueError
from nicos.core.mixins import HasPrecision
from nicos.core.params import Attach, Override, tupleof
from nicos.devices.generic.manual import ManualSwitch
from nicos.devices.generic.slit import FixedCenterSlitAxis, Gap, SizeGapAxis, \
    SlitAxis, TwoAxisSlit


class OffCenteredXSlitAxis(SlitAxis):

    def _convertRead(self, positions):
        return positions[0]

    def _convertStart(self, target, current):
        return target, current[1], current[2], current[3]


class OffCenteredYSlitAxis(SlitAxis):

    def _convertRead(self, positions):
        return positions[1]

    def _convertStart(self, target, current):
        return current[0], target, current[2], current[3]


class OffCenteredWidthSlitAxis(SlitAxis):

    def _convertRead(self, positions):
        return positions[2]

    def _convertStart(self, target, current):
        return current[0], current[1], target, current[3]


class OffCenteredHeightSlitAxis(SlitAxis):

    def _convertRead(self, positions):
        return positions[3]

    def _convertStart(self, target, current):
        return current[0], current[1], current[2], target


class OffCenteredTwoAxisSlit(TwoAxisSlit):
    """Special slit which as 4 independent axes for center and opening.

    It can move the center position and the openings but not the individual
    blades.  The blades will be moved pairwise in horizontal or vertical
    direction.

    There are several motors:
        x - horizontal translation of the whole slit hardware
        y - vertical translation of the whole slit hardware
        horizontal - horizontal opening (width)
        vertical - vertical opening (height)

    """

    attached_devices = {
        'x': Attach('Center x', HasPrecision),
        'y': Attach('Center y', HasPrecision),
    }

    parameter_overrides = {
        'fmtstr': Override(default='(%.2f, %.2f) %.2f x %.2f'),
        'opmode': Override(settable=False, volatile=True),
    }

    valuetype = tupleof(float, float, float, float)

    def _init_adevs(self):
        self._autodevs = [
            ('centerx', OffCenteredXSlitAxis),
            ('width', OffCenteredWidthSlitAxis),
            ('centery', OffCenteredYSlitAxis),
            ('height', OffCenteredHeightSlitAxis),
        ]
        self._axes = [
            self._attached_x, self._attached_y,
            self._attached_horizontal, self._attached_vertical,
        ]
        self._axnames = [
            'x', 'y',
            'horizontal', 'vertical',
        ]

    def _doIsAllowedPositions(self, positions):
        if len(positions) != 4:
            raise InvalidValueError(self, 'arguments required for offcentered '
                                    'mode: [x, y, width, height]')
        for ax, axname, pos in zip(self._axes, self._axnames, positions):
            ok, why = ax.isAllowed(pos)
            if not ok:
                return ok, '[%s slit] %s' % (axname, why)
        return True, ''

    def doReadOpmode(self):
        return 'offcentered'

    def doUpdateOpmode(self, value):
        self.valuetype = tupleof(float, float, float, float)

    def _doReadPositions(self, maxage):
        return [d.read(maxage) for d in self._axes]

    def _doStartPositions(self, positions):
        for dev, t in zip(self._axes, positions):
            dev.move(t)


class SingleAxisGap(Gap):
    """A special gap driven by a single motor.

    The motor drives both blades simulataneously away or towards the center (0)

    All instances have attributes controlling single dimensions that can be
    used as devices, for example in scans.  These attributes are:

    * `width` -- aliases for the opening of the gap

    Example usage::

        >>> scan(slit.width, 0, 1, 6)  # scan over slit width from 0 to 5 mm
    """

    valuetype = float

    attached_devices = {
        'moveable': Attach('Device driving the blades', HasPrecision),
    }

    parameter_overrides = {
        'opmode': Override(settable=False, volatile=True),
        'fmtstr': Override(default='%.2f'),
    }

    def _init_adevs(self):
        self._autodevs = [
            ('center', FixedCenterSlitAxis),
            ('width', SizeGapAxis),
        ]
        self._axes = [self._attached_moveable, ]
        self._axnames = ['moveable']

    def _doIsAllowedPositions(self, positions):
        pos = positions[1] - positions[0]
        ax = self._axes[0]
        axname = self._axnames[0]
        ok, why = ax.isAllowed(pos)
        if not ok:
            return ok, '[%s blade] %s' % (axname, why)
        return self._isAllowedSlitOpening(positions)

    def doReadOpmode(self):
        return 'centered'

    def doRead(self, maxage=0):
        positions = self._doReadPositions(maxage)
        return positions[1] - positions[0]

    def _getPositions(self, target):
        if isinstance(target, (list, tuple)):
            return target
        return [-target / 2, target / 2]

    def _doReadPositions(self, maxage):
        p = self._attached_moveable.read(maxage)
        return [-p / 2, p / 2]

    def _doStartPositions(self, positions):
        self._attached_moveable.move(positions[1] - positions[0])

    def doUpdateOpmode(self, value):
        self.valuetype = float


class PreciseManualSwitch(HasPrecision, ManualSwitch):

    parameter_overrides = {
        'precision': Override(mandatory=False, default=0),
    }
