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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Virtual devices for testing."""

import random
import threading
import time
from math import atan, exp

import numpy as np
from numpy.random import normal

from nicos import session
from nicos.core import MASTER, POLLER, SIMULATION, ArrayDesc, Attach, \
    CanDisable, HasLimits, HasOffset, HasWindowTimeout, InvalidValueError, \
    Measurable, Moveable, MoveError, Override, Param, Readable, \
    SubscanMeasurable, Value, floatrange, intrange, listof, none_or, oneof, \
    status, tupleof
from nicos.core.scan import Scan
from nicos.devices.abstract import CanReference, Coder, Motor
from nicos.devices.generic.detector import ActiveChannel, ImageChannelMixin, \
    PassiveChannel
from nicos.utils import clamp, createThread
from nicos.utils.timer import Timer


class VirtualMotor(HasOffset, CanDisable, Motor):
    """A virtual motor that can be set to move in finite time
    using a thread.
    """

    parameters = {
        'speed':     Param('Virtual speed of the device', settable=True,
                           type=floatrange(0, 1e6), unit='main/s'),
        'jitter':    Param('Jitter of the read value', default=0, unit='main'),
        'curvalue':  Param('Current value', settable=True, unit='main'),
        'curstatus': Param('Current status', type=tupleof(int, str),
                           settable=True, default=(status.OK, 'idle'),
                           no_sim_restore=True),
        'ramp':      Param('Virtual speed of the device', settable=True,
                           type=floatrange(0, 1e6), unit='main/min',
                           volatile=True, no_sim_restore=True),
    }

    _thread = None

    def doInit(self, mode):
        # set current value to be at target on init, helps with devices
        # that switch between being virtual and real
        # If the target is not set, take the configured curvalue and configured
        # offset. This is helpful for the demo, where normally no targets
        # set at clean setup.
        if mode == MASTER:
            if self.target is not None:
                self._setROParam('curvalue', self.target + self.offset)
            else:
                self._setROParam('target', self.curvalue - self.offset)

    def doStart(self, target):
        if self.curstatus[0] == status.DISABLED:
            raise MoveError(self, 'cannot move, motor is disabled')
        pos = float(target) + self.offset
        if self._thread:
            self._setROParam('curstatus', (status.BUSY, 'waiting for stop'))
            self._stop = True
            self._thread.join()
        if self.speed != 0:
            self._setROParam('curstatus', (status.BUSY, 'virtual moving'))
            self._thread = createThread('virtual motor %s' % self,
                                        self.__moving, (pos, ))
        else:
            self.log.debug('moving to %s', pos)
            self._setROParam('curvalue', pos)
            self._setROParam('curstatus', (status.OK, 'idle'))

    def doRead(self, maxage=0):
        return (self.curvalue - self.offset) + \
            self.jitter * (0.5 - random.random())

    def doStatus(self, maxage=0):
        return self.curstatus

    def doStop(self):
        if self.speed != 0 and \
           self._thread is not None and self._thread.is_alive():
            self._stop = True
        else:
            self._setROParam('curstatus', (status.OK, 'idle'))

    def doSetPosition(self, pos):
        self._setROParam('curvalue', pos + self.offset)

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
                time.sleep(self._base_loop_delay)
                self.log.debug('thread moving to %s', value)
                self._setROParam('curvalue', value)
                if value == pos:
                    return
        finally:
            self._stop = False
            self._setROParam('curstatus', (status.OK, 'idle'))

    def doReadRamp(self):
        return self.speed * 60.

    def doWriteRamp(self, value):
        self.speed = value / 60.

    def doEnable(self, on):
        if not on:
            if self.curstatus[0] != status.OK:
                raise InvalidValueError(self, 'cannot disable busy device')
            self.curstatus = (status.DISABLED, 'disabled')
        else:
            if self.curstatus[0] == status.DISABLED:
                self.curstatus = (status.OK, 'idle')


class VirtualReferenceMotor(CanReference, VirtualMotor):
    """Virtual motor device with reference capability."""

    parameters = {
        'refpos': Param('Reference position if given',
                        type=float, settable=False, default=0.0, unit='main'),
        'refswitch': Param('Type of the reference switch',
                           type=oneof('high', 'low', 'ref', None),
                           default=None, settable=False),
    }

    def doReference(self):
        # if self.status(0)[0] == status.BUSY:
        #   raise NicosError(self, 'cannot reference if device is moving.')
        refswitch = self.refswitch
        self.log.debug('reference: %s', refswitch)
        if refswitch == 'high':
            pos = self.absmax
        elif refswitch == 'low':
            pos = self.absmin
        elif refswitch == 'ref':
            pos = self.refpos
        else:
            self.log.warning('Reference switch %r is not allowed.', refswitch)
            return
        _userlimits = self.userlimits  # save user  limits
        # The use of _setROParam suppresses output to inform about change of
        # limits
        self._setROParam('userlimits', self.abslimits)  # open limits
        try:
            self.maw(pos)
            self.setPosition(self.refpos)
            self._setROParam('target', self.refpos)
        finally:
            self._setROParam('userlimits', _userlimits)  # restore user limits


class VirtualCoder(HasOffset, Coder):
    """A virtual coder that just returns the value of a motor, with offset."""

    hardware_access = False

    attached_devices = {
        'motor': Attach('Motor to read out to get coder value', Readable,
                        optional=True)
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, volatile=True),
    }

    def doRead(self, maxage=0):
        val = self._attached_motor.read(maxage) if self._attached_motor else 0
        return val - self.offset

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doSetPosition(self, pos):
        pass

    def doReadUnit(self):
        """For devices with a unit attribute."""
        # prefer configured unit if nothing is set on the motor device
        return self._config.get('unit', self._attached_motor.unit)


class VirtualChannel(ActiveChannel):
    """A virtual detector channel."""
    parameters = {
        'curvalue':  Param('Current value', settable=True, unit='main'),
        'curstatus': Param('Current status', type=tupleof(int, str),
                           settable=True, default=(status.OK, 'idle'),
                           no_sim_restore=True),
    }

    _delay = 0.1
    _thread = None

    def doInit(self, mode):
        self._stopflag = False
        if mode == MASTER:
            self.curvalue = 0

    def doStart(self):
        if self._thread and self._thread.is_alive():
            return
        self.curvalue = 0
        self.doResume()

    def doPause(self):
        self.doFinish()
        return True

    def doResume(self):
        self._stopflag = False
        self.curstatus = (status.BUSY, 'counting')
        self._thread = createThread('%s %s' % (self.__class__.__name__, self),
                                    self._counting)

    def doFinish(self):
        if self._thread and self._thread.is_alive():
            self._stopflag = True
            self._thread.join()
        else:
            self.curstatus = (status.OK, 'idle')

    def doStop(self):
        self.doFinish()

    def doStatus(self, maxage=0):
        return self.curstatus

    def doRead(self, maxage=0):
        return self.curvalue

    def doShutdown(self):
        if self._thread:
            self.doStop()


class VirtualTimer(VirtualChannel):
    """A virtual timer channel for use together with
    `nicos.devices.generic.detector.Detector`.
    """

    parameter_overrides = {
        'unit': Override(default='s'),
        'preselection': Override(type=float),
    }

    is_timer = True

    def _counting(self):
        self.log.debug('timing to %.3f', self.preselection)
        finish_at = time.time() + self.preselection - self.curvalue
        try:
            while not self._stopflag:
                if self.iscontroller and time.time() >= finish_at:
                    self.curvalue = self.preselection
                    break
                time.sleep(self._base_loop_delay)
                self.curvalue += self._base_loop_delay
        finally:
            self.curstatus = (status.OK, 'idle')

    def doSimulate(self, preset):
        if self.iscontroller:
            return [self.preselection]
        return [random.randint(0, 1000)]

    def valueInfo(self):
        return Value(self.name, unit='s', type='time', fmtstr='%.3f'),

    def doTime(self, preset):
        return self.preselection if self.iscontroller else 0


class VirtualCounter(VirtualChannel):
    """A virtual counter channel for use together with
    `nicos.devices.generic.detector.Detector`.
    """

    parameters = {
        'countrate': Param('The maximum count rate', type=float, default=1000.,
                           settable=False),
        'gentype':   Param('Type of generating function',
                           type=oneof('const', 'gauss'), default='gauss',
                           settable=False),
        'type':      Param('Type of channel: monitor or counter',
                           type=oneof('monitor', 'counter'), mandatory=True),
    }

    parameter_overrides = {
        'unit':   Override(default='cts'),
        'fmtstr': Override(default='%d'),
    }

    def doInit(self, mode):
        VirtualChannel.doInit(self, mode)
        self._fcurrent = 0.
        if self.gentype == 'const':
            self._generator = lambda x: self.countrate * x
        elif self.gentype == 'gauss':
            self._generator = lambda x: normal(loc=self.countrate,
                                               scale=self.countrate / 10.) * x

    def doStart(self):
        self._fcurrent = 0.
        VirtualChannel.doStart(self)

    def _counting(self):
        self.log.debug('counting to %d cts with %d cts/s',
                       self.preselection, self.countrate)
        try:
            while not self._stopflag:
                if self.iscontroller and self.curvalue >= self.preselection:
                    self.curvalue = self.preselection
                    break
                time.sleep(self._base_loop_delay)
                self._fcurrent += max(0,
                                      self._generator(self._base_loop_delay))
                self.curvalue = int(self._fcurrent)
        finally:
            self.curstatus = (status.OK, 'idle')

    def doSimulate(self, preset):
        if self.iscontroller:
            return [self.preselection]
        return [random.randint(0, int(self.countrate))]

    def valueInfo(self):
        return Value(self.name, unit='cts', errors='sqrt', type=self.type,
                     fmtstr='%d'),


class VirtualGauss(PassiveChannel):
    """A virtual channel which returns values from gauss curves centered
    at defined positions of movable devices.
    """
    attached_devices = {
        'motors': Attach('Moveables on which the count depends',
                         Moveable, multiple=True),
        'timer':  Attach('Timer device to use as elapsed time instead of '
                         'real time', PassiveChannel, optional=True),
    }

    parameters = {
        'centers': Param('Center of the gaussian',
                         type=listof(float),
                         settable=True),
        'stddev': Param('Standard deviation of the gauss function',
                        type=float,
                        settable=True,
                        ),
        'rate': Param('Amplitude in counts/sec',
                      type=float,
                      settable=True,
                      default=100.),
    }
    _start_time = None
    _end_time = None
    _pause_start = None
    _pause_interval = None

    def doStart(self):
        self._start_time = time.time()
        self._pause_start = None
        self._pause_time = None
        self._pause_interval = 0
        PassiveChannel.doStart(self)

    def doStop(self):
        self._end_time = time.time()
        PassiveChannel.doStop(self)

    def doFinish(self):
        self._end_time = time.time()
        if self._pause_start:
            self.doResume()
        PassiveChannel.doFinish(self)

    def doPause(self):
        self._pause_start = time.time()

    def doResume(self):
        time_paused = time.time() - self._pause_start
        if self._pause_interval:
            self._pause_interval += time_paused
        else:
            self._pause_interval = time_paused

    def doRead(self, maxage=0):
        if self._attached_timer:
            ampl = self._attached_timer.read(maxage)[0] * self.rate
        elif self._end_time:
            elapsed_time = self._end_time - self._start_time
            if self._pause_interval:
                elapsed_time -= self._pause_interval
            ampl = elapsed_time * self.rate
        else:
            ampl = self.rate
        count = 1.
        for mot, center in zip(self._attached_motors, self.centers):
            count *= max(1.0, ampl * np.exp(-(mot.read(maxage) - center)**2 /
                                            2. * self.stddev**2))
        return int(count)

    def valueInfo(self):
        return Value(self.name, unit='cts', errors='sqrt', type='counter',
                     fmtstr='%d'),


class VirtualTemperature(VirtualMotor):
    """A virtual temperature regulation device."""

    parameters = {
        'setpoint': Param('Last setpoint', settable=True, unit='main',
                          category='general'),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False, default='K'),
        'jitter':    Override(default=0.1),
        'curvalue':  Override(default=10),
        'precision': Override(default=1),
    }

    def doStart(self, target):
        self.setpoint = target
        VirtualMotor.doStart(self, target)

    def _step(self, start, end, elapsed, speed):
        # calculate an exponential approximation to the setpoint with a time
        # constant given by self.speed
        gamma = speed / 10.
        cval = end + (start - end) * exp(-gamma*elapsed)
        if abs(cval - end) < self.jitter:
            return end
        return cval


class VirtualRealTemperature(HasWindowTimeout, HasLimits, Moveable):
    """A virtual temperature regulation device with a realistic simulation
    of a sample in a cryostat, with a PID-controlled heater.
    """

    parameters = {
        'jitter':    Param('Jitter of the read-out value', default=0,
                           unit='main'),
        'regulation': Param('Current temperature (regulation)', settable=False,
                            unit='main', default=2.),
        'sample':    Param('Current temperature (sample)', settable=False,
                           unit='main', default=2.),
        'curstatus': Param('Current status', type=tupleof(int, str),
                           settable=True, default=(status.OK, 'idle'),
                           no_sim_restore=True),
        'ramp':      Param('Ramping speed of the setpoint', settable=True,
                           type=none_or(floatrange(0, 1000)), unit='main/min'),
        'loopdelay': Param('Cycle time for internal thread', default=1,
                           settable=True, unit='s', type=floatrange(0.2, 10)),
        'setpoint':  Param('Current setpoint', settable=True, unit='main',
                           category='general', default=2.),
        'heater':    Param('Simulated heater output power in percent',
                           settable=True, unit='%'),
        'heaterpower': Param('Simulated heater output power in Watt',
                             settable=False, unit='W'),
        'maxpower':  Param('Max heater power in W', settable=True, unit='W',
                           default=100),
        'p':         Param('P-value for regulation', settable=True,
                           default=100, unit='%/main'),
        'i':         Param('I-value for regulation', settable=True,
                           default=10, unit='%/mains'),
        'd':         Param('D-value for regulation', settable=True,
                           default=1, unit='%s/main'),
        'mode':      Param('PID control or open loop heater mode',
                           settable=True, default='manualpid',
                           type=oneof('manualpid', 'manual', 'openloop')),
        'speedup':   Param('Speed up simulation by a factor', settable=True,
                           default=1, unit='', type=floatrange(0.01, 100)),
    }

    parameter_overrides = {
        'unit':    Override(mandatory=False, default='K'),
        'timeout': Override(default=900),
    }

    _thread = None
    _window = None
    _starttime = 0
    _stopflag = False

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        if self.curstatus[0] < status.OK:  # clean up old status values
            self._setROParam('curstatus', (status.OK, ''))
        if session.sessiontype != POLLER:  # don't run in the poller!
            self._window = []
            self._statusLock = threading.Lock()
            self._thread = createThread('cryo simulator %s' % self, self.__run)

    def doShutdown(self):
        self._stopflag = True

    def doStart(self, target):
        # do nothing more, it's handled in the thread...
        with self._statusLock:
            # insert target position into history
            # if target is far away -> loop goes busy
            # else loop sets to stable again....
            currtime = time.time()
            self._window.append((currtime, target))
            self._starttime = currtime
            self.curstatus = status.BUSY, 'ramping setpoint'

    def doRead(self, maxage=0):
        return self.regulation + self.jitter * (0.5 - random.random())

    def doStatus(self, maxage=0):
        return self.curstatus

    def doStop(self):
        self.start(self.setpoint)

    #
    # Parameters
    #
    def doWriteMaxpower(self, newpower):
        self.heater = clamp(self.heater * self.maxpower / float(newpower),
                            0, 100)

    def doReadTarget(self):
        # Bootstrapping helper, called at most once.
        # Start target at the initial current temperature, to avoid going into
        # BUSY state right away.
        return self.parameters['regulation'].default

    #
    # calculation helpers
    #
    def __coolerPower(self, temp):
        """returns cooling power in W at given temperature"""
        # quadratic up to 42K, is linear from 40W@42K to 100W@600K
        # return clamp((temp-2)**2 / 32., 0., 40.) + temp * 0.1
        return clamp(15 * atan(temp * 0.01) ** 3, 0., 40.) + temp * 0.1 - 0.2

    def __coolerCP(self, temp):
        """heat capacity of cooler at given temp"""
        return 75 * atan(temp / 50)**2 + 1

    def __heatLink(self, coolertemp, sampletemp):
        """heatflow from sample to cooler. may be negative..."""
        flow = (sampletemp - coolertemp) * \
               ((coolertemp + sampletemp) ** 2)/400.
        cp = clamp(self.__coolerCP(coolertemp) * self.__sampleCP(sampletemp),
                   1, 10)
        return clamp(flow, -cp, cp)

    def __sampleCP(self, temp):
        return 3 * atan(temp / 30) + \
            12 * temp / ((temp - 12.)**2 + 10) + 0.5

    def __sampleLeak(self, temp):
        return 0.02/temp

    #
    # Model is a cooling source with __coolingPower and __coolerCP capacity
    # here we have THE heater and the regulation thermometer
    # this is connected via a __heatLink to a sample with __heatCapacity and
    # here we have the sample thermometer
    #
    def __run(self):
        try:
            self.__moving()
        except Exception as e:
            if not self._stopflag:
                self.log.exception(e)
                self.curstatus = status.ERROR, str(e)

    def __moving(self):
        # complex thread handling:
        # a) simulation of cryo (heat flow, thermal masses,....)
        # b) optional PID temperature controller with windup control
        # c) generating status+updated value+ramp
        # this thread is not supposed to exit!

        # local state keeping:
        regulation = self.regulation
        sample = self.sample
        timestamp = time.time()
        heater = 0
        lastflow = 0
        last_heaters = (0, 0)
        delta = 0
        I = D = 0  # noqa: E741
        lastD = 0
        damper = 1
        lastmode = self.mode
        while not self._stopflag:
            t = time.time()
            h = t - timestamp
            if h < self.loopdelay / damper:
                time.sleep(clamp(self.loopdelay / damper - h, 0.1, 60))
                continue
            h *= self.speedup
            # a)
            sample = self.sample
            regulation = self.regulation
            heater = self.heater

            heatflow = self.__heatLink(regulation, sample)
            self.log.debug('sample = %.5f, regulation = %.5f, heatflow = %.5g',
                           sample, regulation, heatflow)
            newsample = max(0,
                            sample + (self.__sampleLeak(sample) - heatflow) /
                            self.__sampleCP(sample) * h)
            # avoid instabilities due to too small CP
            newsample = clamp(newsample, sample, regulation)
            regdelta = (heater * 0.01 * self.maxpower + heatflow -
                        self.__coolerPower(regulation))
            newregulation = max(0, regulation +
                                regdelta / self.__coolerCP(regulation) * h)

            # b) see
            # http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/
            if self.mode != 'openloop':
                # fix artefacts due to too big timesteps
                # actually I would prefer reducing loopdelay, but I have no
                # good idea on when to increase it back again
                if heatflow * lastflow != -100:
                    if (newregulation - newsample) * (regulation - sample) < 0:
                        # newregulation = (newregulation + regulation) / 2
                        # newsample = (newsample + sample) / 2
                        damper += 1
                lastflow = heatflow

                error = self.setpoint - newregulation
                # use a simple filter to smooth delta a little
                delta = (delta + regulation - newregulation) / 2.

                kp = self.p / 10.             # LakeShore P = 10*k_p
                ki = kp * abs(self.i) / 500.  # LakeShore I = 500/T_i
                kd = kp * abs(self.d) / 2.    # LakeShore D = 2*T_d

                P = kp * error
                I += ki * error * h  # noqa: E741
                D = kd * delta / h

                # avoid reset windup
                I = clamp(I, 0., 100.)  # noqa: E741

                # avoid jumping heaterpower if switching back to pid mode
                if lastmode != self.mode:
                    # adjust some values upon switching back on
                    I = self.heater - P - D  # noqa: E741

                v = P + I + D
                # in damping mode, use a weighted sum of old + new heaterpower
                if damper > 1:
                    v = ((damper ** 2 - 1) * self.heater + v) / damper ** 2

                # damp oscillations due to D switching signs
                if D * lastD < -0.2:
                    v = (v + heater) / 2.
                # clamp new heater power to 0..100%
                heater = clamp(v, 0., 100.)
                lastD = D

                self.log.debug('PID: P = %.2f, I = %.2f, D = %.2f, '
                               'heater = %.2f', P, I, D, heater)

                # check for turn-around points to detect oscillations ->
                # increase damper
                x, y = last_heaters
                if (x + 0.1 < y and y > heater + 0.1) or \
                   (x > y + 0.1 and y + 0.1 < heater):
                    damper += 1
                last_heaters = (y, heater)

            else:
                # self.heaterpower is set manually, not by pid
                heater = self.heater
                last_heaters = (0, 0)

            heater = round(heater, 3)
            sample = newsample
            regulation = newregulation
            lastmode = self.mode

            # c)
            if self.setpoint != self.target:
                if self.ramp == 0:
                    maxdelta = 10000
                else:
                    maxdelta = self.ramp / 60. * h
                try:
                    self.setpoint = round(self.setpoint +
                                          clamp(self.target - self.setpoint,
                                                -maxdelta, maxdelta), 3)
                    self.log.debug('setpoint changes to %r (target %r)',
                                   self.setpoint, self.target)
                except (TypeError, ValueError):
                    # self.target might be None
                    pass

            # keep max self.window seconds long history
            self._cacheCB('value', regulation, t)

            # temperature is stable when all recorded values in the window
            # differ from setpoint by less than tolerance
            with self._statusLock:
                if self.setpoint == self.target:
                    self._setROParam('curstatus', (status.OK, ''))
                    damper -= (damper - 1) / 10.  # max value for damper is 11
                else:
                    self._setROParam('curstatus',
                                     (status.BUSY, 'ramping setpoint'))
            damper -= (damper - 1) / 20.
            self._setROParam('regulation', round(regulation, 3))
            self._setROParam('sample', round(sample, 3))
            self._setROParam('heaterpower',
                             round(heater * self.maxpower * 0.01, 3))
            self._setROParam('heater', heater)
            timestamp = t


class VirtualImage(ImageChannelMixin, PassiveChannel):
    """A virtual 2-dimensional detector that generates a direct beam and
    four peaks of scattering intensity.
    """

    parameters = {
        'size': Param('Detector size in pixels (x, y)',
                      settable=False,
                      type=tupleof(intrange(1, 2048), intrange(1, 2048)),
                      default=(128, 128)),
        'background': Param('Background level, use 0 to switch off',
                            settable=True, type=int, default=10),
    }

    attached_devices = {
        'distance':    Attach('The detector distance for simulation', Moveable,
                              optional=True),
        'collimation': Attach('The collimation', Readable, optional=True),
    }

    _last_update = 0
    _buf = None
    _mythread = None
    _stopflag = False
    _timer = None

    def doInit(self, mode):
        self.arraydesc = ArrayDesc(self.name, self.size[::-1], '<u4')

    def doPrepare(self):
        if self._mythread and self._mythread.is_alive():
            self._stopflag = True
            self._mythread.join()
        self._mythread = None
        self._buf = self._generate(0).astype('<u4')
        self.readresult = [self._buf.sum()]

    def doStart(self):
        self._last_update = 0
        self._timer = Timer()
        self._timer.start()
        self._stopflag = False
        if self._buf is None:
            self._buf = self._generate(0).astype('<u4')
            self.readresult = [self._buf.sum()]
        if not self._mythread:
            self._mythread = createThread('virtual detector %s' % self, self._run)

    def _run(self):
        while not self._stopflag:
            elapsed = self._timer.elapsed_time()
            self.log.debug('update image: elapsed = %.1f', elapsed)
            array = self._generate(self._base_loop_delay).astype('<u4')
            self._buf = self._buf + array
            self.readresult = [self._buf.sum()]
            time.sleep(self._base_loop_delay)

    def doPause(self):
        self._timer.stop()
        return True

    def doResume(self):
        self._timer.restart()

    def doFinish(self):
        self._stopflag = True

    def doStop(self):
        self.doFinish()

    def doStatus(self,  maxage=0):
        if self._mythread and self._mythread.is_alive():
            return status.BUSY,  'busy'
        return status.OK,  'idle'

    def doReadArray(self, _quality):
        return self._buf

    def valueInfo(self):
        return Value(self.name + '.sum', unit='cts', type='counter',
                     errors='sqrt', fmtstr='%d'),

    def _generate(self, t):
        dst = ((self._attached_distance.read() * 5) if self._attached_distance
               else 5)
        coll = (self._attached_collimation.read() if self._attached_collimation
                else '15m')
        xl, yl = self.size
        xx, yy = np.meshgrid(np.linspace(-(xl // 2), (xl // 2) - 1, xl),
                             np.linspace(-(yl // 2), (yl // 2) - 1, yl))
        beam = (t * 100 * np.exp(-xx**2/50) * np.exp(-yy**2/50)).astype(int)
        sigma2 = coll == '10m' and 200 or (coll == '15m' and 150 or 100)
        beam += (
            t * 30 * np.exp(-(xx-dst)**2/sigma2) * np.exp(-yy**2/sigma2) +
            t * 30 * np.exp(-(xx+dst)**2/sigma2) * np.exp(-yy**2/sigma2) +
            t * 20 * np.exp(-xx**2/sigma2) * np.exp(-(yy-dst)**2/sigma2) +
            t * 20 * np.exp(-xx**2/sigma2) * np.exp(-(yy+dst)**2/sigma2)
        ).astype(int)
        return np.random.poisson(np.ascontiguousarray(beam.T +
                                                      self.background))

    def doEstimateTime(self, elapsed):
        return self._timer.remaining_time()


class VirtualScanningDetector(SubscanMeasurable):
    """A virtual detector whose data acquisition consists of scanning a
    moveable device, and taking data points with another detector.
    """

    attached_devices = {
        'scandev':  Attach('Current device to scan', Moveable),
        'detector': Attach('Detector to scan', Measurable),
    }

    parameters = {
        'positions': Param('Positions to scan over', type=listof(float))
    }

    def doInit(self, mode):
        self._last = [0, '']

    def doSetPreset(self, **preset):
        self._lastpreset = preset

    def doStart(self):
        positions = [[p] for p in self.positions]
        dataset = Scan([self._adevs['scandev']], positions, positions,
                       detlist=[self._adevs['detector']],
                       preset=self._lastpreset, subscan=True).run()
        # process the values...
        yvalues = [subset.detvaluelist[0] for subset in dataset.subsets]
        self._last = [sum(yvalues) / float(len(yvalues)), dataset.filenames[0]]

    def valueInfo(self):
        return (Value(self.name + '.mean', unit='cts', fmtstr='%.1f'),
                Value(self.name + '.file', unit='', type='info'))

    def doRead(self, maxage=0):
        return self._last
