#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************

"""MTT class for PUMA.

Takes into account the mobilblock and the additional shielding block change."""

from time import sleep

from nicos.core import status, MoveError, waitForCompletion, Param, Readable, \
    Moveable, Attach
from nicos.utils import createThread
from nicos.devices.generic.axis import Axis


class MTT_Axis(Axis):
    """Axis implemented in Python, with NICOS devices for motor and coders."""

    attached_devices = {
        'io_flag': Attach('Mobilblock signal', Readable),
        'polyswitch': Attach('Main axis encoder device', Moveable),
    }

    parameters = {
        'polypos': Param('Shielding block change position', default=-89.8,
                         unit='deg'),
    }

    def doInit(self, mode):
        Axis.doInit(self, mode)
        self._poly = 0

    def doStart(self, target):
        """Starts the movement of the axis to target."""
        if self._checkTargetPosition(self.read(0), target, error=False):
            self.log.debug('not moving, already at %.4f within precision',
                           target)
            return

        if self.status(0)[0] == status.BUSY:
            self.log.debug('need to stop axis first')
            self.stop()
            waitForCompletion(self, ignore_errors=True)
            # raise NicosError(self, 'axis is moving now, please issue a stop '
            #                  'command and try it again')

        if self._posthread:
            self._posthread.join()
            self._posthread = None

        self._target = target
        self._stoprequest = 0
        self._errorstate = None
        if not self._posthread:
            self._posthread = createThread('positioning thread %s' % self,
                                           self._positioningThread)

    def _preMoveAction(self):
        """This method will be called before the motor will be moved.
        It should be overwritten in derived classes for special actions.

        To abort the move, raise an exception from this method.
        """
        self._poly = self._checkpoly()
#        print 'self._poly =', self._poly

    def _postMoveAction(self):
        """This method will be called after the axis reached the position or
        will be stopped.
        It should be overwritten in derived classes for special actions.

        To signal an error, raise an exception from this method.
        """
#        self._switchpoly()

    def _duringMoveAction(self, position):
        """This method will be called during every cycle in positioning thread.
        It should be used to do some special actions like changing shielding
        blocks, checking for air pressure etc.  It should be overwritten in
        derived classes.

        To abort the move, raise an exception from this method.
        """

    def _positioningThread(self):
        try:
            self._preMoveAction()
        except Exception as err:
            self._setErrorState(MoveError, 'error in pre-move action: %s' % err)
            return
        target = self._target
        self._errorstate = None
        positions = [(target, True)]
        if self.backlash:
            backlash = self.backlash
            lastpos = self.read(0)
            # make sure not to move twice if coming from the side in the
            # direction of the backlash
            backlashpos = target + backlash
            if (backlash > 0 and lastpos < target) or \
               (backlash < 0 and lastpos > target):
                # if backlash position is not allowed, just don't use it
                if self.isAllowed(backlashpos)[0]:
                    positions.insert(0, (backlashpos, False))
                else:
                    # at least try to move to limit
                    if backlashpos > target:
                        limit = self.userlimits[1]
                    else:
                        limit = self.userlimits[0]
                    if self.isAllowed(limit)[0]:
                        positions.insert(0, (limit, False))
                    else:
                        self.log.debug('cannot move to backlash position')
        # Shielding block position
        if abs(self._poly) == 1:
            # print 'positions = ', positions
            positions.insert(0, (self.polypos, True))
            # print 'positions = ', positions

        for (pos, precise) in positions:
            try:
                self._positioning(pos, precise)
            except Exception as err:
                self._setErrorState(MoveError,
                                    'error in positioning: %s' % err)
            if self._stoprequest == 2 or self._errorstate:
                self._poly = 0
                break
            self._switchpoly()
        try:
            self._postMoveAction()
        except Exception as err:
            self._setErrorState(MoveError,
                                'error in post-move action: %s' % err)

    def _positioning(self, target, precise=True):
        self.log.debug('start positioning, target is %s', target)
        seen_inhibit = 0
        moving = False
        offset = self.offset
        tries = self.maxtries
        self._lastdiff = abs(target - self.read(0))
        self._attached_motor.start(target + offset)
        moving = True
        stoptries = 0

        while moving:
            if self._stoprequest == 1:
                self.log.debug('stopping motor')
                self._attached_motor.stop()
                self._stoprequest = 2
                stoptries = 10
                continue
            sleep(self.loopdelay)
            # Check Mobile block change
            seen_inhibit = self._checkinhibit()
            # poll accurate current values and status of child devices so that
            # we can use read() and status() subsequently
            _, pos = self.poll()
            mstatus, mstatusinfo = self._attached_motor.status()
            if mstatus != status.BUSY:
                # print 'mstatus =', mstatus
                # motor stopped; check why
                if self._stoprequest == 2:
                    self.log.debug('stop requested, leaving positioning')
                    # manual stop
                    moving = False
                elif seen_inhibit == 1:
                    # motor stopped because of the MB change
                    tries += 1
