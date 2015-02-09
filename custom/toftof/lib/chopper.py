#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

from time import sleep, time as currenttime

import IO

from nicos.core import Readable, Moveable, HasLimits, Param, Override, Attach,\
     NicosError, intrange, oneof, status, requires, ADMIN, listof, tupleof
from nicos.devices.taco import TacoDevice
from nicos.core import SIMULATION

from nicos.toftof import calculations as calc


class Controller(TacoDevice, Readable):
    """The main controller device of the chopper."""
    taco_class = IO.StringIO

    parameters = {
        'ch5_90deg_offset': Param('Whether chopper 5 is mounted the right way '
                                  '(= 0) or with 90deg offset (= 1)',
                                  type=intrange(0, 1), mandatory=True),
        'phase_accuracy': Param('Required accuracy of the chopper phases',
                                settable=True, default=10, type=float),  # XXX unit?
        'speed_accuracy': Param('Required accuracy of the chopper speeds',
                                settable=True, default=2, type=float),  # XXX unit?
        'resolution':     Param('Current energy resolution',
                                volatile=True, type=tupleof(float, float),),
        'timeout':        Param('Timeout waiting for changes',
                                settable=True, default=90.0, unit='s',
                                type=float),

        # readonly hidden state parameters giving current values
        'wavelength': Param('Selected wavelength',
                            unit='AA', userparam=False, type=float,),
        'speed':      Param('Disk speed',
                            unit='rpm', userparam=False, type=int,),
        'ratio':      Param('Frame-overlap ratio',
                            type=int, userparam=False),
        'crc':        Param('Counter-rotating mode',
                            type=int, userparam=False),
        'slittype':   Param('Slit type',
                            type=int, userparam=False),
        'phases':     Param('Current phases',
                            type=listof(float), userparam=False),
        'changetime': Param('Time of last change',
                            userparam=False, type=float,),
    }

    def _read(self, n):
        return int(self._taco_guard(
            self._dev.communicate, 'M%04d' % n).strip('\x06'))

    def _write(self, n, v):
        self._taco_guard(self._dev.writeLine, 'M%04d=%d' % (n, v))
        # wait for controller to process current commands
        while self._read(4070) != 0:
            sleep(0.04)

    def _write_multi(self, *values):
        tstr = ' '.join('M%04d=%d' % x for x in zip(values[::2], values[1::2]))
        self._taco_guard(self._dev.writeLine, tstr)
        # wait for controller to process current commands
        while self._read(4070) != 0:
            sleep(0.04)

    def doInit(self, mode):
        phases = [0, 0]
        try:
            if mode == SIMULATION:
                raise NicosError('not possible in dry-run/simulation mode')
            wavelength = self._read(4181) / 1000.0
            if wavelength == 0.0:
                wavelength = 4.5
            self._setROParam('wavelength', wavelength)
            self._setROParam('speed', round(self._read(4150) / 1118.4735))
            self._setROParam('ratio', abs(self._read(4507)))
            slittype = self._read(4182)
            if slittype == 2:  # XXX this looks strange
                self._setROParam('slittype', 1)
            else:
                self._setROParam('slittype', 0)
            crc = self._read(4183)
            if crc == 1:
                self._setROParam('crc', 0)
            else:
                self._setROParam('crc', 1)
            for ch in range(2, 8):
                phases.append(
                    int(round(self._read(4048 + ch * 100) / 466.0378)))
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

    def _getparams(self):
        return (self.wavelength, self.speed, self.ratio,
                self.crc, self.slittype)

    def _is_cal(self):
        for ch in range(1, 8):
            ret = self._read(4140 + ch)
            if ret in [0, 1, 2, 6, 8]:
                return False
        return True

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
        if self.crc == 0:
            r1 = 2
            r2 = -1.0
        else:
            r1 = 1
            r2 = 1.0
        rr = self.ratio + 1
        self._write_multi(4073, 1, 4076, 0,  4074, self.speed,
                          4075, phases[1], 4077,
                          int(round(self.wavelength * 1000.0)), 4070, 7)
        self._write_multi(4073, 2, 4076, r1, 4074, r2 * self.speed,
                          4075, phases[2], 4077, int(self.slittype + 1),
                          4070, 7)
        self._write_multi(4073, 3, 4076, 1,  4074, self.speed,
                          4075, phases[3], 4077, int(self.crc + 1), 4070, 7)
        self._write_multi(4073, 4, 4076, 1,  4074, self.speed,
                          4075, phases[4], 4070, 7)
        self._write_multi(4073, 5, 4076, rr, 4074, -1 * self.speed,
                          4075, phases[5], 4070, 7)
        self._write_multi(4073, 6, 4076, 1,  4074, self.speed,
                          4075, phases[6], 4070, 7)
        self._write_multi(4073, 7, 4076, r1, 4074, r2 * self.speed,
                          4075, phases[7], 4070, 7)
        self._setROParam('phases', phases)
        self._setROParam('changetime', currenttime())

    def _stop(self):
        self._phases = [0] + [4500] * 7
        self._setROParam('speed', 0)
        for ch in range(1, 8):
            self._write_multi(4073, ch, 4076, 0, 4074, self.speed,
                              4075, self._phases[ch], 4070, 7)
        self._setROParam('changetime', currenttime())

    def _readspeeds(self):
        return [abs(self._read(4080 + ch)) for ch in range(1, 8)]

    def _readspeeds_actual(self):
        return [abs(self._read(66 + ch * 100)) for ch in range(1, 8)]

    def _readphase(self, ch):
        return self._read(4100 + ch) / 100.0

    def doReadResolution(self):
        return calc.Eres1(self.wavelength, self.speed)

    def doRead(self, maxage=0):
        """Read average speed from all choppers."""
        speeds = self._readspeeds()
        speed = 0.0
        for ch in [1, 2, 3, 4, 6, 7]:
            speed += speeds[ch - 1]
        if self.ratio is not None:
            if self.ratio == 1:
                speed += speeds[5 - 1]
            elif self.ratio < 9:
                speed += speeds[5 - 1] * self.ratio / (self.ratio - 1.0)
            else:
                speed += speeds[5 - 1] * self.ratio / 7.0
            return speed / 7.0
        else:
            return speed / 6.0

    def doReset(self):
        speed = sum(self._readspeeds())
        if speed > 0.5:
            raise NicosError(self, 'Attention: It is strictly forbidden to '
                             'reset the chopper system if one or more discs '
                             'are running!')
        if not self._is_cal():
            self._taco_guard(self._dev.writeLine, '$$$')
            sleep(3)
            self._write(4070, 5)
            self._setROParam('speed', 0)
        self._setROParam('changetime', currenttime())

    def doStatus(self, maxage=0):
        errstates = {0: 'inactive', 1: 'cal', 2: 'com', 8: 'estop'}
        ret = []
        stval = status.OK
        timedout = currenttime() > self.changetime + self.timeout
        # read status values
        for ch in range(1, 8):
            state = self._read(4140 + ch)
            if state in errstates:
                stval = status.ERROR
                ret.append('ch %d: state is %s' % (ch, errstates[state]))
        # read speeds
        for ch in range(1, 8):
            if (self.crc == 0 and ch in [2, 7]) or ch == 5:
                r2 = -1.0
            else:
                r2 = 1.0
            speed = self._read(4080 + ch) * r2
            rat = 1.0
            if ch == 5:
                if self.ratio > 1 and self.ratio <= 8:
                    rat = self.ratio / (self.ratio - 1.0)
                elif self.ratio > 8:
                    rat = self.ratio / 7.0
            nominal = self.speed / rat
            maxdelta = self.speed_accuracy / rat
            if abs(speed - nominal) > maxdelta:
                if timedout:
                    stval = status.ERROR
                else:
                    stval = status.BUSY
                ret.append('ch %d: speed %.2f != nominal %.2f' %
                           (ch, speed, nominal))
        # read phases
        for ch in range(2, 8):
            phase = self._read(4100 + ch)
            if abs(phase - self.phases[ch]) > self.phase_accuracy:
                if timedout:
                    stval = status.ERROR
                else:
                    stval = status.BUSY
                ret.append('ch %d: phase %s != nominal %s' %
                           (ch, phase, self.phases[ch]))
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
            self._write_multi(4073, ch, 4076, 0, 4074, self.speed,
                              4075, self.phases[ch] + angle, 4070, 7)
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
        self._write_multi(4073, ch, 4076, 0, 4074, self.speed,
                          4075, int(round(angle * 100.0)), 4070, 7)
        self._setROParam('changetime', currenttime())

    @requires(level=ADMIN)
    def chrun(self, ch, speed=0):
        ds = round(speed)
        if ds < -22000 or ds > 22000:
            raise NicosError(self, 'disc speed out of safety limits')
        self._discSpeed = ds / 7.0
        if ch < 1 or ch > 7:
            raise NicosError(self, 'invalid chopper number')
        self._write_multi(4073, ch, 4076, 0, 4074, ds, 4070, 7)
        self._setROParam('changetime', currenttime())


