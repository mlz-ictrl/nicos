# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

"""NICOS slit device."""

from nicos import session
from nicos.core import Attach, AutoDevice, HasAutoDevices, HasPrecision, \
    InvalidValueError, Moveable, Override, Param, UsageError, Value, dictof, \
    multiReset, multiStatus, multiWait, oneof, tupleof
from nicos.core.utils import devIter, multiReference
from nicos.devices.abstract import CanReference


class Gap(HasAutoDevices, CanReference, Moveable):
    """Base class for gap devices consisting of two blades."""

    parameters = {
        'opmode': Param(
            'Mode of operation',
            type=oneof('2blades', '2blades_opposite',
                       'centered', 'offcentered'),
            settable=True,
        ),
        'coordinates': Param(
            'Coordinate convention for left/right blades',
            type=oneof('equal', 'opposite'),
            default='equal',
        ),
        'fmtstr_map': Param(
            'A dictionary mapping operation modes to format strings (used for '
            'internal management).',
            type=dictof(str, str),
            settable=False,
            mandatory=False,
            userparam=False,
            default={'2blades': '%.2f %.2f', '2blades_opposite': '%.2f %.2f',
                     'centered': '%.2f', 'offcentered': '%.2f, %.2f'},
        ),
        'parallel_ref': Param(
            'Set to True if the blades\' reference drive can be done in '
            'parallel.',
            type=bool,
            default=False,
        ),
    }

    parameter_overrides = {
        'fmtstr': Override(volatile=True),
        'unit': Override(mandatory=False),
    }

    valuetype = tupleof(float, float)

    hardware_access = False

    _delay = 0.25  # delay between starting to move opposite blades

    def _init_adevs(self):
        raise NotImplementedError

    def doInit(self, _mode):
        self._init_adevs()
        for name in self._axnames:
            self.__dict__[name] = self._adevs[name]
        for name, cls in self._autodevs:
            self.add_autodevice(name, cls, slit=self, unit=self.unit,
                                visibility=self.autodevice_visibility)

    def _getPositions(self, target):
        if self.opmode.endswith('blades'):
            if len(target) != 2:
                raise InvalidValueError(self, 'arguments required for '
                                        f'2-blades mode: {self._axnames}')
            positions = list(target)
        elif self.opmode.endswith('blades_opposite'):
            if len(target) != 2:
                raise InvalidValueError(self, 'arguments required for '
                                        f'2-blades mode: {self._axnames}')
            positions = [-target[0], target[1]]
        elif self.opmode == 'centered':
            if len(target) != 1:
                raise InvalidValueError(self, 'arguments required for '
                                        'centered mode: '
                                        f'[{self._autodevs[1][0]}]')
            positions = [-target[0] / 2, target[0] / 2]
        else:
            if len(target) != 2:
                raise InvalidValueError(self, 'arguments required for '
                                        'off-centered mode: '
                                        f'{[ad[0] for ad in self._autodevs]}')
            positions = [target[0] - target[1] / 2, target[0] + target[1] / 2]
        return positions

    def doIsAllowed(self, target):
        return self._doIsAllowedPositions(self._getPositions(target))

    def _isAllowedSlitOpening(self, positions):
        ok, why = True, ''
        if positions[1] < positions[0]:
            ok, why = False, 'gap is negative'
        return ok, why

    def _doIsAllowedPositions(self, positions):
        f = self.coordinates == 'opposite' and -1 or +1
        for ax, axname, pos in zip(self._axes, self._axnames, positions):
            if axname in ('left', 'bottom'):
                pos *= f
            ok, why = ax.isAllowed(pos)
            if not ok:
                return ok, '[%s blade] %s' % (axname, why)
        return self._isAllowedSlitOpening(positions)

    def doStart(self, target):
        self._doStartPositions(self._getPositions(target))

    def _doStartPositions(self, positions):
        raise NotImplementedError

    def _doStartGap(self, target, alb, art):
        f = self.coordinates == 'opposite' and -1 or +1
        tlb, trt = target
        # determine which axis to move first, so that the blades can
        # not touch when one moves first
        clb, crt = alb.read(0), art.read(0)
        clb *= f
        if trt < crt and tlb < clb:
            # both move to smaller values, need to start left/bottom blade
            # first
            alb.move(tlb * f)
            session.delay(self._delay)
            art.move(trt)
        elif trt > crt and tlb > clb:
            # both move to larger values, need to start right/top blade first
            art.move(trt)
            session.delay(self._delay)
            alb.move(tlb * f)
        else:
            # don't care
            art.move(trt)
            alb.move(tlb * f)

    def doReset(self):
        multiReset(self._axes)
        multiWait(self._axes)

    def doReference(self):
        multiReference(self, self._axes, self.parallel_ref)

    def _doReadPositions(self, maxage):
        clb, crt = [d.read(maxage) for d in self._axes]
        if self.coordinates == 'opposite':
            clb *= -1
        return [clb, crt]

    def doRead(self, maxage=0):
        positions = self._doReadPositions(maxage)
        lb, rt = positions
        if self.opmode == 'centered':
            if abs((lb + rt) / 2) > self._axes[0].precision:
                self.log.warning('slit seems to be off-centered, but is '
                                 'set to "centered" mode')
            return [rt - lb]
        elif self.opmode == 'offcentered':
            return [(lb + rt) / 2, rt - lb]
        elif self.opmode == '2blades_opposite':
            return [-lb, rt]
        else:
            return positions

    def doPoll(self, n, maxage):
        # also poll sub-AutoDevices we created
        for dev in devIter(self.__dict__, baseclass=AutoDevice):
            dev.poll(n, maxage)

    def valueInfo(self):
        vnames = []
        if self.opmode.endswith('centered'):
            if self.opmode.startswith('off'):
                vnames += [center[0] for center in self._autodevs[::2]]
            vnames += list(size[0] for size in self._autodevs[1::2])
        else:
            vnames = self._axnames
        return tuple(Value(f'{self}.{vn}', unit=self.unit, fmtstr='%.2f')
                     for vn in vnames)

    def doStatus(self, maxage=0):
        return multiStatus(list(zip(self._axnames, self._axes)), maxage)

    def doWriteFmtstr(self, value):
        # since self.fmtstr_map is a readonly dict a temp. copy is created
        # to update the dict and then put to cache back
        tmp = dict(self.fmtstr_map)
        tmp[self.opmode] = value
        self._setROParam('fmtstr_map', tmp)

    def doReadFmtstr(self):
        return self.fmtstr_map[self.opmode]

    def doWriteOpmode(self, value):
        if self._cache:
            self._cache.invalidate(self, 'value')
            self._cache.put(self, 'fmtstr', self.fmtstr_map[value])

    def doUpdateOpmode(self, value):
        if value == 'centered':
            self.valuetype = tupleof(float)
        else:
            self.valuetype = tupleof(float, float)


