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
#   Petr Cermak
#
# *****************************************************************************

"""PANDA's Compressor box controlling device for NICOS."""

from Modbus import Modbus

from nicos.core import Readable, Param, status
from nicos.devices.taco import TacoDevice


class WaterControlBox(TacoDevice, Readable):
    """
    Device Object for PANDA's waterflow, controlled by a WUT-device via a
    ModBusTCP interface.
    """

    taco_class = Modbus

    parameters = {
        'slave_addr': Param('Modbus-slave-addr (Beckhoff=0, WUT=1)',
                            type=int, mandatory=True),
        'addr_in':    Param('Base Address for reading inputs',
                            type=int, mandatory=True),
    }

    waterStates = {
        0: 'off',
        1: 'on',
    }

    def doRead(self, maxage=0):
        # read water state
        state = self._taco_guard(self._dev.readCoils,
                                 (self.slave_addr, self.addr_in, 1))
        return self.waterStates[state[0]]

    def doStatus(self, maxage=0):
        return status.OK, ''