class SpeedReadout(Readable):
    """The current speed readout device of the chopper."""
    attached_devices = {
        'chopper': Attach('Chopper controller', Controller),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='rpm'),
    }

    def doRead(self, maxage=0):
        return [v / 279.618375
                for v in self._adevs['chopper']._readspeeds_actual()]

    def doStatus(self, maxage=0):
        return status.OK, 'no status info'


class PropertyChanger(Moveable):
    """This is essentially a ParamDevice

    and can be replace once Controller uses single setters
    (NICOS-style interface).
    """
    attached_devices = {
        'chopper': Attach('Chopper controller', Controller),
    }

    def doStatus(self, maxage=0):
        return status.OK, 'no status info'

    def doRead(self, maxage=0):
        return getattr(self._adevs['chopper'], self._prop)

    def doStart(self, target):
        self._adevs['chopper']._change(self._prop, target)

    def doReadTarget(self):
        return getattr(self._adevs['chopper'], self._prop)


class Wavelength(HasLimits, PropertyChanger):
    """The wave length parameter device of the chopper."""
    _prop = 'wavelength'
    parameter_overrides = {
        'unit':  Override(mandatory=False, default='AA'),
    }
    valuetype = float


class Speed(HasLimits, PropertyChanger):
    """The speed parameter device of the chopper."""
    _prop = 'speed'
    parameter_overrides = {
        'unit':  Override(mandatory=False, default='rpm'),
    }
    valuetype = float


class Ratio(PropertyChanger):
    """The ratio parameter device of the chopper."""
    _prop = 'ratio'
    parameter_overrides = {
        'unit':  Override(mandatory=False, default=''),
        'fmtstr': Override(default='%d'),
    }
    valuetype = oneof(*range(1, 11))


class CRC(PropertyChanger):
    """The crc (rotation direction of disc 5) parameter device of the
    chopper.
    """
    _prop = 'crc'
    parameter_overrides = {
        'unit':   Override(mandatory=False, default=''),
        'fmtstr': Override(default='%d'),
    }
    valuetype = oneof(0, 1)


class SlitType(PropertyChanger):
    """The slit type parameter device of the chopper."""
    _prop = 'slittype'
    parameter_overrides = {
        'unit':  Override(mandatory=False, default=''),
        'fmtstr': Override(default='%d'),
    }
    valuetype = oneof(0, 1, 2)
