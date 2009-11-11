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
__date__   = "2009/10/27"
__version__= "0.0.1"

import threading
import time

from nicm import status
from nicm.device import Moveable
from nicm.errors import ConfigurationError, NicmError, LimitError, PositionError
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
        "followerr": (1, False, "so called following error"),
        "precision": (0, False, "precision between requested target "
                                "and reached position"),
        "maxtries":  (3, False, "number of tries to reach the target"),
        "loopdelay": (0.3, False, "sleep time to check the movement"),
        "unit":      ('', False, "unit of the axis value"),
    }

    def doInit(self):
        if self.coder.getUnit() != self.motor.getUnit():
            raise ConfigurationError('%s: different units for motor '
                                     'and coder' % self)

        self.__checkAbsLimits()
        self.__checkUserLimits(setthem=True)

        self.__offset = 0
        self.__thread = None
        self.__target = self.read()
        self.__mutex = threading.RLock()
        self.__stopRequest = 0
        self.__error = 0
        self.__locked = False

        self.setPar('unit', self.motor.getUnit())

    def doStart(self, target, locked=False):
        """Starts the movement of the axis to target."""
        if self.__locked:
            raise NicmError('%s: this axis is locked' % self)
        if not self.isAllowed(target):
            raise LimitError('%s: target %f is not allowed, limits [%f, %f]' %
                            (self, target,
                             self.getUsermin(), self.getUsermax()))
        if self.__thread:
            if self.__thread.isAlive():
                raise NicmError('%s: axis is moving now, please issue a stop '
                                'command and try it again' % self)
            else:
                self.__thread.join()
                del self.__thread
                self.__thread = None
        try:
            self.__target = target
            self.__stopRequest = 0
            self.__locked = locked   # lock the movement
            self.__error = 0
            if not self.__thread:
                self.__thread = threading.Thread(None, self.__positioning,
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

    def doRead(self):
        """Returns the current position from coder controller."""
        try:
            return self.coder.read() - self.__offset
        except Exception:
            raise NicmError('%s: ' % self)

    def doAdjust(self, target):
        """Sets the current position of the motor/coder controller to
        the target.
        """
        self.__target = target
        diff = (self.read() - self.__target)
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

    def doStatus(self):
        """Returns the status of the motor controller."""
        try:
            if self.__thread and self.__thread.isAlive():
                return status.BUSY
            elif self.__error > 0:
                return status.ERROR
            else:
                return self.motor.status()
        except Exception:
            raise Exception('%s: ' % self)

    def doReset(self):
        """Resets the motor/coder controller."""
        pass

    def doStop(self):
        """Stops the movement of the motor."""
        self.__stopRequest = 1

    def doWait(self):
        """Waits until the movement of the motor has stopped and
        the target position has been reached.
        """
        try:
            while (self.status() == status.BUSY):
                 time.sleep(self.getLoopdelay())
        except Exception:
            raise Exception('%s: ' % self)

    def doLock(self):
        """Locks the axis against any movement."""
        super(Axis, self).doLock()
        self.__locked = True

    def doUnlock(self):
        """Unlocks the axis."""
        super(Axis, self).doUnlock()
        self.__locked = False

    def doSetUsermin(self, value):
        old = self._params['usermin']
        self._params['usermin'] = float(value)
        try:
            self.__checkUserLimits()
        except NicmError, e:
            self._params['usermin'] = old
            raise e

    def doSetUsermax(self, value):
        old = self._params['usermax']
        self._params['usermax'] = float(value)
        try:
            self.__checkUserLimits()
        except NicmError, e:
            self._params['usermax'] = old
            raise e

    def __checkAbsLimits(self):
        absMin = self.getAbsmin()
        absMax = self.getAbsmax()
        if not absMin and not absMax:
            raise ConfigurationError('%s: no absolute limits defined (absMin, absMax)' %
                            self)
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
            raise ConfigurationError('%s: user minimum (%f) below the absolute minimum (%f)' %
                            (self, userMin, absMin))
        if userMin > absMax:
            raise ConfigurationError('%s: user minimum (%f) above the absolute maximum (%f)' %
                            (self, userMin, absMax))
        if userMax > absMax:
            raise ConfigurationError('%s: user maximum (%f) above the absolute maximum (%f)' %
                            (self, userMin, absMax))
        if userMax < absMin:
            raise ConfigurationError('%s: user minimum (%f) below the absolute minimum (%f)' %
                            (self, userMin, absMin))

    def __checkFollowError(self):
        tmp = abs(self.motor.read() - self.coder.read()) 
        # print 'Diff %.3f' % tmp
        return tmp <= self.getFollowerr()

    def __checkTargetPosition(self):
         return abs(self.read() - self.__target) <= self.getPrecision()

    def __positioning(self):
        moving = False
        maxtries = self.getMaxtries()
        self.__error = 0
        if not self.__checkTargetPosition() : 
            self.motor.start(self.__target + self.__offset)
            moving = True
        while moving:
            if self.__stopRequest == 1:
                self.motor.stop()
                self.__stopRequest = 2
                continue
            time.sleep(self.getLoopdelay())
            if not self.__checkFollowError():
                # following error (motor != coder)
                self.motor.stop()
                self.__error = 1
                moving = False
            elif self.motor.status() != status.BUSY:             # motor stopped
                if self.__stopRequest == 2 or self.__checkTargetPosition():
                    # manual stop or target reached
                    moving = False
                    break;
                elif maxtries > 0:
                    # target not reached, get the current position,
                    # sets the motor to this position and restart it
                    currentPos = self.read()
                    self.motor.setPosition(currentPos)
                    self.motor.start(self.__target + self.__offset)
                else:
                    moving = False
                    self.__error = 2
        else:
            pass
            try:
                if self.__error == 1:
                    raise PositionError('%s: following error ' % self)
                elif self.__error == 2:
                    raise PositionError('%s: precision error ' % self)
                else:
                    pass
            except NicmError, e:
                self.printerror()
                raise e
        if self.__locked:
            # if the movement was locked, unlock it
            self.__locked = False

