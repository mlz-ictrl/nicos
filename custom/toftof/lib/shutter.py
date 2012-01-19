#  -*- coding: utf-8 -*-
# *****************************************************************************
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
# Module authors:
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF remote shutter control driver"""

__version__ = "$Revision$"

from time import sleep

from nicos.core import status, oneofdict, Moveable
from nicos.taco.io import DigitalOutput


class Shutter(Moveable):
    """TOFTOF Shutter Control."""

    attached_devices = {
        'open':   (DigitalOutput, 'Shutter open button device'),
        'close':  (DigitalOutput, 'Shutter close button device'),
        'status': (DigitalOutput, 'Shutter status device'),
    }

    valuetype = oneofdict({0: 'closed', 1: 'open'})

    def doStart(self, target):
        """This function opens or closes the TOFTOF instrument shutter."""
        if target == 'open':
            self._adevs['open'].start(1)
            sleep(0.01)
            self._adevs['open'].start(0)
        else:
            self._adevs['close'].start(1)
            sleep(0.01)
            self._adevs['close'].start(0)

    def doStop(self):
        """This function closes the TOFTOF instrument shutter."""
        self.start(0)

    def doRead(self):
        ret = self._adevs['status'].read()
        if ret == 1:
            return 'closed'
        else:
            return 'open'

    def doStatus(self):
        ret = self.read(0)
        if ret == 'open':
            return status.BUSY, 'open'
        else:
            return status.OK, 'closed'
