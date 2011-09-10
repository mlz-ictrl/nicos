#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id: axis.py 606 2011-05-12 18:16:38Z gbrandl $
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
from nicos.utils import tupleof, any, usermethod, waitForStatus
from nicos.device import Moveable, HasOffset, Param, Override
from nicos.errors import ConfigurationError, NicosError, PositionError, \
     MoveError, LimitError
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
        # XXX determine this from motor precision if not given
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

        self._errorstate = None
        self._posthread = None
        self._stoprequest = 0
        if self._mode != 'simulation':
            self._target = self._adevs['coder'].read() - self.offset

    def doReadUnit(self):
        return self._adevs['motor'].unit

    def doReadAbslimits(self):
        # check axis limits against motor absolute limits (the motor should not
        # have user limits defined)
        if 'abslimits' in self._config:
            amin, amax = self._config['abslimits']
            mmin, mmax = self._adevs['motor'].abslimits
            if amin < mmin:
                raise ConfigurationError(self, 'absmin (%s) below the motor '
                                         'absmin (%s)' % (amin, mmin))
            if amax > mmax:
                raise ConfigurationError(self, 'absmax (%s) above the motor '
                                         'absmax (%s)' % (amax, mmax))
        else:
            mmin, mmax = self._adevs['motor'].abslimits
            amin, amax = mmin, mmax
        return amin, amax

    def doStart(self, target, locked=False):
        """Starts the movement of the axis to target."""
        if self._checkTargetPosition(self.doRead(), target, error=False):
            return

        # TODO: stop the axis instead of raising an exception
        if self.doStatus()[0] == status.BUSY:
            raise NicosError(self, 'axis is moving now, please issue a stop '
                            'command and try it again')

        # do limit check here already instead of in the thread
        ok, why = self._adevs['motor'].isAllowed(target + self.offset)
        if not ok:
            raise LimitError(self._adevs['motor'], why)

        if self._posthread:
            self._posthread.join()
            del self._posthread
            self._posthread = None

        self._target = target
        self._stoprequest = 0
        self._errorstate = None
        if not self._posthread:
            self._posthread = threading.Thread(None, self.__positioningThread,
                                               'Positioning thread')
            self.log.debug('start positioning thread')
            self._posthread.start()

    def doStatus(self):
        """Returns the status of the motor controller."""
        if self._errorstate:
            return (status.ERROR, str(self._errorstate))
        elif self._posthread and self._posthread.isAlive():
            return (status.BUSY, 'moving')
        else:
            return self._adevs['motor'].doStatus()

    def doRead(self):
        """Returns the current position from coder controller."""
        if self._errorstate:
            raise self._errorstate
        # XXX read or doRead
        return self._adevs['coder'].read() - self.offset

    def doReset(self):
        """Resets the motor/coder controller."""
        if self.doStatus()[0] != status.BUSY:
            self._errorstate = None
        self._adevs['motor'].setPosition(self._adevs['coder'].doRead())

    def doStop(self):
        """Stops the movement of the motor."""
        if self.doStatus()[0] == status.BUSY:
            self._stoprequest = 1
        else:
            self._stoprequest = 0

    def doWait(self):
        """Waits until the movement of the motor has stopped and
        the target position has been reached.
        """
        waitForStatus(self, self.loopdelay)
        if self._errorstate:
            raise self._errorstate

    def doWriteOffset(self, value):
        """Called on adjust(), overridden to forbid adjusting while moving."""
        if self.doStatus()[0] == status.BUSY:
            raise NicosError(self, 'axis is moving now, please issue a stop '
                            'command and try it again')
        if self._errorstate:
            raise self._errorstate
        HasOffset.doWriteOffset(self, value)

    def _preMoveAction(self):
        """This method will be called before the motor will be moved.
        It should be overwritten in derived classes for special actions.

        To abort the move, raise an exception from this method.
        """

    def _postMoveAction(self):
        """This method will be called after the axis reached the position or
        will be stopped.
        It should be overwritten in derived classes for special actions.

        To signal an error, raise an exception from this method.
        """

    def _duringMoveAction(self, position):
        """This method will be called during every cycle in positioning thread.
        It should be used to do some special actions like changing shielding
        blocks, checking for air pressure etc.  It should be overwritten in
        derived classes.

        To abort the move, raise an exception from this method.
        """

    def _setErrorState(self, cls, text):
        self._errorstate = cls(self, text)
        self.log.error(text)
        return False

    def _checkDragerror(self):
        """Check if a "drag error" occurred, i.e. the values of motor and
        coder deviate too much.  This indicates that the movement is blocked.

        This method sets the error state and returns False if a drag error
        occurs, and returns True otherwise.
        """
        diff = abs(self._adevs['motor'].read() - self._adevs['coder'].read())
        self.log.debug('motor/coder diff: %s' % diff)
        maxdiff = self.dragerror
        if maxdiff <= 0:
            return True
        if diff > maxdiff:
            return self._setErrorState(PositionError,
                'drag error (primary coder): difference %f, maximum %f' %
                (diff, maxdiff))
            return False
        for obs in self._adevs['obs']:
            diff = abs(self._adevs['motor'].read() - obs.read())
            if diff > maxdiff:
                return self._setErrorState(PositionError,
                    'drag error (%s): difference %f, maximum %f' %
                    (obs.name, diff, maxdiff))
        return True

    def _checkMoveToTarget(self, target, pos):
        """Check that the axis actually moves towards the target position.

        This method sets the error state and returns False if a drag error
        occurs, and returns True otherwise.
        """
        delta_last = abs(self._lastpos - target)
        delta_curr = abs(pos - target)
        self.log.debug('position delta: %s, was %s' % (delta_curr, delta_last))
        self._lastpos = pos
        # at the end of the move, the motor can slightly overshoot
        ok = delta_last >= delta_curr or delta_curr < self.precision
        if not ok:
            return self._setErrorState(PositionError,
                'not moving to target: last delta %f, current delta %f'
                % (delta_last, delta_curr))
        return True

    def _checkTargetPosition(self, target, pos, error=True):
        """Check if the axis is at the target position.

        This method returns False if not arrived at target, or True otherwise.
        """
        diff = abs(pos - target)
        maxdiff = self.dragerror
        if diff > self.precision:
            if error:
                # not calling _setErrorState here, since we don't want the error
                # log message in all cases
                self._errorstate = MoveError(self,
                    'precision error: difference %f, precision %f' %
                    (diff, self.precision))
            return False
        for obs in self._adevs['obs']:
            diff = abs(target - obs.read())
            if maxdiff > 0:# and diff > maxdiff:
                if error:
                    self._errorstate = MoveError(self,
                        'precision error (%s): difference %f, maximum %f' %
                        (obs, diff, maxdiff))
                return False
        return True

    def __positioningThread(self):
        try:
            self._preMoveAction()
        except Exception, err:
            self._setErrorState(MoveError, 'error in pre-move action: %s' % err)
        else:
            self._errorstate = None
            if self.backlash:
                # XXX do not move twice if coming from the "right" side
                for pos in self._target + self.backlash, self._target:
                    self.__positioning(pos)
                    if self._stoprequest == 2 or self._errorstate:
                        break
            else:
                self.__positioning(self._target)
            try:
                self._postMoveAction()
            except Exception, err:
                self._setErrorState(MoveError,
                                    'error in post-move action: %s' % err)

    def __positioning(self, target):
        moving = False
        offset = self.offset
        maxtries = self.maxtries
        self._lastpos = self.doRead()
        self._adevs['motor'].start(target + offset)
        moving = True
        devs = [self._adevs['motor'], self._adevs['coder']] + self._adevs['obs']

        while moving:
            if self._stoprequest == 1:
                self.log.debug('stopping motor')
                self._adevs['motor'].stop()
                self._stoprequest = 2
                continue
            sleep(self.loopdelay)
            # poll accurate current values and status of child devices
            for dev in devs:
                dev.poll()
            pos = self._adevs['coder'].read() - self.offset
            if self._adevs['motor'].status()[0] != status.BUSY:
                # motor stopped; check why
                if self._stoprequest == 2:
                    self.log.debug('stop requested, leaving positioning')
                    # manual stop
                    moving = False
                elif self._checkTargetPosition(target, pos):
                    self.log.debug('target reached, leaving positioning')
                    # target reached
                    moving = False
                elif maxtries > 0:
                    self.log.warning(str(self._errorstate))
                    self.log.debug('target not reached, retrying')
                    # target not reached, get the current position,
                    # sets the motor to this position and restart it
                    self._adevs['motor'].setPosition(pos + self.offset)
                    # XXX exception handling!
                    self._adevs['motor'].start(target + self.offset)
                    maxtries -= 1
                else:
                    self.log.debug('target not reached after max tries')
                    moving = False
                    self._setErrorState(MoveError,
                        'target not reached after %d tries' % self.maxtries)
            elif not self._checkMoveToTarget(target, pos):
                self._stoprequest = 1
            elif not self._checkDragerror():
                self._stoprequest = 1
            elif self._stoprequest == 0:
                try:
                    self._duringMoveAction(pos)
                except Exception, err:
                    self._setErrorState(MoveError,
                                        'error in during-move action: %s' % err)
                    self._stoprequest = 1


