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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for MIRA shutter readout/operation."""

import time

import Modbus

from nicos.core import usermethod, Param, ModeError, Readable, status
from nicos.devices.taco.io import TacoDevice
from nicos.core import SIMULATION, SLAVE


class Shutter(TacoDevice, Readable):
    """
    Class for readout of the MIRA shutter via digital input card, and closing
    the shutter via digital output (tied into Pilz security system).
    """

    taco_class = Modbus.Modbus
    valuetype = str

    parameters = {
        'openoffset':   Param('The bit offset for the "shutter open" input',
                              type=int, mandatory=True),
        'closeoffset':  Param('The bit offset for the "shutter closed" input',
                              type=int, mandatory=True),
        'switchoffset': Param('The bit offset for the "close shutter" output',
                              type=int, mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))

    def doStatus(self, maxage=0):
        is_open = self._taco_guard(self._dev.readDiscreteInputs, (0, self.openoffset, 1))[0]
        is_clsd = self._taco_guard(self._dev.readDiscreteInputs, (0, self.closeoffset, 1))[0]
        if is_open + is_clsd == 1:
            return status.OK, ''
        else:
            return status.BUSY, 'moving'

    def doRead(self, maxage=0):
        is_open = self._taco_guard(self._dev.readDiscreteInputs, (0, self.openoffset, 1))[0]
        is_clsd = self._taco_guard(self._dev.readDiscreteInputs, (0, self.closeoffset, 1))[0]
        if is_open and not is_clsd:
            return 'open'
        elif is_clsd and not is_open:
            return 'closed'
        return ''

    @usermethod
    def close(self):
        if self._mode == SLAVE:
            raise ModeError(self, 'closing shutter not allowed in slave mode')
        elif self._sim_active:
            return
        self._taco_guard(self._dev.writeSingleCoil, (0, self.switchoffset, 1))
        time.sleep(0.5)
        self._taco_guard(self._dev.writeSingleCoil, (0, self.switchoffset, 0))
        self.log.info('instrument shutter closed')
