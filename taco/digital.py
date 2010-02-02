#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id $
#
# Description:
#   NICOS TACO digital input/output definition
#
# Author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   $Author $
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

"""
Implementation of TACO DigitalInput and DigitalOutput devices.
"""

__date__   = "$Date $"
__version__= "$Revision $"

from IO import DigitalInput, DigitalOutput

from nicm.device import Readable, Moveable
from taco.base import TacoDevice
from taco.errors import taco_guard


class Input(TacoDevice, Readable):
    """Base class for TACO DigitalInputs."""

    taco_class = DigitalInput


class Output(TacoDevice, Moveable):
    """Base class for TACO DigitalOutputs."""

    taco_class = DigitalOutput

    def doStart(self, value):
        taco_guard(self._dev.write, value)
