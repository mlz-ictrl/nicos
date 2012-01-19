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

from time import sleep, time

from IO import StringIO

from nicos.core import status, intrange, Device, Moveable, \
     Param, NicosError, CommunicationError, ProgrammingError
from nicos.taco.core import TacoDevice
from nicos.taco.io import DigitalInput, DigitalOutput

class Shutter (Moveable):
    """TOFTOF Shutter Control
    """

    attached_devices = {
        'open': (DigitalOutput, 'Shutter open button device'),
        'close': (DigitalOutput, 'Shutter close button device'),
        'status': (DigitalOutput, 'Shutter status device'),
    }

    parameters = {
        'maxtries': Param('Maximum tries before raising', type=int, default=3),
    }

    def doInit (self):
        if self._mode == 'simulation' :
            return
            
    def doStart (self, *args):
        """ This function opens the TOFTOF instrument shutter"""
        maxtry = self.maxtries
        while 1==1:
            try:
                ret = self._adevs['open'].move(1)
                sleep(0.01)
                ret = self._adevs['open'].move(0)
                return
            except:
                if maxtry == 0:
                     self.log.warning("could not send open shutter signal", exc=1)
                     return
                maxtry -= 1
    
    def doStop (self, *args):
        """ This function closes the TOFTOF instrument shutter"""
        maxtry = self.maxtries
        while 1==1:
            try:
                ret = self._adevs['close'].move(1)
                sleep (0.01)
                ret = self._adevs['close'].move(0)
                break
            except:
                if maxtry == 0:
                    self.log.warning("could not send close shutter signal", exc=1)
                    return
                maxtry -= 1

    def doRead (self, *args):
        """ This function returns 1 if shutter is opened, 2 on read error and 0 otherwise """
        maxtry = self.maxtries
        while 1==1:
            try:
                ret = self._adevs['status'].read()
            	if ret == 1:
                    return 0
                else:
                    return 1
            except:
                if maxtry == 0:
                    self.log.warning("could not read shutter status", exc=1)
                    return 2
                maxtry -= 1

    def doStatus (self, *args):
        """ This function returns 1 if shutter is opened, 2 on read error and 0 otherwise """
        ret = self.read()
	if ret == 1 :
            return status.BUSY, 'Open'
        else :
            return status.OK, 'Closed'
