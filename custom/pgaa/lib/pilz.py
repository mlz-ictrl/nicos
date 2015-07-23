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
import time

from nicos.core import tacodev, Param, status
from nicos.devices.taco.io import NamedDigitalOutput
from nicos.core.mixins import HasTimeout
from nicos.core import SIMULATION


class Switch(HasTimeout, NamedDigitalOutput):
    """The Pilz box is connected via the Modbus TCP protocol with the rest of
    the world. Unfortunately the bit for controlling the attenuators and
    shutter are distributed in a wide range over the input and output region
    of the Modbus interface. The Beckhoff TACO server deals with the bits
    and so we have some different devices.
    """
    parameters = {
        'remote':   Param('Device to enable the remote control',
                          type=tacodev, mandatory=True, preinit=True),
        'readback': Param('Device to read back the reached value',
                          type=tacodev, mandatory=True, preinit=True),
        'error':    Param('Device to indicate an error during the move of the '
                          'switch',
                          type=tacodev, mandatory=True, preinit=True),
    }

    def doInit(self, mode):
        NamedDigitalOutput.doInit(self, mode)
        if mode != SIMULATION:
            self._remote = self._create_client(devname=self.remote,
                                               class_=IO.DigitalOutput,
                                               resetok=True, timeout=None)
            self._readback = self._create_client(devname=self.readback,
                                                 class_=IO.DigitalInput,
                                                 resetok=True, timeout=None)
            self._error = self._create_client(devname=self.error,
                                              class_=IO.DigitalInput,
                                              resetok=True, timeout=None)
            self._sleeptime = 0.1

    def _writeValue(self, value):
        self._taco_guard(self._dev.write, value)
        time.sleep(self._sleeptime)

    def _enableRemote(self):
        self._taco_guard(self._remote.write, 1)
        time.sleep(self._sleeptime)

    def _disableRemote(self):
        self._taco_guard(self._remote.write, 0)
        time.sleep(self._sleeptime)

    def doStart(self, target):
        """ At first we have to enable the remote control and after writing
        the value we take the remote control enable bit
        The switch is configured to write a bit, hold it some time and reset it
        """
        value = self.mapping.get(target, target)
        if value == self._taco_guard(self._readback.read):
            return
        self._enableRemote()
        try:
            self._writeValue(value)
        finally:
            self._disableRemote()

    def doRead(self, maxage=0):
        value = self._taco_guard(self._readback.read)
        return self._reverse.get(value, value)

    def doStatus(self, maxage=0):
        if self._taco_guard(self._error.read) == 0:
            return status.OK, 'idle'
        else:
            return status.ERROR, 'target not reached'


class Attenuator(Switch):
    """ The attentuator switch must write always a '1' to change the value."""

    def _writeValue(self, value):
        self._taco_guard(self._dev.write, 1)
        time.sleep(self._sleeptime)
