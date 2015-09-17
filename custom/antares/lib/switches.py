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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

""" Classes to access to the switches via the Pilz Box """

import IO

from nicos.core import tacodev, Param, Override, dictof, SIMULATION
from nicos.devices.taco.io import NamedDigitalOutput


class ReadbackSwitch(NamedDigitalOutput):
    """A switch that uses two TACO devices for write and readout."""

    parameters = {
        'readback':  Param('Device to read back the reached value',
                           type=tacodev, mandatory=True, preinit=True),
        'rwmapping': Param('Map read values to write values and vice versa',
                           type=dictof(int, int)),
    }

    parameter_overrides = {
        'mapping': Override(type=dictof(int, str)),
    }

    def doInit(self, mode):
        super(ReadbackSwitch, self).doInit(mode)
        if mode != SIMULATION:
            self._readback = self._create_client(devname=self.readback,
                                                 class_=IO.DigitalInput,
                                                 resetok=True, timeout=None)

    def doStart(self, target):
        value = self._reverse.get(target, target)
        curVal = self._taco_guard(self._readback.read)
        if value == self.rwmapping.get(curVal, curVal):
            return

        self._taco_guard(self._dev.write, value)

    def doRead(self, maxage=0):
        value = self._taco_guard(self._readback.read)

        self.log.debug('Read raw: %r' % value)
        value = self.rwmapping.get(value, value)
        value = self.mapping.get(value, value)
        self.log.debug('Mapped value: %r' % value)
        return value

    # def doStatus(self, maxage=0):
    #     if self._taco_guard(self._error.read) == 0:
    #         return status.OK, 'idle'
    #     else:
    #         return status.ERROR, 'target not reached'


class ToggleSwitch(ReadbackSwitch):
    """A switch that is toggled every time a '1' is written to the write dev.
    """

    def doStart(self, target):
        value = self._reverse.get(target, target)
        if value == self._taco_guard(self._readback.read):
            return

        self._taco_guard(self._dev.write, 1)
