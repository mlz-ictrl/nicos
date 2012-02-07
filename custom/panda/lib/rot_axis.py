#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA rotary axis for NICOS."""

__version__ = "$Revision$"

#~ from time import sleep, time as currenttime

from nicos.core import status, intrange, oneof, anytype, Device, Param, \
     Readable, Moveable, NicosError, ProgrammingError, TimeoutError, usermethod, none_or
#~ from nicos.abstract import Motor as NicosMotor, Coder as NicosCoder
from nicos.generic.axis import Axis


class RotAxis(Axis):
    ''' special class for ratary axis which is on the same physical position every 360 deg,
    but should only move/rotate in one direction. other direction is either forbidden or used for referencing.'''
    
    parameters = {
        'refpos'   : Param('reference position',
                            type=none_or(float), default=None),
        'wraparound'   : Param('axis wraps around above this value',
                            type=float, default=360),
    }

    def doStart( self, target ):
        if target<self.read():
            d=self._adevs['motor']
            d.setPosition( d.read() - self.wraparound )
            self.poll()
        return Axis.doStart( self, target )
    
    @usermethod
    def reference( self ):
        ''' TODO'''
        pass
