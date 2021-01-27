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
#   Pierre Boillat <pierre.boillat@psi.ch>
#
# *****************************************************************************

""" NIAG shutter devices """

from nicos.core import Attach, Moveable, MoveError, Override, Param, \
    PositionError, Readable, anytype, dictof, listof, multiReset, \
    multiStatus, none_or, status
from nicos.core.mixins import HasTimeout
from nicos.devices.abstract import MappedMoveable


class NiagShutter(HasTimeout, MappedMoveable):
    """ Shutter device for the NIAG beam lines.

    The shutter devices operate using 4 digital IOs (2 outputs and 2 inputs):
        - The digital outputs are used to open and close the shutter by sending
          a pulse
        - The digital inputs indicate whether the shutter is opened, closed
          or in interstage (in the latter case, both inputs are 0)

    An additional digital input indicates whether the shutter is enabled

    Part of the code used for this class was copied or adapted from
    the MultiSwitcher class written by Georg Brandl and Enrico Faulhaber. """

    # the 5 digital IOs (2 pulse outputs, 3 inputs) used to control the shutter
    attached_devices = {
        'do_open': Attach('Output to open the shutter', Moveable),
        'do_close': Attach('Output to close the shutter', Moveable),
        'is_open': Attach('Input to check if shutter is open', Readable),
        'is_closed': Attach('Input to check if shutter is closed', Readable),
        'is_enabled': Attach('Input to check if shutter is enabled', Readable),
    }

    """ copied from the MultiSwitcher class """
    parameters = {
        'blockingmove': Param('Should we wait for the move to finish?',
                              mandatory=False, default=True, settable=True,
                              type=bool),
    }

    """ copied from the MultiSwitcher class """
    parameter_overrides = {
        'mapping': Override(description='Mapping of state names to N values '
                                        'to move the moveables to',
                            type=dictof(anytype, listof(anytype))),
        'fallback': Override(userparam=False, type=none_or(anytype),
                             mandatory=False),
    }

    """ copied from the MultiSwitcher class """
    hardware_access = False

    """ first value in target indicates whether to open the shutter, second
    value whether to close it """

    def _startRaw(self, target):
        self._attached_do_open.start(target[0])
        self._attached_do_close.start(target[1])

    # returns a tuple mad of the (opened?, closed?) values

    def _readRaw(self, maxage=0):
        return tuple([self._attached_is_open.read(maxage),
                      self._attached_is_closed.read(maxage)])

    # based on the method definition from the MultiSwitcher class, simplified
    # because there is no need to define the precision for digital inputs

    def _mapReadValue(self, pos):
        """maps a tuple to one of the configured values"""
        for name, values in self.mapping.items():
            if tuple(pos) == tuple(values):
                return name
        if self.fallback is not None:
            return self.fallback
        raise PositionError(self, 'unknown position of %s: %s' % (
            ', '.join(str(d) for d in self._adevs),
            ', '.join(d.format(p) for (p, d) in zip(pos, self._adevs))))

    # completion is checked by verifying the feedback values, because
    # the "motion" of the outputs (pulses) is finished before the shutter
    # reaches its final position

    def doIsCompleted(self):
        reached = self.doRead() == self.target
        if reached:
            return True
        else:
            # if the position was not reached, consider that the motion
            # is not complete, unless an error is present """
            stat = self.doStatus()
            return stat[0] < status.BUSY

    # based on the definition of the MultiSwitcher class, extended for the
    # needs of the shutter control

    def doStatus(self, maxage=0):
        move_status = multiStatus(self._adevs, maxage)
        # if any of the underlying devices has an error, return it
        if move_status[0] > status.BUSY:
            return move_status
        try:
            # if the enable bit is not active, return "disabled" status
            if not self._attached_is_enabled.read(maxage):
                return status.DISABLED, 'disabled'
            r = self.doRead(maxage)
            # the the device is in the fallback position, it is considered
            # still moving
            if r == self.fallback:
                return status.BUSY, 'target not yet reached'
            return status.OK, 'idle'
        except PositionError as e:
            return status.NOTREACHED, str(e)

    # only allow to start if the enable bit is active

    def doStart(self, pos):
        if self._attached_is_enabled.read():
            return MappedMoveable.doStart(self, pos)
        raise MoveError(self, 'Device is disabled')

    def doReset(self):
        multiReset(self._adevs)


class NiagExpShutter(NiagShutter):
    """ the "NiagExpShutter add the shutter speed control
    functionality to the NiagShutter base class, implemented
    as an additional parameter called 'fast'

    It uses 3 additional digital IOs:
    - 2 outputs to switch to the slow and fast modes, respectively
    - 1 input to check which mode is active (slow = 0, fast = 1) """

    attached_devices = {
        'do_fast': Attach('Output to set the shutter speed to fast', Moveable),
        'do_slow': Attach('Output to set the shutter speed to slow', Moveable),
        'is_fast': Attach('Input to check if the shutter speed is fast',
                          Readable),
    }

    parameters = {
        'fast': Param('Fast shutter opening/closing',
                      mandatory=True, default=False, settable=True,
                      type=bool, volatile=True),
    }

    def doReadFast(self):
        return self._attached_is_fast.read(0) == 0

    # depending on the value, send the pulse to the corresponding output
    def doWriteFast(self, value):
        if value:
            self._attached_do_fast.move(1)
        else:
            self._attached_do_slow.move(1)
