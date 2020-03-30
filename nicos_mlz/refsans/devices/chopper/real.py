#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""Chopper related devices."""

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.core import ADMIN, Moveable, Override, Param, intrange, requires, \
    status
from nicos.core.errors import ConfigurationError
from nicos.core.mixins import DeviceMixinBase, HasOffset
from nicos.core.params import Attach
from nicos.devices.abstract import Motor
from nicos.devices.tango import StringIO

from nicos_mlz.refsans.devices.chopper.base import ChopperDisc as ChopperDiscBase, \
    ChopperDisc2 as ChopperDisc2Base, \
    ChopperDiscTranslation as ChopperDiscTranslationBase, \
    ChopperMaster as ChopperMasterBase


class ChopperBase(DeviceMixinBase):

    attached_devices = {
        'comm': Attach('Communication device', StringIO),
    }

    def _read_controller(self, mvalue):
        # TODO  this has to be fix somehow
        if hasattr(self, 'chopper'):
            what = mvalue % self.chopper
        else:
            what = mvalue
        # self.log.debug('_read_controller what: %s', what)
        res = self._attached_comm.communicate(what)
        res = res.replace('\x06', '')
        # self.log.debug('_read_controller res for %s: %s', what, res)
        return res

    def _read_base(self, what):
        res = self._attached_comm.communicate(what)
        res = res.replace('\x06', '')
        return res

    def _write_controller(self, mvalue, *values):
        # TODO: fix formatting for single values and lists
        # TODO: this has to be fix somehow
        if hasattr(self, 'chopper'):
            what = mvalue % ((self.chopper, ) + values)
        else:
            what = mvalue % (values)
        self.log.debug('_write_controller what: %s', what)
        self._attached_comm.writeLine(what)


class ChopperMaster(ChopperBase, ChopperMasterBase):

    parameters = {
        'fatal': Param('Emergency off: Frontswitch and Backplane',
                       type=str, settable=False, volatile=True,
                       userparam=True),
    }

    parameter_overrides = {
        'delay': Override(volatile=True),
        'resolution': Override(type=intrange(0, 6)),
    }

    def doWriteDelay(self, delay):
        self._write_controller('m4079=%dm4080=%%d' % 1,
                               int(round(delay * 100)))

    def doReadDelay(self):
        return int(self._read_controller('m4080')) / 100.0

    def doReadFatal(self):
        res = int(self._read_controller("m4072"))
        if res == 0:
            return 'ok'
        # else:
        #    self.log.debug('Fatal = %d', res)
        msg = []
        if res & 1:
            msg.append('Invalid command ID')
        if res & 2:
            msg.append('Invalid axis ID')
        if res & 4:
            msg.append('Invalid master speed')
        if res & 8:
            msg.append('Invalid slave speed')
        if res & 0x10:
            msg.append('Invalid position')
        if res & 0x20:
            msg.append('Conflict between speed and position value')
        if res & 0x40:
            msg.append('Invalid gear ratio')
        if res & 0x80:
            msg.append('No commutation')
        if res & 0x100:
            msg.append('unkonwn Error')
        if res & 0x200:
            msg.append('E-stop Frontswitch')
        if res & 0x400:
            msg.append('E-stop backplane: ChopperLogic')
        if res & 0x800:
            msg.append('Overspeed')
        if res & 0x1000:
            msg.append('XY table command while chopper(s) moving (> 1Hz)')
        if res & 0x2000:
            msg.append('XY table command for position > 1 without reference')
        if res & 0x4000:
            msg.append('Chopper command while XY table is moving')
        if res & 0x8000:
            msg.append('XY table amplifier fault (Systec unit)')
        if res & 0x10000:
            msg.append('XY table moving with chopper speed > 1Hz')
        if res & 0x20000:
            msg.append('h1FFFF extra Errors')
        return ', '.join(msg)

    def _hot_off(self):
        self.log.warn('chopper is shut down because of hot cores!')
        self._shut_down()

    def _shut_down(self):
        self._attached_comm.writeLine('$$$')
        session.delay(2.5)

    def _commute(self):
        self.log.info('commute: see in speed history: burst for 3min, '
                      'a break of 20sec, an a peak, final break of 2min '
                      'total ca 6min')
        self._attached_comm.writeLine('m4070=5')
        session.delay(0.5)
        self.log.debug('DEVELOPING just wait!')

    @requires(level=ADMIN)
    def _position(self, disc, angle):
        # This method is only for installing new motors, so it is needed every
        # 5 years, it could be written as part of the disc 2 to 6 but it is
        # also needed for disc 1
        self.log.info('_position: %.2f for disc %d', angle, disc)
        while angle > +180.:
            angle -= 360.
        while angle < -180.:
            angle += 360.
        self.log.info('_position: %.2f for disc %d', angle, disc)
        angle = int(round(angle * 100))
        line = 'm4073=%d m4074=0 m4075=%d m4076=0 m4070=7' % (disc, angle)
        self.log.info('line %s', line)
        self._attached_comm.writeLine(line)
        self.log.info('you should be MP!')

    def doReference(self, *args):
        self.log.info('chopper reference QAD')
        # for dev in self._choppers:
        #     try:
        #         dev.move(0)
        #         session.delay(.5)
        #     except PositionError:
        #         # choppers are in inactive state
        #         pass
        #     except NicosError as e:
        #         self.log.info('%s', e)
        # for dev in self._choppers:
        #     try:
        #         dev.wait()
        #     except PositionError:
        #         # choppers are in inactive state
        #         pass
        #     except NicosError as e:
        #         self.log.info('%s', e)
        self.log.info('check for pending E-Stop')

        fatal = self.fatal  # avoid unneeded hardware access
        if fatal and fatal != 'ok':
            self.log.info('chopper fatal: %s', fatal)
        self.log.info('three BUCKs')
        self._shut_down()

        fatal = self.fatal
        if fatal and fatal != 'ok':
            self.log.error('still fatal %s deny reset: clear Error in RACK2',
                           fatal)
            # return

        self.log.info('Disk2_Pos 1')
        self._attached_chopper2._attached_translation.maw(1)

        self._commute()
        self.wait()

        self._set_all_phases(10)
        self.log.info('reset done')
        self.log.warning('CHECK chopper.delay value! (%.2f)', self.delay)

    def _set_all_phases(self, target=10):
        self.log.info('setting all phases to %d', target)
        for dev in self._choppers[1:]:
            dev.phase = target


