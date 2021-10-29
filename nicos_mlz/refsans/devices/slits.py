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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special devices for Refsans slits."""

import numpy as np

from nicos import session
from nicos.core import SIMULATION, Attach, AutoDevice, HasPrecision, \
    Moveable, Override, Param, Value, dictof, dictwith, floatrange, \
    multiReset, multiStatus, multiWait, oneof, status, tupleof
from nicos.core.errors import MoveError, UsageError
from nicos.core.mixins import HasOffset
from nicos.core.utils import devIter, multiReference
from nicos.devices.abstract import CanReference
from nicos.devices.generic import ManualSwitch
from nicos.devices.generic.sequence import SeqDev, SequencerMixin
from nicos.utils import lazy_property

from nicos_mlz.refsans.devices.mixins import PseudoNOK

SLIT = 'slit'
POINT = 'point'
GISANS = 'gisans'
MODES = [SLIT, POINT, GISANS]
CENTERED = 'centered'


class SingleSlit(PseudoNOK, HasOffset, Moveable):
    """Slit using one axis."""

    hardware_access = False

    attached_devices = {
        'motor': Attach('moving motor', Moveable),
    }

    parameters = {
        'mode': Param('Beam mode',
                      type=oneof(*MODES), settable=True, userparam=True,
                      default='slit', category='general'),
        '_offsets': Param('List of offsets per mode position',
                          settable=False, internal=True,
                          type=dictof(str, float), default={}),
        'opmode': Param('Mode of operation for the slit',
                        type=oneof(CENTERED), userparam=True, settable=True,
                        default=CENTERED, category='experiment'),
    }

    parameter_overrides = {
        'masks': Override(type=dictwith(**{name: float for name in MODES}),
                          unit='', mandatory=True),
    }

    valuetype = float

    def doWriteOffset(self, value):
        HasOffset.doWriteOffset(self, value)
        # deep copy is need to be able to change the values
        d = self._offsets.copy()
        d[self.mode] = value
        self._setROParam('_offsets', d)

    def doRead(self, maxage=0):
        return self._attached_motor.read(maxage) - self.masks[self.mode] - \
            self.offset

    def doIsAllowed(self, target):
        return self._attached_motor.isAllowed(target + self.masks[self.mode])

    def doStop(self):
        self._attached_motor.stop()

    def doStart(self, target):
        self._attached_motor.start(
            target + self.masks[self.mode] + self.offset)

    def doWriteMode(self, mode):
        self._attached_motor.start(self._attached_motor.read(0) +
                                   self.masks[mode] - self.masks[self.mode])
        # update the offset parameter from offset mapping
        self._setROParam('offset', self._offsets.get(mode, 0.))
        self.log.debug('New offset is now: %f', self.offset)


class DoubleSlit(PseudoNOK, Moveable):
    """Double slit using two SingleSlits."""

    hardware_access = False

    attached_devices = {
        'slit_r': Attach('Reactor side single slit', SingleSlit),
        'slit_s': Attach('Sample side single slit', SingleSlit),
    }

    parameters = {
        'mode': Param('Modus of Beam',
                      type=oneof(*MODES), settable=True, userparam=True,
                      default='slit', category='experiment'),
        'maxheight': Param('Max opening of the slit',
                           type=floatrange(0), settable=False, default=12.),
        'opmode': Param('Mode of operation for the slit',
                        type=oneof(CENTERED),  # '2blades' is possible
                        userparam=True, settable=True, default=CENTERED,
                        category='experiment'),
    }

    parameter_overrides = {
        'nok_start': Override(volatile=True),
        'nok_end': Override(volatile=True),
    }

    def doInit(self, mode):
        # Even if the slit could not be become closer then 0 and not more
        # opened the maxheight the instrument scientist want to scan over
        # the limits to find out the 'open' and 'closed' point for the neutrons
        self.valuetype = tupleof(floatrange(-1, self.maxheight + 1), float)
        # generate auto devices
        for name, idx, opmode in [('height', 0, CENTERED),
                                  ('center', 1, CENTERED)]:
            self.__dict__[name] = SingleSlitAxis('%s.%s' % (self.name, name),
                                                 slit=self, unit=self.unit,
                                                 lowlevel=True, index=idx,
                                                 opmode=opmode)
        self._motors = [self._attached_slit_r, self._attached_slit_s]

    def doStatus(self, maxage=0):
        st = Moveable.doStatus(self, maxage)
        if st[0] == status.OK:
            return st[0], self.name  # display device name
        return st

    def doWriteMode(self, mode):
        for d in self._motors:
            d.mode = mode

    def _calculate_slits(self, arg, direction):
        self.log.debug('calculate slits: dir:%s mode:%s arg %s', direction,
                       self.mode, str(arg))
        if direction:
            reactor, sample = arg
            opening = self.maxheight - (sample - reactor)
            height = (sample + reactor) / 2.0
            res = [opening, height]
        else:
            opening, height = arg
            reactor = height - (self.maxheight - opening) / 2.0
            sample = height + (self.maxheight - opening) / 2.0
            res = [reactor, sample]
        self.log.debug('res %s', res)
        return res

    def doRead(self, maxage=0):
        return self._calculate_slits([self._attached_slit_r.read(maxage),
                                      self._attached_slit_s.read(maxage)],
                                     True)

    def doIsAllowed(self, targets):
        self.log.debug('DoubleSlit doIsAllowed %s', targets)
        why = []
        try:
            self.valuetype((targets[0], 0))
        except ValueError as e:
            why.append('%s' % e)
        for dev, pos in zip([self._attached_slit_r, self._attached_slit_s],
                            self._calculate_slits(targets, False)):
            ok, _why = dev.isAllowed(pos)
            if not ok:
                why.append('%s: requested position %.3f %s out of limits; %s'
                           % (dev, pos, dev.unit, _why))
            else:
                self.log.debug('%s: requested position %.3f %s allowed', dev,
                               pos, dev.unit)
        if why:
            return False, '; '.join(why)
        return True, ''

    def doStop(self):
        for dev in self._adevs.values():
            dev.stop()

    def doStart(self, targets):
        """Generate and start a sequence if none is running."""
        for dev, target in zip([self._attached_slit_r, self._attached_slit_s],
                               self._calculate_slits(targets, False)):
            dev.start(target)

    def doReadNok_Start(self):
        return self._attached_slit_r.nok_start

    def doReadNok_End(self):
        return self._attached_slit_s.nok_end

    def doPoll(self, n, maxage):
        # also poll sub-AutoDevices we created
        for dev in devIter(self.__dict__, baseclass=AutoDevice):
            dev.poll(n, maxage)

    def valueInfo(self):
        return (Value('%s.height' % self, unit=self.unit, fmtstr='%.2f'),
                Value('%s.center' % self, unit=self.unit, fmtstr='%.2f'))


class DoubleSlitSequence(SequencerMixin, DoubleSlit):

    attached_devices = {
        'adjustment': Attach('positioning Frame of b3h3', ManualSwitch),
    }

    def doStart(self, targets):
        """Generate and start a sequence if non is running.

        Just calls ``self._startSequence(self._generateSequence(target))``
        """
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])
        self._startSequence(self._generateSequence(targets))

    def doStatus(self, maxage=0):
        self.log.debug('DoubleSlitSequence status')
        st = SequencerMixin.doStatus(self, maxage)
        if st[0] != status.OK:
            return st
        st = DoubleSlit.doStatus(self, maxage=maxage)
        self.log.debug('DoubleSlitSequence status %s', st)
        if st[0] == status.OK:
            return st[0], self.name  # display device name
        return st

    def _generateSequence(self, target):
        """Generate and start a sequence if none is running.

        be sure not to cross the blades
        """

        self.log.debug('Frame %s %s', self._adjustment_offset(), target)

        center = self.center.read(0)
        dif = target[1] - center
        self.log.debug('safe %s dif %.2f center %.2f', target, dif, center)
        if True and False:  # pylint: disable=condition-evals-to-constant
            safe_seq = []
            step = (target[0] + .5001) * np.sign(dif)
            akt = center + step
            while True:
                if akt == target[1]:
                    safe_seq.append([target[0], akt])
                    break
                if dif > 0:
                    if akt > target[1]:
                        safe_seq.append([target[0], target[1]])
                        break
                else:
                    if akt < target[1]:
                        safe_seq.append([target[0], target[1]])
                        break
                safe_seq.append([target[0], akt])
                akt += step
            sequence = []
            for s in safe_seq:
                targets = self._calculate_slits(s, False)
                self.log.debug('seq  %s targets %s', s, targets)
                if dif > 0:
                    sequence += [
                        SeqDev(self._attached_slit_s, targets[1],
                               stoppable=True),
                        SeqDev(self._attached_slit_r, targets[0],
                               stoppable=True),
                    ]
                else:
                    sequence += [
                        SeqDev(self._attached_slit_r, targets[0],
                               stoppable=True),
                        SeqDev(self._attached_slit_s, targets[1],
                               stoppable=True),
                    ]
            self.log.info('Seq len: %d', len(sequence))
        else:
            targets = self._calculate_slits(target, False)
            if dif < 0:
                self.log.info('DoubleSlitSequence Seq swap')
                sequence = [
                    SeqDev(self._attached_slit_s, targets[1],
                           stoppable=True),
                    SeqDev(self._attached_slit_r, targets[0],
                           stoppable=True),
                ]
            else:
                self.log.info('DoubleSlitSequence Seq org')
                sequence = [
                    SeqDev(self._attached_slit_r, targets[0],
                           stoppable=True),
                    SeqDev(self._attached_slit_s, targets[1],
                           stoppable=True),
                ]
            self.log.debug('Seq_2: %r', sequence)
        return sequence

    def _adjustment_offset(self):
        return int(self._attached_adjustment.read(0)[:-2]) - 110

    def doRead(self, maxage=0):
        pos = DoubleSlit.doRead(self, maxage=maxage)
        self.log.debug('Frame %s %d', pos, self._adjustment_offset())
        return pos


class SingleSlitAxis(AutoDevice, Moveable):

    valuetype = float

    hardware_access = False

    attached_devices = {
        'slit': Attach('Slit whose axis is controlled', Moveable),
    }

    parameters = {
        'index': Param('Which index of the super slit is used for this device',
                       type=int, userparam=False),
        'opmode': Param('Mode of the super slit to be used for this device',
                        type=str, userparam=False, category='experiment'),
    }

    @lazy_property
    def slit(self):
        return self._attached_slit

    def _conv(self, target):
        """convert our target value to target values for the main slit axis"""
        pos = list(self.slit.target if self.slit.target else self.slit.read())
        pos[self.index] = target
        return tuple(pos)

    def doRead(self, maxage=0):
        """read main slit's raw values and convert to our opmode"""
        return self.slit.read(0)[self.index]

    def doStart(self, target):
        """convert our target value to target values for the main slit axis
         and start movement there"""
        self.slit.start(self._conv(target))

    def doIsAllowed(self, target):
        return self.slit.isAllowed(self._conv(target))


