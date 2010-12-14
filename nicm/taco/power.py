#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   TACO power supply classes
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
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

"""TACO power supply classes."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from time import sleep

import TACOStates
from PowerSupply import CurrentControl, VoltageControl

from nicm import status
from nicm.device import Moveable, HasOffset, Param
from nicm.errors import MoveError
from nicm.taco.base import TacoDevice


class Supply(HasOffset, TacoDevice, Moveable):
    """Base class for TACO power supplies."""

    parameters = {
        'ramp': Param('Ramp for the supply; can be zero to deactivate ramping',
                      type=float, unit='main/min', default=0),
        'variance': Param('Variance of the read value to the write value; can '
                          'be zero to deactivate variance check',
                          type=float, unit='%', default=0),
    }

    def doReadRamp(self):
        return self._taco_guard(self._dev.ramp)

    def doWriteRamp(self, value):
        self._taco_guard(self._dev.setRamp, value)

    def doRead(self):
        return self._taco_multitry('read', 2, self._dev.read) - self.offset

    def doStart(self, value, fromvarcheck=False):
        self._taco_multitry('write', 2, self._dev.write, value + self.offset)
        sleep(0.5)  # wait until server goes into "moving" status
        self.doWait()
        if self.variance > 0:
            maxdelta = value * (self.variance/100.) + 0.1
            newvalue = self.doRead()
            if abs(newvalue - value) > maxdelta:
                if not fromvarcheck:
                    self.printwarning('value %s instead of %s exceeds variance'
                                      % (newvalue, value))
                    self.doStart(value, fromvarcheck=True)
                else:
                    raise MoveError(self,
                                    'power supply failed to set correct value')

    def doStatus(self):
        state = self._taco_guard(self._dev.deviceState)
        if state == TACOStates.DEVICE_NORMAL:
            return status.OK, 'device normal'
        elif state == TACOStates.MOVING:
            return status.BUSY, 'ramping'
        else:
            return status.ERROR, TACOStates.stateDescription(state)

    def doWait(self):
        errors = 0
        while True:
            st, msg = self.doStatus()
            if st == status.OK:
                return
            elif st == status.ERROR:
                errors += 1
                if errors == 5:
                    raise MoveError(self, 'wait failed, device in error state')
                self.doReset()
            sleep(0.5)


class CurrentSupply(Supply):
    taco_class = CurrentControl


class VoltageSupply(Supply):
    taco_class = VoltageControl
