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

"""Devices for the Beckhoff Busklemmensystem."""

from Modbus import Modbus

from nicos.core import Param, listof
from nicos.devices.taco.io import DigitalOutput, NamedDigitalOutput
from nicos.core import SIMULATION


class BeckhoffDigitalOutput(DigitalOutput):
    """
    Device object for a digital output device via a Beckhoff modbus interface.
    """
    taco_class = Modbus
    valuetype = listof(int)

    parameters = {
        'startoffset': Param('Starting offset of digital output values',
                             type=int, mandatory=True),
        'bitwidth':    Param('Number of bits to switch', type=int,
                             mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))

    def doRead(self, maxage=0):
        return tuple(self._taco_guard(self._dev.readCoils, (0,
                                      self.startoffset, self.bitwidth)))

    def doStart(self, value):
        self._taco_guard(self._dev.writeMultipleCoils, (0,
                         self.startoffset) + tuple(value))

    def doIsAllowed(self, target):
        try:
            if len(target) != self.bitwidth:
                return False, ('value needs to be a sequence of length %d, '
                               'not %r' % (self.bitwidth, target))
        except TypeError:
            return False, 'invalid value for device: %r' % target
        return True, ''

    def doReadFmtstr(self):
        return '[' + ', '.join(['%s'] * self.bitwidth) + ']'


class BeckhoffNamedDigitalOutput(NamedDigitalOutput):
    taco_class = Modbus

    parameters = {
        'startoffset': Param('Starting offset of digital output values',
                             type=int, mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))
        NamedDigitalOutput.doInit(self, mode)

    def doStart(self, target):
        value = self.mapping.get(target, target)
        self._taco_guard(self._dev.writeMultipleCoils,
                         (0, self.startoffset) + (value,))

    def doRead(self, maxage=0):
        value = self._taco_guard(self._dev.readCoils,
                                 (0, self.startoffset, 1))[0]
        return self._reverse.get(value, value)
