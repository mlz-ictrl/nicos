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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import Param, status, oneof, Override, ConfigurationError, \
    HasLimits, HasPrecision, Moveable
from nicos.devices.tango import PyTangoDevice
from .generic import GenericLimaCCD
from .optional import LimaCooler


class Andor2LimaCCD(GenericLimaCCD):
    """
    This device class is an extension to the GenericLimaCCD that adds the
    hardware specific functionality for all Andor SDK2 based cameras.
    """

    HSSPEEDS = [5, 3, 1, 0.05]  # Values from sdk manual
    VSSPEEDS = [38.55, 76.95]  # Values from sdk manual
    PGAINS = [1, 2, 4]  # Values from sdk manual

    parameters = {
        'hsspeed': Param('Horizontal shift speed',
                         type=oneof(*HSSPEEDS), settable=True, default=5,
                         unit='MHz', volatile=True, category='general'),
        'vsspeed': Param('Vertical shift speed',
                         type=oneof(*VSSPEEDS), settable=True, default=76.95,
                         unit='ms/shift', volatile=True, category='general'),
        'pgain':   Param('Preamplifier gain',
                         type=oneof(*PGAINS), settable=True, default=4,
                         volatile=True, category='general'),
    }

    parameter_overrides = {
        'hwdevice': Override(mandatory=True),
    }

    def doReadHsspeed(self):
        index = self._hwDev._dev.adc_speed

        try:
            return self.HSSPEEDS[index]
        except IndexError:
            raise ConfigurationError(self, 'Camera uses unknown hs speed '
                                     '(index: %d)' % index)

    def doWriteHsspeed(self, value):
        index = self.HSSPEEDS.index(value)
        self._hwDev._dev.adc_speed = index

    def doReadVsspeed(self):
        index = self._hwDev._dev.vs_speed

        try:
            return self.VSSPEEDS[index]
        except IndexError:
            raise ConfigurationError(self, 'Camera uses unknown vs speed '
                                     '(index: %d)' % index)

    def doWriteVsspeed(self, value):
        index = self.VSSPEEDS.index(value)
        self._hwDev._dev.vs_speed = index

    def doReadPgain(self):
        index = self._hwDev._dev.p_gain

        try:
            return self.PGAINS[index]
        except IndexError:
            raise ConfigurationError(self, 'Camera uses unknown preamplifier '
                                     'gain (index: %d)' % index)

    def doWritePgain(self, value):
        index = self.PGAINS.index(value)
        self._hwDev._dev.p_gain = index


class Andor2TemperatureController(PyTangoDevice, HasLimits, HasPrecision,
                                  LimaCooler, Moveable):
    """
    This devices provides access to the cooling feature of Andor2 cameras.
    """

    def doRead(self, maxage=0):
        return self._dev.temperature

    def doStatus(self, maxage=0):  # pylint: disable=W0221
        coolerState = self._dev.cooler
        temperature = self.doRead()
        sp = self._dev.temperature_sp

        nicosState = status.UNKNOWN

        if self.doReadCooleron():
            if abs(temperature - sp) < self.precision:
                nicosState = status.OK
            else:
                nicosState = status.BUSY
        else:
            if temperature > -10:
                nicosState = status.OK
            else:
                nicosState = status.BUSY

        return (nicosState, coolerState)

    def doStart(self, value):
        if value > -10:
            self.doWriteCooleron(False)
        else:
            self._dev.temperature_sp = value
            self.doWriteCooleron(True)
