# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

"""Device classes for Cetoni Nemesys syringe."""

import time

import numpy

from nicos import session
from nicos.core import Attach, Param, errors
from nicos.core.sessions.utils import MASTER
from nicos.core import usermethod
from nicos.devices.entangle import HasOffset, Motor, NamedDigitalOutput, Sensor
from nicos.utils import createThread
from nicos.utils.pid import PID


class TextProgressIndicator:
    _line = ['⠆', '⠃', '⠉', '⠘', '⠰', '⠤']
    _len = len(_line)

    @classmethod
    def next(cls):
        return cls._line[int(time.time()) % cls._len]


class CetoniSensor(HasOffset, Sensor):
    """Device for Cetoni pressure sensor."""

    def doRead(self, maxage=0):
        return self._dev.value - self.offset

    def read_weighted(self):
        values = []
        for _ in range(50):
            values.append(self.doRead())
            session.delay(0.1)
        return numpy.mean(values), numpy.std(values)


class CetoniSyringe(Motor):
    """Device for Cetoni Nemesys high pressure syringe pump.
    This device can attach pressure sensor and 4-state valve."""

    attached_devices = {
        'pressure': Attach('Pressure sensor related to the syringe', CetoniSensor),
        'valve': Attach('Cetoni valve related to the syringe', NamedDigitalOutput),
    }

    parameters = {
        'pid_mode': Param('Flag for PID mode, True when is active', type=bool,
                          settable=True, internal=True, default=False),
        'indicator': Param('ASCII progress bar indicator for PID', type=str,
                           settable=True, internal=True, default=''),
        'pid_ready': Param('Flag is True when PID reaches the target value',
                           type=bool, settable=True, internal=True,
                           default=False),
    }

    def doInit(self, mode):
        self._max_speed = float(self._getProperty('maxspeed'))
        self._max_volume = float(self._getProperty('absmax'))
        self._pressure_limit = float(self._getProperty('limit'))
        self._x, self._y = [], []
        self._pressure = self._attached_pressure
        self._valve = self._attached_valve
        if mode == MASTER:
            self.userlimits = (0.0, int(self._max_volume * 10) / 10.0)
            self.pid_mode = False
            self.pid_ready = False
        self._stop_pid = False
        self._pid_thread = None

    def doEnable(self, on):
        self.pollinterval = 0.5 if on else self._config.get('pollinterval', 300)
        self._pressure.pollinterval = 0.5 if on else self._config.get('pollinterval', 300)
        self._valve.pollinterval = 0.5 if on else self._config.get('pollinterval', 300)
        Motor.doEnable(self, on)

    def doStatus(self, maxage=0):
        if self._mode == MASTER and self.pid_mode:
            self.indicator = TextProgressIndicator.next()
        msg = f'PID {self.indicator}' if self.pid_mode else self._dev.status()
        if self.pid_ready:
            msg += ' Ok'
        return self.tango_status_mapping.get(self._dev.state()), msg

    def doStart(self, target):
        if self.pid_mode:
            self.stop_pid()
        Motor.doStart(self, target)

    def doStop(self):
        if self.pid_mode:
            self.stop_pid()
        Motor.doStop(self)

    def doReset(self):
        if self.pid_mode:
            self.stop_pid()
        Motor.doReset(self)

    def set_fill_level(self, level, speed):
        self.doStatus() # updates self.indicator
        # bypasses doStart() to not break possible PID mode
        self.speed = speed
        self._dev.value = level
        self._hw_wait()

    def dispense_to_cell(self, volume, t=0):
        if self._valve.doRead() != 'outlet':
            self.set_valve_state('outlet')
        speed = abs(volume / t) \
            if t and abs(volume / t) < self._max_speed \
            else self._max_speed
        fill_level = self.doRead() - volume
        if 0 <= speed <= self._max_speed and 0 <= fill_level <= self._max_volume:
            self.speed = speed
            self.doStart(fill_level)
        else:
            raise errors.InvalidValueError(self, 'Target speed or fill level '
                                                 'are out of limits')

    def suck_from_cell(self, volume, t=0):
        self.dispense_to_cell(-volume, t)

    @usermethod
    def keep_pressure(self, target_pressure, rewrite_xy=True):
        """Sets and keeps specific pressure in the syringe using PID.

        Example:

        >>> syringe.keep_pressure(42)

        Sets and keeps 42 bars in the syringe.
        """
        if self._valve.doRead() not in ('closed', 'outlet'):
            raise errors.NicosError(self, 'Corresponding valve should be either'
                                    ' in \"closed\" or \"outlet\" state.')
        self.set_pressure(target_pressure, rewrite_xy)
        if not self._pid_thread:
            self.pid_mode = True
            self._pid_thread = createThread('', self._pid_loop,
                                            (target_pressure, ))
        else:
            raise errors.NicosError(self, 'Another PID thread is running.')

    @usermethod
    def set_pressure(self, target_pressure, rewrite_xy=True):
        """Sets specific pressure in the syringe.

        Example:

        >>> syringe.set_pressure(42)

        Sets 42 bars in the syringe.
        """
        if not 1 <= target_pressure <= self._pressure_limit:
            raise errors.NicosError(self, 'Target pressure is out of limits.')
        if self.pid_mode:
            self.stop_pid()
        if rewrite_xy:
            self._x, self._y = [], []
        pressure = self._pressure.doRead()
        fill = self.doRead()
        step = -0.005 if pressure < target_pressure else 0.005
        while 0 < fill < self._max_volume:
            self.set_fill_level(fill, self._max_speed)
            self._x.append(self.doRead())
            pressure = self._pressure.doRead()
            self._y.append(pressure)
            fill += step
            if step > 0 and pressure <= target_pressure:
                break
            if step < 0 and pressure >= target_pressure:
                break
        if not 0 < fill < self._max_volume:
            raise errors.NicosError(self, 'Can\'t reach the pressure from '
                                          'current syringe fill level.')
        k = (self._y[-1] - self._y[-2]) / (self._x[-1] - self._x[-2])
        b = self._y[-1] - k * self._x[-1]
        fill_level = (target_pressure - b) / k
        self.set_fill_level(fill_level, self._max_speed)

    def _pid_loop(self, target_pressure):

        def virtual_pressure(arg):
            if self._y[-1] - self._y[0] > 0:
                if arg >= self._x[0]:
                    return self._y[0]
                elif arg <= self._x[-1]:
                    return self._y[-1]
            else:
                if arg <= self._x[0]:
                    return self._y[0]
                elif arg >= self._x[-1]:
                    return self._y[-1]
            for i, _ in enumerate(self._x):
                if self._x[i + 1] < arg <= self._x[i] \
                        or self._x[i] < arg <= self._x[i+1]:
                    k = (self._y[i + 1] - self._y[i]) / \
                        (self._x[i + 1] - self._x[i])
                    b = self._y[i] - k * self._x[i]
                    return k * arg + b

        # trains PID algorithm on values measured before, saves a lot of time
        t = 0.0
        delta = self._x[0] - self.doRead()
        pid = PID(init_arg=delta, setpoint=target_pressure,
                  P=1e-4, I=1e-4, D=5e-5, current_time=t)
        while not self._stop_pid:
            pressure = virtual_pressure(self._x[0] - delta)
            delta = pid.update(pressure, t)
            t += 1
            if 0.999 < pressure / target_pressure < 1.001:
                break
            if t > 10000:
                self.stop_pid()
                raise errors.InvalidValueError(self,
                                               'PID controller can\'t reach the'
                                               ' condition.')

        # once good precision is obtained on virtual syringe, it is transferred
        # to the real one
        t = time.time() - t
        buf = []
        while not self._stop_pid:
            self.set_fill_level(self._x[0] - delta, 0.1)
            pressure = self._pressure.doRead()
            buf.append(pressure)
            if len(buf) > 10:
                mean = numpy.mean(buf)
                std = numpy.std(buf)
                self.pid_ready = mean - std <= target_pressure <= mean + std
                del buf[0]
            delta = pid.update(pressure, time.time() - t)
            time.sleep(0.5)

    def stop_pid(self):
        self._stop_pid = True
        self._pid_thread.join()
        self._pid_thread = None
        self._stop_pid = False
        self.pid_ready = False
        self.pid_mode = False

    def set_valve_state(self, state):
        self._valve.doStart(state)
        while self._valve.doRead() != state:
            session.delay(0.1)

    @usermethod
    def debubble(self, volume, number):
        """Method to release the bubbles from the syringe.
        Bubbles are supposed to be released by pumping the solution the Cetoni
        syringe is connected to in specifyed amount of *volume* a *number*
        of times.

        Example:

        >>> syringe.debubble(5, 3)

        Should pump 5 ml of a solvent 3 times.
        """
        state = self._valve.read()
        self.set_valve_state('inlet')
        speed = self.speed
        self.speed = self._max_speed
        self.start(0)
        for _ in range(number):
            self.start(volume)
            self._hw_wait()
            self.start(0)
            self._hw_wait()
        self.set_valve_state(state)
        self.speed = speed