class Gap(CanReference, Moveable):
    """A rectangular gap consisting of 2 blades.

    The gap can operate in four "opmodes", controlled by the `opmode`
    parameter:

    * '2blades' -- both blades are controlled separately.  Values read from the
      slit are lists in the order ``[left, right]``; for ``move()`` the same
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

    parameters = {
        'opmode': Param('Mode of operation for the slit',
                        type=oneof('2blades', '2blades_opposite',
                                   'centered', 'offcentered'),
                        settable=True),
        'coordinates': Param('Coordinate convention for left/right and '
                             'top/bottom blades', default='equal',
                             type=oneof('equal', 'opposite')),
        'fmtstr_map': Param('A dictionary mapping operation modes to format '
                            'strings (used for internal management).',
                            type=dictof(str, str), settable=False,
                            mandatory=False, userparam=False,
                            default={
                                '2blades': '%.2f %.2f',
                                '2blades_opposite': '%.2f %.2f',
                                'centered': '%.2f',
                                'offcentered': '%.2f, %.2f',
                            }),
        'parallel_ref': Param('Set to True if the blades\' reference drive '
                              'can be done in parallel.', type=bool,
                              default=False),
    }

    parameter_overrides = {
        'fmtstr': Override(volatile=True),
        'unit': Override(mandatory=False),
    }

    valuetype = tupleof(float, float)

    hardware_access = False

    _delay = 0.25  # delay between starting to move opposite blades

    def doInit(self, mode):
        self._axes = [self._attached_left, self._attached_right]
        self._axnames = ['left', 'right']

        for name in self._axnames:
            self.__dict__[name] = self._adevs[name]

        for name, cls in [
            ('center', CenterGapAxis), ('width', WidthGapAxis),
        ]:
            self.__dict__[name] = cls('%s.%s' % (self.name, name), gap=self,
                                      unit=self.unit, lowlevel=True)

    def doShutdown(self):
        for name in ['center', 'width']:
            if name in self.__dict__:
                self.__dict__[name].shutdown()

    def _getPositions(self, target):
        if self.opmode == '2blades':
            # if len(target) != 2:
            #     raise InvalidValueError(self, 'arguments required for '
            #                             '2-blades mode: [left, right]')
            positions = list(target)
        elif self.opmode == '2blades_opposite':
            # if len(target) != 2:
            #     raise InvalidValueError(self, 'arguments required for '
            #                             '4-blades mode: [left, right]')
            positions = [-target[0], target[1]]
        elif self.opmode == 'centered':
            # if len(target) != 1:
            #     raise InvalidValueError(self, 'arguments required for '
            #                             'centered mode: [width]')
            positions = [-target[0] / 2, target[0] / 2]
        else:
            # if len(target) != 2:
            #     raise InvalidValueError(self, 'arguments required for '
            #                             'offcentered mode: [center, width]')
            positions = [target[0] - target[1] / 2, target[0] + target[1] / 2]
        return positions

    def doIsAllowed(self, target):
        return self._doIsAllowedPositions(self._getPositions(target))

    def _isAllowedSlitOpening(self, positions):
        ok, why = True, ''
        if positions[1] < positions[0]:
            ok, why = False, 'gap opening is negative'
        return ok, why

    def _doIsAllowedPositions(self, positions):
        f = self.coordinates == 'opposite' and -1 or +1
        for ax, axname, pos in zip(self._axes, self._axnames, positions):
            if axname in ('left'):
                pos *= f
            ok, why = ax.isAllowed(pos)
            if not ok:
                return ok, '[%s blade] %s' % (axname, why)
        return self._isAllowedSlitOpening(positions)

    def doStart(self, target):
        self._doStartPositions(self._getPositions(target))

    def _doStartPositions(self, positions):
        f = self.coordinates == 'opposite' and -1 or +1
        tl, tr = positions
        # determine which axes to move first, so that the blades can
        # not touch when one moves first
        cl, cr = self._doReadPositions(0)
        al, ar = self._axes
        if tr < cr and tl < cl:
            # both move to smaller values, need to start right blade first
            al.move(tl * f)
            session.delay(self._delay)
            ar.move(tr)
        elif tr > cr and tl > cl:
            # both move to larger values, need to start left blade first
            ar.move(tr)
            session.delay(self._delay)
            al.move(tl * f)
        else:
            # don't care
            ar.move(tr)
            al.move(tl * f)

    def doReset(self):
        multiReset(self._axes)
        multiWait(self._axes)

    def doReference(self):
        multiReference(self, self._axes, self.parallel_ref)

    def _doReadPositions(self, maxage):
        cl, cr = [d.read(maxage) for d in self._axes]
        if self.coordinates == 'opposite':
            cl *= -1
        return [cl, cr]

    def doRead(self, maxage=0):
        l, r = positions = self._doReadPositions(maxage)
        if self.opmode == 'centered':
            if abs((l + r) / 2) > self._attached_left.precision:
                self.log.warning('gap seems to be offcentered, but is '
                                 'set to "centered" mode')
            return [r - l]
        elif self.opmode == 'offcentered':
            return [(l + r) / 2, r - l]
        elif self.opmode == '2blades_opposite':
            return [-l, r]
        return positions

    def doPoll(self, n, maxage):
        # also poll sub-AutoDevices we created
        for dev in devIter(self.__dict__, baseclass=AutoDevice):
            dev.poll(n, maxage)

    def valueInfo(self):
        if self.opmode == 'centered':
            return Value('%s.width' % self, unit=self.unit, fmtstr='%.2f')
        elif self.opmode == 'offcentered':
            return Value('%s.center' % self, unit=self.unit, fmtstr='%.2f'), \
                Value('%s.width' % self, unit=self.unit, fmtstr='%.2f')
        return Value('%s.left' % self, unit=self.unit, fmtstr='%.2f'), \
            Value('%s.right' % self, unit=self.unit, fmtstr='%.2f')

    def doStatus(self, maxage=0):
        return multiStatus(list(zip(self._axnames, self._axes)))

    def doReadUnit(self):
        return self._attached_left.unit

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

    def doUpdateOpmode(self, value):
        if value == 'centered':
            self.valuetype = tupleof(float)
        else:
            self.valuetype = tupleof(float, float)


class GapAxis(AutoDevice, Moveable):
    """
    "Partial" devices for slit axes, useful for e.g. scanning
    over the device slit.centerx.
    """

    attached_devices = {
        'gap': Attach('Slit whose axis is controlled', Gap),
    }

    valuetype = float

    hardware_access = False

    def doRead(self, maxage=0):
        positions = self._attached_gap._doReadPositions(maxage)
        return self._convertRead(positions)

    def doStart(self, target):
        currentpos = self._attached_gap._doReadPositions(0.1)
        positions = self._convertStart(target, currentpos)
        self._attached_gap._doStartPositions(positions)

    def doIsAllowed(self, target):
        currentpos = self._attached_gap._doReadPositions(0.1)
        positions = self._convertStart(target, currentpos)
        return self._attached_gap._doIsAllowedPositions(positions)


class CenterGapAxis(GapAxis):

    def doStart(self, target):
        if self._attached_gap.opmode == 'centered':
            raise UsageError("Can't move center if gap is in 'centered' mode")

    def _convertRead(self, positions):
        return (positions[0] + positions[1]) / 2.

    def _convertStart(self, target, current):
        width = current[1] - current[0]
        return (target - width / 2, target + width / 2)


class WidthGapAxis(GapAxis):

    def _convertRead(self, positions):
        return positions[1] - positions[0]

    def _convertStart(self, target, current):
        center = (current[0] + current[1]) / 2.
        return (center - target / 2, center + target / 2)