class HorizontalGap(Gap):
    """A rectangular horizontal gap consisting of 2 blades.

    The gap can operate in four "opmodes", controlled by the `opmode`
    parameter:

    * '2blades' -- both blades are controlled separately.  Values read from the
      gap are lists in the order ``[left, right]``; for ``move()`` the same
      list of coordinates has to be supplied.
    * '2blades_opposite' -- like '2blades', but left/right opposite coordinate
      systems, i.e. [5, 5] is an opening of 10.
    * 'centered' -- only width is controlled; the gap is centered at the zero
      value of the left-right coordinates.  Values read and written are in the
      form ``[width]``.
    * 'offcentered' -- the center and width are controlled.  Values are read
      and written are in the form ``[center, width]``.

    Normally, the lower level ``right`` and ``left`` devices need to share a
    common coordinate system, i.e. when ``right.read() == left.read()`` the gap
    is closed.  A different convention can be selected when setting
    `coordinates` to ``"opposite"``: in this case, the blades meet at
    coordinate 0, and both move in positive direction when they open.

    All instances have attributes controlling single dimensions that can be
    used as devices, for example in scans.  These attributes are:

    * `left`, `right` -- controlling the blades individually, independent of
      the opmode
    * `center`, `width` -- controlling "logical" coordinates of the gap,
      independent of the opmode

    Example usage::

        >>> move(gap.center, 5)       # move gap center
        >>> scan(gap.width, 0, 1, 6)  # scan over slit width from 0 to 5 mm
    """

    attached_devices = {
        'left': Attach('Left blade', HasPrecision),
        'right': Attach('Right blade', HasPrecision),
    }

    def _init_adevs(self):
        self._autodevs = [('center', CenterGapAxis), ('width', SizeGapAxis)]
        self._axes = [self._attached_left, self._attached_right]
        self._axnames = ['left', 'right']

    def _doStartPositions(self, positions):
        self._doStartGap(positions, self._attached_left, self._attached_right)

    def doReadUnit(self):
        return self._attached_left.unit


