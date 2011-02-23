#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
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
# *****************************************************************************

"""NICOS axis classes."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import threading
from time import sleep

from Motor import Motor as TACOMotor
import TACOStates

from nicos import status
from nicos.taco import TacoDevice
from nicos.utils import tupleof, any
from nicos.device import Moveable, HasOffset, HasLimits, Param, Override
from nicos.errors import ConfigurationError, NicosError, PositionError
from nicos.errors import ProgrammingError, MoveError, LimitError
from nicos.abstract import Axis as BaseAxis, Motor, Coder


class Axis(BaseAxis):
    """An axis implemented in Python, with NICOS devices for motor and coders."""

    attached_devices = {
        'motor': Motor,
        'coder': Coder,
        'obs':   [Coder],
    }

    # TODO: add validation for new parameter values where needed

    parameter_overrides = {
        'precision': Override(mandatory=True),
        # these are not mandatory for the axis: the motor should have them
        # defined anyway, and by default they are correct for the axis as well
        'abslimits': Override(mandatory=False),
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

        self.__error = 0
        self.__thread = None
        self.__target = self.__read()
        self.__mutex = threading.RLock()
        self.__stopRequest = 0

    def doReadUnit(self):
        return self._adevs['motor'].unit

    def doReadAbslimits(self):
        # check axis limits against motor absolute limits (the motor should not
        # have user limits defined)
        if 'abslimits' in self._config:
            amin, amax = self._config['abslimits']
            mmin, mmax = self._adevs['motor'].abslimits
            mmin -= self.offset
            mmax -= self.offset
            if amin < mmin:
                raise ConfigurationError(self, 'absmin (%s) below the motor '
                                         'absmin (%s)' % (amin, mmin))
            if amax > mmax:
                raise ConfigurationError(self, 'absmax (%s) below the motor '
                                         'absmax (%s)' % (amax, mmax))
        else:
            mmin, mmax = self._adevs['motor'].abslimits
            amin, amax = mmin - self.offset, mmax - self.offset
        return amin, amax

    def doStart(self, target, locked=False):
        """Starts the movement of the axis to target."""
        if self.__checkTargetPosition(self.doRead(), target, error=0):
            return

        # TODO: stop the axis instead of raising an exception
        if self.doStatus()[0] == status.BUSY:
            raise NicosError(self, 'axis is moving now, please issue a stop '
                            'command and try it again')

        # do limit check here already instead of in the thread
        ok, why = self._adevs['motor'].isAllowed(target + self.offset)
        if not ok:
            raise LimitError(self._adevs['motor'], why)

        if self.__thread:
            self.__thread.join()
            del self.__thread
            self.__thread = None

        self.__target = target
        self.__stopRequest = 0
        self.__error = 0
        if not self.__thread:
            self.__thread = threading.Thread(None, self.__positioningThread,
                                             'Positioning thread')
            self.printdebug("start thread")
            self.__thread.start()

    def doStatus(self):
        """Returns the status of the motor controller."""
        if self.__error > 0:
            return (status.ERROR, self.__errorDesc.get(self.__error, ''))
        elif self.__thread and self.__thread.isAlive():
            return (status.BUSY, 'moving')
        else:
            return self._adevs['motor'].doStatus()

    def doRead(self):
        """Returns the current position from coder controller."""
        self.__checkErrorState()  # XXX really?
        return self.__read()

    def doReset(self):
        """Resets the motor/coder controller."""
        if self.doStatus()[0] != status.BUSY:
            self.__error = 0
        self._adevs['motor'].setPosition(self._adevs['coder'].doRead())

    def doStop(self):
        """Stops the movement of the motor."""
        if self.doStatus()[0] == status.BUSY:
            self.__stopRequest = 1
        else:
            self.__stopRequest = 0

    def doWait(self):
        """Waits until the movement of the motor has stopped and
        the target position has been reached.
        """
        while self.doStatus()[0] == status.BUSY:
            sleep(self.loopdelay)
        else:
            self.__checkErrorState()

    def doWriteOffset(self, value):
        """Called on adjust(), overridden to forbid adjusting while moving."""
        if self.doStatus()[0] == status.BUSY:
            raise NicosError(self, 'axis is moving now, please issue a stop '
                            'command and try it again')
        self.__checkErrorState()
        HasOffset.doWriteOffset(self, value)

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

    __errorDesc = {
        1: 'drag error',
        2: 'precision error',
        3: 'pre move error',
        4: 'post move error',
        5: 'action during the move failed',
        6: 'maxtries reached',
    }

    def __checkErrorState(self):
        st = self.doStatus()
        if st[0] == status.ERROR:
            if self.__error == 1:
                raise PositionError(self, st[1])
            elif self.__error in self.__errorDesc:
                raise MoveError(self, st[1])
            else:
                raise ProgrammingError(self, 'unknown error constant %s' %
                                       self.__error)

    def __read(self):
        return self._adevs['coder'].doRead() - self.offset

    def __checkDragerror(self):
        diff = abs(self._adevs['motor'].doRead() -
                   self._adevs['coder'].doRead())
        self.printdebug('motor/coder diff: %s' % diff)
        maxdiff = self.dragerror
        if maxdiff <= 0:
            return True
        ok = diff <= maxdiff
        if ok:
            for i in self._adevs['obs']:
                diff = abs(self._adevs['motor'].doRead() - i.doRead())
                ok = ok and (diff <= maxdiff)
        if not ok:
            self.__error = 1
        return ok

    def __checkTargetPosition(self, target, pos, error=2):
        diff = abs(pos - target)
        maxdiff = self.dragerror
        ok = diff <= self.precision
        if ok:
            for i in self._adevs['obs']:
                diff = abs(target - i.doRead())
                if maxdiff > 0:
                    ok = ok and (diff <= maxdiff)
        if not ok:
            self.__error = error
        return ok

    def __checkMoveToTarget(self, target, pos, error=1):
        delta_last = abs(self.__lastPosition - target)
        delta_curr = abs(pos - target)
        self.printdebug('position delta: %s, was %s' % (delta_curr, delta_last))
        self.__lastPosition = pos
        # at the end of the move, the motor can slightly overshoot
        ok = delta_last >= delta_curr or delta_curr < self.precision
        if not ok:
             self.__error = error
        return ok

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

    def __positioning(self, target):
        moving = False
        offset = self.offset
        maxtries = self.maxtries
        self.__lastPosition = self.doRead()
        self._adevs['motor'].start(target + offset)
        moving = True

        while moving:
            if self.__stopRequest == 1:
                self.printdebug('stopping motor')
                self._adevs['motor'].stop()
                self.__stopRequest = 2
                continue
            sleep(self.loopdelay)
            pos = self.__read()
            if self._adevs['motor'].doStatus()[0] != status.BUSY:
                # motor stopped; check why
                if self.__stopRequest == 2:
                    self.printdebug('stop requested, leaving positioning')
                    # manual stop
                    moving = False
                elif self.__checkTargetPosition(target, pos):
                    self.printdebug('target reached, leaving positioning')
                    # target reached
                    moving = False
                elif maxtries > 0:
                    self.printdebug('target not reached, retrying')
                    # target not reached, get the current position,
                    # sets the motor to this position and restart it
                    self._adevs['motor'].setPosition(pos + self.offset)
                    self._adevs['motor'].start(target + self.offset)
                    maxtries -= 1
                else:
                    self.printdebug('target not reached after max tries')
                    moving = False
                    self.__error = 6
            elif not self.__checkMoveToTarget(target, pos):
                self.printdebug('not moving to target')
                self.__stopRequest = 1
            elif not self.__checkDragerror():
                self.printdebug('drag error detected')
                self.__stopRequest = 1
            elif self.__stopRequest == 0:
                if not self._duringMoveAction(pos):
                    self.__stopRequest = 1
                    self.__error = 5


class TacoAxis(TacoDevice, BaseAxis):
    """Interface for TACO Axis server devices."""

    taco_class = TACOMotor

    # XXX the usermin/usermax resources of the Taco device are currently not
    # used or queried at all by this class

    def doStart(self, target):
        # TODO: stop axis if already moving
        
        self._taco_guard(self._dev.start, target + self.offset)

    def doWait(self):
        while self.doStatus()[0] == status.BUSY:
            sleep(0.1)

    def doRead(self):
        return self._taco_guard(self._dev.read) - self.offset

    def doReset(self):
        # XXX is this correct? deviceReset does a reference drive...
        self._taco_guard(self._dev.deviceInit)

    def doSetPosition(self, target):
        self._taco_guard(self._dev.setpos, target)

    def doStatus(self):
        state = self._taco_guard(self._dev.deviceState)
        if state in (TACOStates.DEVICE_NORMAL, TACOStates.STOPPED):
            return (status.OK, 'idle')
        elif state in (TACOStates.MOVING, TACOStates.STOP_REQUESTED):
            return (status.BUSY, 'moving')
        else:
            return (status.ERROR, TACOStates.stateDescription(state))

    def doStop(self):
        self._taco_guard(self._dev.stop)

    def doReadSpeed(self):
        return self._taco_guard(self._dev.speed)

    def doWriteSpeed(self, value):
        self._taco_guard(self._dev.setSpeed, value)

    def doReadDragerror(self):
        return float(self._taco_guard(
            self._dev.deviceQueryResource, 'dragerror'))

    def doWriteDragerror(self, value):
        self._taco_update_resource('dragerror', str(value))

    def doReadPrecision(self):
        return float(self._taco_guard(
            self._dev.deviceQueryResource, 'precision'))

    def doWritePrecision(self, value):
        self._taco_update_resource('precision', str(value))

    def doReadMaxtries(self):
        return int(self._taco_guard(
            self._dev.deviceQueryResource, 'maxtries'))

    def doWriteMaxtries(self, value):
        self._taco_update_resource('maxtries', str(value))

    def doReadLoopdelay(self):
        return float(self._taco_guard(
            self._dev.deviceQueryResource, 'loopdelay'))

    def doWriteLoopdelay(self, value):
        self._taco_update_resource('loopdelay', str(value))

    def doReadBacklash(self):
        return float(self._taco_guard(
            self._dev.deviceQueryResource, 'backlash'))

    def doWriteBacklash(self, value):
        self._taco_update_resource('backlash', str(value))


class HoveringAxis(TacoAxis):

    attached_devices = {
        'switch': Moveable,
    }

    parameters = {
        'startdelay': Param('Delay after switching on air', type=float,
                            mandatory=True, unit='s'),
        'stopdelay':  Param('Delay before switching off air', type=float,
                            mandatory=True, unit='s'),
        'switchvalues': Param('[off, on] value to write to switch device',
                              type=tupleof(any, any), default=(0, 1)),
    }

    def doInit(self):
        self._poll_thread = None

    def doStart(self, target):
        if self._poll_thread:
            raise NicosError(self, 'axis is already moving')
        self._adevs['switch'].move(self.switchvalues[1])
        sleep(self.startdelay)
        TacoAxis.doStart(self, target)
        self._poll_thread = threading.Thread(target=self.__thread)
        self._poll_thread.setDaemon(True)
        self._poll_thread.start()

    def __thread(self):
        sleep(0.1)
        while self.doStatus()[0] == status.BUSY:
            sleep(0.1)
        sleep(self.stopdelay)
        try:
            self._adevs['switch'].move(self.switchvalues[0])
        finally:
            self._poll_thread = None

    def doWait(self):
        if self._poll_thread:
            self._poll_thread.join()
