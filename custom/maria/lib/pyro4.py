# -*- coding: utf-8 -*-
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

import threading

import Pyro4

from nicos.core import status
from nicos.core.constants import SIMULATION
from nicos.core.device import Moveable
from nicos.core.mixins import HasCommunication, HasTimeout
from nicos.core.params import Param, Override, dictof, oneofdict


globalLock = threading.Lock()


class Pyro4Device(HasCommunication):
    """Basic Pyro4 device."""

    hardware_access = True

    parameters = {
        "pyro4device": Param("Pyro4 device name", type=str,
                             mandatory=True, preinit=True),
        "hmackey": Param("Pyro4 HMAC key", type=str,
                          mandatory=False, preinit=True),
        "timeout": Param("Pyro4 timeout", type=int,
                         default=1.5, preinit=True),
    }

    def doPreinit(self, mode):
        self._dev = None
        if mode != SIMULATION:
            Pyro4.config.COMMTIMEOUT = self.timeout
            if hasattr(Pyro4.config, "MAX_RETRIES"):
                # pylint: disable=assigning-non-slot
                Pyro4.config.MAX_RETRIES = self.comtries
            if self.hmackey and hasattr(Pyro4.config, "HMAC_KEY"):  # Pyro 4.18
                # pylint: disable=assigning-non-slot
                Pyro4.config.HMAC_KEY = self.hmackey
            self._dev = Pyro4.Proxy(self.pyro4device)
            if self.hmackey and hasattr(self._dev, "_pyroHMACKey"):  # Pyro 4.43
                self._dev._pyroHmacKey = self.hmackey
            self._dev._pyroRelease()


class DigitalOutput(Pyro4Device, HasTimeout, Moveable):
    """
    A devices that can set and read a digital value corresponding to a
    bitfield.
    """

    lastStart = None
    valuetype = int
    parameter_overrides = {
        'unit': Override(mandatory=False),
        'timeout': Override(default=1.),
    }

    def doRead(self, maxage=0):
        with globalLock, self._dev:
            return self._dev.afp_state_get()

    def doStart(self, value):
        if self.read(0) != value:
            with globalLock, self._dev:
                self.lastStart = value
                self._dev.afp_flip_do()

    def doStatus(self, maxage=0):
        return status.OK, ""


class NamedDigitalOutput(DigitalOutput):
    """
    A DigitalOutput with numeric values mapped to names.
    """

    parameters = {
        'mapping': Param('A dictionary mapping state names to integer values',
                         type=dictof(str, int), mandatory=True),
    }

    def doInit(self, mode):
        self._reverse = dict((v, k) for (k, v) in self.mapping.items())
        # oneofdict: allows both types of values (string/int), but normalizes
        # them into the string form
        self.valuetype = oneofdict(self._reverse)

    def doStart(self, target):
        value = self.mapping.get(target, target)
        DigitalOutput.doStart(self, value)

    def doRead(self, maxage=0):
        value = DigitalOutput.doRead(self, maxage)
        return self._reverse.get(value, value)
