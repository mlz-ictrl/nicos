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

"""Allows to measure in voltage on Keysight 34420."""

import time
from time import time as currenttime

import numpy as np

from nicos.core import Attach, Device, Measurable, Override, Param, Waitable, \
    status
from nicos.core.mixins import HasWindowTimeout
from nicos.core.params import Value, none_or, oneof
from nicos.devices.entangle import StringIO


class BaseK34420(Device):

    attached_devices = {
        'k34420': Attach('Direct k34420', StringIO,
                         optional=True),
    }

    _canCurrent = False
    _measuring = False

    def comm(self, cmd, response=False):
        self.log.debug('commDirect: %r', cmd)
        if response:
            resp = self._attached_k34420.communicate(cmd)
            self.log.debug('  ->: %r', resp)
            return resp
        self._attached_k34420.writeLine(cmd)

        time.sleep(0.01)
        return None

    def doInit(self, mode):
        self.comm('*CLS;SYST:PRES')
        time.sleep(0.1)
        self.comm(':CONF:VOLT')
        self.log.debug('init complete')
        self.doReset()


class VoltageDev(HasWindowTimeout, BaseK34420, Waitable):

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
        if history and len(history) > 1:
            return np.polyfit(history[0], history[1], 1)[0] * 60
        return 0

    def doRead(self, maxage=0):
        resp = ''
        while not resp:
            resp = self.comm('MEAS?', True)
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
        if not self._started or self.isAtTarget():
            return (status.OK, 'stable')
        return (status.BUSY, 'unstable')

    # def doPoll(self, n, maxage):
    #     return (self.status(0), self.read(0))

    def doTime(self, old_value, target):
        return self.window

    def doReset(self):
        pass


class Voltmeter(BaseK34420, Measurable):

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
            resp = self.comm('MEAS?', True)
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
