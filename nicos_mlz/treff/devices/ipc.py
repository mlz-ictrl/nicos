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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""IPC (Institut für Physikalische Chemie, Göttingen) hardware classes for
Juelich Profibus variant."""


from nicos import session
from nicos.core.params import Param, intrange, oneof
from nicos.devices.abstract import CanReference, Motor as NicosMotor
from nicos.devices.vendor.ipc import IPC_MAGIC, IPCModBusTaco, \
    InvalidCommandError, Motor as IPCMotor


SDA_OFFSET_V35 = 31
SRD_OFFSET = 128

START = 32
DIR_POS = 34
DIR_NEG = 35
SET_CURR_POS = 43
MOVE_REL = 46
REF = 47


class IPCModBusTacoJPB(IPCModBusTaco):
    """IPC protocol communication over TACO RS-485 server, Juelich Profibus
    variant."""

    def _check_server_running(self, dev):
        pass

    def send(self, addr, cmd, param=0, length=0):
        return self._taco_guard(self._dev.genSDA, addr, cmd - SDA_OFFSET_V35,
                                length, param)

    def get(self, addr, cmd, param=0, length=0):
        if cmd >= 139:  # not supported in profibus variant
            raise InvalidCommandError(self, "Command %d %s not supported"
                                      % (cmd, IPC_MAGIC[cmd][0]))
        return self._taco_guard(self._dev.genSRD, addr, cmd - SRD_OFFSET,
                                length, param)

    def doReadBustimeout(self):
        return 0.5

    def doUpdateBustimeout(self, value):
        self.log.debug("doUpdateBustimeout not supported in this version.")


class Motor(CanReference, IPCMotor):

    parameters = {
        "refspeed":  Param("Speed for driving into the limit switch on "
                           "reference. Afterwards the speed defined for the "
                           "motor will be used to perform the reference drive.",
                           type=intrange(0, 255), mandatory=True),
        "refsteps":  Param("Reference position in steps",
                           type=intrange(0, 999999), mandatory=True),
        "reflimit":  Param("Starting position for reference drive, "
                           "negative or positive limit switch",
                           type=oneof("neg", "pos"), default="neg"),
        "limitdist": Param("Distance from limit switch in steps",
                           type=intrange(0, 999999), mandatory=True),
    }

    def doWriteUserlimits(self, limits):
        NicosMotor.doWriteUserlimits(self, limits)

    def doReference(self):
        curspeed = self.speed  # store current speed
        self.log.debug("set speed to %d", self.refspeed)
        self.speed = self.refspeed
        try:
            # drive to limit switch
            direction = DIR_POS if self.reflimit == "pos" else DIR_NEG
            self._attached_bus.send(self.addr, direction)
            session.delay(0.1)
            self._attached_bus.send(self.addr, START)
            session.delay(0.2)
            self._hw_wait()
            # drive in opposite direction in order to leave limit switch
            direction = DIR_NEG if direction == DIR_POS else DIR_POS
            self._attached_bus.send(self.addr, direction)
            session.delay(0.1)
            self._attached_bus.send(self.addr, MOVE_REL, self.limitdist, 6)
            session.delay(0.2)
            self._hw_wait()
            # reference drive
            self._attached_bus.send(self.addr, REF, curspeed, 3)
            session.delay(0.2)
            self._hw_wait()
            # set current position in steps
            self._attached_bus.send(self.addr, SET_CURR_POS, self.refsteps, 6)
            session.delay(0.2)
        finally:
            self.log.debug("restore previous speed to %d", curspeed)
            self.speed = curspeed  # restore previous speed
