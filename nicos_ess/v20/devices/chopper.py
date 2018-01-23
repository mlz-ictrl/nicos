#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Michael Wedel <michael.wedel@esss.se>
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Michael Hart <michael.hart@stfc.ac.uk>
#
# *****************************************************************************

from nicos.devices.epics import EpicsReadable, EpicsMoveable
from nicos.core import status, Override, Attach, usermethod, \
    Moveable, SIMULATION, tupleof


class EpicsFloatMoveable(EpicsMoveable):
    """
    Handles EPICS devices which can set and read a float value, but without limits.
    """
    valuetype = float


class EpicsFloatReadable(EpicsReadable):
    """
    Handles EPICS devices which can read a float value, but without limits.
    """
    valuetype = float


class EpicsStringMoveable(EpicsMoveable):
    """
    Handles EPICS devices which can set and read a string value.
    """
    valuetype = str


class EpicsEnumMoveable(EpicsMoveable):
    """
    Handles EPICS devices which can set and read an int value.
    """
    valuetype = str
    enum_strs = []

    def doInit(self, mode):
        if mode != SIMULATION:
            self.enum_strs = list(self._get_pvctrl('writepv', 'enum_strs', []))
            self.log.info('%s',self.enum_strs)

    def doStart(self, value):
        real_value = value
        if isinstance(value, str):
            real_value = self.enum_strs.index(value.lower())

        self._put_pv('writepv', real_value)

    def doRead(self, maxage=None):
        return self.enum_strs[self._get_pv('readpv')]


class EssChopper(Moveable):
    attached_devices = {
        'speed': Attach('Speed of the chopper disc.', EpicsMoveable),
        'phase': Attach('Phase of the chopper disc', EpicsMoveable),
        'parkposition': Attach('Position in parked state', EpicsMoveable),
        'state': Attach('Current state of the chopper', EpicsReadable,
                        optional=True),
        'command': Attach('Command PV of the chopper', EpicsMoveable)
    }

    state_map=[(status.OK, 'Initializing'),
               (status.OK, 'Interlocked'),
               (status.OK, 'Ready'),
               (status.OK, 'Rotating'),
               (status.BUSY, 'Stopping'),
               (status.ERROR, 'Emergency Stopping'),
               (status.ERROR, 'Locked')]

    parameter_overrides = {
        'fmtstr': Override(default='%.2f %.2f'),
        'unit': Override(mandatory=False),
    }

    hardware_access = False
    valuetype = tupleof(float, float)

    def doRead(self, maxage=0):
        return [self._attached_speed.read(maxage),
                self._attached_phase.read(maxage)]

    def doStart(self, pos):
        if hasattr(self, '_attached_state') and \
           self._attached_state.read() == 'init':
            self.initialize()

        self._attached_speed.move(pos[0])
        self._attached_phase.move(pos[1])
        self._attached_command.move('start')

    def doStop(self):
        self._attached_command.move('stop')

    # def doReadAbslimits(self):
    #    return [(0.0, 40.0), (0.0, 360.0)]

    def doStatus(self, maxage=0):
        if hasattr(self, '_attached_state'):
            state = int(self._attached_state.read())
            if 0 <= state < 7:
                return self.state_map[state]
            else:
                return status.WARN, 'Unhandled state: %s' % state

        return status.WARN, 'State PV is missing, no reliable state information.'

    @usermethod
    def initialize(self):
        self._attached_command.move('init')

    @usermethod
    def deinitialize(self):
        self._attached_command.move('deinit')

    @usermethod
    def parkAt(self, position):
        self._attached_parkposition.move(position)
        self._attached_command.move('park')

    @usermethod
    def unlock(self):
        self._attached_command.move('unlock')
