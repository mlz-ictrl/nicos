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
#   Johannes Schwarz <johannes.schwarz@frm2.tum.de>
#
# *****************************************************************************
"""Classes for the sample changer."""

from IO import StringIO

from nicos.core import Attach, Device, Moveable, Readable, status
from nicos.devices.taco import NamedDigitalOutput, TacoDevice
from nicos.panda.mcc2 import MCC2Motor


class TacoSerial(TacoDevice, Device):
    taco_class = StringIO

    def communicate(self, what):
        return self._taco_guard(self._dev.communicate, what)


class SamplePusher(NamedDigitalOutput):

    attached_devices = {
        'sensort': Attach('Sensor on top of the tube.', Readable),
        'sensorl': Attach('sensor on the downside', Readable),
        'motor': Attach('dont allow movement if motor is moving', Moveable),
    }

    def doInit(self, mode):
        NamedDigitalOutput.doInit(self, mode)
        self._target_sens = None

    def doIsAllowed(self, pos):
        if self._attached_motor.status(0)[0] == status.BUSY:
            return (False, 'motor moving')
        if not (self._attached_motor.read(0) in (1.000, 2.000, 3.000, 4.000,
                                                 5.000, 6.000, 7.000, 8.000,
                                                 9.000, 10.000, 11.000, 12.000,
                                                 13.000, 14.000, 15.000,
                                                 16.000)):
            return False, 'invalid motor position'
        return True, 'ok'

    def doStart(self, val):
        pos = self.mapping.get(val, val)
        self._taco_guard(self._dev.write, pos)
        if pos == 0:
            self._target_sens = self._attached_sensort
        elif pos == 1:
            self._target_sens = self._attached_sensorl

    def doStatus(self, maxage=0):
        # it is a local object so poller gives wrong state here but maw works
        if self._target_sens:
            if self._target_sens.read(maxage) == 0:
                return status.BUSY, 'moving'
            elif self._target_sens.read(maxage) == 1:
                self._target_sens = None
        return status.OK, 'idle'

    def doRead(self, maxage=0):
        if self._attached_sensort.read(maxage):
            return self._reverse.get(0, 0)
        elif self._attached_sensorl.read(maxage):
            return self._reverse.get(1, 1)


class SampleMotor(MCC2Motor):
    attached_devices = {
        'sensor': Attach('Active sensor locks the motor', Readable)
    }

    def doInit(self, mode):
        MCC2Motor.doInit(self, mode)
        # unlock motor
        self.comm('XP27S1')

    def doIsAllowed(self, pos):
        if pos == self.doRead():
            return (True, 'ok')
        if not self._attached_sensor.read(0):
            return False, 'top sensor not active'
        return True, 'ok'
