#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Virtual devices for testing."""

import time
import random
import threading
from math import exp, ceil, sqrt

import numpy as np
from collections import deque

from nicos import session
from nicos.services.poller.psession import PollerSession
from nicos.core import status, Readable, HasOffset, HasLimits, Param, Override, \
    none_or, oneof, tupleof, floatrange, Measurable, Moveable, Value, \
    ImageProducer, ImageType, SIMULATION
from nicos.devices.abstract import Motor, Coder
from nicos.devices.generic.detector import Channel


class VirtualMotor(Motor, HasOffset):
    """A virtual motor that can be set to move in finite time using a thread."""

    parameters = {
        'speed':     Param('Virtual speed of the device', settable=True,
                           type=floatrange(0, 1e6), unit='main/s'),
        'jitter':    Param('Jitter of the read value', default=0, unit='main'),
        'curvalue':  Param('Current value', settable=True, unit='main'),
        'curstatus': Param('Current status', type=tupleof(int, str),
                           settable=True, default=(status.OK, 'idle')),
        'ramp':      Param('Virtual speed of the device', settable=True,
                           type=floatrange(0, 1e6), unit='main/min'),
    }

    _thread = None

    def doStart(self, pos):
        pos = float(pos) + self.offset
        if self.speed != 0:
            if self._thread:
                self.stop()
                self._thread.join()
            self.curstatus = (status.BUSY, 'virtual moving')
            self._thread = threading.Thread(target=self.__moving, args=(pos,),
                                            name='virtual motor %s' % self)
            self._thread.daemon = True
            self._thread.start()
        else:
            self.curstatus = (status.BUSY, 'virtual moving')
            self.log.debug('moving to %s' % pos)
            self.curvalue = pos
            self.curstatus = (status.OK, 'idle')

    def doRead(self, maxage=0):
        return (self.curvalue - self.offset) + \
            self.jitter * (0.5 - random.random())

    def doStatus(self, maxage=0):
        return self.curstatus

    def doStop(self):
        if self.speed != 0 and \
           self._thread is not None and self._thread.isAlive():
            self._stop = True
        else:
            self.curstatus = (status.OK, 'idle')

    def doSetPosition(self, pos):
        self.curvalue = pos + self.offset

    def _step(self, start, end, elapsed, speed):
        delta = end - start
        sign = +1 if delta > 0 else -1
        value = start + sign * speed * elapsed
        if (sign == 1 and value >= end) or (sign == -1 and value <= end):
            return end
        return value

    def __moving(self, pos):
        speed = self.speed
        try:
            self._stop = False
            start = self.curvalue
            started = time.time()
            while 1:
                value = self._step(start, pos, time.time() - started, speed)
                if self._stop:
                    self.log.debug('thread stopped')
                    return
                time.sleep(0.2)
                self.log.debug('thread moving to %s' % value)
                self.curvalue = value
                if value == pos:
                    return
        finally:
            self._stop = False
            self.curstatus = (status.OK, 'idle')
            self._thread = None

    def doReadRamp(self):
        return self.speed * 60.

    def doWriteRamp(self, value):
        self.speed = value / 60.


class VirtualCoder(Coder, HasOffset):
    """A virtual coder that just returns the value of a motor, with offset."""

    attached_devices = {
        'motor': (Readable, 'Motor to read out to get coder value')
    }

    def doRead(self, maxage=0):
        val = self._adevs['motor'] and self._adevs['motor'].read(maxage) or 0
        return val - self.offset

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doSetPosition(self, _pos):
        pass


class VirtualTimer(Channel):
    """A virtual timer channel for use together with
    `nicos.devices.generic.detector.MultiChannelDetector`.
    """

    def doInit(self, mode):
        self.__finish = False

    def doStart(self):
        if self.ismaster:
            self.__finish = False
            thr = threading.Thread(target=self.__thread,
                                   name='virtual timer %s' % self)
            thr.daemon = True
            thr.start()

    def doIsCompleted(self):
        return self.__finish

    def __thread(self):
        finish_at = time.time() + self.preselection
        while time.time() < finish_at and not self.__finish:
            time.sleep(0.1)
        self.__finish = True

    def doStop(self):
        self.__finish = True

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doRead(self, maxage=0):
        if self.ismaster:
            return self.preselection
        return random.randint(0, 1000)

    def doSimulate(self, preset):
        return [self.doRead()]

    def doReadUnit(self):
        return 's'

    def valueInfo(self):
        return Value(self.name, unit='s', type='time', fmtstr='%.3f'),

    def doTime(self, preset):
        if self.ismaster:
            return self.preselection
        else:
            return 0


