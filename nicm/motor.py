#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS motor definition
#
# Author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
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
NICOS motor definition.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicm import status
from nicm.coder import Coder
from nicm.device import Moveable, Param


class Motor(Moveable, Coder):
    """Base class for all motors.

    This class inherits from Coder since a Motor can be used instead of a true
    encoder to supply the current position to an Axis.
    """

    parameters = {
        'speed': Param('The motor speed in units/second', settable=True),
    }

    def setPosition(self, pos):
        """Sets the current position of the motor controller to the target."""
        self.doSetPosition(pos)

    def doInit(self):
        """Initializes the class."""
        pass

    def doStart(self, target):
        """Starts the movement of the motor to target."""
        pass

    def doRead(self):
        """Returns the current position from motor controller."""
        return 0

    def doSetPosition(self, target):
        """Sets the current position of the motor controller to the target."""
        pass

    def doStatus(self):
        """Returns the status of the motor controller."""
        return status.OK

    def doReset(self):
        """Resets the motor controller."""
        pass

    def doStop(self):
        """Stops the movement of the motor."""
        pass
