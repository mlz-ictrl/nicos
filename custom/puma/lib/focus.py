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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************

"""Focus class for PUMA. """

from time import sleep

from nicos.core import status, MoveError, waitForStatus, Param
from nicos.utils import createThread
from nicos.devices.generic.axis import Axis


class focus_Axis(Axis):
    """Axis implemented in Python, with NICOS devices for motor and coders."""

    parameters = {
        'uplimit':       Param('The upper limit', unit='deg'),
        'lowlimit':       Param('The lower limit', unit='deg'),
        'startpos':      Param('The backlash position', unit='deg'),
        'flatpos':       Param('The flat position', unit='deg'),
    }

    def doStart(self, target):
        """Starts the movement of the axis to target."""
        if self._checkTargetPosition(self.read(0), target, error=False):
            self.log.debug('not moving, already at %.4f within precision' %
                           target)
            return

        if self.status(0)[0] == status.BUSY:
            self.log.debug('need to stop axis first')
            self.stop()
            waitForStatus(self, ignore_errors=True)
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

    def _positioningThread(self):
        try:
            self._preMoveAction()
        except Exception as err:
            self._setErrorState(MoveError, 'error in pre-move action: %s' %
                                err)
            return
        target = self._target

        if target == 0:
            target = self.flatpos
        elif target > self.uplimit:
            target = self.uplimit
        elif target < self.lowlimit:
            target = self.lowlimit

        self._errorstate = None
        positions = [(target, True)]

        direct = (target - self.read(0))*(self.read(0) - self.startpos)
        if direct < 0:
            positions.insert(0, (self.startpos, True))

        for (pos, precise) in positions:
            try:
                self._positioning(pos, precise)
            except Exception as err:
                self._setErrorState(MoveError,
                                    'error in positioning: %s' % err)
            if self._stoprequest == 2 or self._errorstate:
                break
        try:
            self._postMoveAction()
        except Exception as err:
            self._setErrorState(MoveError,
                                'error in post-move action: %s' % err)

    def _positioning(self, target, precise=True):
        self.log.debug('start positioning, target is %s' % target)
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
            # poll accurate current values and status of child devices so that
            # we can use read() and status() subsequently
            _, pos = self.poll()
            mstatus, mstatusinfo = self._attached_motor.status()
            if mstatus != status.BUSY:
                # motor stopped; check why
                if self._stoprequest == 2:
                    self.log.debug('stop requested, leaving positioning')
                    # manual stop
                    moving = False
                elif not precise and not self._errorstate:
                    self.log.debug('motor stopped and precise positioning '
                                   'not requested')
                    moving = False
                elif self._checkTargetPosition(target, pos):
                    self.log.debug('target reached, leaving positioning')
                    # target reached
                    moving = False
                elif mstatus == status.ERROR:
                    self.log.debug('motor in error status (%s), trying reset' %
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
                        self.log.warning('last try: %s' % self._errorstate)
                    else:
                        self.log.debug('target not reached, retrying: %s' %
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
