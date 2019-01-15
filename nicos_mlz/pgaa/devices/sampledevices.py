#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
"""Auxiliary classes for the sample changer."""

from __future__ import absolute_import, division, print_function

from nicos.core import SIMULATION, Attach, Override, Readable, status
from nicos.devices.taco import NamedDigitalOutput

from nicos_mlz.panda.devices.mcc2 import MCC2Motor


class SamplePusher(NamedDigitalOutput):

    attached_devices = {
        'sensort': Attach('Sensor on top of the tube.', Readable),
        'sensorl': Attach('Sensor on the downside', Readable),
    }

    parameter_overrides = {
        'unit': Override(default=''),
        'fmtstr': Override(default='%s'),
    }

    def doInit(self, mode):
        NamedDigitalOutput.doInit(self, mode)
        self._target_sens = None

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

    def doInit(self, mode):
        MCC2Motor.doInit(self, mode)
        # unlock motor
        if mode != SIMULATION:
            self.comm('XP27S1')
