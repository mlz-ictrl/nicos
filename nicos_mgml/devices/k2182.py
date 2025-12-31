# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Petr Čermák <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""Allows to measure in voltage on K2182A over k6221."""

import time
from time import time as currenttime

import numpy as np

from nicos.core import SIMULATION, Attach, ConfigurationError, Device, \
    Measurable, Override, Param, Waitable, oneof, status
from nicos.core.mixins import HasWindowTimeout
from nicos.core.params import Value, none_or
from nicos.devices.entangle import StringIO


class BaseK2182(Device):

    attached_devices = {
        'k6221': Attach('Keithley to communicate via', StringIO,
                        optional=True),
        'k2182': Attach('Direct k2182', StringIO,
                        optional=True),
    }

    _canCurrent = False
    _measuring = False

    def commCurrent(self, cmd, response=False):
        if self._attached_k6221 is not None:
            self.log.debug('commCurrent: %r', cmd)
            if response:
                resp = self._attached_k6221.communicate(cmd)
                self.log.debug('  ->: %r', resp)
                return resp
            self._attached_k6221.writeLine(cmd)
        else:
            raise ConfigurationError('Communication with current source not possible')
        time.sleep(0.01)
        return None

    def commVoltage(self, cmd, response=False):
        if self._attached_k2182 is not None:
            self.log.debug('commDirect: %r', cmd)
            if response:
                resp = self._attached_k2182.communicate(cmd)
                self.log.debug('  ->: %r', resp)
                return resp
            self._attached_k2182.writeLine(cmd)
        elif self._attached_k6221 is not None:
            self.log.debug('commV: %r', cmd)
            if response:
                resp = self._attached_k6221.multiCommunicate((
                    [0.05, 0], [f':SYST:COMM:SER:SEND "{cmd}"', ':SYST:COMM:SER:ENT?']))
                self.log.debug('  ->: %r', resp)
                return resp[0]
            self._attached_k6221.writeLine(f':SYST:COMM:SER:SEND "{cmd}"')
        else:
            raise Exception()
        time.sleep(0.01)
        return None

    @property
    def CanCurrent(self):
        return self._canCurrent

    def doInit(self, mode):
        if self._attached_k6221 is not None and self._attached_k2182 is not None:
            raise ConfigurationError('Both k6221 and k2182 attached!')
        if self._attached_k6221 is None and self._attached_k2182 is None:
            raise ConfigurationError('No communication device attached!')
        if mode != SIMULATION:
            if self._attached_k2182 is not None:
                self._canCurrent = False
            if self._attached_k6221 is not None:
                self._canCurrent = True
            # reset device
            self.commVoltage('*CLS;SYST:PRES')
            time.sleep(0.1)
            # set units
            self.commVoltage(':CONF:VOLT')
            self.log.debug('init complete')
            self.doReset()


