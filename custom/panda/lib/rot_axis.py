#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Param, NicosError, none_or, ConfigurationError
from nicos.core.utils import devIter
from nicos.devices.generic.axis import Axis
from nicos.devices.generic.virtual import VirtualMotor
from nicos.core import SIMULATION, MASTER, MAINTENANCE


class RefAxis(Axis):
    parameters = {
        'refpos':   Param('reference position',
                          type=none_or(float), default=None),
        'autoref':  Param('Number of movements before autoreferencing, '
                          'None/0=disable, >0:count all moves, <0:count only negative moves',
                          type=none_or(int), default=None, settable=True),
        'refspeed': Param('Motorspeed when referencing or None/0 to use normal speed setting',
                          type=none_or(float), default=None),
    }

    _moves = 0
    _referencing = False

    def doStart(self, target):
        if target < self.read():
            self._moves += 1
        elif self.autoref and self.autoref > 0:
            self._moves += 1

        if self.autoref and self._moves > abs(self.autoref) and not self._referencing:
            self.log.info('self.autoref limit reached => referencing NOW')
            self.reference(target)    # WARNING: This takes a while !

        return Axis.doStart(self, target)  # handles offset as well

    def doReference(self, gotopos=None):  # pylint: disable=W0221
        """references this axis by finding the reference switch and then setting current position to refpos.
        1) Finding the refswitch by going backwards until the refswitch (=negative limit switch) fires,
        2) then go forward a little until the switch is not active,
        3) then crawl SLOWLY backwards to hit it again.
        4) current position is set to self.refpos (e.g. the reference is stored, the referencing done)
        If an axis can't go reliably backwards (e.g. blocking) in step 1) then this fails!!!

        the refpos must be within motor.abslimits!
        """

        try:
            self._referencing = True
            m = self._adevs['motor']
            oldspeed = m.speed

            # Check initial conditions
            if self.refpos is None:
                self.log.error('Can\'t reference, no refpos specified!')
                return
            if self._mode not in [MASTER, MAINTENANCE]:
                if self._mode == SIMULATION:
                    self.log.info(self, 'would reference')
                else:
                    self.log.error(self, 'Can\'t reference if not in master or maintenance mode!')
                return

            # helper for DRY: check for ANY Refswitch
            def refsw():
                st = m.doStatus(0)[1]
                self.log.debug('Checking Status %r for refswitch:' % st)
                return st.lower().find('limit switch') > -1

            # figure out the final position (=current position or gotpos, if gotopos is given)
            oldpos = self.doRead() if gotopos is None else gotopos

            # Step 1) Try to hit the refswitch by turning backwards in a fast way
            self.log.info('Referencing: FAST Mode: find refswitch')
            try:
                m.doStart(m.abslimits[0])
            except NicosError:
                pass        # if refswitch is already active, doStart gives an exception
            m.wait()        # wait until a) refswitch fires or b) movement finished
            m.poll()
            if not refsw() and self._checkTargetPosition(self.read(0), self.abslimits[0], error=False):
                self.log.error('Referencing: No refswitch found!!! Exiting')
                self.doStart(oldpos)
                return

            # Step 2) Try find a position without refswitch active, but close to it.
            self.log.info('Referencing: FAST Mode: looking for inactive refswitch')
            for stepsize in [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200]:
                self.log.debug('trying %s' % self.format(stepsize, unit=True))
                m.doStart(m.doRead() + stepsize)
                m.wait()
                m.poll()
                if not refsw():
                    break
            else:
                self.log.error('Referencing: RefSwitch still active after '
                               '388.8 %s, exiting!' % self.unit)
                self.doStart(oldpos)
                return

            # Step 3) Now SLOWLY crawl onto the refswitch
            if self.refspeed:
                m.speed = self.refspeed
            tries = 7
            self.log.info('Referencing: SLOW Mode: find refswitch')
            while not(refsw()) and tries > 0:
                self.log.debug('Another %d slots left to try' % tries)
                try:
                    m.doStart(m.doRead() - stepsize / 3.)  # pylint: disable=W0631
                except NicosError:
                    pass        # if refswitch is already active, doStart gives an exception
                m.wait()
                tries -= 1
            m.stop()
            m.speed = oldspeed
            if tries == 0:
                self.log.error('Referencing: RefSwitch still not active after %.1f %s, exiting!'
                               % (self.wraparound, self.unit))
                self.doStart(oldpos)
                self.wait()
                self.poll()
                return
            # Step 4) We are _at_ refswitch, motor stopped
            # => we are at refpos, communicate this to the motor
            self.log.info('Found Refswitch at %.2f, should have been at %.2f, lost %.3f %s'
                          % (m.doRead(), self.refpos, m.doRead() - self.refpos, self.unit))
            self.poll()
            for d in devIter(self._adevs, onlydevs=True):
                if hasattr(d, 'setPosition'):
                    try:
                        d.setPosition(self.refpos)
                    except NicosError as e:
                        self.log.error(e)
            self.poll()

            self.log.info('Referenced, moving to position (%.2f)...' % oldpos)
            self.wait()
            self.doStart(oldpos)
            # if gotopos was given, do not wait...
            if gotopos is None:
                self.wait()
                self.poll()
            self._moves = 0
        finally:
            m.speed = oldspeed
            self._referencing = False


