#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# **************************************************************************
"""Support Code for REFSANS's NOK's."""

from nicos import session
from nicos.core import SIMULATION
from nicos.core.params import Override, Param, floatrange, intrange, none_or
from nicos.devices.abstract import CanReference
from nicos.devices.vendor.ipc import Motor as IPCMotor


# heavily based upon old nicm_nok.py, backlash is handled by an axis nowadays
class NOKMotorIPC(CanReference, IPCMotor):
    """Basically a IPCMotor with referencing."""

    parameters = {
        'refpos': Param('Reference position in phys. units',
                        unit='main', type=none_or(float), mandatory=True),
    }

    parameter_overrides = {
        'zerosteps': Override(default=500000, mandatory=False),
        'unit': Override(default='mm', mandatory=False),
        'backlash': Override(type=floatrange(0.0, 0.0)),  # only 0 is allowed!
        'speed': Override(default=10),
        'accel': Override(default=10),
        'slope': Override(default=2000),
        'confbyte': Override(default=48),
        'divider': Override(type=intrange(-1, 7)),
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            self._attached_bus.ping(self.addr)
            if self._hwtype == 'single':
                if self.confbyte != self.doReadConfbyte():
                    self.doWriteConfbyte(self.confbyte)
                    self.log.warning('Confbyte mismatch between setup and card'
                                     ', overriding card value to 0x%02x',
                                     self.confbyte)
            # make sure that the card has the right "last steps"
            # This should not applied at REFSANS, since it disturbs the running
            # TACO server settings
            # if self.steps != self.doReadSteps():
            #     self.doWriteSteps(self.steps)
            #     self.log.warning('Resetting stepper position to last known '
            #                      'good value %d', self.steps)
            self._type = 'stepper motor, ' + self._hwtype
        else:
            self._type = 'simulated stepper'

    def doReference(self):
        bus = self._attached_bus
        bus.send(self.addr, 34)  # always go forward (positive)
        bus.send(self.addr, 47, self.speed, 3)  # reference with normal speed
        # may need to sleep a little here....
        session.delay(0.1)
        self.wait()
        self.doSetPosition(self.refpos)
