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

import time
from nicos.core import Param, NicosError, usermethod, none_or, tupleof, status
from nicos.devices.generic.axis import Axis
from nicos.devices.generic.virtual import VirtualMotor


class RotAxis(Axis):
    ''' special class for rotary axis which is on the same physical position every 360 deg,
    but should only move/rotate in one direction. other direction is either forbidden or used for referencing.'''

    parameters = {
        'refpos'   : Param('reference position',
                            type=none_or(float), default=None),
        'wraparound'   : Param('axis wraps around above this value',
                            type=float, default=360.),
        'autoref'   : Param('Number of movements before autoreferencing, None/0=disable, positive=count all moves, negative=count only negative moves',
                            type=none_or(int), default=None),
        'refspeed'   : Param('Motorspeed when referencing or None/0 to use normal speed setting',
                            type=none_or(float), default=None),
    }

    _moves = 0
    _referencing = False

    def doStart( self, target ):
        if self._checkTargetPosition(self.read(0), target, error=False):
            return

        if target<self.read():
            d = self._adevs['motor']
            d.setPosition( d.read() - self.wraparound )
            self.poll()
            self._moves += 1
        else:
            if self.autoref and self.autoref > 0:
                self._moves += 1
        if self.autoref and self._moves > abs( self.autoref ) and not self._referencing:
            self.log.info( 'self.autoref limit reached => referencing NOW' )
            self.reference( target )    # WARNING: This takes a while !
            self._moves = 0     # not checking the success of referencing is intentional!
        return Axis.doStart( self, target )

    @usermethod
    def reference( self, gotopos=None ):
        ''' references this axis by finding the reference switch and then setting current position to refpos.
        1) Finding the refswitch by going backwards until the refswitch (=negative limit switch) fires,
        2) then go forward a little until the switch is not active,
        3) then crawl SLOWLY backwards to hit it again.
        4) current position is set to self.refpos (e.g. the reference is stored, the referencing done)
        If an axis can't go reliably backwards (e.g. blocking) in step 1) then rewrite this code to use forward scanning!!!'''

        try:
            self._referencing = True
            m = self._adevs['motor']
            oldspeed = m.speed

            # Check initial conditions
            if self.refpos == None:
                self.log.error( 'Can\'t reference, no refpos specified!')
                return
            if not( -self.wraparound <= self.refpos <= self.wraparound ):
                raise ValueError(' Refpos needs to be a float within [-%.1f .. %.1f] '
                                            %( self.wraparound, self.wraparound )
                                            )
            if self._mode not in ['master','maintenance']:
                if self._mode == 'simulation':
                    self.log.info(self, 'would reference')
                else:
                    self.log.error(self, 'Can\'t reference if not in master or maintenance mode!')
                return

            # helper for DRY
            def refsw():
                return m.doStatus()[1].find('limit switch')>-1

            # figure out the final position (=current position or gotpos, if gotopos is given)
            oldpos = gotopos is None and self.doRead() or gotopos

            # Step 1) Try to hit the refswitch by turning backwards in a fast way
            self.log.info('Referencing: FAST Mode: find refswitch')
            while m.doRead()<0:
                m.setPosition( m.doRead() + self.wraparound )
                m.poll()
            try:
                m.doStart( m.doRead() - self.wraparound )
            except NicosError, e:
                pass        # if refswitch is already active, doStart gives an exception
            m.wait()        # wait until a) refswitch fires or b) we did a complete turn
            if not refsw():
                self.log.error('Referencing: No refswitch found!!! Exiting')
                return

            # Step 2) Try find a position without refswitch active, but close to it.
            tries = self.wraparound/10+1
            self.log.info('Referencing: FAST Mode: looking for inactive refswitch')
            while refsw() and tries>0:
                self.log.debug('Another %d 10 %s slots left to try'%(tries,self.unit))
                m.doStart( m.doRead() + 10 ) #This should never fail unless something is broken
                m.wait()
                tries -= 1
            if tries == 0:
                self.log.error( 'Referencing: RefSwitch still active after %.1f %s, exiting!'
                                        %(self.wraparound,self.unit)
                                        )
                self.doStart( oldpos )
                self.wait()
                self.poll()
                return

            # Step 3) Now SLOWLY crowl onto the refswitch
            if self.refspeed:
                m.speed = self.refspeed
            tries = 7
            self.log.info('Referencing: SLOW Mode: find refswitch')
            while not(refsw()) and tries>0:
                self.log.debug( 'Another %d 3 %s slots left to try'
                                        %( tries, self.unit )
                                        )
                try:
                    m.doStart( m.doRead() - 3 )
                except NicosError, e:
                    pass        # if refswitch is already active, doStart gives an exception
                m.wait()
                tries -= 1
            m.stop()
            m.speed = oldspeed
            if tries == 0:
                self.log.error( 'Referencing: RefSwitch still not active after %.1f %s, exiting!'
                                        %(self.wraparound,self.unit)
                                        )
                self.doStart( oldpos )
                self.wait()
                self.poll()
                return
            # Step 4) We are _at_ refswitch, motor stopped
            # => we are at refpos, communicate this to the motor
            self.log.info('Found Refswitch at %.1f, should have been at %.1f, lost %.2f %s'
                                %(
                                    self.doRead() % self.wraparound,
                                    self.refpos,
                                    abs( self.doRead() % self.wraparound - self.refpos ),
                                    self.unit,
                                )   )
            self.poll()
            m.setPosition( self.refpos )
            self.poll()
            self.log.info('Referenced, moving to position (%.2f)....'%oldpos)
            self.wait()
            self.doStart( oldpos )
            # if gotopos was given, do not wait...
            if gotopos is None:
                self.wait()
                self.poll()
        finally:
            self._referencing = False
            m.speed = oldspeed


class VirtualRotAxisMotor(VirtualMotor):
    ''' used for testing the above code in demo mode....'''
    def _refswitch( self ):
        return 200.%360.<=self.doRead()%360.<=220.%360.     # simulate a refswitch between 200 and 220
    def doStart( self, pos ):
        if self.curvalue > pos: # going backwards
            if self._refswitch():
                raise NicosError(self, 'Can\'t go backwards, Limit-switch is active!')
        return VirtualMotor.doStart( self, pos )

    def doStatus(self, maxage=0):
        if self._refswitch():
            return (self.curstatus[0],'limit switch - active, '+self.curstatus[1])
        else:
            return self.curstatus

    def _step(self, start, end, elapsed, speed):
        if end < start: # going backwards
            if self._refswitch():
                self._stop = True       # force a stop
                return self.curvalue
        return VirtualMotor._step( self, start, end, elapsed, speed )


