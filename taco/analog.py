#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id $
#
# Description:
#   NICOS TACO analog input/output definition
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

"""Implementation of TACO AnalogInput and AnalogOutput devices."""

__author__  = "$Author $"
__date__    = "$Date $"
__version__ = "$Revision $"

from time import sleep

from IO import AnalogInput, AnalogOutput

from nicm import status
from nicm.device import Readable, Moveable
from taco.base import TacoDevice
from taco.errors import taco_guard


class Input(TacoDevice, Readable):
    """Base class for TACO AnalogInputs."""

    taco_class = AnalogInput


class Output(TacoDevice, Moveable):
    """Base class for TACO AnalogOutputs."""

    parameters = {
        'loopdelay': (0.3, False, 'Wait loop delay in seconds.'),
    }

    taco_class = AnalogOutput

    def doStart(self, value):
        taco_guard(self._dev.write, value)

    def doWait(self):
        while self.status() == status.BUSY:
            sleep(self.getLoopdelay())