class VerticalGap(Gap):
    """A rectangular vertical gap consisting of 2 blades.

    The gap can operate in four "opmodes", controlled by the `opmode`
    parameter:

    * '2blades' -- both blades are controlled separately.  Values read from the
      gap are lists in the order ``[bottom, top]``; for ``move()`` the same
      list of coordinates has to be supplied.
    * '2blades_opposite' -- like '2blades', but bottom/top opposite coordinate
      systems, i.e. [5, 5] is an opening of 10.
    * 'centered' -- only height is controlled; the gap is centered at the zero
      value of the top-bottom coordinates.  Values read and written are in the
      form ``[height]``.
    * 'offcentered' -- the center and height are controlled.  Values are read
      and written are in the form ``[center, height]``.

    Normally, the lower level ``top`` and ``bottom`` devices need to share a
    common coordinate system, i.e. when ``top.read() == bottom.read()`` the gap
    is closed.  A different convention can be selected when setting
    `coordinates` to ``"opposite"``: in this case, the blades meet at
    coordinate 0, and both move in positive direction when they open.

    All instances have attributes controlling single dimensions that can be
    used as devices, for example in scans.  These attributes are:

    * `bottom`, `top` -- controlling the blades individually, independent of
      the opmode
    * `center`, `height` -- controlling "logical" coordinates of the gap,
      independent of the opmode

    Example usage::

        >>> move(gap.center, 5)        # move gap center
        >>> scan(gap.height, 0, 1, 6)  # scan over gap height from 0 to 5 mm
    """

    attached_devices = {
        'bottom': Attach('Bottom blade', HasPrecision),
        'top': Attach('Top blade', HasPrecision),
    }

    def _init_adevs(self):
        self._autodevs = [('center', CenterGapAxis), ('height', SizeGapAxis)]
        self._axes = [self._attached_bottom, self._attached_top]
        self._axnames = ['bottom', 'top']

    def _doStartPositions(self, positions):
        self._doStartGap(positions, self._attached_bottom, self._attached_top)

    def doReadUnit(self):
        return self._attached_bottom.unit


