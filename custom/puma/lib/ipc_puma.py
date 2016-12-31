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

"""PUMA specific modifications to NICOS's module for IPC
(Institut für Physikalische Chemie, Göttingen) hardware classes."""

from nicos.core import Override, status
from nicos.devices.vendor.ipc import Coder as IPCCoder, Motor as IPCMotor, \
    SlitMotor as IPCSlitMotor


class Coder(IPCCoder):
    """Same as vendor.ipc.Coder but don't write the config byte
    """
    parameter_overrides = {
        'confbyte': Override(settable=False),
    }

    def doWriteConfbyte(self, byte):
        self.log.warning('Config byte can\'t be changed like this.')
#        self._attached_bus.send(self.addr, 154, byte, 3)
        return


class Motor(IPCMotor):
    """Same as vendor.ipc.Motor but don't write the config byte."""
    parameter_overrides = {
        'confbyte': Override(settable=False),
    }

    def doWriteConfbyte(self, value):
        self.log.warning('Config byte can\'t be changed like this.')
        return
#       if self._hwtype == 'single':
#           self._attached_bus.send(self.addr, 49, value, 3)
#       else:
#           raise InvalidValueError(self, 'confbyte not supported by card')
#       self.log.info('parameter change not permanent, use _store() '
#                     'method to write to EEPROM')

    def doWriteSteps(self, value):
        self.log.debug('not setting new steps value: %s', value)
#        self._adevs['bus'].send(self.addr, 43, value, 6)
        return


class Motor1(IPCMotor):
    """Same as vendor.ipc.Motor but don't care about limit swtches"""
    parameter_overrides = {
        'confbyte': Override(settable=False),
    }

    def doWriteConfbyte(self, value):
        self.log.warning('Config byte can\'t be changed like this.')
        return
#       if self._hwtype == 'single':
#           self._adevs['bus'].send(self.addr, 49, value, 3)
#       else:
#           raise InvalidValueError(self, 'confbyte not supported by card')
#       self.log.info('parameter change not permanent, use _store() '
#                     'method to write to EEPROM')

    def doStatus(self, maxage=0):
        state = self._adevs['bus'].get(self.addr, 134)
        st = status.OK

        msg = ''
        # msg += (state & 2) and ', backward' or ', forward'
        # msg += (state & 4) and ', halfsteps' or ', fullsteps'
        if state & 16:
            msg += ', inhibit active'
        if state & 128:
            msg += ', reference switch active'
        if state & 256:
            msg += ', software limit - reached'
        if state & 512:
            msg += ', software limit + reached'
        if state & 16384 == 0:
            msg += ', external power stage enabled'
        if state & 32:
            msg += ', limit switch - active'
        if state & 64:
            msg += ', limit switch + active'
        if self._hwtype == 'single':
            msg += (state & 8) and ', relais on' or ', relais off'
            if state & 8:
                # on single cards, if relay is ON, card is supposedly BUSY
                st = status.BUSY
        if state & 32768:
            st = status.BUSY
            msg += ', waiting for start/stopdelay'

        # check error states last
#        if state & 32 and state & 64:
#            st = status.ERROR
#            msg = msg.replace('limit switch - active, limit switch + active',
#                'EMERGENCY STOP pressed or both limit switches broken')
#        if state & 1024:
#            st = status.ERROR
#            msg += ', device overheated'
#        if state & 2048:
#            st = status.ERROR
#            msg += ', motor undervoltage'
#        if state & 4096:
#            st = status.ERROR
#            msg += ', motor not connected or leads broken'
#        if state & 8192:
#            st = status.ERROR
#            msg += ', hardware failure or device not reset after power-on'

        # if it's moving, it's not in error state! (except if the emergency
        # stop is active)
        if state & 1 and (state & 96 != 96):
            st = status.BUSY
            msg = ', moving' + msg
        self.log.debug('status is %d:%s', st, msg[2:])
        return st, msg[2:]


class SlitMotor(IPCSlitMotor):
    """XXX: Same as vendor.ipc.SlitMotor."""
