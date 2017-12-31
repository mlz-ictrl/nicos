# -*- coding: utf-8 -*-
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""PUMA device classes for the secondary collimator changer."""

from nicos import session
from nicos.core import Attach, Moveable, Override, Param, Readable, intrange, \
    oneof, status
from nicos.core.constants import MASTER
from nicos.core.errors import ConfigurationError, NicosError, PositionError
from nicos.core.mixins import HasTimeout
from nicos.core.utils import devIter
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqMethod, \
    SeqSleep


class StopByUserRequest(NicosError):
    """Exception raised when user send a stop."""

    category = 'User stop requested'


class BlockingSequencer(BaseSequencer):
    """Implement a blocking sequencer to avoid hardware damages."""

    def doStart(self, target):
        BaseSequencer.doStart(self, target)
        self._hw_wait()  # blocking move due to use of tt and st device!


class PumaSecCollBlockChanger(Moveable):
    """Implement the block changing device of he PUMA secondary collimator.

    The mechanics sometimes is blocked and the movement as to done again
    from starting point.
    """

    attached_devices = {
        'a2_setting': Attach('state setting of the units', Moveable),
        'a2_status': Attach('state word of the units', Readable),
    }

    parameters = {
        'ordnum': Param('Lift number',
                        type=intrange(0, 7), mandatory=True),
        'maxtries': Param('Number of tries to reach the target',
                          type=intrange(1, 0xffffffff), default=3,
                          settable=True),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%s'),
        'unit': Override(mandatory=False, default=''),
    }

    valuetype = oneof('in', 'out')

    def doInit(self, mode):
        if mode == MASTER:
            self._init_hw()

    def _read_status(self, maxage=0):
        return (self._attached_a2_status.read(maxage) >> (self.ordnum * 2)) & 3

    def doRead(self, maxage=0):
        val = 1 - (self._read_status(maxage) & 1)
        if val == 1:
            return 'in'
        elif val == 0:
            return 'out'
        else:
            return 'unknown'

    def doStatus(self, maxage=0):
        stat = self._read_status(maxage) & 0x2  # 0xaaaa  # 43690
        if stat == 0x2:
            return status.OK, 'idle'
        return status.BUSY, 'moving'

    def doReset(self, *args):
        self._init_hw()

    def _init_hw(self):
        tmp1 = self._attached_a2_status.read(0)
        tmp2 = sum(((tmp1 >> (2 * i)) & 1) << i for i in range(8))
        self.log.debug('Device status read from hardware: %s', tmp1)
        self.log.debug('Device Status sent to hardware: %s', tmp2)
        # send to hardware
        self._attached_a2_setting.move(tmp2)

    def doStart(self, target):
        _from = self.read(0)
        for _ in range(self.maxtries):
            self.log.debug('try %d: move to %s', _, target)
            self._moveto(target)
            if self.read(0) == target:
                return
            self.log.debug('move back to start pos: %s', _from)
            self._moveto(_from)  # move back to starting point
        raise PositionError(self, 'could not move to target: %r' % target)

    def _moveto(self, target):
        tmp = self._attached_a2_setting.read(0)
        if target == 'in':
            tmp &= (0xFF - (1 << self.ordnum))
        else:
            tmp |= (1 << self.ordnum)
        self.log.debug('target: %s, write to hw: 0x%x', target, tmp)
        self._attached_a2_setting.move(tmp)
        session.delay(0.5)  # give LOGO PLC some time to change the state
        self._hw_wait()


class PumaSecCollLift(HasTimeout, BlockingSequencer):
    """Implement the lift of the PUMA secondary collimator.

    This can be both a cover and a frame holder. Only control instances of
    this class directly if you know what you are doing!
    """

    attached_devices = {
        'tt': Attach('two theta axis monochromator', Moveable),
        'st': Attach('phi sample', Moveable),
        'block': Attach('block changing device', Moveable),
    }

    parameters = {
        'angle': Param('Value of the 2theta axis in changing position',
                       type=float, mandatory=True),
        'stpos': Param('Value of the sample table position to move the 2theta '
                       'axis', type=float, settable=False, default=60),
    }

    parameter_overrides = {
        'timeout': Override(default=600),
        'unit': Override(mandatory=False, default=''),
    }

    valuetype = oneof('in', 'out')

    def doRead(self, maxage=0):
        return self._attached_block.read(maxage)

    def doReset(self, *args):
        BaseSequencer.doReset(self, *args)

        self._attached_block.reset()
        self._attached_tt.reset()
        self._attached_st.reset()
        session.delay(0.5)
        if self.doStatus(0)[0] != status.OK:
            raise NicosError(self, 'cannot reset secondary collimator lift '
                             'unit')

    def doStatus(self, maxage=0):
        """Return highest statusvalue."""
        stati = [self._seq_status]
        for dev in devIter(self._getWaiters(), Readable):
            stat = dev.status(maxage)
            # ignore busy status of attached tt and st devices since they
            # will used in each device and the state of this device should
            # not changed if no sequence is running
            if dev in [self._attached_tt, self._attached_st]:
                if stat[0] == status.BUSY:
                    continue
            stati.append(stat)
        # sort inplace by first element, i.e. status code
        stati.sort(key=lambda st: st[0])
        # select highest (worst) status
        # if no status is 'worse' then _seq_status, this is _seq_status
        _status = stati[-1]
        if self._seq_is_running():
            return max(status.BUSY, _status[0]), _status[1]
        return _status

    def _generateSequence(self, position):
        seq = []
        if not self.isAtTarget(self.doRead(0)):
            # The limited space at some positions requires a folding of the
            # instrument
            st_target = 60. if self.angle > -85. else 109.
            if st_target != self.stpos:
                raise ConfigurationError(self, 'st_target != stpos')
            # Only move if the setup (folding of 'st') is not correctly
            if abs(self._attached_st.read(0) - self.stpos) > \
               self._attached_st.precision:
                seq.append(SeqDev(self._attached_tt, -60., stoppable=True))
                seq.append(SeqDev(self._attached_st, self.stpos,
                                  stoppable=True))
            # the configured positions are with offet = 0 !
            # if the user changes the offset the change positions will not
            # change!
            tt_pos = self.angle - self._attached_tt.offset
            seq.append(SeqDev(self._attached_tt, tt_pos, stoppable=True))
            seq.append(SeqDev(self._attached_block, position))
            seq.append(SeqSleep(2))
        return seq


class PumaSecCollPair(HasTimeout, BlockingSequencer):
    """Implements a single collimator changer.

    It uses both a cover lift and a frame lift and automatically sets the
    right one in the beam.
    """

    attached_devices = {
        'cover': Attach('cover holder', Moveable),
        'frame': Attach('frame holder', Moveable),
        'a2_press': Attach('switch on/off pressure for valve unit',
                           Moveable),
        'a2_lgon': Attach('switch on/off logos', Moveable),
        'a2_powvalunit': Attach('switch on/off power of valve unit (overheat)',
                                Moveable),
    }

    parameters = {
        'autoonoff': Param('', type=bool, default=False),
        'chkmotiontime': Param('', default=1),
    }

    parameter_overrides = {
        'timeout': Override(default=600),
        'unit': Override(mandatory=False, default=''),
    }

    valuetype = oneof('cover', 'frame', 'open')

    def doInit(self, mode):
        self._devices = [self._attached_frame, self._attached_cover]

    def doRead(self, maxage=0):
        r1 = 0 if self._attached_cover.read(maxage) == 'out' else 1
        r2 = 0 if self._attached_frame.read(maxage) == 'out' else 1
        if r1 and r2:
            raise NicosError(self, 'frame and cover in beam?!')
        if r1:
            return 'cover'
        elif r2:
            return 'frame'
        else:
            return 'open'

    def doReset(self):
        for d in self._devices:
            d.reset()
            session.delay(1)
        if self.doStatus(0)[0] != status.OK:
            raise NicosError(self, 'cannot reset')

    def _checkpower(self, onoff):
        on_off_str = 'on' if onoff else 'off'
        msg = ''
        if self._attached_a2_powvalunit.read(0) != onoff:
            msg += 'valve unit not switched "%s"; check device!' % on_off_str
        if self._attached_a2_lgon.read(0) != onoff:
            msg += ' logo device not switched "%s"; check device!' % on_off_str
        if self._attached_a2_press.read(0) != onoff:
            if onoff:
                msg += ' no air pressure for alpha2 changing unit; check air '\
                       'pressure'
            else:
                msg += ' air pressure for alpha2 changing unit not switched '\
                       'off!'
        if msg:
            raise NicosError(self, msg)

    def _generateSequence(self, target):
        seq = []
        if not self.isAtTarget(self.read(0)):
            # self.reset()
            # session.delay(2)
            # switch on hardware
            if True or self.autoonoff:  # ask why on/off automatic is needed
                seq.append(SeqDev(self._attached_a2_powvalunit, 1))
                seq.append(SeqSleep(2))
                seq.append(SeqDev(self._attached_a2_lgon, 1))
                seq.append(SeqSleep(2))  # necessary for initialisation of logo
                seq.append(SeqDev(self._attached_a2_press, 1))
                seq.append(SeqSleep(2))
                seq.append(SeqMethod(self, '_checkpower', 1))

            # we have to make a case differentiation because
            # the order of execution is important !
            if target == 'cover':
                seq.append(SeqDev(self._attached_frame, 'out'))
                seq.append(SeqDev(self._attached_cover, 'in'))
            elif target == 'frame':
                seq.append(SeqDev(self._attached_cover, 'out'))
                seq.append(SeqDev(self._attached_frame, 'in'))
            elif target == 'open':
                seq.append(SeqDev(self._attached_cover, 'out'))
                seq.append(SeqDev(self._attached_frame, 'out'))

            if self.autoonoff:  # and self.doStatus(0)[0] == status.OK
                seq.append(SeqDev(self._attached_a2_powvalunit, 0))
                seq.append(SeqDev(self._attached_a2_lgon, 0))
                seq.append(SeqDev(self._attached_a2_press, 0))
                seq.append(SeqSleep(self.chkmotiontime))
                seq.append(SeqMethod(self, '_checkpower', 0))
        return seq


class PumaSecondaryCollimator(HasTimeout, BlockingSequencer):
    """Secondary collimator of Puma.

    Uses a couple of single collimators to set the desired collimation as a
    combination of these.
    """

    attached_devices = {
        'diaphragma': Attach('fixed diaphragma', Moveable),
        'pair1': Attach('30 min collimator', Moveable, optional=True),
        'pair2': Attach('45 min collimator', Moveable),
        'pair3': Attach('60 min collimator', Moveable),
        'a2_status': Attach('', Readable),
    }

    parameters = {
        'chkmotiontime': Param('', default=2),
    }

    parameter_overrides = {
        'timeout': Override(default=600),
    }

    # Since the magnet of the 30' collimator cover is not working all values
    # for the 30' collimation use are forbidden !
    valuetype = oneof(120, 60, 45, 24)  # , 30, 20, 14)

    def doInit(self, mode):
        # the numerical value is to be interpreted as a bit mask,
        # which of the pairs to set to frame (if bit is 1),
        # otherwise to cover position
        self._switchlist = [[120, 60, 45, 30, 24, 20, 14],
                            [0, 4, 2, 1, 6, 5, 7]]
        self._pairs = {
            0: self._attached_pair1,
            1: self._attached_pair2,
            2: self._attached_pair3,
            3: self._attached_diaphragma
        }
        if self._attached_pair1:
            self.valuetype = oneof(120, 60, 45, 24, 30, 20, 14)

    def _generateSequence(self, target):
        seq = []
        if not self.isAtTarget(self.read(0)):
            position = None
            for i, val in enumerate(self._switchlist[0]):
                if target == val:
                    position = self._switchlist[1][i]
                    break
            # ask for diaphragma to switch in
            if position == 0:
                self.log.debug('no diaphragma')
                seq.append(SeqDev(self._pairs[3], 'cover'))
            else:
                self.log.debug('diaphragma')
                seq.append(SeqDev(self._pairs[3], 'frame'))
            seq.append(SeqSleep(self.chkmotiontime))

            # ask for changing the devices pair 1-3
            for i in range(3):
                if self._pairs[i]:  # Ignore pair1 if not used
                    if (position & (1 << i)):
                        self.log.debug('switching to frame: %s',
                                       self._pairs[i])
                        seq.append(SeqDev(self._pairs[i], 'frame'))
                    else:
                        self.log.debug('switching to cover: %s',
                                       self._pairs[i])
                        seq.append(SeqDev(self._pairs[i], 'cover'))
                    seq.append(SeqSleep(self.chkmotiontime))
        return seq

    def doRead(self, maxage=0):
        res0 = 0
        for i in range(3):
            if self._pairs[i]:
                if self._pairs[i].read(maxage) == 'frame':
                    res0 |= 1 << i
        if self._pairs[3].read(maxage) == 'frame':
            self.log.info('diaphragma alpha2 in beam')
        else:
            self.log.info('no diaphragma alpha2 in beam')
        for i, val in enumerate(self._switchlist[1]):
            if res0 == val:
                return self._switchlist[0][i]

    def doReset(self):
        BaseSequencer.doReset(self)
        for d in self._adevs:
            d.reset()
            session.delay(2)
        if self.doStatus()[0] == status.OK:
            raise NicosError(self, 'cannot reset')

    def _printstatus(self):
        a2_status = self._attached_a2_status.read()
        self.a1 = 1 - ((a2_status >> (0 * 2)) & 1)
        self.a1 = self._int2string(self.a1)
        self.a2 = 1 - ((a2_status >> (1 * 2)) & 1)
        self.a2 = self._int2string(self.a2)
        self.a3 = 1 - ((a2_status >> (2 * 2)) & 1)
        self.a3 = self._int2string(self.a3)
        self.b1 = 1 - ((a2_status >> (3 * 2)) & 1)
        self.b1 = self._int2string(self.b1)
        self.b2 = 1 - ((a2_status >> (4 * 2)) & 1)
        self.b2 = self._int2string(self.b2)
        self.b3 = 1 - ((a2_status >> (5 * 2)) & 1)
        self.b3 = self._int2string(self.b3)
        self.c1 = 1 - ((a2_status >> (6 * 2)) & 1)
        self.c1 = self._int2string(self.c1)
        self.c2 = 1 - ((a2_status >> (7 * 2)) & 1)
        self.c2 = self._int2string(self.c2)

        pa1 = 'A1 - Diaphragma:           %s' % (self.a1)
        pa2 = 'A2 - Cover diaphragma:     %s' % (self.a2)
        pa3 = 'A3 - 30" collimator:       %s' % (self.a3)
        pb1 = 'B1 - Cover 30" collimator: %s' % (self.b1)
        pb2 = 'B2 - 45" collimator:       %s' % (self.b2)
        pb3 = 'B3 - Cover 45" collimator: %s' % (self.b3)
        pc1 = 'C1 - 60" collimator:       %s' % (self.c1)
        pc2 = 'C2 - Cover 60" collimator: %s' % (self.c2)

        outstring = '\n'.join([pa1, pa2, '', pa3, pb1, '', pb2, pb3, '',
                               pc1, pc2])
        self.log.info('%s', outstring)

    def _int2string(self, a):
        return 'OUT' if a == 0 else 'IN'
