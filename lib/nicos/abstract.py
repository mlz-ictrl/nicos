#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
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

"""Definition of abstract base device classes."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicos.device import Readable, Moveable, HasLimits, HasOffset, \
     HasPrecision, Param, Override, usermethod


class Coder(HasPrecision, Readable):
    """Base class for all coders."""

    def doRead(self):
        """Returns the current position from encoder controller."""
        return 0

    def doSetPosition(self, target):
        """Sets the current position of the encoder controller to the target."""
        pass

    def doReset(self):
        """Resets the encoder controller."""
        pass


class Motor(HasLimits, Moveable, Coder, HasPrecision):
    """Base class for all motors.

    This class inherits from Coder since a Motor can be used instead of a true
    encoder to supply the current position to an Axis.
    """

    parameters = {
        'speed': Param('The motor speed', unit='main/s', settable=True),
    }

    @usermethod
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

    def doReset(self):
        """Resets the motor controller."""
        pass

    def doStop(self):
        """Stops the movement of the motor."""
        pass


class Axis(HasLimits, HasOffset, HasPrecision, Moveable):
    """Base class for all axes."""

    parameters = {
        'dragerror': Param('The so called \'Schleppfehler\' of the axis',
                           unit='main', default=1, settable=True),
        'maxtries':  Param('Number of tries to reach the target', type=int,
                           default=3, settable=True),
        'loopdelay': Param('The sleep time when checking the movement',
                           unit='s', default=0.3, settable=True),
        'backlash':  Param('The maximum allowed backlash', unit='main',
                           settable=True),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False, settable=True),
    }

    @usermethod
    def setPosition(self, pos):
        """Sets the current position of the motor controller to the target."""
        self.doSetPosition(pos)

    def doSetPosition(self, target):
        """Sets the current position of the motor controller to the target."""
        pass