class Slit(HorizontalGap, VerticalGap):
    """A rectangular slit consisting of four blades.

    The slit can operate in four "opmodes", controlled by the `opmode`
    parameter:

    * '4blades' -- all four blades are controlled separately.  Values read from
      the slit are lists in the order ``[left, right, bottom, top]``; for
      ``move()`` the same list of coordinates has to be supplied.
    * '4blades_opposite' -- like '4blades', but left/right and bottom/top have
      opposite coordinate systems, i.e. [5, 5, 5, 5] is an opening of 10x10.
    * 'centered' -- only width and height are controlled; the slit is centered
      at the zero value of the left-right and bottom-top coordinates.  Values
      read and written are in the form ``[width, height]``.
    * 'offcentered' -- the center and width/height are controlled.  Values read
      and written are in the form ``[centerx, centery, width, height]``.

    Normally, the lower level ``right`` and ``left`` as well as the ``bottom``
    and ``top`` devices need to share a common coordinate system, i.e. when
    ``right.read() == left.read()`` the slit is closed.  A different convention
    can be selected when setting `coordinates` to ``"opposite"``: in this case,
    the blades meet at coordinate 0, and both move in positive direction when
    they open.

    All instances have attributes controlling single dimensions that can be used
    as devices, for example in scans.  These attributes are:

    * `left`, `right`, `bottom`, `top` -- controlling the blades individually,
      independent of the opmode
    * `centerx`, `centery`, `width`, `height` -- controlling "logical"
      coordinates of the slit, independent of the opmode

    Example usage::

        >>> move(slit.centerx, 5)      # move slit center
        >>> scan(slit.width, 0, 1, 6)  # scan over slit width from 0 to 5 mm
    """

    parameter_overrides = {
        'opmode': Override(
            type=oneof('4blades', '4blades_opposite',
                       'centered', 'offcentered'),
            default='4blades',
        ),
        'coordinates': Override(
            description='Coordinate convention for left/right and top/bottom '
                        'blades',
        ),
        'fmtstr_map': Override(
            default={'4blades': '%.2f %.2f %.2f %.2f',
                     '4blades_opposite': '%.2f %.2f %.2f %.2f',
                     'centered': '%.2f x %.2f',
                     'offcentered': '(%.2f, %.2f) %.2f x %.2f'},
        ),
    }

    valuetype = tupleof(float, float, float, float)

    def _init_adevs(self):
        self._autodevs = [('centerx', CenterXSlitAxis),
                          ('width', WidthSlitAxis),
                          ('centery', CenterYSlitAxis),
                          ('height', HeightSlitAxis)]
        self._axes = [self._attached_left, self._attached_right,
                      self._attached_bottom, self._attached_top]
        self._axnames = ['left', 'right', 'bottom', 'top']

    def _getPositions(self, target):
        if self.opmode.startswith('4blades'):
            if len(target) != 4:
                raise InvalidValueError(self, 'arguments required for '
                                        f'4-blades mode: {self._axnames}')
            positions = (HorizontalGap._getPositions(self, target[:2])
                         + VerticalGap._getPositions(self, target[2:]))
        elif self.opmode == 'centered':
            if len(target) != 2:
                raise InvalidValueError(self, 'arguments required for '
                                        'centered mode: [width, height]')
            positions = (HorizontalGap._getPositions(self, target[:1])
                         + VerticalGap._getPositions(self, target[1:]))
        else:
            if len(target) != 4:
                raise InvalidValueError(self, 'arguments required for off-'
                                        'centered mode: [xcenter, ycenter, '
                                        'width, height]')
            positions = (HorizontalGap._getPositions(self, target[::2])
                         + VerticalGap._getPositions(self, target[1::2]))
        return positions

    def _isAllowedSlitOpening(self, positions):
        if positions[1] < positions[0]:
            return False, 'horizontal slit opening is negative'
        elif positions[3] < positions[2]:
            return False, 'vertical slit opening is negative'
        return True, ''

    def _doStartPositions(self, positions):
        HorizontalGap._doStartPositions(self, positions[:2])
        VerticalGap._doStartPositions(self, positions[2:])

    def _doReadPositions(self, maxage):
        cl, cr, cb, ct = [d.read(maxage) for d in self._axes]
        if self.coordinates == 'opposite':
            cl *= -1
            cb *= -1
        return [cl, cr, cb, ct]

    def doRead(self, maxage=0):
        positions = self._doReadPositions(maxage)
        l, r, b, t = positions
        if self.opmode == 'centered':
            if abs((l + r) / 2) > self._attached_left.precision or \
               abs((t + b) / 2) > self._attached_top.precision:
                self.log.warning('slit seems to be off-centered, but is '
                                 'set to "centered" mode')
            return [r - l, t - b]
        elif self.opmode == 'offcentered':
            return [(l + r) / 2, (t + b) / 2, r - l, t - b]
        elif self.opmode == '4blades_opposite':
            return [-l, r, -b, t]
        else:
            return positions

    def doUpdateOpmode(self, value):
        if value == 'centered':
            self.valuetype = tupleof(float, float)
        else:
            self.valuetype = tupleof(float, float, float, float)


class SlitAxis(AutoDevice, Moveable):
    """
    "Partial" devices for slit axes, useful for e.g. scanning
    over the device slit.centerx.
    """

    attached_devices = {
        'slit': Attach('Slit whose axis is controlled', Gap),
    }

    valuetype = float

    hardware_access = False

    def doRead(self, maxage=0):
        positions = self._attached_slit._doReadPositions(maxage)
        return self._convertRead(positions)

    def doStart(self, target):
        currentpos = self._attached_slit._doReadPositions(0.1)
        positions = self._convertStart(target, currentpos)
        self._attached_slit._doStartPositions(positions)

    def doIsAllowed(self, target):
        currentpos = self._attached_slit._doReadPositions(0.1)
        positions = self._convertStart(target, currentpos)
        return self._attached_slit._doIsAllowedPositions(positions)