class RotAxis(RefAxis):
    """special class for rotary axis which is on the same physical position every 360 deg,
    but should only move/rotate in one direction. other direction is either
    forbidden or used for referencing.
    """

    parameters = {
        'wraparound': Param('axis wraps around above this value',
                            type=float, default=360.),
    }

    def doStart(self, target):
        if self._checkTargetPosition(self.read(0), target, error=False):
            return  # already at target

        # change current position if we want to go backwards
        if target < self.read():
            # a negative move would be interpreted as positive by the RefAxis,
            # as we mod current position
            if self.autoref and self.autoref < 0:
                self._moves += 1  # always count wraparound moves.
            d = self._adevs['motor']
            d.setPosition(d.read() - self.wraparound)
            self.poll()

        return RefAxis.doStart(self, target)

    def doReference(self, gotopos=None):  # pylint: disable=W0221
        """references this axis by finding the reference switch and then setting current position to refpos.
        1) Finding the refswitch by going backwards until the refswitch (=negative limit switch) fires,
        2) then go forward a little until the switch is not active,
        3) then crawl SLOWLY backwards to hit it again.
        4) current position is set to self.refpos (e.g. the reference is stored, the referencing done)
        If an axis can't go reliably backwards (e.g. blocking) in step 1) then this fails!!!
        """

        if not (-self.wraparound <= self.refpos <= self.wraparound):
            raise ConfigurationError(self, 'Refpos needs to be a float within [-%.1f .. %.1f]'
                                     % (self.wraparound, self.wraparound))
        try:
            self._referencing = True
            m = self._adevs['motor']
            oldspeed = m.speed

            # Check initial conditions
            if self.refpos is None:
                self.log.error('Can\'t reference, no refpos specified!')
                return
            if self._mode not in [MASTER, MAINTENANCE]:
                if self._mode == SIMULATION:
                    self.log.info(self, 'would reference')
                else:
                    self.log.error(self, 'Can\'t reference if not in master or maintenance mode!')
                return

            # helper for DRY: check for ANY Refswitch
            def refsw():
                return m.doStatus()[1].lower().find('limit switch') > -1

            # figure out the final position (=current position or gotopos, if gotopos is given)
            oldpos = self.doRead() if gotopos is None else gotopos

            # Step 1) Try to hit the refswitch by turning backwards in a fast way
            self.log.info('Referencing: FAST Mode: find refswitch')
            while m.doRead() < self.wraparound:
                m.setPosition(m.doRead() + self.wraparound)
                m.poll()
            try:
                m.doStart(m.doRead() - self.wraparound)
            except NicosError:
                pass        # if refswitch is already active, doStart gives an exception
            m.wait()        # wait until a) refswitch fires or b) we did a complete turn
            if not refsw():
                self.log.error('Referencing: No refswitch found!!! Exiting')
                return

            # Step 2) Try find a position without refswitch active, but close to it.
            tries = self.wraparound/10+1
            self.log.info('Referencing: FAST Mode: looking for inactive refswitch')
            while refsw() and tries > 0:
                self.log.debug('Another %d 10 %s slots left to try' % (tries, self.unit))
                m.doStart(m.doRead() + 10)  # This should never fail unless something is broken
                m.wait()
                tries -= 1
            if tries == 0:
                self.log.error('Referencing: RefSwitch still active after %.1f %s, exiting!'
                               % (self.wraparound, self.unit))
                self.doStart(oldpos)
                self.wait()
                self.poll()
                return

            # Step 3) Now SLOWLY crowl onto the refswitch
            if self.refspeed:
                m.speed = self.refspeed
            tries = 7
            self.log.info('Referencing: SLOW Mode: find refswitch')
            while not(refsw()) and tries > 0:
                self.log.debug('Another %d 3 %s slots left to try'
                               % (tries, self.unit))
                try:
                    m.doStart(m.doRead() - 3)
                except NicosError:
                    pass        # if refswitch is already active, doStart gives an exception
                m.wait()
                tries -= 1
            m.stop()
            m.speed = oldspeed
            if tries == 0:
                self.log.error('Referencing: RefSwitch still not active after %.1f %s, exiting!'
                               % (self.wraparound, self.unit))
                self.doStart(oldpos)
                self.wait()
                self.poll()
                return
            # Step 4) We are _at_ refswitch, motor stopped
            # => we are at refpos, communicate this to the motor
            self.log.info('Found Refswitch at %.1f, should have been at %.1f, lost %.2f %s'
                          % (m.doRead() % self.wraparound, self.refpos,
                             abs(m.doRead() % self.wraparound - self.refpos), self.unit))
            self.poll()
            for d in devIter(self._adevs, onlydevs=True):
                if hasattr(d, 'setPosition'):
                    try:
                        d.setPosition(self.refpos)
                    except NicosError as e:
                        self.log.error(e)
            self.poll()
            self.log.info('Referenced, moving to position (%.2f)...' % oldpos)
            self.wait()
            self.doStart(oldpos)
            # if gotopos was given, do not wait...
            if gotopos is None:
                self.wait()
                self.poll()
            self._moves = 0
        finally:
            m.speed = oldspeed
            self._referencing = False


class VirtualRotAxisMotor(VirtualMotor):
    """used for testing the above code in demo mode....
    simulates a refswitch between 200 and 220
    """
    def _refswitch(self):
        return 200. <= self.doRead() <= 220.

    def doStart(self, pos):
        if self.curvalue > pos:  # going backwards
            if self._refswitch():
                raise NicosError(self, 'Can\'t go backwards, Limit-switch is active!')
        return VirtualMotor.doStart(self, pos)

    def doStatus(self, maxage=0):
        if self._refswitch():
            return (self.curstatus[0], 'limit switch - active, ' + self.curstatus[1])
        else:
            return self.curstatus

    def _step(self, start, end, elapsed, speed):
        if end < start:  # going backwards
            if self._refswitch():
                self._stop = True       # force a stop
                return self.curvalue
        return VirtualMotor._step(self, start, end, elapsed, speed)
