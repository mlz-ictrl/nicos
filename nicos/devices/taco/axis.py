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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS axis classes."""

from time import sleep

import TACOStates
from Motor import Motor as TACOMotor

from nicos.core import ModeError, Moveable, Param, Attach, SLAVE, anytype, \
    oneof, requires, status, tupleof, usermethod
from nicos.devices.abstract import Axis as BaseAxis, CanReference
from nicos.devices.generic.sequence import SequencerMixin, SeqDev, SeqSleep, SeqCall
from nicos.devices.taco.core import TacoDevice


class Axis(CanReference, TacoDevice, BaseAxis):
    """Interface for TACO Axis server devices."""

    taco_class = TACOMotor

    _TACO_STATUS_MAPPING = dict(TacoDevice._TACO_STATUS_MAPPING)
    _TACO_STATUS_MAPPING[TACOStates.INIT] = (status.BUSY, 'referencing')
    _TACO_STATUS_MAPPING[TACOStates.RESETTING] = (status.BUSY, 'referencing')
    _TACO_STATUS_MAPPING[TACOStates.ALARM] = (status.NOTREACHED, 'position not reached')

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
        # do not call deviceReset by default as it does a reference drive
        'resetcall': Param('What TACO method to call on reset (deviceInit or '
                           'deviceReset)', settable=True, default='deviceInit',
                           type=oneof('deviceInit', 'deviceReset')),
    }

    def doStart(self, target):
        self._taco_guard(self._dev.start, target + self.offset)

    def doRead(self, maxage=0):
        return self._taco_guard(self._dev.read) - self.offset

    def doTime(self, start, end):
        s, v, a = abs(start - end), self.speed, self.accel
        if s > v**2/a:  # do we reach nominal speed?
            return s/v + v/a
        return 2*(s/a)**0.5

    def doReset(self):
        self._taco_reset(self._dev, self.resetcall)

    @usermethod
    @requires(level='admin', helpmsg='use adjust() to set a new offset')
    def setPosition(self, pos):
        """Sets the current position of the axis to the target.

        This operation is forbidden in slave mode, and does the right thing
        virtually in simulation mode.
        """
        if self._mode == SLAVE:
            raise ModeError(self, 'setting new position not possible in '
                            'slave mode')
        elif self._sim_active:
            self._sim_setValue(pos)
            return
        self._taco_guard(self._dev.setpos, pos)
        # update current value in cache
        self.read(0)

    def doStop(self):
        self._taco_guard(self._dev.stop)

    def doReference(self):
        """Do a reference drive of the axis (do not use with encoded axes)."""
        self.log.info('referencing the axis, please wait...')
        self._taco_guard(self._dev.deviceReset)
        while self._taco_guard(self._dev.deviceState) \
                                  in (TACOStates.INIT, TACOStates.RESETTING):
            sleep(0.3)
        if self._taco_guard(self._dev.isDeviceOff):
            self._taco_guard(self._dev.deviceOn)
        if self.read() != self.refpos:
            self._taco_guard(self._dev.setpos, self.refpos)

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

    def _readMotorParam(self, resource, conv=float):
        motorname = self._taco_guard(self._dev.deviceQueryResource, 'motor')
        client = TACOMotor(motorname)
        return conv(client.deviceQueryResource(resource))

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


class HoveringAxis(SequencerMixin, Axis):
    """An axis that also controls air for airpads."""

    attached_devices = {
        'switch': Attach('The device used for switching air on and off', Moveable),
    }

    parameters = {
        'startdelay':   Param('Delay after switching on air', type=float,
                              mandatory=True, unit='s'),
        'stopdelay':    Param('Delay before switching off air', type=float,
                              mandatory=True, unit='s'),
        'switchvalues': Param('(off, on) values to write to switch device',
                              type=tupleof(anytype, anytype), default=(0, 1)),
    }

    hardware_access = True

    def _generateSequence(self, target):  # pylint: disable=W0221
        return [
            SeqDev(self._attached_switch, self.switchvalues[1]),
            SeqSleep(self.startdelay),
            SeqCall(Axis.doStart, self, target),
            SeqCall(self._hw_wait),
            SeqSleep(self.stopdelay),
            SeqDev(self._attached_switch, self.switchvalues[0]),
        ]

    def _hw_wait(self):
        # overridden: query Axis status, not HoveringAxis status
        while Axis.doStatus(self, 0)[0] == status.BUSY:
            sleep(self._base_loop_delay)

    def doStart(self, target):
        if self._seq_is_running():
            self.stop()
            self.log.info('waiting for axis to stop...')
            self.wait()
        if abs(target - self.read()) < self.precision:
            return
        self._startSequence(self._generateSequence(target))

    def doStop(self):
        # stop only the axis, but the sequence has to run through
        Axis.doStop(self)

    def doTime(self, start, end):
        return Axis.doTime(self, start, end) + self.startdelay + self.stopdelay