class VoltageDev(HasWindowTimeout, BaseK2182, Waitable):

    parameters = {
        '_started': Param('When start was initiated',
                          type=none_or(float),
                          unit='s', userparam=False, settable=True),
        'derivative': Param('Current change of the value within window',
                            unit='/min', category='general'),
        'maxderivative': Param('Current change of the value within window',
                               unit='/min', settable=True, type=none_or(float),
                               category='general'),
        'unit': Param('Unit for voltage values',
                      type=oneof('V', 'mV', 'uV', 'nV', 'mbar', 'torr'),
                      settable=True, default='V',),
    }

    def getValueInUnits(self, resp):
        if self.unit in {'mbar', 'torr'}:
            c = {
                'mbar': 5.5,
                'torr': 5.625,
            }[self.unit]
            return 10**(float(resp) - c)
        return {
            'V': 1.0,
            'mV': 1e3,
            'uV': 1e6,
            'nV': 1e9,
        }[self.unit] * float(resp)

    def doPoll(self, n, maxage):
        if n % 5 == 0:
            self._pollParam('derivative', 1)

    def doReadDerivative(self):
        history = [x for x in self._history if x[1] is not None]
        history = np.array(history).T
        if history is not None and len(history) > 1:
            return np.polyfit(history[0], history[1], 1)[0] * 60
        return 0

    def doRead(self, maxage=0):
        resp = ''
        while not resp:
            resp = self.commVoltage(':DATA:FRESh?', True)
            time.sleep(0.05)
        return self.getValueInUnits(resp)

    def start(self, pos):
        # self.log.info(f'Reseting to {pos}!')
        self._started = currenttime()
        self.resetTimeout(None)
        self.isAtTarget()

    def isAtTarget(self, pos=None, target=None):
        ct = currenttime()
        self._cacheCB('value', pos, ct)

        self._pollParam('derivative', 1)
        # check subset of _history which is in window
        # also check if there is at least one value before window
        # to know we have enough datapoints
        hist = self._history[:]
        window_start = ct - self.window
        hist_in_window = [v for (t, v) in hist if t >= window_start and v]
        # self.log.info(f'windows start {window_start} histin {hist_in_window}')
        if len(hist_in_window) > 0:
            if self.maxderivative is None:
                stable = abs(max(hist_in_window) - min(hist_in_window)) <= self.precision
            else:
                stable = abs(self.derivative) <= self.maxderivative
        else:
            stable = False
        if 0 < len(hist_in_window) < len(hist) and stable:  # pylint: disable=len-as-condition
            if self._started and ct - self._started > self.window:  # always wait for window
                self._clearTimeout()
                self._setROParam('_started', None)
                self.log.info('I am at target')
                return True
        return False

    def doStatus(self, maxage=0):
        # as in manual, p. 15-10
        for _ in range(10):
            try:
                stb = int(self.commVoltage(':STAT:OPER:COND?', True))
                break
            except Exception as ex:
                self.log.debug('Exc: %s', ex)
                time.sleep(0.05)
        else:
            return (status.UNKNOWN, 'cant get status bits')

        stats = []
        if (stb & (1 << 0)) != 0:
            stats.append('calibrating')
        if (stb & (1 << 4)) != 0:
            stats.append('measuring')
        if (stb & (1 << 5)) != 0:
            stats.append('waiting for trigger')
        if (stb & (1 << 8)) != 0:
            stats.append('filter settled')
        if (stb & (1 << 10)) != 0:
            stats.append('idle')
            return (status.WARN, f'not measuring ({", ".join(stats)})')

        if not self._started or self.isAtTarget():
            return (status.OK, f'stable ({", ".join(stats)})')
        return (status.BUSY, f'unstable ({", ".join(stats)})')

    # def doPoll(self, n, maxage):
    #     return (self.status(0), self.read(0))

    def doTime(self, old_value, target):
        return self.window

    def doReset(self):
        # start measuring continuesly
        self.commVoltage(':INIT:CONT 1')


class Voltmeter(BaseK2182, Measurable):

    parameters = {
        'unit': Param('Unit for voltage values',
                      type=oneof('V', 'mV', 'uV', 'nV'), settable=True,
                      default='V',),
    }

    parameter_overrides = {
        'pollinterval': Override(default=60),
        'maxage':       Override(default=70),
    }

    _value = 0

    def getValueInUnits(self, resp):
        return {
            'V': 1.0,
            'mV': 1e3,
            'uV': 1e6,
            'nV': 1e9,
        }[self.unit] * float(resp)

    def doStart(self):
        self.log.debug('asked doStart')
        self._measuring = True
        resp = ''
        while not resp:
            resp = self.commVoltage('READ?', True)
            time.sleep(0.05)
        self._value = self.getValueInUnits(resp)
        self._measuring = False

    def doSetPreset(self, **preset):
        pass

    def doRead(self, maxage=0):
        self.log.debug('asked doRead')
        return self._value

    def valueInfo(self):
        """Return list of active channels."""
        return Value('U', unit=self.unit, fmtstr=self.fmtstr),

    def doReset(self):
        pass

    def doFinish(self):
        pass

    def doStop(self):
        pass

    def doStatus(self, maxage=0):
        if self._measuring:
            return (status.BUSY, 'measuring')
        return (status.OK, 'idle')
