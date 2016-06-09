#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""NICOS temperature controller classes."""

import TACOStates
import Temperature

from nicos.core import status, oneof, Param, Readable, Moveable, HasLimits, \
    Override, HasWindowTimeout, MoveError, PositionError
from nicos.devices.taco.core import TacoDevice


class TemperatureSensor(TacoDevice, Readable):
    """TACO temperature sensor device."""
    taco_class = Temperature.Sensor


class TemperatureController(TacoDevice, HasWindowTimeout, HasLimits, Moveable):
    """TACO temperature controller device."""
    taco_class = Temperature.Controller

    _TACO_STATUS_MAPPING = dict(TacoDevice._TACO_STATUS_MAPPING)
    _TACO_STATUS_MAPPING[TACOStates.UNDEFINED] = (status.NOTREACHED,
                                                  'temperature not reached')

    parameters = {
        'setpoint':  Param('Current temperature setpoint', unit='main',
                           category='general'),
        'mode':      Param('Control mode (manual, zone or openloop)',
                           type=oneof('manual', 'zone', 'openloop'),
                           settable=True),
        'p':         Param('The P control parameter', settable=True,
                           type=float, category='general', chatty=True),
        'i':         Param('The I control parameter', settable=True,
                           type=float, category='general', chatty=True),
        'd':         Param('The D control parameter', settable=True,
                           type=float, category='general', chatty=True),
        'ramp':      Param('Temperature ramp in K/min', unit='K/min',
                           settable=True, volatile=True, chatty=True),
        'timeoutaction':  Param('What to do when a timeout occurs',
                                type=oneof('continue', 'raise'), settable=True),
        'heaterpower':    Param('Current heater power', unit='W',
                                category='general'),
        'controlchannel': Param('Control channel, possible values depend '
                                'on the type of device',
                                type=str, category='general', settable=True,
                                chatty=True),
        'maxheaterpower': Param('Maximum heater output', unit='W',
                                settable=True, category='general'),
    }

    parameter_overrides = {
        'userlimits': Override(volatile=True),
        'precision':  Override(mandatory=False),  # can be read from server
    }

    @property
    def errorstates(self):
        return {status.ERROR: MoveError, status.NOTREACHED: PositionError} \
            if self.timeoutaction == 'raise' else {status.ERROR: MoveError}

    def doStart(self, target):
        if self.status()[0] == status.BUSY:
            self.log.debug('stopping running temperature change')
            self._taco_guard(self._dev.stop)
            self._hw_wait()
        self._taco_guard(self._dev.write, target)
        self._pollParam('setpoint', 100)

    def doTime(self, oldvalue, newvalue):
        if self.ramp:
            ramptime = 60 * abs(newvalue - oldvalue) / self.ramp
        else:
            ramptime = 0
        return ramptime + self.window

    def doStop(self):
        # NOTE: TACO stop sets the setpoint to the current temperature,
        # regardless of ramp
        if self.ramp and self.status(0)[0] == status.BUSY:
            self._taco_guard(self._dev.stop)

    def doPoll(self, n, maxage):
        if self.ramp:
            self._pollParam('setpoint', 1)
            self._pollParam('heaterpower', 1)
        if n % 50 == 0:
            self._pollParam('setpoint', 60)
            self._pollParam('heaterpower', 60)
            self._pollParam('p')
            self._pollParam('i')
            self._pollParam('d')
            self._pollParam('mode')

    def doReadSetpoint(self):
        return self._taco_guard(self._dev.setpoint)

    def doReadP(self):
        return self._taco_guard(self._dev.pParam)

    def doReadI(self):
        return self._taco_guard(self._dev.iParam)

    def doReadD(self):
        return self._taco_guard(self._dev.dParam)

    def doReadRamp(self):
        return self._taco_guard(self._dev.ramp)

    def doReadHeaterpower(self):
        # despite the name this gives the current heater output in Watt
        return self._taco_guard(self._dev.manualHeaterOutput)

    def doReadPrecision(self):
        return float(self._taco_guard(self._dev.deviceQueryResource,
                                      'tolerance'))

    def doReadWindow(self):
        return float(self._taco_guard(self._dev.deviceQueryResource,
                                      'window')[:-1])

    def doReadTimeout(self):
        return float(self._taco_guard(self._dev.deviceQueryResource,
                                      'timeout')[:-1])

    def doReadControlchannel(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'channel')

    def doReadMode(self):
        modes = {1: 'manual', 2: 'zone', 3: 'openloop'}
        return modes[int(self._taco_guard(
            self._dev.deviceQueryResource, 'defaultmode')[:-1])]

    def doReadUserlimits(self):
        """Try to get up-to-date values from the hardware.

        If one of the limits is not supported, we keep any set limit value.
        """
        try:
            limits = list(self._params['userlimits'])
        except Exception:
            limits = list(self.abslimits)
        for i, res in enumerate(['usermin', 'usermax']):
            try:
                limits[i] = float(self._dev.deviceQueryResource(res))
            except Exception as err:
                if str(err) != 'resource not supported':
                    self.log.warning('Could not query %s: %s' % (res, err))
        return tuple(limits)

    def doReadMaxheaterpower(self):
        return float(self._taco_guard(self._dev.deviceQueryResource,
                                      'maxpower'))

    def doWriteP(self, value):
        self._taco_guard(self._dev.setPParam, value)

    def doWriteI(self, value):
        self._taco_guard(self._dev.setIParam, value)

    def doWriteD(self, value):
        self._taco_guard(self._dev.setDParam, value)

    def doWriteRamp(self, value):
        self._taco_guard(self._dev.setRamp, value)

    def __stop_and_set(self, resource, value):
        # helper for all resources which need to stop the devices first.
        # do it, but give a warning
        self.log.warning('Stopping device to set %r, you may need to '
                         'start/move it again.' % resource)
        self._taco_guard(self._dev.stop)
        # do wait for real stop
        self._hw_wait()
        self._taco_update_resource(resource, str(value))

    def doWritePrecision(self, value):
        self.__stop_and_set('tolerance', value)

    def doWriteWindow(self, value):
        self.__stop_and_set('window', value)

    def doWriteTimeout(self, value):
        self.__stop_and_set('timeout', value)

    def doWriteControlchannel(self, value):
        self.__stop_and_set('channel', value)

    def doWriteMode(self, value):
        modes = {'manual': '1', 'zone': '2', 'openloop': '3'}
        self.__stop_and_set('defaultmode', modes[value])

    def doWriteMaxheaterpower(self, value):
        self.__stop_and_set('maxpower', value)

    def doWriteUserlimits(self, limits):
        wlimits = HasLimits.doWriteUserlimits(self, limits)
        if wlimits:
            limits = wlimits
        try:
            self.__stop_and_set('usermax', limits[1])
        except Exception as err:
            if str(err) != 'resource not supported':
                self.log.warning('Error during update of usermax resource: %s'
                                 % err)