#                    print 'reset inhibit'
                    seen_inhibit = 0
#                    print 'moving ', moving, self._stoprequest
                elif not precise and not self._errorstate:
                    self.log.debug('motor stopped and precise positioning '
                                   'not requested')
                    moving = False
                elif self._checkTargetPosition(target, pos):
                    self.log.debug('target reached, leaving positioning')
                    # target reached
                    moving = False
                elif mstatus == status.ERROR:
                    self.log.debug('motor in error status (%s), trying reset',
                                   mstatusinfo)
                    # motor in error state -> try resetting
                    newstatus = self._attached_motor.reset()
                    # if that failed, stop immediately
                    if newstatus[0] == status.ERROR:
                        moving = False
                        self._setErrorState(MoveError, 'motor in error state: '
                                            '%s' % newstatus[1])
                elif tries > 0:
                    if tries == 1:
                        self.log.warning('last try: %s', self._errorstate)
                    else:
                        self.log.debug('target not reached, retrying: %s',
                                       self._errorstate)
                    self._errorstate = None
                    # target not reached, get the current position, set the
                    # motor to this position and restart it. _getReading is the
                    # 'real' value, may ask the coder again (so could slow
                    # down!)
                    self._attached_motor.setPosition(self._getReading())
                    self._attached_motor.start(target + self.offset)
                    tries -= 1
                else:
                    moving = False
                    self._setErrorState(MoveError, 'target not reached after '
                                        '%d tries: %s' % (self.maxtries,
                                                          self._errorstate))
            elif not self._checkMoveToTarget(target, pos):
                self.log.debug('stopping motor because not moving to target')
                self._attached_motor.stop()
                # should now go into next try
            elif not self._checkDragerror():
                self.log.debug('stopping motor due to drag error')
                self._attached_motor.stop()
                # should now go into next try
            elif self._stoprequest == 0:
                try:
                    self._duringMoveAction(pos)
                except Exception as err:
                    self._setErrorState(MoveError, 'error in during-move '
                                        'action: %s' % err)
                    self._stoprequest = 1
            elif self._stoprequest == 2:
                # motor should stop, but does not want to?
                stoptries -= 1
                if stoptries < 0:
                    self._setErrorState(MoveError, 'motor did not stop after '
                                        'stop request, aborting')
                    moving = False

    def _checkpoly(self):
        current = self.read(0)
        if self._target < self.polypos and current >= self.polypos:
            return -1
        elif self._target > self.polypos and current <= self.polypos:
            return 1
        return 0

    def _switchpoly(self):
        """
        function to start air pressure cylinder for additional shielding block
        """
#       print 'Switch poly0, mtt = ', self.read(0)
        temp = self.read(0)
        if abs(temp - self.polypos) <= 0.1:
            # print 'Switch poly'
            if self._poly < 0 and self._attached_polyswitch.read() != 1:
                self._attached_polyswitch.move(1)
                sleep(10)
                if self._attached_polyswitch.read() != 1:
                    self._setErrorState(MoveError, 'shielding block in way, '
                                        'cannot move 2Theta monochromator')
            elif self._poly > 0 and self._attached_polyswitch.read() != 0:
                self._attached_polyswitch.move(0)
                sleep(10)
                if self._attached_polyswitch.read() != 0:
                    self._setErrorState(MoveError, 'shielding block not on '
                                        'position, measurement without'
                                        'shielding yields to enlarged '
                                        'background')

    def _checkinhibit(self):

        """
        function to check if a mobil block change arised
        """

        inh = self._attached_io_flag.read(0)
        if inh == 1:
            self._attached_motor.stop()
            t = 20
            self.log.debug('Waiting for MB. mtt = %s', self.read(0))
            while self._attached_io_flag.read(0) == 1:
                sleep(1)
#                print 'Waiting for MB'
                t -= 1
                if t < 0:
                    self._setErrorState(MoveError, 'timeout occured during '
                                        'wait for mobile block change')
                    self._stoprequest = 2
                    self.log.debug('Error state = %s', self._errorstate)
                    break
        return inh
