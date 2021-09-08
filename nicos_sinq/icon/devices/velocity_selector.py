#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
"""
Support for the digital I/O driven velocity selector @ ICON
"""
from nicos.core import Attach, Moveable, Override, Readable, status
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqSleep, \
    SequenceItem


class VSState(Moveable):
    """
    This class switches the velocity selector on and off and
    checks if the thing can actually run
    """
    attached_devices = {
        'on': Attach('Writable I/O for switching on the VS',
                     Moveable),
        'off': Attach('Writable I/O for switching off the VS',
                      Moveable),
        'state': Attach('Readable I/O for the runable state of the VS',
                        Readable),
        'hand': Attach('Readable I/O for manual state VS',
                       Readable),
        'ready': Attach('Readable I/O for the ready state of the VS',
                        Readable),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    _target = None

    def isAllowed(self, pos):
        if self._attached_ready.read(0) == 0:
            return False, 'VS not switched on'
        if self._attached_hand.read(0) == 1:
            return False, 'VS is in manual mode'
        if pos in ['on', 'off']:
            return True, ''
        return False, '%s not allowed, only on/off permitted'

    def doRead(self, maxage=0):
        if self._attached_state.read(maxage) == 1:
            return 'on'
        return 'off'

    def doStart(self, target):
        self._target = target
        if target == 'on':
            self._attached_on.start(1)
            return
        self._attached_off.start(1)

    def doStatus(self, maxage=0):
        cur = self.read(maxage)
        if cur == self._target:
            self._attached_on.start(0)
            self._attached_off.start(0)
            return status.OK, 'Done'
        return status.BUSY, 'Waiting ...'


class SeqWaitValue(SequenceItem):
    """
    A little class which waits until a readable device has reached a certain
    value
    """
    def __init__(self, dev, wait_value, tolerance):
        SequenceItem.__init__(self)
        self._dev = dev
        self._wait_value = wait_value
        self._tolerance = tolerance

    def isCompleted(self):
        pos = self._dev.read(0)
        return bool(abs(pos - self._wait_value) < self._tolerance)


class VSSpeed(BaseSequencer):
    """
    This class controls the speed of the velocity selector. While the
    readback is a plain analog readable, setting the set point is
    special: The 12 bit set point is split across two individual
    bytes of a digital output port.
    """

    attached_devices = {
        'state': Attach('Device for controlling the state of the VS',
                        Moveable),
        'setp': Attach('Device for setting the velocity setpoint',
                       Moveable),
        'rbv': Attach('Readback for the speed',
                      Readable)
    }

    _target = None

    def isAllowed(self, pos):
        test, reason = self._attached_state.isAllowed('on')
        if not test:
            return test, reason
        if pos < 0 or pos > 124.35:
            return False, 'Pos outside range 0 - 124.35 Hz'
        return True, ''

    def _generateSequence(self, target):
        seq = []

        if target < 5:
            seq.append(SeqDev(self._attached_setp, 0))
            seq.append(SeqWaitValue(self._attached_rbv, 0, 5))
            seq.append(SeqDev(self._attached_state, 'off'))
        elif abs(self._attached_rbv.read(0) - target) >= 1.0:
            seq.append(SeqDev(self._attached_state, 'on'))
            seq.append(SeqDev(self._attached_setp, target))
            seq.append(SeqWaitValue(self._attached_rbv, target, 1.0))
            # Repeat enough of this pair until sufficient stabilisation
            # has been reached
            seq.append(SeqSleep(5))
            seq.append(SeqWaitValue(self._attached_rbv, target, 1.0))
            seq.append(SeqSleep(5))
            seq.append(SeqWaitValue(self._attached_rbv, target, 1.0))
            seq.append(SeqSleep(5))
            seq.append(SeqWaitValue(self._attached_rbv, target, 1.0))

        return seq

    def doRead(self, maxage=0):
        readval = self._attached_rbv.read(maxage)
        if readval > 5:
            return readval
        return 0

    def doStatus(self, maxage=0):
        if self._seq_is_running():
            return status.BUSY, 'Ramping up speed'
        return status.OK, 'Arrived'


class VSLambda(Moveable):
    """
    This class maps between wavelength and velocity selector speed
    """

    attached_devices = {
        'speed': Attach(
            'Device for controlling the speed of the velocity selector',
            Moveable)
    }

    def _lambdaToSpeed(self, wavelength):
        if wavelength == 0:
            return 0
        return 3.569084E+2/wavelength - 2.807392

    def isAllowed(self, pos):
        speed = self._lambdaToSpeed(pos)
        return self._attached_speed.isAllowed(speed)

    def doStart(self, target):
        self._attached_speed.start(self._lambdaToSpeed(target))

    def doRead(self, maxage=0):
        speed = self._attached_speed.read(maxage)
        if speed >= 5:
            return 1./(2.801839E-3*speed + 7.865861E-3)
        return 0
