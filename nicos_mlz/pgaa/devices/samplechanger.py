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

from nicos.core import Attach, Device, Moveable, Override, Readable, status
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqSleep
from nicos.devices.taco import NamedDigitalOutput, TacoDevice
from nicos_mlz.panda.devices.mcc2 import MCC2Motor


class TacoSerial(TacoDevice, Device):
    taco_class = StringIO

    def communicate(self, what):
        return self._taco_guard(self._dev.communicate, what)


class SamplePusher(NamedDigitalOutput):

    attached_devices = {
        'sensort': Attach('Sensor on top of the tube.', Readable),
        'sensorl': Attach('Sensor on the downside', Readable),
        'motor': Attach('Stage rotation', Moveable),
    }

    parameter_overrides = {
        'unit': Override(default=''),
        'fmtstr': Override(default='%s'),
    }

    def doInit(self, mode):
        NamedDigitalOutput.doInit(self, mode)
        self._target_sens = None

    def doIsAllowed(self, pos):
        if self._attached_motor.status(0)[0] == status.BUSY:
            return False, 'motor moving'
        if self._attached_motor.read(0) not in (1., 2., 3., 4., 5., 6., 7., 8.,
                                                9., 10., 11., 12., 13., 14.,
                                                15., 16.):
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


class SampleChanger(BaseSequencer):
    """The PGAA sample changer device."""

    attached_devices = {
        'motor': Attach('Stage rotation', Moveable),
        'push': Attach('', Moveable),  # SamplePusher),
    }

    parameter_overrides = {
        'unit': Override(default=''),
        'fmtstr': Override(default='%.f'),
    }

    def _generateSequence(self, target):
        seq = []
        if target != self.doRead(0):
            seq.append(SeqDev(self._attached_push, 'up', stoppable=False))
            seq.append(SeqSleep(2))
            seq.append(SeqDev(self._attached_motor, target,
                              stoppable=False))
            seq.append(SeqSleep(2))
            seq.append(SeqDev(self._attached_push, 'down', stoppable=False))
        return seq

    def doRead(self, maxage=0):
        return self._attached_motor.read(maxage)
