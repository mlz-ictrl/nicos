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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA's Attenuator controling device for NICOS."""

from nicos.core import InvalidValueError, Moveable, Param, floatrange, listof

from Modbus import Modbus

from nicos.devices.taco import TacoDevice
from nicos.core import SIMULATION


class SatBox(TacoDevice, Moveable):
    """
    Device Object for PANDA's Attenuator, controlled by a WUT-device via a ModBusTCP interface.
    """
    taco_class = Modbus

    valuetype = int

    parameters = {
        'blades': Param('Thickness of the blades, starting with lowest bit',
                         type=listof(floatrange(0, 1000)), mandatory=True),
        'slave_addr': Param('Modbus-slave-addr (Beckhoff=0,WUT=1)',
                       type=int,mandatory=True),
        'addr_out': Param('Base Address for activating Coils',
                           type=int, mandatory=True),
        #~ 'addr_in': Param('Base Address for reading switches giving real blade state',
                           #~ type=int, mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            if self.slave_addr == 0: # only disable Watchdog for Beckhoff!
                self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))

    def doRead(self, maxage=0):
        # just read back the OUTPUT values, scale with bladethickness and sum up
        return sum(b*r for b, r in zip(self.blades,
                    self._taco_guard(
                        self._dev.readCoils, (self.slave_addr, self.addr_out, len(self.blades))))
                    )

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
            return self.doStart(rpos + 1)
        self.log.debug('setting blades: %s' %
                       [s * b for s, b in zip(which, self.blades)]
                      )
        self._taco_guard(self._dev.writeMultipleCoils, (self.slave_addr,
                         self.addr_out) + tuple(which))

    def doIsAllowed(self, target):
        if not (0 <= target <= sum(self.blades)):
            return False, 'Value outside range 0..%d' % sum(self.blades)
        if int(target) != target:
            return False, 'Value must be an integer !'
        return True, ''
