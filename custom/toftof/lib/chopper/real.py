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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF chopper calculations and chopper control (MACCON)."""

from time import time as currenttime

import IO

from nicos import session
from nicos.core import ADMIN, NicosError, SIMULATION, requires, status

from nicos.devices.taco import TacoDevice
from nicos.pycompat import xrange as range  # pylint: disable=W0622

from nicos.toftof import calculations as calc

from nicos.toftof.chopper.base import BaseChopperController

WAVE_LENGTH = 4181
ACT_POS = 4191
SPEED = 4150
RATIO = 4507
SLIT_TYPE = 4182
CRM = 4183
# The (set) phases for each channel are PHASE + 100 * channel
PHASE_SET = 4048
# The set speed for each channel is ACT_SPEED + channel
ACT_SPEED = 4080
# ACT_SPEED = 4090
# The current speed for each channel is CURRENT_SPEED + 100 * channel
CURRENT_SPEED = 66
# The phase for each channel is PHASE + channel
ACT_PHASE = 4100
ERR_SPEED = 4120
ERR_PHASE = 4130
# The states for each channel are STATE + channel
STATUS = 4140
ST_INACTIVE = 0
ST_CALIB1 = 1
ST_CALIB2 = 2
ST_CALIB3 = 3
ST_ASYNC = 4
ST_SYNC = 5
ST_IDLE = 6
ST_POS = 7
ST_ESTOP = 8

# select channel
AXIS_ID = 4073
PAR_SPEED = 4074
PAR_POS = 4075
PAR_GEAR = 4076
SET_PARAM = 4077

# CHECK FOR TAKE OVER PARAMS
DES_CMD = 4070
C_READY = 0
C_BRAKE = 1
C_RESET = 2
C_IDLE = 3
C_RESUME = 4
C_CALIBRATE = 5
C_STOP = 6
C_ACCEPT = 7
C_NO_CMD = 9


class Controller(TacoDevice, BaseChopperController):
    """The main controller device of the chopper."""

    taco_class = IO.StringIO

    # XXX: maybe HasWindowTimeout is better suited here....

    def _read(self, n):
        return int(self._taco_guard(
            self._dev.communicate, 'M%04d' % n).strip('\x06'))

    def _write(self, n, v):
        self._taco_guard(self._dev.writeLine, 'M%04d=%d' % (n, v))
        # wait for controller to process current commands
        while self._read(DES_CMD) != C_READY:
            session.delay(0.04)

    def doRead(self, maxage=0):
        return BaseChopperController.doRead(self, maxage)

    def doInit(self, mode):
        phases = [0, 0]
        try:
            if mode == SIMULATION:
                raise NicosError('not possible in dry-run/simulation mode')
            wavelength = self._read(WAVE_LENGTH) / 1000.0
            if wavelength == 0.0:
                wavelength = 4.5
            self._setROParam('wavelength', wavelength)
            self._setROParam('speed', round(self._read(SPEED) / 1118.4735))
            self._setROParam('ratio', abs(self._read(RATIO)))
            slittype = self._read(SLIT_TYPE)
            if slittype == 2:  # XXX this looks strange
                self._setROParam('slittype', 1)
            else:
                self._setROParam('slittype', 0)
            crc = self._read(CRM)
            if crc == 1:
                self._setROParam('crc', 0)
            else:
                self._setROParam('crc', 1)
            for ch in range(2, 8):
                phases.append(
                    int(round(self._read(PHASE_SET + ch * 100) / 466.0378)))
            self._setROParam('phases', phases)
        except NicosError:
            self._setROParam('wavelength', 4.5)
            self._setROParam('speed', 0)
            self._setROParam('ratio', 1)
            self._setROParam('slittype', 0)
            self._setROParam('crc', 1)
            self._setROParam('phases', [0] * 8)
            self.log.warning('could not read initial data from PMAC chopper '
                             'controller', exc=1)

    def _is_cal(self):
        for ch in range(1, 8):
            ret = self._read(STATUS + ch)
            if ret in [ST_INACTIVE, ST_CALIB1, ST_CALIB2, ST_IDLE, ST_ESTOP]:
                return False
        return True

    def _writevalues(self, axis, gear=None, speed=None, phase=None, param=None):
        values = [(AXIS_ID, axis)]
        if gear is not None:
            values.append((PAR_GEAR, gear,))
        if speed is not None:
            values.append((PAR_SPEED, speed,))
        if phase is not None:
            values.append((PAR_POS, phase,))
        if param is not None:
            values.append((SET_PARAM, param,))
        values.append((DES_CMD, C_ACCEPT,))

        tstr = ' '.join('M%04d=%d' % x for x in values)
        self._taco_guard(self._dev.writeLine, tstr)
        # wait for controller to process current commands
        while self._read(DES_CMD) != C_READY:
            session.delay(0.04)

    def _change(self, name, value):
        """Internal interface to change a chopper value."""
        if not self._is_cal():
            raise NicosError(self, 'chopper system not yet calibrated')
        if name == 'wavelength':
            self._setROParam('wavelength', round(value * 1000.0) / 1000.0)
        elif name == 'speed':
            assert 150 <= value <= 22000
            self._setROParam('speed', value)
        elif name == 'ratio':
            assert value in range(1, 11)
            self._setROParam('ratio', value)
        elif name == 'crc':
            assert value in [0, 1]
            self._setROParam('crc', value)
        elif name == 'slittype':
            assert value in [0, 1, 2]
            self._setROParam('slittype', value)
        # calculate new phases
        phases = [0]
        for ch in range(1, 8):
            phi = calc.phi(ch, self.speed, self.wavelength, self.crc,
                           self.slittype, self.ratio, self.ch5_90deg_offset)
            assert -180. <= phi <= 180.
            phases.append(int(round(100.0 * phi)))
        r1, r2 = (2, -1.0) if self.crc == 0 else (1, 1.0)
        rr = self.ratio + 1
        self._writevalues(1, 0, self.speed, phases[1],
                          int(round(self.wavelength * 1000.0)))
        self._writevalues(2, r1, r2 * self.speed, phases[2],
                          int(self.slittype + 1))
        self._writevalues(3, 1, self.speed, phases[3], int(self.crc + 1))
        self._writevalues(4, 1, self.speed, phases[4])
        self._writevalues(5, rr, -1 * self.speed, phases[5])
        self._writevalues(6, 1, self.speed, phases[6])
        self._writevalues(7, r1, r2 * self.speed, phases[7])
        self._setROParam('phases', phases)
        self._setROParam('changetime', currenttime())

    def _stop(self):
        self._phases = [0] + [4500] * 7
        self._setROParam('speed', 0)
        for ch in range(1, 8):
            self._writevalues(ch, 0, self.speed, self._phases[ch])
        self._setROParam('changetime', currenttime())

    def _readspeeds(self):
        return [abs(self._read(ACT_SPEED + ch)) for ch in range(1, 8)]

    def _readspeeds_actual(self):
        return [abs(self._read(CURRENT_SPEED + ch * 100))
                for ch in range(1, 8)]

    def _readphase(self, ch):
        return self._read(ACT_PHASE + ch) / 100.0

    def doReset(self):
        speed = sum(self._readspeeds())
        if speed > 0.5:
            raise NicosError(self, 'Attention: It is strictly forbidden to '
                             'reset the chopper system if one or more discs '
                             'are running!')
        if not self._is_cal():
            self._taco_guard(self._dev.writeLine, '$$$')
            session.delay(3)
            self._write(DES_CMD, C_CALIBRATE)
            self._setROParam('speed', 0)
        self._setROParam('changetime', currenttime())

    def doStatus(self, maxage=0):
        errstates = {  # 0: 'inactive',
                     1: 'cal',
                     2: 'com',
                     8: 'estop',
        }
        ret = []
        stval = status.OK
        # read status values
        for ch in range(1, 8):
            state = self._read(STATUS + ch)
            if state in errstates:
                stval = status.ERROR
                ret.append('ch %d: state is %s' % (ch, errstates[state]))
        # read speeds
        for ch in range(1, 8):
            if (self.crc == 0 and ch in [2, 7]) or ch == 5:
                r2 = -1.0
            else:
                r2 = 1.0
            speed = self._read(ACT_SPEED + ch) * r2
            rat = 1.0
            if ch == 5:
                if self.ratio > 1 and self.ratio <= 8:
                    rat = self.ratio / (self.ratio - 1.0)
                elif self.ratio > 8:
                    rat = self.ratio / 7.0
            nominal = self.speed / rat
            maxdelta = self.speed_accuracy / rat
            if abs(speed - nominal) > maxdelta:
                msg = 'ch %d: speed %.2f != nominal %.2f' % (ch, speed,
                                                             nominal)
                ret.append(msg)
                if self.isTimedOut():
                    stval = status.OK  # NOTREACHED
                    self.log.warning(msg)
                else:
                    stval = status.BUSY
        # read phases
        for ch in range(2, 8):
            phase = self._readphase(ch)
            phase_diff = abs(phase - self.phases[ch] / 100.)
            if phase_diff > self.phase_accuracy:
                if self.isTimedOut():
                    # Due to some problems with the electronics the phase of
                    # the chopper disc 5 may have a phase differs from real
                    # value in the range of 360 or 270 degrees
                    if ch == 5:
                        msg = 'cd 5 phase %.2f != %.2f' % (
                            phase, self.phases[ch] / 100.)
                        if phase_diff >= 360:
                            if phase_diff % 360 <= self.phase_accuracy:
                                self.log.warning(msg)
                                continue
                        elif phase_diff > 180:
                            if phase_diff >= (360. - self.phase_accuracy) or \
                               abs(phase_diff - 270) <= self.phase_accuracy:
                                self.log.warning(msg)
                                continue
                        stval = status.ERROR
                    else:
                        stval = status.ERROR
                else:
                    stval = status.BUSY
                msg = 'ch %d: phase %s != nominal %s' % (
                    ch, phase, self.phases[ch] / 100.)
                ret.append(msg)
                if self.isTimedOut():
                    stval = status.OK  # NOTREACHED
                    self.log.warning(msg)
                else:
                    stval = status.BUSY
        return stval, ', '.join(ret) or 'normal'

    @requires(level=ADMIN)
    def adjust(self, angle=0.0):
        while angle > 180.0:
            angle -= 360
        while angle < -180.0:
            angle += 360
        self._setROParam('phases', [0, -26, 1, 19, 13, 1, -13, 62])
        self._setROParam('speed', 0)
        for ch in range(1, 8):
            self._writevalues(ch, 0, self.speed, self.phases[ch] + angle)
        self._setROParam('changetime', currenttime())

    @requires(level=ADMIN)
    def chmoveto(self, ch, angle=0.0):
        while angle > 180.0:
            angle -= 360
        while angle < -180.0:
            angle += 360
        if ch < 1 or ch > 7:
            raise NicosError(self, 'invalid chopper number')
        self._adjust()
        self._setROParam('speed', 0)
        self._writevalues(ch, 0, self.speed, int(round(angle * 100.0)))
        self._setROParam('changetime', currenttime())

    @requires(level=ADMIN)
    def chrun(self, ch, speed=0):
        ds = round(speed)
        if ds < -22000 or ds > 22000:
            raise NicosError(self, 'disc speed out of safety limits')
        self._discSpeed = ds / 7.0
        if ch < 1 or ch > 7:
            raise NicosError(self, 'invalid chopper number')
        self._writevalues(ch, 0, ds)
        self._setROParam('changetime', currenttime())
