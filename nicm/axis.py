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
#   $Author$
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

"""
NICOS axis definition.
"""

__author__ = "Jens Krüger <jens.krueger@frm2.tum.de>"
__date__   = "$Date$"
__version__= "$Revision$"

import threading
import time

from nicm import status
from nicm.device import Moveable
from nicm.errors import ConfigurationError, NicmError, LimitError, PositionError
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
        if self.coder.getUnit() != self.motor.getUnit():
            raise ConfigurationError('%s: different units for motor '
                                     'and coder' % self)
        # Check that all observers have the same unit as the motor
        for i in self.obs :
            if self.motor.getUnit() != i.getUnit():
                raise ConfigurationError('%s: different units for motor '
                                     'and observer' % (self % i))

        self.__checkAbsLimits()
        self.__checkUserLimits(setthem=True)

        self.__offset = 0
        self.__thread = None
        self.__target = self.__read()
        self.__mutex = threading.RLock()
        self.__stopRequest = 0
        self.__error = 0
        self.__locked = False
        self.__dragErrorCount = 0

        self.setPar('unit', self.motor.getUnit())

    def doVersion(self):
        """ returns the version of the module (class)"""
        return __version__

    def doStart(self, target, locked=False):
        """Starts the movement of the axis to target."""
        if self.__locked:
            raise NicmError('%s: this axis is locked' % self)
        if not self.__checkTargetPosition(self.read(), 0) :
            return

        # TODO: stop the axis instead of raising an exception
        if self.status() == status.BUSY :
            raise NicmError('%s: axis is moving now, please issue a stop '
                                'command and try it again' % self)
        if not self.isAllowed(target):
            raise LimitError('%s: target %f is not allowed, limits [%f, %f]' %
                           (self, target, self.getUsermin(), self.getUsermax()))

        if self.__thread:
            self.__thread.join()
            del self.__thread
            self.__thread = None

        try:
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
        except Exception:
            raise Exception('%s: anything went wrong' % self)

    def doIsAllowed(self, target):
        if not self.getUsermin() <= target <= self.getUsermax() :
            return False, 'limits are [%f, %f]' % (self.getUsermin(),
                                                   self.getUsermax())
        return True, ''

    def doStatus(self):
        """Returns the status of the motor controller."""
        if self.__error > 0:
            return status.ERROR
        elif self.__thread and self.__thread.isAlive():
            return status.BUSY
        else:
            return self.motor.status()

    def doRead(self):
        """Returns the current position from coder controller."""
        self.__checkErrorState()
        return self.__read()

    def doAdjust(self, target):
        """Sets the current position of the motor/coder controller to
        the target.
        """
        self.__checkErrorState()
        if self.status() == status.BUSY :
            raise NicmError('%s: axis is moving now, please issue a stop '
                            'command and try it again' % self)
        diff = (self.read() - target)
        self.__target = target
        self.__offset += diff

        # Avoid the use of the setPar method for the absolute limits
        # due to the limitations of the hardware
        if (diff < 0):
                self._params['absMax'] = self.getAbsmax() - diff
                self._params['absMin'] = self.getAbsmin() - diff
        else:
                self._params['absMin'] = self.getAbsmin() - diff
                self._params['absMax'] = self.getAbsmax() - diff
        self.__checkAbsLimits()

        if (diff < 0):
                self._params['userMin'] = self.getUsermin() - diff
                self._params['userMax'] = self.getUsermax() - diff
        else:
                self._params['userMax'] = self.getUsermax() - diff
                self._params['userMin'] = self.getUsermin() - diff
        self.__checkUserLimits()

    def doReset(self):
        """Resets the motor/coder controller."""
        if self.status() != status.BUSY :
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
            time.sleep(self.getLoopdelay())
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

    def doSetUsermin(self, value):
        """ sets the user minimum value to value after
        checking the value against absolute limits and user maximum."""
        old = self._params['usermin']
        self._params['usermin'] = float(value)
        try:
            self.__checkUserLimits()
        except NicmError, e:
            self._params['usermin'] = old
            raise e

    def doSetUsermax(self, value):
        """ sets the user maximum value to value after
        checking the value against absolute limits and user minimum."""
        old = self._params['usermax']
        self._params['usermax'] = float(value)
        try:
            self.__checkUserLimits()
        except NicmError, e:
            self._params['usermax'] = old
            raise e

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
        if self.status() == status.ERROR :
            if self.__error == 1:
                raise PositionError('%s: drag error ' % self)
            elif self.__error == 2:
                raise MoveError('%s: precision error ' % self)
            elif self.__error == 3:
                raise MoveError('%s: pre move error ' % self)
            elif self.__error == 4:
                raise MoveError('%s: post move error ' % self)
            elif self.__error == 5:
                raise MoveError('%s: action during the move failed ' % self)
            elif self.__error == 6:
                raise MoveError('%s: move failed maxtries reached' % self)
            else:
                raise ProgrammingError('%s: Axis::doStart()' % self)

    def __read(self):
        try :
            return self.coder.read() - self.__offset
        except Exception:
            raise NicmError('%s: ' % self)

    def __checkAbsLimits(self):
        absMin = self.getAbsmin()
        absMax = self.getAbsmax()
        if not absMin and not absMax:
            raise ConfigurationError('%s: no absolute limits defined '
                                     '(absMin, absMax)' % self)
        if absMin >= absMax:
            raise ConfigurationError('%s: lower limit is too large [%f, %f]' %
                                     (self, absMin, absMax))

    def __checkUserLimits(self, setthem=False):
        absMin = self.getAbsmin()
        absMax = self.getAbsmax()
        userMin = self.getUsermin()
        userMax = self.getUsermax()
        if not userMin and not userMax and setthem:
            # if both not set (0) then use absolute min. and max.
            userMin = absMin
            userMax = absMax
            self._params['usermin'] = userMin
            self._params['usermax'] = userMax
        if (userMin >= userMax):
            raise ConfigurationError('%s: lower user limit is too large [%f, %f]' %
                                     (self, userMin, userMax))
        if userMin < absMin:
            raise ConfigurationError('%s: user minimum (%f) below the absolute '
                                     'minimum (%f)' % (self, userMin, absMin))
        if userMin > absMax:
            raise ConfigurationError('%s: user minimum (%f) above the absolute '
                                     'maximum (%f)' % (self, userMin, absMax))
        if userMax > absMax:
            raise ConfigurationError('%s: user maximum (%f) above the absolute '
                                     'maximum (%f)' % (self, userMin, absMax))
        if userMax < absMin:
            raise ConfigurationError('%s: user minimum (%f) below the absolute '
                                     'minimum (%f)' % (self, userMin, absMin))

    def __checkDragerror(self):
        tmp = abs(self.motor.read() - self.coder.read())
        # print 'Diff %.3f' % tmp
        dragDiff = self.getDragerror()
        dragOK = tmp <= dragDiff
        if dragOK :
            for i in self.obs :
                tmp = abs(self.motor.read() - i.read())
                dragOK = dragOK and (tmp <= dragDiff)
        if not dragOK :
            self.__error = 1
        return dragOK

    def __checkTargetPosition(self, target, pos, error = 2):
        tmp = abs(pos - target)
        posOK = tmp <= self.getPrecision()
        if posOK :
            for i in self.obs :
                tmp = abs(target - i.read())
                posOK = posOK and (tmp <= self.getDragerror())
        if not posOK :
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
        if not self._preMoveAction() :
            self.__error = 3
        else :
            self.__error = 0
            for pos in self.__target + self.getBacklash(), self.__target:
                self.__positioning(pos)
                if self.__stopRequest == 2 or self.__error != 0:
                   break
            if not self._postMoveAction():
                self.__error = 4
        if self.__locked:
            # if the movement was locked, unlock it
            self.__locked = False

    def __positioning(self, target):
        moving = False
        maxtries = self.getMaxtries()
        self.__lastPosition = self.read()
        __target = target + self.__offset
        self.motor.start(__target)
        moving = True

        while moving:
            if self.__stopRequest == 1:
                self.motor.stop()
                self.__stopRequest = 2
                continue
            time.sleep(self.getLoopdelay())
            try:
                pos = self.read()
            except NicmError:
                pass
            if not self.__checkMoveToTarget(__target, pos) or \
                   not self.__checkDragerror():
                # drag error (motor != coder)
                # distance to target will be greater
                self.__stopRequest = 1
            elif self.motor.status() != status.BUSY:             # motor stopped
                if self.__stopRequest == 2 or \
                       self.__checkTargetPosition(__target, pos):
                    # manual stop or target reached
                    moving = False
                elif maxtries > 0:
                    # target not reached, get the current position,
                    # sets the motor to this position and restart it
                    self.motor.setPosition(pos)
                    self.motor.start(__target)
                    maxtries -= 1
                else:
                    moving = False
                    self.__error = 6
            elif self.__stopRequest == 0:
                if  not self._duringMoveAction(pos):
                    self.__stopRequest = 1
                    self.__error = 5

