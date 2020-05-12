#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""Classes to access to the switches via the Pilz Box."""

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.core import SIMULATION, Param, status, tangodev
from nicos.core.mixins import HasTimeout
from nicos.devices.tango import NamedDigitalOutput
from nicos.utils import HardwareStub


class Switch(HasTimeout, NamedDigitalOutput):
    """The Pilz box is connected via the Modbus TCP protocol.

    Unfortunately the bit for controlling the attenuators and shutter are
    distributed in a wide range over the input and output region of the Modbus
    interface.

    The TANGO server deals with the bits and so we have some different devices.
    """

    parameters = {
        'remote': Param('Device to enable the remote control',
                        type=tangodev, mandatory=True, preinit=True),
        'readback': Param('Device to read back the reached value',
                          type=tangodev, mandatory=True, preinit=True),
        'error': Param('Device to indicate an error during the move of the '
                       'switch',
                       type=tangodev, mandatory=True, preinit=True),
    }

    def doInit(self, mode):
        NamedDigitalOutput.doInit(self, mode)
        # Don't create PyTango device in simulation mode
        if mode != SIMULATION:
            self._remote = self._createPyTangoDevice(devname=self.remote)
            self._readback = self._createPyTangoDevice(devname=self.readback)
            self._error = self._createPyTangoDevice(devname=self.error)
            self._sleeptime = 0.1
        else:
            self._remote = HardwareStub(self)
            self._readback = HardwareStub(self)
            self._error = HardwareStub(self)

    def _writeValue(self, value):
        self._dev.value = value
        session.delay(self._sleeptime)

    def _enableRemote(self):
        self._remote.value = 1
        session.delay(self._sleeptime)

    def _disableRemote(self):
        self._remote.value = 0
        session.delay(self._sleeptime)

    def doStart(self, target):
        """Writing sequence to reach target.

        At first we have to enable the remote control and after writing
        the value we take the remote control enable bit
        The switch is configured to write a bit, hold it some time and reset it
        """
        value = self.mapping.get(target, target)
        if value == self._readback.value:
            return
        self._enableRemote()
        try:
            self._writeValue(value)
        finally:
            self._disableRemote()

    def doRead(self, maxage=0):
        value = self._readback.value
        return self._reverse.get(value, value)

    def doStatus(self, maxage=0):
        if self._error.value == 0:
            return status.OK, 'idle'
        return status.ERROR, 'target not reached'


class Attenuator(Switch):
    """The attentuator switch must write always a '1' to change the value."""

    def _writeValue(self, value):
        self._dev.value = 1
        session.delay(self._sleeptime)