class VirtualCounter(Channel):
    """A virtual counter channel for use together with
    `nicos.devices.generic.detector.MultiChannelDetector`.
    """

    parameters = {
        'countrate':  Param('The maximum countrate', default=1000),
        'type':       Param('Type of channel: monitor or counter',
                            type=oneof('monitor', 'counter'), mandatory=True),
    }

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doRead(self, maxage=0):
        if self.ismaster:
            return self.preselection
        return random.randint(0, self.countrate)

    def doSimulate(self, preset):
        return [self.doRead()]

    def doIsCompleted(self):
        return True

    def doReadUnit(self):
        return 'cts'

    def valueInfo(self):
        return Value(self.name, unit='cts', errors='sqrt', type=self.type,
                     fmtstr='%d'),


class VirtualTemperature(VirtualMotor):
    """A virtual temperature regulation device."""

    parameters = {
        'tolerance': Param('Tolerance for wait()', default=1, settable=True,
                           unit='main', category='general'),
        'setpoint':  Param('Last setpoint', settable=True, unit='main',
                           category='general'),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False, default='K'),
        'jitter':    Override(default=0.1),
        'curvalue':  Override(default=10),
    }

    def doStart(self, pos):
        self.setpoint = pos
        VirtualMotor.doStart(self, pos)

    def doWait(self):
        while self.curstatus[0] == status.BUSY:
            if abs(self.read(0) - self.setpoint) < self.tolerance:
                break
            time.sleep(0.1)
        # wait returns earlier than status is idle. This violates NICOS philosophy!
        self.curstatus = (status.OK, 'idle')

    def _step(self, start, end, elapsed, speed):
        # calculate an exponential approximation to the setpoint with a time
        # constant given by self.speed
        gamma = speed / 10.
        cval = end + (start - end) * exp(-gamma*elapsed)
        if abs(cval - end) < self.jitter:
            return end
        return cval


def clamp(value, minval, maxval):
    return min(max(value, minval), maxval)


