#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************

u"""PUMA specific modifications to NICOS's module for IPC.

(Institut für Physikalische Chemie, Göttingen) hardware classes.
"""

from nicos.core import Override, status
from nicos.devices.vendor.ipc import Coder as IPCCoder, Motor as IPCMotor


class Coder(IPCCoder):
    """Same as vendor.ipc.Coder but don't write the config byte."""

    parameter_overrides = {
        'confbyte': Override(settable=False),
    }

    def doWriteConfbyte(self, byte):
        self.log.warning('Config byte can\'t be changed like this.')
        # self._attached_bus.send(self.addr, 154, byte, 3)
        return


class Motor(IPCMotor):
    """Same as vendor.ipc.Motor but don't write the config byte."""

    parameter_overrides = {
        'confbyte': Override(settable=False),
    }

    def doWriteConfbyte(self, value):
        self.log.warning('Config byte can\'t be changed like this.')
        # if self._hwtype == 'single':
        #     self._attached_bus.send(self.addr, 49, value, 3)
        # else:
        #     raise InvalidValueError(self, 'confbyte not supported by card')
        # self.log.info('parameter change not permanent, use _store() method '
        #               'to write to EEPROM')
        return

    def doWriteSteps(self, value):
        self.log.debug('not setting new steps value: %s', value)
        # self._attached_bus.send(self.addr, 43, value, 6)
        return


class Motor1(IPCMotor):
    """Same as vendor.ipc.Motor but don't care about limit swtches."""

    parameter_overrides = {
        'confbyte': Override(settable=False),
    }

    def doWriteConfbyte(self, value):
        self.log.warning('Config byte can\'t be changed like this.')
        # if self._hwtype == 'single':
        #     self._attached_bus.send(self.addr, 49, value, 3)
        # else:
        #     raise InvalidValueError(self, 'confbyte not supported by card')
        # self.log.info('parameter change not permanent, use _store() method '
        #               'to write to EEPROM')
        return

    def doStatus(self, maxage=0):
        state = self._attached_bus.get(self.addr, 134)
        st = status.OK

        msg = ''
        # msg += (state & 2) and ', backward' or ', forward'
        # msg += (state & 4) and ', halfsteps' or ', fullsteps'
        if state & 0x10:
            msg += ', inhibit active'
        if state & 0x80:
            msg += ', reference switch active'
        if state & 0x100:
            msg += ', software limit - reached'
        if state & 0x200:
            msg += ', software limit + reached'
        if state & 0x4000 == 0:
            msg += ', external power stage enabled'
        if state & 0x20:
            msg += ', limit switch - active'
        if state & 0x40:
            msg += ', limit switch + active'
        if self._hwtype == 'single':
            msg += (state & 8) and ', relais on' or ', relais off'
            if state & 8:
                # on single cards, if relay is ON, card is supposedly BUSY
                st = status.BUSY
        if state & 0x8000:
            st = status.BUSY
            msg += ', waiting for start/stopdelay'

        # check error states last
        # if state & 0x20 and state & 0x40:
        #     st = status.ERROR
        #     msg = msg.replace('limit switch - active, limit switch + active '
        #                       'EMERGENCY STOP pressed or both limit switches'
        #                       ' broken')
        # if state & 0x400:
        #     st = status.ERROR
        #     msg += ', device overheated'
        # if state & 0x800:
        #     st = status.ERROR
        #     msg += ', motor undervoltage'
        # if state & 0x1000:
        #     st = status.ERROR
        #     msg += ', motor not connected or leads broken'
        # if state & 0x2000:
        #     st = status.ERROR
        #     msg += ', hardware failure or device not reset after power-on'

        # if it's moving, it's not in error state! (except if the emergency
        # stop is active)
        if state & 1 and (state & 0x60 != 0x60):
            st = status.BUSY
            msg = ', moving' + msg
        self.log.debug('status is %d:%s', st, msg[2:])
        return st, msg[2:]
