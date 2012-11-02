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

from nicos.core import status, oneof, anytype, Device, Param, \
     Readable, Moveable, NicosError, ProgrammingError, TimeoutError, usermethod, none_or
#~ from nicos.devices.abstract import Motor as NicosMotor, Coder as NicosCoder
from nicos.devices.generic.axis import Axis


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
        if self._checkTargetPosition(self.read(0), target, error=False):
            return
        if target<self.read():
            d=self._adevs['motor']
            d.setPosition( d.read() - self.wraparound )
            self.poll()
        return Axis.doStart( self, target )

    @usermethod
    def reference( self ):
        ''' references this axis by finding the reference switch and setting current position to refpos'''
        if self.refpos == None:
            self.log.error( 'Can\'t reference, no refpos specified!')
            return
        if not( -360.0<=self.refpos<=360.0 ):
            raise ValueError(' Refpos needs to be a float within [-360.0 .. 360.0] ')
        if self._mode not in ['master','maintenance']:
            raise UsageError('Can\'t reference if not in master or maintenance mode!')

        oldpos=self.doRead()
        m=self._adevs['motor']
        def refsw():
            return m.doStatus()[1].find('limit switch')>-1
        self.log.info('Referencing: FAST Mode: find refswitch')
        while m.doRead()<0:
            m.setPosition( m.doRead() + self.wraparound )
        try:
            m.doStart( m.doRead()-360 )
        except NicosError, e:
            pass        # if refswitch is already active, doStart gives an exception
        m.wait()
        if not refsw():
            self.log.error('Referencing: No refswitch found!!! Exiting')
            return
        tries=36
        self.log.info('Referencing: FAST Mode: looking for a position without refswitch active')
        while refsw() and tries>0:
            self.log.debug('Another %d 10° slots left to try'%tries)
            m.doStart( m.doRead() + 10 )
            m.wait()
            tries-=1
        if tries==0:
            self.log.error( 'Referencing: RefSwitch still active after 360°, exiting!')
            self.doStart( oldpos )
            self.wait()
            self.poll()
            return
        # ok, now we are at a position where the refswitch is not active, now turn backward until it triggers to find a rough idea
        oldspeed=m.speed
        m.speed=oldspeed/4      # quarter speed for better accuracy
        tries=7
        self.log.info('Referencing: SLOW Mode: Now looking for refswitch going active')
        while not(refsw()) and tries>0:
            self.log.debug('Another %d 3° slots left to try'%tries)
            m.doStart( m.doRead() - 3 )
            m.wait()
            tries-=1
        m.stop()
        m.speed=oldspeed
        if tries==0:
            self.log.error( 'Referencing: RefSwitch still not active after 360°, exiting!')
            self.doStart( oldpos )
            self.wait()
            self.poll()
            return
        # ok, we are at refswitch, motor stopped as soon as it triggered
        # => we are at refpos, communicate this to the motor
        self.log.info('Found Refswitch at %.1f, should have been at %.1f...'%(self.doRead()%self.wraparound,self.refpos))
        self.poll()
        m.setPosition( self.refpos )
        self.poll()
        self.log.info('Referenced, moving to old position (%.2f)....'%oldpos)
        self.doStart( oldpos )
        self.wait()
        self.poll()