class ChopperDisc(ChopperBase, ChopperDiscBase, Moveable):

    parameters = {
        'condition': Param('Internal condition',
                           type=str, settable=False, volatile=True,
                           userparam=True),
        'speedup': Param('Acceleration of the rotation speed',
                         type=intrange(0, 50), userparam=False,
                         settable=False, default=50),
    }

    parameter_overrides = {
        'phase': Override(volatile=True),
        'current': Override(volatile=True),
        'mode': Override(volatile=True),
    }

    def doStart(self, target):
        if self.speedup:
            self._attached_comm.write('m4062=%d' % self.speedup)
            session.delay(.4)  # .1 is too short; .2 does not work correctly
            self.log.info('speed up >%s<',
                          self._attached_comm.communicate('m4062'))
        self.log.info('set speed %d', target)
        if self.chopper != 1 or self.gear != 0:
            self.log.warning('changed chopper:%d gear:%d edge:%s',
                             self.chopper, self.gear, self.edge)
        self._write_controller(
            'm4073=%d m4074=%.0f m4075=0 m4076=0 m4070=7', round(target))
        if self.speedup:
            self._attached_comm.write('m4062=25')
            session.delay(.4)
            self.log.info('speed down >%s<',
                          self._attached_comm.communicate('m4062'))

    def doRead(self, maxage=0):
        return self._current_speed()

    def doReadCurrent(self):
        # res = int(self._read_controller('m%s68'))  # peak current
        # averaged current
        res = int(self._read_controller('m420%s')) / 1e3
        self.log.debug('current: %d', res)
        return res

    def doReadMode(self):
        res = int(self._read_controller('m414%s'))
        self.log.debug('mode: %d', res)
        return res

    def doReadCondition(self):
        res = int(self._read_controller('#%s?'), 16)
        self.log.debug('condition: %d', res)
        line = []
        All = False
        if res & 1 and All:
            line.append('In Position')
        if res & 2:
            line.append('Warning Following Error')
        if res & 4:
            line.append('Fatal Following Error')
        if res & 8:
            line.append('Amplifier Fault Error')
        if res & 0x10:
            line.append('Backlash Direction Flag')
        if res & 0x20 and All:
            line.append('I2T Amplifier Fault Error')
        if res & 0x40:
            line.append('Integrated Fatal Following Error')
        if res & 0x80 and All:
            line.append('Trigger Move')
        if res & 0x100:
            line.append('Phasing Reference Error')
        if res & 0x200 and All:
            line.append('Phasing Search/Read Active')
        if res & 0x400 and All:
            line.append('Home Complete')
        if res & 0x800 and All:
            line.append('Stopped on Position Limit')
        if res & 0x1000 and All:
            line.append('Stopped on Desired Position Limit')
        if res & 0x2000 and All:
            line.append('Foreground In-Position')
        if res & 0x4000 and All:
            line.append('Reserved for future use')
        if res & 0x8000 and All:
            line.append('Assigned to C.S.')
        if res & 0x10000 and All:
            line.append('BIT16')
        if res & 0x20000 and All:
            line.append('BIT17')
        if res & 0x40000 and All:
            line.append('BIT18')
        if res & 0x80000 and All:
            line.append('BIT19')
        if res & 0x100000 and All:
            line.append('BIT20')
        if res & 0x200000 and All:
            line.append('BIT21')
        if res & 0x400000 and All:
            line.append('BIT22')
        if res & 0x800000 and All:
            line.append('BIT23')
        if res & 0x1000000 and All:
            line.append('Maximum Rapid Speed')
        if res & 0x2000000 and All:
            line.append('Alternate Command-Output Mode')
        if res & 0x4000000 and All:
            line.append('Software Position Capture')
        if res & 0x8000000 and All:
            line.append('Error Trigger')
        if res & 0x10000000 and All:
            line.append('Following Enabled')
        if res & 0x20000000 and All:
            line.append('Following Offset Mode')
        if res & 0x40000000 and All:
            line.append('Phased Motor')
        if res & 0x80000000 and All:
            line.append('Alternate Source/Destination')
        if res & 0x100000000 and All:
            line.append('User-Written Servo Enable')
        if res & 0x200000000 and All:
            line.append('User-Written Phase Enable')
        if res & 0x400000000 and All:
            line.append('Home Search in Progress')
        if res & 0x800000000 and All:
            line.append('Block Request')
        if res & 0x1000000000 and All:
            line.append('Abort Deceleraction')
        if res & 0x2000000000 and All:
            line.append('Desired Velocity Zero')
        if res & 0x4000000000 and All:
            line.append('Data Block Error')
        if res & 0x8000000000 and All:
            line.append('Dwell in Progress')
        if res & 0x10000000000 and All:
            line.append('Integration Mode')
        if res & 0x20000000000 and All:
            line.append('Move Timer Active')
        if res & 0x40000000000 and All:
            line.append('Open Loop Mode')
        if res & 0x80000000000 and All:
            line.append('Amplifier Enabled')
        if res & 0x100000000000 and All:
            line.append('Extended Servo Algorithm Enabled')
        if res & 0x200000000000 and All:
            line.append('Positive End Limit Set')
        if res & 0x400000000000 and All:
            line.append('Negative End Limit Set')
        if res & 0x800000000000 and All:
            line.append('Motor Activated')
        if not line:
            return 'ok'
        return 'Debug: %s ' % ', '.join(line)

    def doReadPhase(self):
        res = int(self._read_controller('m410%s'))
        if res == 99999:
            return 0
        # The Chopper understands "negative hundreths degrees"
        # res /= 100.
        res /= -100.  # SB
        # since we changed the sign above, change sign of reference
        # set_to = (res - self.reference) * self.gear
        set_to = res * self.gear + self.reference  # SB
        # The Chopper uses -180..180 degrees, we use 0..360 degrees
        while set_to < 0.:
            set_to += 360.
        while set_to >= 360.:
            set_to -= 360.
        self.log.debug('read %.2f phase  %.2f ref %.2f gear %d SB', res,
                       set_to, self.reference, self.gear)
        return set_to

    def doWritePhase(self, value):
        # Change sign of offset since the sign of the value is now changed
        # afterwards
        set_to = (value - self.reference) / self.gear  # SB
        self.log.info('Disk %d angle %0.2f Phase %0.2f gear %d ref %.2f',
                      self.chopper, value, set_to, self.gear, self.reference)
        # We think in 0..360 degrees, choppers 1 to 4 in -180..180 degrees
        # and choppers 5 and 6 in -90..90 degrees
        while set_to > (+180. / self.gear):
            set_to -= 360. / self.gear
        while set_to < (-180. / self.gear):
            set_to += 360. / self.gear
        # The Chopper understands "negative hundreths degrees"
        set_to = int(round(set_to * -100))  # SB
        self.log.debug('Disk %d Phase %d gear %d', self.chopper, set_to,
                       self.gear)
        # Notausgang = 10
        # while Notausgang:
        #    Notausgang -= 1
        #    res = self._read_base('m4070')
        #    if res == '0':
        #        break
        #    if Notausgang < 0:
        #        break
        #    self.log.info('warten %s', res)
        #    #session.delay(0.04) 4 loops!
        #    session.delay(0.2)
        #    TODO
        self._write_controller(
            'm4073=%d m4074=0 m4075=%d m4076=%d m4070=7', set_to, self.gear)
        session.delay(5)  # MP: isso

    def doStatus(self, maxage=0):
        if hasattr(self, 'chopper'):
            self.log.debug('doStatus chopperdisc %d', self.chopper)
        else:
            self.log.debug('doStatus chopperdisc no number')
        if self.doIsAtTarget(self.doRead(0)) or self.chopper != 1:
            mode = self.mode
            if mode == 0:
                return status.ERROR, 'inactive'
            elif mode == 1:
                return status.ERROR, 'not calibrated'
            elif mode == 2:
                return status.BUSY, 'commute'
            elif mode == 3:
                return status.BUSY, 'brake'
            elif mode == 4:
                if self.chopper == 1:
                    return status.OK, 'speed'
                else:
                    return status.WARN, 'speed'
            elif mode == 5:
                return status.OK, 'phase'
            elif mode == 6:
                return status.ERROR, 'idle'
            elif mode == 7:
                return status.WARN, 'position'
            elif mode == 8:
                return status.ERROR, 'E-Stop'
            else:
                return status.ERROR, 'unknown >%d<' % mode
        return status.BUSY, 'moving'

    def doIsCompleted(self):
        if self.chopper == 1:
            st = self.status(0)
            if st[0] in self.busystates:
                return False
            if st[0] in self.errorstates:
                raise self.errorstates[st[0]](self, st[1])
            return True

        return self.mode == 5 or self.doIsAtTarget(self.doRead(0))

    def doFinish(self):
        if self.chopper == 1:
            return True
        return self.mode != 5  # no further checks if synced

    def _current_speed(self):
        res = float(self._read_controller('m408%s'))
        self.log.debug('_current_speed: %f', res)
        return res


