# -*- coding: utf-8 -*-
"""
    nicm.motor
    ~~~~~~~~~~

    NICOS motor definition.
"""

__author__ = "Jens Krüger <jens.krueger@frm2.tum.de>"
__date__   = "2009/10/27"
__version__= "0.0.1"

from nicm import status
from nicm.device import Moveable


class Motor(Moveable):
    """Base class for all motors."""

    def setPosition(self, pos):
        self.doSetPosition(pos)

    def doInit(self):
        """Initializes the class."""
        pass

    def doStart(self, target):
        """Starts the movement of the motor to target."""
        pass

    def doRead(self) :
        """Returns the current position from motor controller."""
        return 0

    def doSetPosition(self, target) :
        """Sets the current position of the motor controller to the target."""
        pass

    def doStatus(self) :
        """Returns the status of the motor controller."""
        return status.OK

    def doReset(self) :
        """Resets the motor controller."""
        pass

    def doStop(self) :
        """Stops the movement of the motor."""
        pass
