#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

import math

import sys

from nicos import session

from nicos.core import Attach, Moveable, Override, Param, status, tupleof
from nicos.core.mixins import HasTimeout
from nicos.core.utils import filterExceptions, multiStatus

from nicos.devices.abstract import CanReference

from nicos.pycompat import reraise


class PumaMultiDetectorLayout(CanReference, HasTimeout, Moveable):
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

    valuetype = tupleof(*(float for i in range(2 * _num_axes)))

    parameters = {
        'general_reset': Param('',
                               type=bool, settable=False, default=False,),
        'raildistance': Param('',
                              type=float, settable=False, default=20.,
                              unit='mm',),
        'detectorradius': Param('',
                                type=float, settable=False, default=761.9,
                                unit='mm'),
        '_status': Param('read only status',
                         type=bool, settable=False, userparam=False,
                         default=False),
    }

    parameter_overrides = {
        'timeout': Override(default=600.),
        'unit': Override(mandatory=False, default='', settable=False),
        'fmtstr': Override(volatile=True),
    }

    hardware_access = False
    stoprequest = 0
    threadstate = None
    D2R = math.pi / 180
    R2D = 1. / D2R
    # [-100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100]
    hortranslation = range(-100, 101, 20)
    anglis = [2.28, 2.45, 2.38, 2.35, 2.30, 2.43, 2.37, 2.43, 2.32, 2.36]

    def doInit(self, mode):
        self._rotdetector0 = self._attached_rotdetector
        self._rotdetector1 = self._rotdetector0[::-1]
        self._rotguide0 = self._attached_rotguide
        self._rotguide1 = self._rotguide0[::-1]
        self._setROParam('_status', False)

    def doStatus(self, maxage=0):
        if self._status:
            return status.BUSY, 'moving'
        return multiStatus(self._attached_rotdetector +
                           self._attached_rotguide, maxage)

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
        for dev, pos in zip(self._rotdetector0, target[:self._num_axes]):
            ok, _why = dev.isAllowed(pos)
            if ok:
                self.log.debug('%s: requested position %.3f deg allowed', dev,
                               pos)
            else:
                why.append('%s: requested position %.3f deg out of limits; %s'
                           % (dev, pos, _why))
        # now check detector and guide rotation allowed within single limits
        # and sequence limits
        if why:
            return False, '; '.join(why)
        return self._sequentialAngleLimit(target[:self._num_axes])

    def doStart(self, target):
        """Move multidetector to correct scattering angle of multi analyzer.

        It takes account into the different origins of the analyzer blades.
        """
        try:
            # check if requested positions already reached within precision
            check = self._checkPositionReached(target[0:self._num_axes], 'raw')
            self._printPos()
            if check:
                self.log.debug('device already at requested position, nothing '
                               'to do!')
                return

            self.log.debug('try to start multidetector')
            self._setROParam('_status', True)

            # reference of guide blades before movement
            # self.reference('det')
            # self.wait()
            # self.reference('guide')
            # self.wait()

            # calculate the angles for the device movement
            # pos = self._correctAnglesMove(position) # 11 angles for device

            # move individual guide to zero
            # self.rg1.reference() # guide No 1 is defect

            # Most left position of the guides
            l = min(self._rotguide0[0].read(0), -5)
            # spread the guides to the left with a distance of 0.5 deg to
            # ensure all guides can be moved to zero position and will not
            # touch another guide
            for i, d in enumerate(self._rotguide0):
                self.log.info('move %s to %f', d, l + 0.5 * i)
                d.move(l + 0.5 * i)
                session.delay(0.5)
            self.log.debug('Wait for finishing')
            self._hw_wait(self._rotguide0)
            # remove all remaining move commands on cards due to touching any
            # limit switch
            self.stop()

            # move all guides to zero position starting with the most right
            # guide so the guides and detectors are in well defined state.
            for d in self._rotguide1:
                d.move(0)
                session.delay(0.5)
            self._hw_wait(self._rotguide1)
            # remove all remaining move commands on cards due to touching any
            # limit switch
            self.stop()

            # move detectors to device angle
            self.log.debug('Collision sorting')
            # Goetz collision sort
            nstart = [[0] * self._num_axes] * self._num_axes
            for i in range(self._num_axes):
                for j in range(i + 1, self._num_axes):
                    if target[i] < self._rotdetector0[j].read(0) + 2.5:
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
                            self.log.info('Move detector #%d', i + 1)
                            self._rotdetector0[i].move(target[i])
                            session.delay(2)
                            for j in range(self._num_axes):
                                nstart[j][i] = 0
            self._hw_wait(self._rotdetector0)
            # remove all remaining move commands on cards due to touching any
            # limit switch
            self.stop()

            # self.rg1.reference()   # guide No 1 is defect
            for n in [10, 0, 9, 1, 8, 2, 7, 3, 6, 4, 5]:
                self._rotguide0[n].move(target[n + self._num_axes])
                self.log.info('Move guide #%d', n + 1)
            self._hw_wait(self._rotguide0)
            # remove all remaining move commands on cards due to touching any
            # limit switch
            self.stop()
        finally:
            self._setROParam('_status', False)

    def doReset(self):
        for dev in self._rotguide0 + self._rotdetector0:
            # one reset per card is sufficient, since the card will be reset
            # completely
            if dev.motor.addr in [71, 77, 83, 89]:
                dev.reset()

    def doReference(self, *args):
        # self.doReset()
        self.stop()
        for d, g in zip(self._rotdetector1, self._rotguide1):
            self.log.info('reference: %s, %s', d, g)
            self._reference_det_guide(d, g)
            session.delay(1.5)
        for i, (d, g) in enumerate(zip(self._rotdetector0, self._rotguide0)):
            d.userlimits = d.abslimits
            d.move(d.read(0) + 10 - i)
            g.reference()
            self._hw_wait([d, g])
        self.log.info('referencing of guides is finished')
        for d in self._rotguide1:
            d.move(0)
            session.delay(1)
        self._hw_wait(self._rotguide1)
        self.log.info('zeroing of guides finished')

    def doRead(self, maxage=0):
        return [d.read(maxage) for d in self._rotdetector0 + self._rotguide0]

    def _reference_det_guide(self, det, guide):
        """Drive 'det' and 'guide' devices to references.

        The 'det' device will be moved to its reference position, whereas the
        'guide' device will only moved to a position hitting the upper limit
        switch. So the 'det' and 'guide' devices are in a position all other
        pairs could be referenced too.

        If the 'guide' hits the upper limit switch and the 'det' is not at it's
        reference position it will be moved away in steps of 1 deg.
        """
        try:
            if not det.motor.isAtReference('high') and \
               not det.motor.isAtReference('low'):
                det.reference()
                self._hw_wait([det])
                while guide.motor.isAtReference('low'):
                    while guide.motor.isAtReference('low'):
                        p = guide.motor.read(0)
                        if not guide.motor.isAllowed(p - 1)[0]:
                            self.log.info('set new position: %f', (p + 1))
                            guide.motor.setPosition(p + 1)
                            self.log.info('new position is: %f',
                                          guide.motor.read(0))
                            session.delay(1)
                            self.log.info('new position is: %f',
                                          guide.motor.read(0))
                        guide.motor.move(p - 1)
                        self._hw_wait([guide])
                    det.reference()
                    self._hw_wait([det])
                self.log.info('det: %f', det.read(0))
            else:
                det.motor._setrefcounter()
            if not guide.motor.isAtReference('low'):
                guide.motor.reference('low')
            else:
                det.motor._setrefcounter()
            self.log.info('after guide ref start, det: %f', det.read(0))
            self._hw_wait([guide])
        finally:
            pass

    def _hw_wait(self, devices):
        loops = 0
        final_exc = None
        devlist = devices[:]  # make a 'real' copy of the list
        while devlist:
            loops += 1
            for dev in devlist[:]:
                try:
                    done = dev.doStatus(0)[0]
                except Exception:
                    dev.log.exception('while waiting')
                    final_exc = filterExceptions(sys.exc_info(), final_exc)
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
            reraise(*final_exc)

    def _read_corr(self):
        """Read the physical unit of axis."""
        readraw0, _readraw1 = self._read_raw()

        temp0 = self._correctAnglesRead(readraw0)
        temp1 = temp0  # self._correctAnglesRead(readraw0, 'guide')

        self.log.debug('detector rotation corrected:       %r', temp0)
        self.log.debug('detector guide rotation corrected: %r', temp1)

        return [temp0, temp1]

    def _read_raw(self):
        """Read the physical unit of axis."""
        readraw0 = [d.read() for d in self._rotdetector0]
        readraw1 = [d.read() for d in self._rotguide0]
        self.log.debug('detector rotation raw:  %r', readraw0)
        self.log.debug('detector guide rotation raw: %r', readraw1)
        return [readraw0, readraw1]

    def _printPos(self):
        out = []
        for i, dev in enumerate(self._attached_rotdetector):
            out.append('detector rotation %2d: %7.2f %s' % (i, dev.read(),
                                                            dev.unit))
        for i, dev in enumerate(self._attached_rotguide):
            out.append('guide rotation    %2d: %7.2f %s' % (i, dev.read(),
                                                            dev.unit))
        self.log.debug('%s', '\n'.join(out))

    def _checkPositionReached(self, pos, mode):
        """Check whether requested position is reached within some limit."""
        self.log.debug('length of list: %d', 0 if pos is None else len(pos))
        if not pos:
            return False

        if mode == 'raw':
            temp = self._read_raw()[0]
        elif mode == 'cor':
            temp = self._read_cor()[0]
        else:
            self.log.warn('not a valid mode given; corrected values or raw '
                          'values?')
            return False

        check = 0
        reached = []
        nonreached = []

        for i, p in enumerate(pos):
            self.log.debug('%s %s', p, temp[i])
            if abs(p - temp[i]) <= self._rotdetector0[i].precision:
                reached.append(i)
                check += 1
            else:
                nonreached.append(i)
        self.log.debug('not reached: %s', nonreached)
        self.log.debug('reached    : %s', reached)
        self.log.debug('check      : %s', check)
        return check == len(pos)

    def _readAnaTranslation(self):
        """Read the translation value of the individual analyzer blades.

        Needed for the calculation of real angles of detectors due to different
        origins
        """
        anatranslist1 = list(range(-125, -5, 20)) + [0] + \
            list(range(25, 126, 20))
        # anatranslist1 = [-125, -105, -85, -65, -45, -25, 0, 25, 45, 65, 85,
        #                  105, 125]

        # anatranslist = self._attached_man._read()[0:self._num_axes]
        # for i in range(len(anatranslist)):
        #     if anatranslist[i] <= 125.:
        #         temp = anatranslist[i] - 125.
        #         anatranslist1.append(temp)
        #     else:
        #         temp = anatranslist[i]
        #         anatranslist1.append(temp)
        # self.log.debug('anatranslist raw: %s', anatranslist)
        # self.log.debug('anatranslist cor: %s', anatranslist1)
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
            angle = pos[i] * self.D2R
            read0 = (self.detectorradius + trans[i]) * math.tan(angle)  # b
            read0 += self.hortranslation[i]  # b corrected
            # b/a: a corrected detector radius
            temp = read0 / (self.detectorradius + trans[i])
            temp = math.atan(temp)  # calc angle radian
            temp = temp * self.R2D  # convert to degrees
            read1.append(temp)  # list append
        self.log.debug('corrected detector angles: %s', read1)
        return read1

    def _correctAnglesMove(self, pos):
        trans = self._readAnaTranslation()
        read1 = []

        for i in range(len(self._rotdetector0)):
            angle = pos[i] * self.D2R
            # b: without taking into account the horizontal shift
            read0 = math.tan(angle) * (self.detectorradius + trans[i])
            read0 -= self.hortranslation[i]  # b check if minus/plus?
            # b/a: a corrected detector radius
            temp = read0 / self.detectorradius
            temp = math.atan(temp)  # calc angle radian
            temp = temp * self.R2D  # convert to degrees
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
        # for dev in lis:
        #     templs1 = (dev.motor._status() >> 5) & 1
        #     if what == 'det':
        #         ref += dev.motor.isAtReference()
        #         if templs1 == 1 and (lis[i].refswitch == 'high'):
        #             highlimit.append(1)
        #             lowlimit.append(0)
        #             refswitches.append(1)
        #             ref += 1
        #         elif templs1 == 0 and (lis[i].refswitch == 'high'):
        #             highlimit.append(0)
        #             lowlimit.append(0)
        #             refswitches.append(0)
        #     elif what == 'guide':
        #         ref += dev.motor.isAtReference()
        #         if templs1 == 1 and (lis[i].refswitch == 'low'):
        #             highlimit.append(0)
        #             lowlimit.append(1)
        #             refswitches.append(1)
        #             ref += 1
        #         elif templs1 == 0 and (lis[i].refswitch == 'low'):
        #             highlimit.append(0)
        #             lowlimit.append(0)
        #             refswitches.append(0)
        #     self.log.debug('%s %s', dev, ref)

        return ref == len(lis)

    def _sequentialAngleLimit(self, pos):
        """Check individual movement ranges allowed for detector or guide."""
        check = 0
        allowed = []
        notallowed = []
        self.log.debug('position: %s', pos)
        self.log.debug('anglis: %s', self.anglis)
        why = []

        for i in range(len(pos)):
            self.log.debug('check position %s %s', i, pos[i])
            if i == 0:
                if abs(pos[i] - pos[i + 1]) > self.anglis[0]:
                    allowed.append(i)
                    check += 1
                else:
                    why.append('case 0: %s %s %s' % (pos[i], pos[i + 1],
                                                     self.anglis[0]))
                    notallowed.append(i)
            elif i == 10:
                if abs(pos[i] - pos[i - 1]) > self.anglis[9]:
                    allowed.append(i)
                    check += 1
                else:
                    why.append('case 10: %s %s %s' % (pos[i], pos[i - 1],
                                                      self.anglis[9]))
                    notallowed.append(i)
            else:
                if abs(pos[i] - pos[i + 1]) > self.anglis[i] and \
                   abs(pos[i] - pos[i - 1]) > self.anglis[i]:
                    allowed.append(i)
                    check += 1
                else:
                    why.append('%s %s %s %s' % (pos[i - 1], pos[i], pos[i + 1],
                                                self.anglis[i]))
                    notallowed.append(i)
            self.log.debug('check: %s', check)
        self.log.debug('movement allowed for the following axes: %s', allowed)
        if check != self._num_axes:
            self.log.warn('movement not allowed for the following axes: %s',
                          notallowed)
            return False, '; '.join(why)
        return True, ''
