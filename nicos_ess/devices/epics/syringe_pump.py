# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
from nicos.core import SIMULATION, Attach, InvalidValueError, Override, \
    Param, oneof, pvname, status, usermethod
from nicos.devices.abstract import MappedMoveable
from nicos.devices.epics.pva import EpicsDevice, EpicsStringReadable


class SyringePumpController(EpicsDevice, MappedMoveable):
    """
    A device for controlling the NE1002 and NE1600 syringe pumps.
    """
    parameters = {
        'start_pv':
            Param('PV for starting the device',
                  type=pvname,
                  mandatory=True,
                  userparam=False),
        'stop_pv':
            Param('PV for stopping the device',
                  type=pvname,
                  mandatory=True,
                  userparam=False),
        'purge_pv':
            Param('PV for purging the device',
                  type=pvname,
                  mandatory=True,
                  userparam=False),
        'pause_pv':
            Param('PV for pausing and resuming the device',
                  type=pvname,
                  mandatory=True,
                  userparam=False),
        'message_pv':
            Param('PV for reading error messages from the device',
                  type=pvname,
                  mandatory=True,
                  userparam=False),
    }

    parameter_overrides = {
        'unit':
            Override(mandatory=False, settable=False, userparam=False),
        'mapping':
            Override(mandatory=False,
                     settable=False,
                     userparam=False,
                     volatile=True),
    }

    attached_devices = {
        'status': Attach('Status of device', EpicsStringReadable),
    }

    _commands = {}

    def doInit(self, mode):
        self._commands = {
            'start': self.start_pump,
            'stop': self.stop_pump,
            'purge': self.purge,
            'pause': self.pause_pump,
            'resume': self.resume_pump
        }
        MappedMoveable.doInit(self, mode)
        self.valuetype = oneof(*self._commands)

    def _get_pv_parameters(self):
        return {'start_pv', 'stop_pv', 'purge_pv', 'pause_pv', 'message_pv'}

    def doStart(self, target):
        if target in self._commands:
            self._commands[target]()

    def doStop(self):
        self.stop_pump()

    def doRead(self, maxage=0):
        return self._attached_status.read(maxage)

    def doReadMapping(self):
        return {cmd: i for i, cmd in enumerate(self._commands.keys())}

    def doStatus(self, maxage=0):
        if self._mode == SIMULATION:
            return status.OK, ''
        device_msg = self._get_pv('message_pv', as_string=True)
        if device_msg:
            return status.ERROR, device_msg

        return self._attached_status.status(maxage)

    @usermethod
    def start_pump(self):
        """Start pumping"""
        if self._mode == SIMULATION:
            return
        curr_state = self._attached_status.read(0)
        if curr_state != 'Stopped':
            raise InvalidValueError('Cannot start from the current state, '
                                    'please stop the pump first')
        self._put_pv('start_pv', 1)

    @usermethod
    def stop_pump(self):
        """Stop pumping"""
        if self._mode == SIMULATION:
            return
        curr_state = self._attached_status.read(0)
        if curr_state == 'Stopped':
            self.log.warning("Stop request ignored as pump already stopped")
            return
        self._put_pv('stop_pv', 2)

    @usermethod
    def purge(self):
        """Purge the pump"""
        if self._mode == SIMULATION:
            return
        curr_state = self._attached_status.read(0)
        if curr_state != 'Stopped':
            raise InvalidValueError('Cannot purge from the current state, '
                                    'please stop the pump first')
        self._put_pv('purge_pv', 3)

    @usermethod
    def pause_pump(self):
        """Pause pumping"""
        if self._mode == SIMULATION:
            return
        curr_state = self._attached_status.read(0)
        if curr_state not in ['Infusing', 'Withdrawing']:
            raise InvalidValueError('Cannot pause from the current state '
                                    f'({curr_state})')
        self._put_pv('pause_pv', 4)

    @usermethod
    def resume_pump(self):
        """Resume pumping"""
        if self._mode == SIMULATION:
            return
        curr_state = self._attached_status.read(0)
        if curr_state != 'Paused':
            self.log.warning("Resume request ignored as pump is not paused")
            return
        self._put_pv('pause_pv', 5)