class ChopperDisc2(ChopperDisc2Base, ChopperDisc):
    """Chopper disc 2 device."""

    # Due to a limitation of the hardware the position of the chopper disc2
    # position can be 0 but it is not a valid position. It indicates that the
    # hardware is not referenced. The parameter read raises always an error, so
    #  the device can't be initialised.

    # To overcome the problem the parameter type for the hardware is extended
    # to the 0 position, but the writing of 0 raises an error.

    parameter_overrides = {
        'pos': Override(type=intrange(0, 5), volatile=True, settable=True,
                        fmtstr='%d', unit=''),
    }

    def doWritePos(self, target):
        if target == 0:
            raise ConfigurationError(self, "'%d' is an invalid value for "
                                     "parameter 'pos'" % target)
        self._attached_translation.move(target)


class ChopperDiscTranslation(ChopperDiscTranslationBase, ChopperBase,
                             HasOffset, Motor):
    """Chopper disc translation device."""

    parameters = {
        '_lastpos': Param('Store last valid position',
                          type=int, settable=False, internal=True,
                          mandatory=False, default=1),
    }

    def doStart(self, value):
        self.log.info('requested position %d', value)
        what = 'm4077=%d' % value
        self.log.debug('doWritePos what: %s', what)
        res = self._attached_comm.writeLine(what)
        self.log.debug('doWritePos res: %d', res)
        # Better solution would be to take the solution from TOFTOF
        session.delay(.1)  # time is needed to transfer and initiate start

    def _read_pos(self):
        what = 'm4078'
        self.log.debug('_read_pos what: %s', what)
        res = self._attached_comm.communicate(what)
        res = int(res.replace('\x06', ''))
        self.log.debug('_read_pos what: %s pos: %d', what, res)
        return res

    def doRead(self, maxage=0):
        self.log.debug('doRead')
        res = self._read_pos()
        stat = self._status(res)
        if stat[0] == status.OK:
            if self._lastpos != res:
                self._setROParam('_lastpos', res)
            return res
        if stat[0] == status.BUSY:
            return self._lastpos
        return res  # This should always raise an error

    def _status(self, val):
        self.log.debug('_status: %d', val)
        if val == 99:
            return status.BUSY, 'moving'
        elif val == 0:
            return status.NOTREACHED, 'device not referenced'
        try:
            self.valuetype(val)
            return status.OK, ''
        except ValueError:
            return status.ERROR, 'Unknown status from read(): %d' % val

    def doStatus(self, maxage=0):
        return self._status(self._read_pos())
