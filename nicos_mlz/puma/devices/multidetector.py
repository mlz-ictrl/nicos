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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#
# *****************************************************************************
"""PUMA multi detector class."""

from itertools import tee
from math import atan, degrees, radians, tan

import numpy as np

from nicos import session
from nicos.core import SIMULATION, SLAVE, Attach, Moveable, Override, Param, \
    floatrange, listof, oneof, status, tupleof
from nicos.core.errors import ModeError, MoveError
from nicos.core.mixins import HasTimeout
from nicos.core.utils import filterExceptions, usermethod
from nicos.devices.abstract import CanReference
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqMethod


class MultiDetectorLayout(CanReference, HasTimeout, BaseSequencer):
    """PUMA multidetector arrangement device.

    There are 11 detector/blades(collimator) combinations moving on a circle.
    The detector tubes are mounted vertically and the blade can be moved around
    the detector, where the pivot point is the center of the detector tube.
    """

    _num_axes = 11

    attached_devices = {
        'rotdetector': Attach('Detector tube position devices',
                              Moveable, multiple=_num_axes),
        'rotguide': Attach('Detector guide devices',
                           Moveable, multiple=_num_axes),
        # 'man': Attach('multi analyzer', Moveable),
        'att': Attach('Coupled axes detector', Moveable),
    }

    valuetype = tupleof(*(float,) * 2 * _num_axes)

    parameters = {
        'general_reset': Param('',
                               type=bool, settable=False, default=False),
        'raildistance': Param('',
                              type=float, settable=False, default=20.,
                              unit='mm'),
        'detectorradius': Param('',
                                type=float, settable=False, default=761.9,
                                unit='mm'),
        'refgap': Param('Gap between detectors during the reference of the '
                        'guides',
                        type=floatrange(2.75, 4.1), settable=False,
                        userparam=True, default=3.),
        'gapoffset': Param('Minimum gap for the det 1 from reference position',
                           type=float, settable=False, userparam=False,
                           default=4.),
        'parkpos': Param('Detector and guide positions to park the '
                         'multidetector in a safe position',
                         type=listof(float), settable=False, userparam=False,
                         default=[-14.9, -17.5, -20., -22.5, -25., -27.5, -30.,
                                  -32.5, -35., -37.5, -40.,
                                  3.5, 2.75, 2.5, 2.25, 2.0, 1.75, 1.5, 1.25,
                                  1.0, 0.75, 0.5]),
        'tubediameter': Param('diameter of detector tubes',
                              type=floatrange(0, None), unit='mm',
                              category='general', default=25.4),
        'psdchannelwidth': Param('PSD channel width',
                                 type=floatrange(0, None), category='general',
                                 unit='mm', prefercache=False, default=0.7),
        'opmode': Param('Operation mode, either "multi" for multi analysis or '
                        ' "pa" for polarization analysis',
                        type=oneof('multi', 'pa'), settable=True,
                        default='multi'),
    }

    parameter_overrides = {
        'timeout': Override(default=600.),
        'unit': Override(mandatory=False, default='', settable=False),
        'fmtstr': Override(volatile=True),
    }

    hardware_access = False
    threadstate = None
    # [-100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100]
    hortranslation = range(-100, 101, 20)
    anglis = [2.28, 2.45, 2.38, 2.35, 2.30, 2.43, 2.37, 2.43, 2.32, 2.36]

    @usermethod
    def park(self, blocking=True):
        """Move device to the ``park`` position.

        The park position is given by the ``parkposition`` parameter.
        It generate ands starts a sequence if none is running.

        The call blocks the daemon execution if ``blocking`` is set to True.
        """
        if self._mode == SLAVE:
            raise ModeError(self, f'parking not allowed in {self._mode} mode')
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot park device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])
        self._startSequence([SeqMethod(self, '_move_guides_to_zero_pos'),
                             SeqMethod(self, '_move_detectors', self.parkpos),
                             ] +
                            [SeqDev(d, p) for d, p in zip(
                                self._rotguide1, self.parkpos[11:][::-1])])
        if blocking:
            # block the move to be sure that the device has reached target
            # before it can be dismounted or the position sensitive detectors
            # can be used
            self.wait()

    def doInit(self, mode):
        self._rotdetector0 = self._attached_rotdetector
        self._rotdetector1 = self._rotdetector0[::-1]
        self._rotguide0 = self._attached_rotguide
        self._rotguide1 = self._rotguide0[::-1]

    def valueInfo(self):
        ret = []
        for dev in self._attached_rotdetector + self._attached_rotguide:
            ret.extend(dev.valueInfo())
        return tuple(ret)

    def doReadFmtstr(self):
        return ', '.join('%s = %s' % (v.name, v.fmtstr)
                         for v in self.valueInfo())

    def doIsAllowed(self, target):
        # check if requested position is allowed in principle
        why = []
        for dev, pos in zip(self._rotdetector0 + self._rotguide0, target):
            ok, _why = dev.isAllowed(pos)
            if ok:
                self.log.debug('%s: requested position %.3f deg allowed', dev,
                               pos)
            else:
                why.append('%s: requested position %.3f deg out of limits; %s'
                           % (dev, pos, _why))
        if why:
            return False, '; '.join(why)
        # now check detector and guide rotation allowed within single limits
        # and sequence limits
        return self._sequentialAngleLimit(target)

    def _move_guides_to_zero_pos(self):
        """Move all guides to a position '0.'.

        Starting at the most left  guide looking for the first guide where the
        position is >= 0 so the devices left from it may be moved without any
        problem to position 0. Repeat as long all none of the positions is < 0.
        The move all with positions > 0 to 0.
        """
        self.log.debug('move all guides to zero position')
        while min(d.read(0) for d in self._rotguide0) < 0:
            for d in self._rotguide0:
                if d.read(0) >= 0:
                    for d1 in self._rotguide1[self._rotguide0.index(d):]:
                        d1.maw(0)
            self.log.debug('%r', [d.read(0) for d in self._rotguide0])
        for d in self._rotguide0:
            if not d.isAtTarget(target=0):
                d.maw(0)

        # remove all remaining move commands on cards due to touching any limit
        # switch
        for d in self._rotguide0:
            d.stop()

    def _move_detectors(self, target):
        """Move detectors to their positions.

        The order of the movement is calculated to avoid clashes during the
        movement.
        """
        self.log.debug('Collision sorting')
        nstart = np.zeros((self._num_axes, self._num_axes), dtype=np.int8)
        rotpos = [d.read(0) for d in self._rotdetector0]
        for i in range(self._num_axes):
            for j in range(i + 1, self._num_axes):
                if target[i] < rotpos[j] + 2.5:
                    nstart[i][j] = 1
        self.log.debug('Collision sorting done: %r', nstart)

        istart = [0] * self._num_axes
        for _k in range(self._num_axes):
            if 0 not in istart:
                break
            # ready = 1
            # for i in range(self._num_axes):
            #     if istart[i] == 0:
            #         ready = 0
            # if ready != 0:
            #     break
            for i in range(self._num_axes):
                if istart[i] == 0:
                    if sum(nstart[i][i + 1:self._num_axes]) == 0:
                        istart[i] = 1
                        self.log.debug('Move detector #%d', i + 1)
                        self._rotdetector0[i].move(target[i])
                        session.delay(2)
                        for j in range(self._num_axes):
                            nstart[j][i] = 0
        self._hw_wait(self._rotdetector0)
        # remove all remaining move commands on cards due to touching any limit
        # switch
        for d in self._rotdetector0:
            d.stop()

    def _move_guides(self, target):
        """Move all guides to their final position.

        Starting with the most outer guides towards the inner ones all guides
        may started one after the other, since should have target positions
        increasing with their position numbers.
        """
        for n in [10, 0, 9, 1, 8, 2, 7, 3, 6, 4, 5]:
            self._rotguide0[n].move(target[n + self._num_axes])
            self.log.debug('Move guide #%d', n + 1)
        self._hw_wait(self._rotguide0)
        # remove all remaining move commands on cards due to touching any limit
        # switch
        for d in self._rotguide0:
            d.stop()

    def _generateSequence(self, target):
        """Move multidetector to correct scattering angle of multi analyzer.

        It takes account into the different origins of the analyzer blades.
        """
        # check if requested positions already reached within precision
        if self.isAtTarget(target=target):
            self.log.debug('device already at position, nothing to do!')
            return []

        return [
            SeqMethod(self, '_move_guides_to_zero_pos'),
            # The detectors can be  moved without any restriction.
            SeqMethod(self, '_move_detectors', target),
            SeqMethod(self, '_move_guides', target),
        ]

    def doRead(self, maxage=0):
        return [d.read(maxage) for d in self._rotdetector0 + self._rotguide0]

    def doReset(self):
        for dev in self._rotguide0 + self._rotdetector0:
            # one reset per card is sufficient, since the card will be reset
            # completely
            if dev.motor.addr in [71, 77, 83, 89]:
                dev.reset()

    def doReference(self):
        # self.doReset()
        # remove all remaining move commands on cards due to touching
        # any limit switch
        self.stop()
        self.log.info('Compacting all elements')
        for d, g in zip(self._rotdetector0, self._rotguide0):
            self.log.debug('reference: %s, %s', d, g)
            self._reference_det_guide(d, g)
            session.delay(1.5)
        self.log.info('Spread elements to reference guides.')
        for i, (d, g) in enumerate(zip(self._rotdetector1,
                                       self._rotguide1)):
            d.userlimits = d.abslimits
            pos = d.read(0)
            d.move(self.gapoffset - (10 - i) * self.refgap)
            while abs(pos - d.read(0)) < (self.refgap - 0.2):
                session.delay(1)
            g.reference()
            self._hw_wait([d, g])
            g.maw(0)
        self.log.info('referencing of guides is finished')

    def _reference_det_guide(self, det, guide):
        """Drive 'det' and 'guide' devices to references.

        The 'det' device will be moved to its reference position, whereas the
        'guide' device will only moved to a position hitting the upper limit
        switch. So the 'det' and 'guide' devices are in a position all other
        pairs could be referenced too.

        If the 'guide' hits the upper limit switch and the 'det' is not at it's
        reference position it will be moved away in steps of 1 deg.
        """
        not_ref_switch = 'low' if guide.motor.refswitch == 'high' else 'high'
        try:
            det.reference()
            self._hw_wait([det])
            while guide.motor.isAtReference():
                if guide.motor.isAtReference(not_ref_switch):
                    self._clear_guide_reference(guide)
                while guide.motor.isAtReference():
                    self._step(guide)
                det.reference()
                self._hw_wait([det])
            while guide.motor.isAtReference():
                self._step(guide)
            while not guide.motor.isAtReference():
                guide.reference()
                self._hw_wait([guide])
        finally:
            pass

    def _step(self, guide, size=1):
        """Move device 'guide' a step 'size' away.

        The sign of the size gives the direction the value the distance.
        """
        p = guide.motor.read(0)
        if not guide.motor.isAllowed(p + size)[0]:
            guide.motor.setPosition(p - size)
            session.delay(1)
        guide.motor.maw(p + size)

    def _clear_guide_reference(self, guide):
        """Move all guides right from the 'guide' to free the limit switch.

        If there is a guide in between free, then free only left from this one
        """
        self.log.debug('clearing guide: %s', guide)
        while True:
            # find the first free guide from left side
            freeguides = self._rotguide1
            free = None
            for g in self._rotguide0[self._rotguide0.index(guide) + 1:]:
                not_ref_sw = 'low' if g.motor.refswitch == 'high' else 'high'
                if not g.motor.isAtReference(not_ref_sw):
                    free = g
                    freeguides = self._rotguide1[self._rotguide1.index(g):]
                    self.log.debug('found free guide: %s, %r', free,
                                   freeguides)
                    break

            # Try to free all left from found free guide if there was one
            for g in freeguides:
                for d in freeguides:
                    if d == g:
                        break
                    while d.motor.isAtReference():
                        self._step(d)
                    self._step(d)
                self._step(g)
                # if the found free is not free any more try the next round
                if free and free.motor.isAtReference():
                    break
                if g == guide:
                    return
            if free is None:
                self.log.warning("Can't free the guide: %s. Please check "
                                 'manually why!', guide)

    def _hw_wait(self, devices):
        loops = 0
        final_exc = None
        devlist = devices[:]  # make a 'real' copy of the list
        while devlist:
            loops += 1
            for dev in devlist[:]:
                try:
                    done = dev.doStatus(0)[0]
                except Exception as exc:
                    dev.log.exception('while waiting')
                    final_exc = filterExceptions(exc, final_exc)
                    # remove this device from the waiters - we might still
                    # have its subdevices in the list so that _hw_wait()
                    # should not return until everything is either OK or
                    # ERROR
                    devlist.remove(dev)
                if done == status.BUSY:
                    # we found one busy dev, normally go to next iteration
                    # until this one is done (saves going through the whole
                    # list of devices and doing unnecessary HW communication)
                    if loops % 10:
                        break
                    # every 10 loops, go through everything to get an accurate
                    # display in the action line
                    continue
                devlist.remove(dev)
            if devlist:
                session.delay(self._base_loop_delay)
        if final_exc:
            raise final_exc

    def _read_corr(self):
        """Read the physical unit of axis."""
        readraw0 = self._read_raw()

        temp1 = temp0 = self._correctAnglesRead(readraw0[:self._num_axes])

        self.log.debug('detector rotation corrected:       %r', temp0)
        self.log.debug('detector guide rotation corrected: %r', temp1)

        return [temp0, temp1]

    def _read_raw(self):
        """Read the physical unit of axis."""
        readraw0 = [d.read() for d in self._rotdetector0]
        readraw1 = [d.read() for d in self._rotguide0]
        self.log.debug('detector rotation raw:  %r', readraw0)
        self.log.debug('detector guide rotation raw: %r', readraw1)
        return readraw0 + readraw1

    def _printPos(self):
        out = []
        for i, dev in enumerate(self._attached_rotdetector):
            out.append('detector rotation %2d: %7.2f %s' % (i, dev.read(),
                                                            dev.unit))
        for i, dev in enumerate(self._attached_rotguide):
            out.append('guide rotation    %2d: %7.2f %s' % (i, dev.read(),
                                                            dev.unit))
        self.log.debug('%s', '\n'.join(out))

    def doIsAtTarget(self, pos, target):
        self._printPos()
        return self._checkPositionReached(target, 'raw')

    def _checkPositionReached(self, target, mode):
        """Check whether requested position is reached within some limit."""
        self.log.debug('length of list: %d', 0 if target is None else
                       len(target))
        if not target:
            return False

        if mode == 'raw':
            pos = self._read_raw()
        elif mode == 'cor':
            pos = self._read_cor()
        else:
            self.log.warning('not a valid mode given; corrected values or raw '
                             'values?')
            return False

        check = 0
        reached = []
        nonreached = []
        precs = [d.precision for d in self._rotdetector0 + self._rotguide0]
        for i, (t, p, prec) in enumerate(zip(target, pos, precs)):
            self.log.debug('%s %s', t, p)
            if abs(t - p) <= prec:
                reached.append(i)
                check += 1
            else:
                nonreached.append(i)
        self.log.debug('not reached: %s', nonreached)
        self.log.debug('reached    : %s', reached)
        self.log.debug('check      : %s', check)
        return check == len(target)

    def _readAnaTranslation(self):
        """Read the translation value of the individual analyzer blades.

        Needed for the calculation of real angles of detectors due to different
        origins
        """
        # [-125, -105, -85, -65, -45, -25, 0, 25, 45, 65, 85, 105, 125]
        anatranslist1 = list(range(-125, -5, 20)) + [0] + \
            list(range(25, 126, 20))
        return anatranslist1

    def _readZeroAna(self):
        """Read whether the whole analyser table is rotated.

        Needed for the calculation of real angles of detectors due to different
        origins
        """
        self.anarot = self._attached_att.read()
        return self.anarot

    def _correctZeroAna(self, position):
        return position - self._readZeroAna()

    def _correctAnglesRead(self, pos):
        trans = self._readAnaTranslation()
        read1 = []

        for i in range(len(self._rotdetector0)):
            angle = radians(pos[i])
            read0 = (self.detectorradius + trans[i]) * tan(angle)  # b
            read0 += self.hortranslation[i]  # b corrected
            # b/a: a corrected detector radius
            temp = read0 / (self.detectorradius + trans[i])
            temp = atan(temp)  # calc angle radian
            temp = degrees(temp)  # convert to degrees
            read1.append(temp)  # list append
        self.log.debug('corrected detector angles: %s', read1)
        return read1

    def _correctAnglesMove(self, pos):
        trans = self._readAnaTranslation()
        read1 = []

        for i in range(len(self._rotdetector0)):
            angle = radians(pos[i])
            # b: without taking into account the horizontal shift
            read0 = tan(angle) * (self.detectorradius + trans[i])
            read0 -= self.hortranslation[i]  # b check if minus/plus?
            # b/a: a corrected detector radius
            temp = read0 / self.detectorradius
            temp = atan(temp)  # calc angle radian
            temp = degrees(temp)  # convert to degrees
            read1.append(temp)  # list append
        self.log.debug('corrected detector angles: %s', read1)
        return read1

    def _checkLimitSwitches(self, what):
        lis = []
        if what in ['det', 'all']:
            lis += self._rotdetector0
        if what == ['guide', 'all']:
            lis += self._rotguide0

        ref = sum(dev.motor.isAtReference() for dev in lis)
        return ref == len(lis)

    def _sequentialAngleLimit(self, pos):
        """Check individual movement ranges allowed for detector or guide."""
        dtarget = pos[:self._num_axes]

        def is_reverse_sorted(l):
            l1, l2 = tee(l)
            next(l2, None)
            return all(a >= b for a, b in zip(l1, l2))

        def is_sorted(l):
            l1, l2 = tee(l)
            next(l2, None)
            return all(a <= b for a, b in zip(l1, l2))

        if not is_reverse_sorted(dtarget):
            return False, 'detector targets not a list of consecutive values'
        check = set(range(1, self._num_axes + 1))
        allowed = check.copy()
        self.log.debug('position: %s', pos)
        self.log.debug('anglis: %s', self.anglis)
        why = []

        for i in range(self._num_axes):
            self.log.debug('check position %s %s', i, pos[i])
            if i == 0:
                if abs(dtarget[i] - dtarget[i + 1]) < self.anglis[0]:
                    why.append('case 0: %s %s %s' % (
                        dtarget[i], dtarget[i + 1], self.anglis[0]))
                    allowed.discard(i + 1)
            elif i == 10:
                if abs(dtarget[i] - dtarget[i - 1]) < self.anglis[9]:
                    why.append('case 10: %s %s %s' % (
                        dtarget[i], dtarget[i - 1], self.anglis[9]))
                    allowed.discard(i + 1)
            else:
                if abs(dtarget[i] - dtarget[i + 1]) < self.anglis[i] or \
                   abs(dtarget[i] - dtarget[i - 1]) < self.anglis[i]:
                    why.append('%s %s %s %s' % (
                        dtarget[i - 1], dtarget[i], dtarget[i + 1],
                        self.anglis[i]))
                    allowed.discard(i)
        self.log.debug('movement allowed for the following detectors: %s',
                       ', '.join([str(i) for i in allowed]))
        notallowed = check - allowed
        if notallowed:
            self.log.warning('movement not allowed for the following '
                             'detectors: %s',
                             ', '.join([str(i) for i in notallowed]))
            return False, '; '.join(why)

        allowed = check.copy()
        gtarget = pos[self._num_axes:]
        if self.opmode == 'multi' and not is_sorted(gtarget):
            return False, 'detector guide targets not a list of consecutive ' \
                'values %s' % (gtarget,)
        first = 0
        last = self._num_axes - 1
        rg1_min = -7.5
        if dtarget[first] < 4.2:
            rg1_min += 1.4 * (dtarget[first] - 4.2)
        rg11_max = 21.9
        if dtarget[last] < -23.5:
            rg11_max += 1.4 * (23.5 + dtarget[last - 1])
        if not (rg1_min <= gtarget[first] <= gtarget[first + 1]):
            why.append('rg1: %s %s %s' % (rg1_min, gtarget[first],
                                          gtarget[first + 1]))
            allowed.discard(first + 1)
        if not (gtarget[last - 1] <= gtarget[last] <= rg11_max):
            why.append('rg11: %s %s %s' % (gtarget[last - 1], gtarget[last],
                                           rg11_max))
            allowed.discard(last + 1)
        if self.opmode == 'multi':
            for i in range(1, last):
                if not (gtarget[i - 1] <= gtarget[i] <= gtarget[i + 1]):
                    why.append('rg%i: %s %s %s' % (i + 1, gtarget[i - 1],
                                                   gtarget[i], gtarget[i + 1]))
                    allowed.discard(i + 1)
        notallowed = check - allowed
        if notallowed:
            self.log.warning('movement not allowed for the following guides: '
                             '%s', ', '.join([str(i) for i in notallowed]))
            return False, why
        return True, ''