class VirtualRealTemperature(HasLimits, Moveable):
    parameters = {
        'jitter':    Param('Jitter of the read-out value', default=0,
                           unit='main'),
        'regulation': Param('Current temperature (regulation)', settable=False,
                           unit='main'),
        'sample':    Param('Current temperature (sample)', settable=False,
                           unit='main'),
        'curstatus': Param('Current status', type=tupleof(int, str),
                           settable=True, default=(status.OK, 'idle')),
        'ramp':      Param('Ramping speed of the setpoint', settable=True,
                           type=none_or(floatrange(0, 1000)), unit='main/min'),
        'tolerance': Param('Tolerance for wait()', default=1, settable=True,
                           unit='main', category='general'),
        'window':    Param('Window for wait()', default=60, settable=True,
                           unit='s', category='general'),
        'loopdelay': Param('Cycle time for internal thread', default=1,
                           settable=True, unit='s', type=floatrange(0.2, 10)),
        'timeout':   Param('Timeout for wait()', default=900, settable=True,
                           unit='s', category='general'),
        'setpoint':  Param('Current setpoint', settable=False, unit='main',
                           category='general'),
        'heaterpower': Param('Simulated heater output power in percent',
                           settable=False, unit='%'),
        'maxpower':  Param('Max heater power in W', settable=True, unit='W',
                           default=100),
        'p':         Param('P-value for regulation', settable=True,
                           default=100, unit='%/main'),
        'i':         Param('I-value for regulation', settable=True,
                           default=10, unit='%/mains'),
        'd':         Param('D-value for regulation', settable=True,
                           default=2, unit='%s/main'),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False, default='K'),
    }

    _thread = None
    _window = None

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        if not isinstance(session, PollerSession): # dont run in the poller!
            self._window = deque([], ceil(self.window/self.loopdelay))
            self._thread = threading.Thread(target=self.__run,
                                        name='Cryo simulator %s' % self)
            self._thread.daemon = True
            self._thread.start()

    def doStart(self, pos):
        # do nothing more, its handled in the thread...
        self.curstatus = status.BUSY, 'moving'

    def doRead(self, maxage=0):
        return self.regulation + self.jitter * (0.5 - random.random())

    def doStatus(self, maxage=0):
        return self.curstatus

    def doStop(self):
        self.start(self.setpoint)

    def doPoll(self, nr):
        self._pollParam('setpoint', 1)
        self._pollParam('curvalue', 1)
        self._pollParam('curstatus', 1)

    #
    # parameters
    #

    def doWriteWindow(self, window):
        self._window = deque(self._window if self._window else [],
                             ceil(window/self.loopdelay))
    def doWriteLoopdelay(self, loopdelay):
        self._window = deque(self._window if self._window else [],
                             ceil(self.window/loopdelay))

    #
    # calculation helpers
    #
    def __coolerPower(self, temp):
        """returns cooling power in W at given temperature"""
        # 0 below 2K, increasing quadratic up to 40K, is 50W above 40K
        return max(min(100, temp**2 / 16) - 0.25, 0) / 2.

    def __coolerCP(self, temp):
        """heat capacity of cooler at given temp"""
        return 100

    def __heatLink(self, coolertemp, sampletemp):
        """heatflow from sample to cooler. may be negative..."""
        return clamp(sampletemp-coolertemp, -10, 10)

    def __sampleCP(self, temp):
        return 10

    def __sampleLeak(self, temp):
        return 1

    #
    # Model is a cooling source with __coolingPower and __coolerCP capacity
    # here we have THE heater and the regulation thermometer
    # this is connected via a __heatLink to a sample with __heatCapacity and
    # __leak thermal flow, here we have the sample thermometer
    #
    def __run(self):
        try:
            self.__moving()
        except Exception as e:
            self.log.exception(e)
            self.curstatus = status.ERROR, str(e)

    def __moving(self):
        # complex thread handling:
        # a) simulation of cryo (heat flow, thermal masses,....)
        # b) PID temperature controller with optional windup control
        # c) generating status+updated value+ramp
        # this thread is no supposed to exit!

        # local state keeping:
        regulation = self.regulation
        sample = self.sample
        setpoint = self.setpoint
        stable = False
        heater = 0
        I = D = 0
        while True:
            # a)
            heatflow = self.__heatLink(regulation, sample)
            self.log.debug('sample = %.5f, regulation = %.5f, heatflow = %.5g'
                           % (sample, regulation, heatflow))
            newsample = max(0, sample + (self.__sampleLeak(sample) - heatflow) /
                               self.__sampleCP(sample) * self.loopdelay)
            newregulation = max(0, regulation + (heater * 0.01 * self.maxpower
                + heatflow - self.__coolerPower(regulation)) /
                self.__coolerCP(regulation) * self.loopdelay)

            # b) see
            # www.cds.caltech.edu/~murray/books/AM08/pdf/am06-pid_16Sep06.pdf
            error = setpoint - newregulation
            h = self.loopdelay
            kp = self.p / 10        # LakeShore P = 10*k_p
            ki = kp * self.i / 500  # LakeShore I = 500/T_i
            kd = kp * self.d / 2    # LakeShore D = 2*T_d
            if self.i:
                # Windup control time constant
                kt = sqrt(500 / self.i * self.d / 2)
            else:
                kt = 0
            Tf = self.d / 20        # Differential filtering time constant

            P = kp * error
            D = Tf / (Tf + h) * D - \
                kd / (Tf + h) * (newregulation - regulation)
            v = P + I + D
            heater = clamp(v, 0., 100.)
            self.log.debug('PID: P = %.2f, I = %.2f, D = %.2f, heater = %.2f' %
                           (P, I, D, heater))
            I += ki * h * error + kt * h * (heater - v)

            sample = newsample
            regulation = newregulation

            # c)
            if self.setpoint != self.target:
                if self.ramp == 0:
                    maxdelta = 10000
                else:
                    maxdelta = self.ramp / 60 * self.loopdelay
                try:
                    setpoint += clamp(self.target - setpoint,
                                      -maxdelta, maxdelta)
                    self.log.debug('setpoint changes to %r' % setpoint)
                except (TypeError, ValueError):
                    # self.target might be None
                    pass
            self._window.append(regulation)
            # temperature is stable when all recorded values in the window
            # differ from setpoint by less than tolerance
            stable = max(abs(x - self.setpoint) for x in self._window) \
                <= self.tolerance
            # but status is only OK if setpoint is already at target
            if stable and setpoint == self.target:
                # XXX TODO: timeout
                self.curstatus = status.OK, 'stable'
            else:
                self.curstatus = status.BUSY, 'moving'
            self._setROParam('setpoint', setpoint)
            self._setROParam('regulation', regulation)
            self._setROParam('sample', sample)
            self._setROParam('heaterpower', heater)
            time.sleep(self.loopdelay)


