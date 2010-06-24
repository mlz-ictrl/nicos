#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS temperature controller classes
#
# Author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""NICOS temperature controller classes."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time

import TACOStates
import Temperature

from nicm import status
from nicm.device import Readable, Moveable
from nicm.errors import CommunicationError, TimeoutError
from nicm.taco.base import TacoDevice


class Sensor(TacoDevice, Readable):
    taco_class = Temperature.Sensor

    parameters = {
        'sensortype': (None, False, 'The sensor type.'),
        'curvename':  (None, False, 'The sensor curve name.'),
        'serno':      (None, False, 'The sensor serial number.'),
    }

    # from LakeShore 340 operating manual
    sensor_types = {
        0: 'Special',
        1: 'Silicon Diode',
        2: 'GaAlAs Diode',
        3: 'Platinum 100 (250 Ohm)',
        4: 'Platinum 100 (500 Ohm)',
        5: 'Platinum 1000',
        6: 'Rhodium Iron',
        7: 'Carbon-Glass',
        8: 'Cernox',
        9: 'RuOx',
        10: 'Germanium',
        11: 'Capacitor',
        12: 'Thermocouple',
    }

    def doGetSensortype(self):
        stype = self._taco_guard(self._dev.deviceQueryResource, 'sensortype')
        return self.sensor_types.get(stype, str(stype))

    def doGetCurvename(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'curvename')

    def doGetSerno(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'serno')


class Controller(TacoDevice, Moveable):
    taco_class = Temperature.Controller

    attached_devices = {
        'primary_sensor': Sensor,
    }

    parameters = {
        'setpoint':  (None, False, 'The current temperature setpoint.'),
        'p':         (None, False, 'The P control parameter.'),
        'i':         (None, False, 'The I control parameter.'),
        'd':         (None, False, 'The D control parameter.'),
        'ramp':      (None, False, 'The temperature ramp in K/s.'),
        'tolerance': (None, False, 'The window\'s temperature tolerance in K.'),
        'window':    (None, False,
                      'The time window for checking stable temperature in s.'),
        'timeout':   (None, False,
                      'The maximum time in s to wait for stable temperature.'),
        'unit':      (None, False, 'The unit of temperature.'),
        'loopdelay': (1, False, 'The sleep time in s when waiting.'),
    }

    def doInit(self):
        TacoDevice.doInit(self)

    def doRead(self):
        return self._adevs['primary_sensor'].read()

    def doStart(self, target):
        if self.status() == status.BUSY:
            self.printdebug('stopping running temperature change')
            self._taco_guard(self._dev.stop)
        self._taco_guard(self._dev.write, target)

    def doStatus(self):
        state = self._taco_guard(self._dev.deviceState)
        if state == TACOStates.MOVING:
            return status.BUSY
        elif state in [TACOStates.PRESELECTION_REACHED,
                       TACOStates.DEVICE_NORMAL]:
            return status.OK
        elif state == TACOStates.UNDEFINED:
            return status.NOTREACHED
        else:
            return status.ERROR

    def doWait(self):
        delay = self.loopdelay
        while 1:
            v = self.read()
            self.printdebug('current temperature %7.3f %s' % (v, self.unit))
            s = self.status()
            if s == status.OK:
                return v
            elif s == status.ERROR:
                raise CommunicationError(self, 'device in error state')
            elif s == status.NOTREACHED:
                raise TimeoutError(self, 'temperature not reached in %s seconds'
                                   % self.timeout)
            time.sleep(delay)

    def doReset(self):
        self._taco_guard(self._dev.deviceReset)

    def doGetSetpoint(self):
        return self._taco_guard(self._dev.setpoint)

    def doGetP(self):
        return self._taco_guard(self._dev.pParam)

    def doGetI(self):
        return self._taco_guard(self._dev.iParam)

    def doGetD(self):
        return self._taco_guard(self._dev.dParam)

    def doGetRamp(self):
        return self._taco_guard(self._dev.ramp)

    def doGetTolerance(self):
        return float(self._taco_guard(self._dev.deviceQueryResource,
                                      'tolerance'))

    def doGetWindow(self):
        return float(self._taco_guard(self._dev.deviceQueryResource,
                                      'window')[:-1])

    def doGetTimeout(self):
        return float(self._taco_guard(self._dev.deviceQueryResource,
                                      'timeout')[:-1])

    def doSetP(self, value):
        return self._taco_guard(self._dev.setPParam, value)

    def doSetI(self, value):
        return self._taco_guard(self._dev.setIParam, value)

    def doSetD(self, value):
        return self._taco_guard(self._dev.setDParam, value)

    def doSetRamp(self, value):
        return self._taco_guard(self._dev.setRamp, value)

    def doSetTolerance(self, value):
        self._taco_update_resource('tolerance', str(value))

    def doSetWindow(self, value):
        self._taco_update_resource('window', str(value))

    def doSetTimeout(self, value):
        self._taco_update_resource('timeout', str(value))

    def doSetLoopdelay(self, value):
        self._params['loopdelay'] = value