class TacoAxis(TacoDevice, BaseAxis):
    """Interface for TACO Axis server devices."""

    taco_class = TACOMotor

    parameters = {
        'speed':     Param('Motor speed', unit='main/s', settable=True),
        'accel':     Param('Motor acceleration', unit='main/s^2',
                           settable=True),
        'refspeed':  Param('Speed driving to reference switch', unit='main/s',
                           settable=True),
        'refswitch': Param('Switch to use as reference', type=str,
                           settable=True),
        'refpos':    Param('Position of the reference switch', unit='main',
                           settable=True),
    }

    # XXX the usermin/usermax resources of the Taco device are currently not
    # used or queried at all by this class

    def doStart(self, target):
        self._taco_guard(self._dev.start, target + self.offset)

    def doWait(self):
        st = waitForStatus(self, 0.3)
        if st[0] == status.ERROR:
            raise MoveError(self, st[1])
        elif st[0] == status.NOTREACHED:
            raise PositionError(self, st[1])

    def doRead(self):
        return self._taco_guard(self._dev.read) - self.offset

    def doReset(self):
        self._taco_guard(self._dev.deviceReset)
        self._taco_guard(self._dev.deviceOn)

    def doSetPosition(self, target):
        self._taco_guard(self._dev.setpos, target)

    def doStatus(self):
        state = self._taco_guard(self._dev.deviceState)
        if state in (TACOStates.DEVICE_NORMAL, TACOStates.STOPPED):
            return (status.OK, 'idle')
        elif state in (TACOStates.MOVING, TACOStates.STOP_REQUESTED):
            return (status.BUSY, 'moving')
        elif state == TACOStates.INIT:
            return (status.BUSY, 'referencing')
        elif state == TACOStates.ALARM:
            return (status.NOTREACHED, 'position not reached')
        else:
            return (status.ERROR, TACOStates.stateDescription(state))

    def doStop(self):
        self._taco_guard(self._dev.stop)

    @usermethod
    def reference(self):
        """Do a reference drive of the axis (do not use with encoded axes)."""
        motorname = self._taco_guard(self._dev.deviceQueryResource, 'motor')
        client = TACOMotor(motorname)
        self.log.info('referencing the axis, please wait...')
        self._taco_guard(client.deviceReset)
        while self._taco_guard(client.deviceState) == TACOStates.INIT:
            sleep(0.3)
        self._taco_guard(client.deviceOn)
        self.setPosition(self.refpos)
        self.log.info('reference drive complete, position is now ' +
                      self.format(self.doRead()))

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

    # resources that need to be set on the motor, not the axis device

    def _readMotorParam(self, resource, type=float):
        motorname = self._taco_guard(self._dev.deviceQueryResource, 'motor')
        client = TACOMotor(motorname)
        return type(client.deviceQueryResource(resource))

    def _writeMotorParam(self, resource, value):
        motorname = self._taco_guard(self._dev.deviceQueryResource, 'motor')
        client = TACOMotor(motorname)
        client.deviceOff()
        try:
            client.deviceUpdateResource(resource, str(value))
        finally:
            client.deviceOn()

    def doReadAccel(self):
        return self._readMotorParam('accel')

    def doWriteAccel(self, value):
        self._writeMotorParam('accel', value)

    def doReadRefspeed(self):
        return self._readMotorParam('refspeed')

    def doWriteRefspeed(self, value):
        self._writeMotorParam('refspeed', value)

    def doReadRefswitch(self):
        return self._readMotorParam('refswitch', str)

    def doWriteRefswitch(self, value):
        self._writeMotorParam('refswitch', value)

    def doReadRefpos(self):
        return self._readMotorParam('refpos')

    def doWriteRefpos(self, value):
        self._writeMotorParam('refpos', value)


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
        if abs(target - self.read()) < self.precision:
            return
        self._adevs['switch'].move(self.switchvalues[1])
        sleep(self.startdelay)
        TacoAxis.doStart(self, target)
        self._poll_thread = threading.Thread(target=self._pollthread)
        self._poll_thread.setDaemon(True)
        self._poll_thread.start()

    def _pollthread(self):
        sleep(0.1)
        waitForStatus(self, 0.2)
        sleep(self.stopdelay)
        try:
            self._adevs['switch'].move(self.switchvalues[0])
        finally:
            self._poll_thread = None

    def doWait(self):
        if self._poll_thread:
            self._poll_thread.join()

    def doStatus(self):
        state = self._taco_guard(self._dev.deviceState)
        if state in (TACOStates.DEVICE_NORMAL, TACOStates.STOPPED,
                     TACOStates.TRIPPED):
            # TRIPPED means: both limit switches or inhibit active
            # which is normal when air is switched off
            return (status.OK, 'idle')
        elif state in (TACOStates.MOVING, TACOStates.STOP_REQUESTED):
            return (status.BUSY, 'moving')
        elif state == TACOStates.ALARM:
            return (status.NOTREACHED, 'position not reached')
        else:
            return (status.ERROR, TACOStates.stateDescription(state))
