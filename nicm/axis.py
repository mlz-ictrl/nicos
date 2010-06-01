#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS axis definition
#
# Author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""NICOS axis definition."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import threading
import time

from nicm import status
from nicm.device import Moveable
from nicm.errors import ConfigurationError, NicmError, PositionError
from nicm.errors import ProgrammingError, MoveError
from nicm.motor import Motor as NicmMotor
from nicm.coder import Coder as NicmCoder


class Axis(Moveable):
    """Base class for all axes."""

    attached_devices = {
        'motor' : NicmMotor,
        'coder' : NicmCoder,
        'obs'   : [NicmCoder],
    }

    parameters = {
        "dragerror": (1, False, "so called 'Schleppfehler'"),
        "precision": (0, False, "precision between requested target "
                                "and reached position"),
        "maxtries":  (3, False, "number of tries to reach the target"),
        "loopdelay": (0.3, False, "sleep time to check the movement"),
        "unit":      ('', False, "unit of the axis value"),
        "backlash":  (0.0, False, "value of the backlash"),
    }

    def doInit(self):
        # Check that motor and unit have the same unit
        if self._adevs['coder'].unit != self._adevs['motor'].unit:
            raise ConfigurationError(self, 'different units for motor and coder'
                                     ' (%s vs %s)' % (self._adevs['motor'].unit,
                                                      self._adevs['coder'].unit))
        # Check that all observers have the same unit as the motor
        for ob in self._adevs['obs']:
            if self._adevs['motor'].unit != ob.unit:
                raise ConfigurationError(self, 'different units for motor '
                                         'and observer %s' % ob)

        self.__offset = 0
        self.__thread = None
        self.__target = self.__read()
        self.__mutex = threading.RLock()
        self.__stopRequest = 0
        self.__error = 0
        self.__locked = False
        self.__dragErrorCount = 0

        self.unit = self._adevs['motor'].unit
        self.__checkMotorLimits()

    def __checkMotorLimits(self):
        # check axis limits against motor absolute limits (the motor should not
        # have user limits defined)
        absmin = self.absmin
        absmax = self.absmax
        if not absmin and not absmax:
            self._params['absmin'] = self._adevs['motor'].absmin
            self._params['absmax'] = self._adevs['motor'].absmax
        else:
            if absmin < self._adevs['motor'].absmin:
                raise ConfigurationError(self, 'absmin below the motor absmin')
            if absmax > self._adevs['motor'].absmax:
                raise ConfigurationError(self, 'absmax below the motor absmax')

    def doStart(self, target, locked=False):
        """Starts the movement of the axis to target."""
        if self.__locked:
            raise NicmError(self, 'this axis is locked')
        if self.__checkTargetPosition(self.read(), target, error=0):
            return

        # TODO: stop the axis instead of raising an exception
        if self.status() == status.BUSY:
            raise NicmError(self, 'axis is moving now, please issue a stop '
                            'command and try it again')

        if self.__thread:
            self.__thread.join()
            del self.__thread
            self.__thread = None

        self.__target = target
        self.__stopRequest = 0
        self.__locked = locked   # lock the movement
        self.__error = 0
        self.__dragErrorCount = 0
        if not self.__thread:
            self.__thread = threading.Thread(None, self.__positioningThread,
                                             'Positioning thread')
            self.printdebug("start thread")
            self.__thread.start()

    def doStatus(self):
        """Returns the status of the motor controller."""
        if self.__error > 0:
            return status.ERROR
        elif self.__thread and self.__thread.isAlive():
            return status.BUSY
        else:
            return self._adevs['motor'].status()

    def doRead(self):
        """Returns the current position from coder controller."""
        self.__checkErrorState()
        return self.__read()

    def doAdjust(self, target):
        """Sets the current position of the motor/coder controller to
        the target.
        """
        self.__checkErrorState()
        if self.status() == status.BUSY:
            raise NicmError(self, 'axis is moving now, please issue a stop '
                            'command and try it again')
        diff = (self.read() - target)
        self.__target = target
        self.__offset += diff

        # Avoid the use of the setPar method for the absolute limits
        if (diff < 0):
                self._params['absmax'] = self.absmax - diff
                self._params['absmin'] = self.absmin - diff
        else:
                self._params['absmin'] = self.absmin - diff
                self._params['absmax'] = self.absmax - diff
        self._Moveable__checkAbsLimits()

        if (diff < 0):
                self._params['usermin'] = self.usermin - diff
                self._params['usermax'] = self.usermax - diff
        else:
                self._params['usermax'] = self.usermax - diff
                self._params['usermin'] = self.usermin - diff
        self._Moveable__checkUserLimits()

    def doReset(self):
        """Resets the motor/coder controller."""
        if self.status() != status.BUSY:
            self.__error = 0

    def doStop(self):
        """Stops the movement of the motor."""
        if self.status() == status.BUSY:
            self.__stopRequest = 1
        else:
            self.__stopRequest = 0

    def doWait(self):
        """Waits until the movement of the motor has stopped and
        the target position has been reached.
        """
        while (self.status() == status.BUSY):
            time.sleep(self.loopdelay)
        else:
            self.__checkErrorState()

    def doLock(self):
        """Locks the axis against any movement."""
        super(Axis, self).doLock()
        self.__locked = True

    def doUnlock(self):
        """Unlocks the axis."""
        super(Axis, self).doUnlock()
        self.__locked = False

    # TODO: add validation for new parameter values where needed

    def doSetDragerror(self, value):
        self._params['dragerror'] = value

    def doSetPrecision(self, value):
        self._params['precision'] = value

    def doSetMaxtries(self, value):
        self._params['maxtries'] = value

    def doSetLoopdelay(self, value):
        self._params['loopdelay'] = value

    def doSetBacklash(self, value):
        self._params['backlash'] = value

    def _preMoveAction(self):
        """ This method will be called before the motor will be moved.
        It should be overwritten in derived classes for special actions"""
        return True

    def _postMoveAction(self):
        """ This method will be called after the axis reached the position or
        will be stopped.
        It should be overwritten in derived classes for special actions"""
        return True

    def _duringMoveAction(self, position):
        """ This method will be called during every cycle in positioning thread
        It should be used to do some special actions like open and close some
        neutron guides or change some blocks, ....
        It should be overwritte in derived classes
        """
        return True

    def __checkErrorState(self):
        if self.status() == status.ERROR:
            if self.__error == 1:
                raise PositionError(self, 'drag error')
            elif self.__error == 2:
                raise MoveError(self, 'precision error')
            elif self.__error == 3:
                raise MoveError(self, 'pre move error')
            elif self.__error == 4:
                raise MoveError(self, 'post move error')
            elif self.__error == 5:
                raise MoveError(self, 'action during the move failed')
            elif self.__error == 6:
                raise MoveError(self, 'move failed maxtries reached')
            else:
                raise ProgrammingError(self, 'unknown error constant %s' %
                                       self.__error)

    def __read(self):
        return self._adevs['coder'].read() - self.__offset

    def __checkDragerror(self):
        tmp = abs(self._adevs['motor'].read() - self._adevs['coder'].read())
        # print 'Diff %.3f' % tmp
        dragDiff = self.dragerror
        if dragDiff <= 0:
            return True
        dragOK = tmp <= dragDiff
        if dragOK:
            for i in self._adevs['obs']:
                tmp = abs(self._adevs['motor'].read() - i.read())
                dragOK = dragOK and (tmp <= dragDiff)
        if not dragOK:
            self.__error = 1
        return dragOK

    def __checkTargetPosition(self, target, pos, error = 2):
        tmp = abs(pos - target)
        dragDiff = self.dragerror
        posOK = tmp <= self.precision
        if posOK:
            for i in self._adevs['obs']:
                tmp = abs(target - i.read())
                if dragDiff > 0:
                    posOK = posOK and (tmp <= dragDiff)
        if not posOK:
            self.__error = error
        return posOK

    def __checkMoveToTarget(self, target, pos, error = 3):
        diffLast = abs(self.__lastPosition - target)
        diffCurr = abs(pos - target)
        self.__lastPosition = pos
        posOK = diffLast >= diffCurr
        if not posOK:
             self.__error = error
        return posOK

    def __positioningThread(self):
        if not self._preMoveAction():
            self.__error = 3
        else:
            self.__error = 0
            if self.backlash:
                for pos in self.__target + self.backlash, self.__target:
                    self.__positioning(pos)
                    if self.__stopRequest == 2 or self.__error != 0:
                        break
            else:
                self.__positioning(self.__target)
            if not self._postMoveAction():
                self.__error = 4
        if self.__locked:
            # if the movement was locked, unlock it
            self.__locked = False

    def __positioning(self, target):
        moving = False
        maxtries = self.maxtries
        self.__lastPosition = self.read()
        __target = target + self.__offset
        self._adevs['motor'].start(__target)
        moving = True

        while moving:
            if self.__stopRequest == 1:
                self._adevs['motor'].stop()
                self.__stopRequest = 2
                continue
            time.sleep(self.loopdelay)
            try:
                pos = self.read()
            except NicmError:
                pass
            if not self.__checkMoveToTarget(__target, pos) or \
                   not self.__checkDragerror():
                # drag error (motor != coder)
                # distance to target will be greater
                self.__stopRequest = 1
            elif self._adevs['motor'].status() != status.BUSY:
                # motor stopped
                if self.__stopRequest == 2 or \
                       self.__checkTargetPosition(__target, pos):
                    # manual stop or target reached
                    moving = False
                elif maxtries > 0:
                    # target not reached, get the current position,
                    # sets the motor to this position and restart it
                    self._adevs['motor'].setPosition(pos)
                    self._adevs['motor'].start(__target)
                    maxtries -= 1
                else:
                    moving = False
                    self.__error = 6
            elif self.__stopRequest == 0:
                if  not self._duringMoveAction(pos):
                    self.__stopRequest = 1
                    self.__error = 5

