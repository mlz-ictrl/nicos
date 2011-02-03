#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""Taco motor class for NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from Motor import Motor as TACOMotor
import TACOStates

from nicos import status
from nicos.taco import TacoDevice
from nicos.abstract import Motor as BaseMotor

class Motor(TacoDevice, BaseMotor):
    """TACO motor implementation class."""

    taco_class = TACOMotor

    def doStart(self, target):
        self._taco_guard(self._dev.start, target)

    def doSetPosition(self, target):
        self._taco_guard(self._dev.setpos, target)

    def doStatus(self):
        state = self._taco_guard(self._dev.deviceState)
        if state == TACOStates.DEVICE_NORMAL:
            return (status.OK, 'idle')
        elif state == TACOStates.MOVING:
            return (status.BUSY, 'moving')
        else:
            return (status.ERROR, TACOStates.stateDescription(state))

    def doStop(self):
        self._taco_guard(self._dev.stop)

    def doReadSpeed(self):
        return self._taco_guard(self._dev.speed)

    def doWriteSpeed(self, value):
        self._taco_guard(self._dev.setSpeed, value)
