# -*- coding: utf-8 -*-
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

import math
import time

from nicos.devices.abstract import Motor as NicosMotor
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqSleep
from nicos.core.device import Moveable
from nicos.core.params import Param, Override
from nicos.core import Attach
from nicos.core.errors import LimitError


class MicrostepMotor(BaseSequencer, NicosMotor):
    """Virtual motor which implements software based micro stepping for an
    attached Moveable device.
    """

    STATUS_TIME = .3  # waitForCompletion 300 ms
    CODE_TIME = .05   # additional code execution time in polling routine

    attached_devices = {
        "motor": Attach("Motor device which will be moved.", Moveable),
    }

    parameters = {
        "microstep": Param("Software/Pseudo micro step size",
                           type=float, settable=True, mandatory=False,
                           default=0.01),
        "maxtime": Param("Maximum time for one micro step in seconds",
                         type=float, settable=True, mandatory=False,
                         default=0.8),
        "maxspeed": Param("Maximum speed",
                          type=float, settable=False, mandatory=False),
    }

    parameter_overrides = {
        "abslimits": Override(mandatory=False)
    }

    def doInit(self, mode):
        self._setROParam("maxspeed", self.microstep / self.maxmovetime)
        self._delay = self.maxtime
        if self.speed < 1e-8:
            self.log.warning("Speed has not been set. Set maximum speed %.4f",
                             self.maxspeed)
            self.speed = self.maxspeed

    @property
    def motor(self):
        return self._attached_motor

    def _maxmovetime(self, t):
        # maximum movement time including polling time plus additional code
        # execution time.
        return t + MicrostepMotor.STATUS_TIME + MicrostepMotor.CODE_TIME

    @property
    def maxmovetime(self):
        return self._maxmovetime(self.maxtime)

    def doReadAbslimits(self):
        return self._attached_motor.abslimits

    def doWriteAbslimits(self, value):
        self._attached_motor.abslimits = value

    def doReadUserlimits(self):
        return self._attached_motor.userlimits

    def doWriteUserlimits(self, value):
        self._attached_motor.userlimits = value

    def doReadUnit(self):
        return self._attached_motor.unit

    def doWriteUnit(self, value):
        self._attached_motor.unit = value

    def doWriteSpeed(self, value):
        delay = self.microstep / value
        self.log.debug("""
   delay: %.4f
maxspeed: %.4f
 maxtime: %.4f""", delay, self.maxspeed, self.maxtime)
        if value < self.maxspeed or math.fabs(self.maxspeed - value) < 1e-5:
            self._delay = delay
        else:
            raise LimitError(self, "Speed too high. Maximum speed is %.4f"
                             % self.maxspeed)

    def doWriteMaxtime(self, value):
        self._setROParam("maxspeed", self.microstep / self._maxmovetime(value))
        if self.speed > self.maxspeed:
            self.log.warning("Speed too high. Set speed to %.4f",
                             self.maxspeed)
            self.speed = self.maxspeed

    def doWriteMicrostep(self, value):
        self._setROParam("maxspeed", value / self.maxmovetime)
        if self.speed > self.maxspeed:
            self.log.warning("Speed too high. Set speed to %.4f",
                             self.maxspeed)
            self.speed = self.maxspeed

    def doRead(self, maxage=0):
        return self._attached_motor.read(maxage)

    def _generateSequence(self, target, *args, **kwargs):
        pos = self.read(0)
        s = self.microstep if (target - pos) >= 0 else -self.microstep
        n = int((target - pos) / s)
        # handle floating point overflows
        # check whether or not one last microstep fits into movement to target.
        if (math.fabs((pos + (n + 1) * s) - target)
           < math.fabs(self.microstep / 10)):
            n += 1
        res = [(SeqDev(self._attached_motor, pos + i * s),
                SeqSleep(self._delay)) for i in range(1, n)]
        res.append((SeqDev(self._attached_motor, target), SeqSleep(self._delay)))
        return res

    def _sequence(self, sequence):
        t = time.time()
        res = BaseSequencer._sequence(self, sequence)
        t = time.time() - t
        self.log.info("Movement finished, time elapsed %.4f.", t)
        return res

    def doStop(self):
        if not self._seq_is_running():
            self._stopAction(-1)
        BaseSequencer.doStop(self)

    def _stopAction(self, _nr):
        self._attached_motor.stop()