class Virtual2DDetector(ImageProducer, Measurable):
    """A virtual 2-dimensional detector that generates a direct beam and
    four peaks of scattering intensity."""

    attached_devices = {
        'distance':    (Moveable, 'the detector distance for simulation'),
        'collimation': (Readable, 'the collimation'),
    }

    parameters = {
        'lastcounts': Param('Current total number of counts', settable=True,
                            type=int),
    }

    imagetype = ImageType((128, 128), '<u4')
    _buf = None
    _mythread = None
    _stopflag = False

    def doSetPreset(self, **preset):
        self._lastpreset = preset

    def doStart(self):
        t = self._lastpreset.get('t', 1)
        if self._mythread:
            self._stopflag = True
            self._mythread.join()
        self._mythread = threading.Thread(target=self._run,  args=(t, ))
        self._mythread.start()

    def _run(self,  maxtime):
        try:
            starttime = now = time.time()
            while True:
                array = self._generate(now - starttime).astype('<u4')
                self._buf = array
                self.lastcounts = array.sum()
                self.updateImage(array)
                if self._stopflag or now > (starttime + maxtime):
                    break
                time.sleep(min(1, maxtime - now + starttime))
                now = time.time()
        finally:
            self._stopflag = False
            self._mythread = None

    def doStop(self):
        self._stopflag = True

    def doStatus(self,  maxage=0):
        if self._stopflag or self._mythread:
            return status.BUSY,  'busy'
        return status.OK,  'idle'

    def readImage(self):
        return self._buf

    def readFinalImage(self):
        return self._buf

    def clearImage(self):
        self._buf = self._generate(0).astype('<u4')
        self.lastcounts = 0

    def doRead(self, maxage=0):
        return [self.lastcounts, self.lastfilename]

    def valueInfo(self):
        return (Value(self.name + '.sum', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'),
                Value(self.name + '.file', type='info', fmtstr='%s'))

    def doIsCompleted(self):
        return not self._mythread

    def _generate(self, t):
        dst = (self._adevs['distance'].read() * 5) if self._adevs['distance'] \
              else 5
        coll = self._adevs['collimation'].read() if self._adevs['collimation'] \
              else '15m'
        xx, yy = np.meshgrid(np.linspace(-64, 63, 128), np.linspace(-64, 63, 128))
        beam = (t * 100 * np.exp(-xx**2/50) * np.exp(-yy**2/50)).astype(int)
        sigma2 = coll == '10m' and 200 or (coll == '15m' and 150 or 100)
        beam += t * 30 * np.exp(-(xx-dst)**2/sigma2) * np.exp(-yy**2/sigma2) + \
            t * 30 * np.exp(-(xx+dst)**2/sigma2) * np.exp(-yy**2/sigma2) + \
            t * 20 * np.exp(-xx**2/sigma2) * np.exp(-(yy-dst)**2/sigma2) + \
            t * 20 * np.exp(-xx**2/sigma2) * np.exp(-(yy+dst)**2/sigma2)
        return np.random.poisson(beam)
