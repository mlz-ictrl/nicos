# -*- coding: utf-8 -*-
"""
    nicm.coder
    ~~~~~~~~~~

    NICOS coder definition.
"""

__author__ = "Jens Krüger <jens.krueger@frm2.tum.de>"
__date__   = "2009/10/27"
__version__= "0.0.1"

from nicm import status
from nicm.device import Readable


class Coder(Readable):
    """Base class for all coders."""

    def doRead(self):
        """Returns the current position from encoder controller."""
        return 0

    def doSetPosition(self, target):
        """Sets the current position of the encoder controller to the target."""
        pass

    def doStatus(self):
        """Returns the status of the encoder controller."""
        return status.OK

    def doReset(self):
        """Resets the encoder controller."""
        pass
