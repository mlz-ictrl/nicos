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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#
# *****************************************************************************
"""PUMA multi detector class."""

import math

from nicos import session

from nicos.core import Attach, Moveable, Override, Param
from nicos.core.errors import PositionError
from nicos.core.mixins import HasTimeout
from nicos.core.utils import multiWait


class PumaMultiDetectorLayout(HasTimeout, Moveable):

    attached_devices = {
        'rotdetector': Attach('', Moveable, multiple=11),
        'rotguide': Attach('', Moveable, multiple=11),
        # 'man': Attach('multi analyzer', Moveable),
        'att': Attach('coupled axes detector', Moveable),
    }

    parameters = {
        'general_reset': Param('',
                               type=bool, settable=False, default=False,),
        'raildistance': Param('',
                              type=float, settable=False, default=20.,
                              unit='mm',),
        'detectorradius': Param('',
                                type=float, settable=False, default=761.9,
                                unit='mm'),
    }

    parameter_overrides = {
        'timeout': Override(default=600.),
        'unit': Override(mandatory=False, default='', settable=False),
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

    def doIsAllowed(self, target):
        notallowed = []
        # check if list of requested positions is complete
        if len(target) != 22:
            return False, 'requested positions not complete: no. of positions'\
                          ' %d instead of 22 ! (%s)' % (len(target), target)
        # check if requested position is allowed in principle
        why = []
        for i, dev in enumerate(self._attached_rotdetector):
            ok, _why = dev.isAllowed(target[i])
            if ok:
                self.log.debug('requested rotation %2d to %.2f deg allowed',
                               i + 1, target[i])
            else:
                why.append('requested rotation %2d to %.2f deg out of limits;'
                           '%s' % (i + 1, target[i], _why))
                notallowed.append(1)
        # doAllowed for guide
        # now check detector and guide rotation allowed within single limits
        # and sequence limits

        if notallowed or not self._sequentialAngleLimit(target[0:11]):
            if notallowed:
                self.log.warn('notallowed : %r %s', notallowed, '; '.join(why))
                return False, '; '.join(why)
            return False, 'Some of the positions are to close to others'
        return True, ''

    def doStart(self, target):
        """Move multidetector to correct scattering angle of multi analyzer.

        It takes account into the different origins of the analyzer blades.
        """
        # check if requested positions already reached within precision
        check = self._checkPositionReached(target[0:11], 'raw')
        self._printPos()
        if check:
            self.log.debug('device already at requested position, nothing to!')
            return

        self.log.debug('try to start multidetector')

        # reference of guide blades before movement
        # self.reference('det')
        # self.wait()
        # self.reference('guide')
        # self.wait()

        # calculate the angles for the device movement
        # pos = self._correctAnglesMove(position) # 11 angle values for device

        # move individual guide to zero
        # self.rg1.reference() # guide No 1 is defect
        for i, d in enumerate(self._rotguide1):
            d.move(-0.5 * i)
        multiWait(self._rotguide1)

        # move device to device angle
        # Goetz collision sort
        nstart = [[0] * 11] * 11
        for i in range(11):
            for j in range(11):
                nstart[i][j] = 0
            i1 = i + 1
            for j in range(i1, 11):
                if target[i] < self._rotdetector0[j].read() + 2.5:
                    nstart[i][j] = 1

        istart = [0] * 11
        for _k in range(11):
            if 0 not in istart:
                break
            # ready = 1
            # for i in range(11):
            #     if istart[i] == 0:
            #         ready = 0
            # if ready != 0:
            #     break
            for i in range(11):
                _sum = 0
                if istart[i] == 1:
                    continue
                i1 = i + 1
                for j in range(i1, 11):
                    _sum += nstart[i][j]
                if _sum != 0:
                    continue
                istart[i] = 1
                self._rotdetector0[i].move(target[i])
                session.delay(2)
                for j in range(11):
                    nstart[j][i] = 0
        multiWait(self._rotdetector0)

        # self.rg1.reference()   # guide No 1 is defect
        for n in [10, 0, 9, 1, 8, 2, 7, 3, 6, 4, 5]:
            self._rotguide0[n].move(target[n + 11])
            self.log.info('guide No %s', n + 1)
        multiWait(self._rotguide0)

    def doReset(self):
        for dev in self._rotguide0 + self._rotdetector0:
            dev.reset()

    def doReference(self, what='all', order=0):
        if what == 'det':
            if order == 0:
                for d in self._rotdetector0:
                    d.reference()
                    session.delay(10)
            elif order == 1:
                for d in self._rotdetector1:
                    d.reference()
                    session.delay(10)
            multiWait(self._rotdetector0)
        elif what == 'guide':
            if order == 0:
                for d in self._rotguide0:
                    d.reference()
                    session.delay(10)
            elif order == 1:
                for d in self._rotguide1:
                    d.reference()
                    session.delay(10)
            multiWait(self._rotguide0)
        if self._checkLimitSwitches(what) != 1:
            raise PositionError('reference drive failed')
        self.log.info('reference drive successful')

    def doStop(self):
        for dev in self._rotdetector0 + self._rotguide0:
            dev.stop()

    def doRead(self, maxage=0):
        return [d.read(maxage) for d in self._rotdetector0 + self._rotguide0]

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
            self.log.info('%s %s', p, temp[i])
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

        # anatranslist = self.man._read()[0:11]
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
        self.anarot = self.att.read()
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
        highlimit = []
        lowlimit = []
        refswitches = []
        ref = 0

        if what == 'det':
            lis = self._rotdetector0
        elif what == 'guide':
            lis = self._rotguide0
        else:
            return False

        for i in range(11):
            templs1 = (lis[i].motor._status() >> 5) & 1
            # templs2 = (lis[i].stepper._status() >> 6) & 1
            if what == 'det':
                if templs1 == 1 and (lis[i].refswitch == 'high'):
                    highlimit.append(1)
                    lowlimit.append(0)
                    refswitches.append(1)
                    ref += 1
                elif templs1 == 0 and (lis[i].refswitch == 'high'):
                    highlimit.append(0)
                    lowlimit.append(0)
                    refswitches.append(0)
            elif what == 'guide':
                if templs1 == 1 and (lis[i].refswitch == 'low'):
                    highlimit.append(0)
                    lowlimit.append(1)
                    refswitches.append(1)
                    ref += 1
                elif templs1 == 0 and (lis[i].refswitch == 'low'):
                    highlimit.append(0)
                    lowlimit.append(0)
                    refswitches.append(0)

            self.log.info('%s %s', lis[i], ref)

        self.log.info('highlimit: %s', highlimit)
        self.log.info('lowlimit:  %s', lowlimit)
        self.log.info('refswitch: %s', refswitches)

        return ref == len(lis)

    def _sequentialAngleLimit(self, pos):
        """Check individual movement ranges allowed for detector or guide."""
        check = 0
        allowed = []
        notallowed = []
        self.log.debug('position: %s', pos)
        self.log.debug('anglis: %s', self.anglis)

        for i in range(len(pos)):
            self.log.debug('check position %s %s', i, pos[i])
            if i == 0:
                if abs(pos[i] - pos[i + 1]) > self.anglis[0]:
                    allowed.append(i)
                    check += 1
                else:
                    self.log.warn('case 0: %s %s %s', pos[i], pos[i + 1],
                                  self.anglis[0])
                    notallowed.append(i)
            elif i == 10:
                if abs(pos[i] - pos[i - 1]) > self.anglis[9]:
                    allowed.append(i)
                    check += 1
                else:
                    self.log.warn('case 10: %s %s %s', pos[i], pos[i - 1],
                                  self.anglis[9])
                    notallowed.append(i)
            else:
                if abs(pos[i] - pos[i + 1]) > self.anglis[i] and \
                   abs(pos[i] - pos[i - 1]) > self.anglis[i]:
                    allowed.append(i)
                    check += 1
                else:
                    self.log.warn('%s %s %s %s', pos[i - 1], pos[i],
                                  pos[i + 1], self.anglis[i])
                    notallowed.append(i)
            self.log.debug('check: %s', check)
        self.log.debug('movement allowed for the following axes: %s', allowed)
        if check != 11:
            self.log.warn('movement not allowed for the following axes: %s',
                          notallowed)
            return False
        return True
