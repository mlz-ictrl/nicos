#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""PANDA's Attenuator controling device for NICOS."""

from Modbus import Modbus

from nicos import session
from nicos.core import InvalidValueError, Moveable, Param, floatrange, listof,\
    oneof, SIMULATION, status, HasTimeout, Override
from nicos.devices.taco import TacoDevice


class SatBox(HasTimeout, TacoDevice, Moveable):
    """
    Device Object for PANDA's Attenuator

    controlled by a WUT-device via a ModBusTCP interface via a ModBus TACO
    Server.
    """
    taco_class = Modbus

    valuetype = int

    parameters = {
        'blades':     Param('Thickness of the blades, starting with lowest '
                            'bit',
                            type=listof(floatrange(0, 1000)), mandatory=True),
        'slave_addr': Param('Modbus-slave-addr (Beckhoff=0, WUT=1)',
                            type=int, mandatory=True),
        'addr_out':   Param('Base Address for activating Coils',
                            type=int, mandatory=True),
        'addr_in':    Param('Base Address for reading switches giving real'
                            'blade state',
                            type=int, mandatory=True),
        'readout':    Param('Determine blade state from output or from '
                            'switches',
                            type=oneof('switches', 'outputs'), mandatory=True,
                            default='output', chatty=True),
    }

    parameter_overrides = {
        'timeout': Override(default=5),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            if self.slave_addr == 0:  # only disable Watchdog for Beckhoff!
                self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))

    def _readOutputs(self, maxage=0):
        # just read back the OUTPUT values
        return self._taco_guard(self._dev.readCoils,
                                (self.slave_addr, self.addr_out,
                                 len(self.blades)))

    def _readSwitches(self):
        # deduce blade state from switches
        state = self._taco_guard(self._dev.readCoils,
                                 (self.slave_addr, self.addr_in,
                                  2 * len(self.blades)))
        realstate = []
        for i in range(0, len(self.blades)*2, 2):
            bladestate = state[i:i+2]
            if bladestate == (0, 1):
                realstate.append(1)
            elif bladestate == (1, 0):
                realstate.append(0)
            else:
                realstate.append(None)
        return tuple(realstate)

    def doRead(self, maxage=0):
        bladestate = self._readSwitches() if self.readout == 'switches' else \
            self._readOutputs()
        # only sum up blades which are used for sure (0/None->ignore)
        return sum(b * r for b, r in zip(self.blades, bladestate) if r)

    def doStatus(self, maxage=0):
        if self.readout == 'outputs':
            return status.OK, ''
        if self._readSwitches() == self._readOutputs():
            return status.OK, ''
        return status.BUSY, 'moving'

    def doStart(self, rpos):
        if rpos > sum(self.blades):
            raise InvalidValueError(self, 'Value %d too big!, maximum is %d'
                                    % (rpos, sum(self.blades)))
        which = [0] * len(self.blades)
        pos = rpos
        # start with biggest blade and work downwards, ignoring disabled blades
        for bladewidth in reversed(self.blades):
            if bladewidth and pos >= bladewidth:
                which[self.blades.index(bladewidth)] = 1
                pos -= bladewidth
        if pos != 0:
            self.log.warning('Value %d impossible, trying %d instead!' %
                             (rpos, rpos + 1))
            return self.start(rpos + 1)
        self.log.debug('setting blades: %s' %
                       [s * b for s, b in zip(which, self.blades)]
                       )
        self._taco_guard(self._dev.writeMultipleCoils,
                         (self.slave_addr, self.addr_out) + tuple(which))
        if self.readout == 'output':
            # if we have no readback, give blades time to react
            session.delay(1)

    def doIsAllowed(self, target):
        if not (0 <= target <= sum(self.blades)):
            return False, 'Value outside range 0..%d' % sum(self.blades)
        return True, ''
