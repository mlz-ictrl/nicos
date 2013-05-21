#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Taco motor class for NICOS."""

from Motor import Motor as TACOMotor
import TACOStates

from nicos.core import status, waitForStatus, Param, Override, \
     oneof
from nicos.devices.abstract import CanReference, Motor as BaseMotor
from nicos.devices.taco.core import TacoDevice


class Motor(CanReference, TacoDevice, BaseMotor):
    """TACO motor implementation class."""

    taco_class = TACOMotor

    parameters = {
        # do not call deviceReset by default as it does a reference drive
        'resetcall':  Param('What TACO method to call on reset (deviceInit or '
                            'deviceReset)', settable=True, default='deviceInit',
                            type=oneof('deviceInit', 'deviceReset')),
    }

    parameter_overrides = {
        'abslimits':  Override(mandatory=False),
    }

    def doReset(self):
        try:
            if self.resetcall == 'deviceReset':
                self._taco_guard(self._dev.deviceReset)
            else:
                self._taco_guard(self._dev.deviceInit)
        except Exception:
            pass
        if self._taco_guard(self._dev.isDeviceOff):
            self._taco_guard(self._dev.deviceOn)

    def doReference(self):
        self._taco_guard(self._dev.deviceReset)
        self.doWait()

    def doStart(self, target):
        self._taco_guard(self._dev.start, target)

    def doWait(self):
        waitForStatus(self)

    def doSetPosition(self, target):
        self._taco_guard(self._dev.setpos, target)

    def doStatus(self, maxage=0):
        state = self._taco_guard(self._dev.deviceState)
        if state == TACOStates.DEVICE_NORMAL:
            return status.OK, 'idle'
        elif state == TACOStates.MOVING:
            return status.BUSY, 'moving'
        elif state in (TACOStates.INIT, TACOStates.RESETTING):
            return status.BUSY, 'referencing'
        else:
            return status.ERROR, TACOStates.stateDescription(state)

    def doStop(self):
        self._taco_guard(self._dev.stop)

    def doReadSpeed(self):
        return self._taco_guard(self._dev.speed)

    def doWriteSpeed(self, value):
        self._taco_guard(self._dev.setSpeed, value)

    def doReadAbslimits(self):
        m1 = float(self._taco_guard(self._dev.deviceQueryResource, 'limitmin'))
        m2 = float(self._taco_guard(self._dev.deviceQueryResource, 'limitmax'))
        if m1 >= m2:
            self.log.warning('TACO limitmin/max (%s, %s) are not usable' %
                             (m1, m2))
            return (0, 0)
        return (m1, m2)