class CenterGapAxis(SlitAxis):

    def doStart(self, target):
        if self._attached_slit.opmode == 'centered':
            raise UsageError('moving center in "centered" mode is not allowed')
        SlitAxis.doStart(self, target)

    def _convertRead(self, positions):
        return (positions[0] + positions[1]) / 2

    def _convertStart(self, target, current):
        gap = current[1] - current[0]
        return target - gap / 2, target + gap / 2


class CenterXSlitAxis(CenterGapAxis):

    def _convertRead(self, positions):
        return (positions[0] + positions[1]) / 2

    def _convertStart(self, target, current):
        width = current[1] - current[0]
        return target - width / 2, target + width / 2, current[2], current[3]


class CenterYSlitAxis(CenterGapAxis):

    def _convertRead(self, positions):
        return (positions[2] + positions[3]) / 2

    def _convertStart(self, target, current):
        height = current[3] - current[2]
        return current[0], current[1], target - height / 2, target + height / 2


class SizeGapAxis(SlitAxis):

    def _convertRead(self, positions):
        return positions[1] - positions[0]

    def _convertStart(self, target, current):
        center = (current[0] + current[1]) / 2
        return center - target / 2, center + target / 2


class WidthSlitAxis(SlitAxis):

    def _convertRead(self, positions):
        return positions[1] - positions[0]

    def _convertStart(self, target, current):
        centerx = (current[0] + current[1]) / 2.
        return (centerx - target / 2, centerx + target / 2,
                current[2], current[3])


class HeightSlitAxis(SlitAxis):

    def _convertRead(self, positions):
        return positions[3] - positions[2]

    def _convertStart(self, target, current):
        centery = (current[2] + current[3]) / 2
        return (current[0], current[1],
                centery - target / 2, centery + target / 2)


class TwoAxisSlit(CanReference, Moveable):
    """A rectangular slit consisting of 2 orthogonal slits.

    All instances have attributes controlling single dimensions that can be used
    as devices, for example in scans.  These attributes are:

    * `width`, `height` -- aliases for the horizontal and vertical slits

    Example usage::

        >>> scan(slit.width, 0, 1, 6)  # scan over slit width from 0 to 5 mm
    """

    attached_devices = {
        'horizontal': Attach('Horizontal slit', HasPrecision),
        'vertical':   Attach('Vertical slit', HasPrecision),
    }

    parameters = {
        'parallel_ref': Param('Set to True if the blades\' reference drive '
                              'can be done in parallel.', type=bool,
                              default=False),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%.2f %.2f'),
        'unit': Override(mandatory=False),
    }

    valuetype = tupleof(float, float)

    hardware_access = False

    def doInit(self, _mode):
        self._slits = [self._attached_horizontal, self._attached_vertical]
        self._slitnames = ['horizontal', 'vertical']

        for name in self._slitnames:
            self.__dict__[name] = self._adevs[name]
        self.__dict__['width'] = self.horizontal
        self.__dict__['height'] = self.vertical

    def doIsAllowed(self, target):
        if len(target) != 2:
            raise InvalidValueError(self, 'arguments required for centered '
                                    'mode: [width, height]')
        for slit, slitname, pos in zip(self._slits, self._slitnames, target):
            ok, why = slit.isAllowed(pos)
            if not ok:
                return ok, '[%s slit] %s' % (slitname, why)
        return True, ''

    def doStart(self, target):
        th, tv = target
        self._attached_horizontal.move(th)
        self._attached_vertical.move(tv)

    def doReset(self):
        for ax in self._slits:
            ax.reset()
        for ax in self._slits:
            ax.wait()

    def doReference(self):
        multiReference(self, self._slits, self.parallel_ref)

    def doRead(self, maxage=0):
        return [d.read(maxage) for d in self._slits]

    def valueInfo(self):
        return Value('%s.width' % self, unit=self.unit, fmtstr='%.2f'), \
            Value('%s.height' % self, unit=self.unit, fmtstr='%.2f')

    def doStatus(self, maxage=0):
        return multiStatus(list(zip(self._slitnames, self._slits)))

    def doReadUnit(self):
        return self._attached_horizontal.unit
