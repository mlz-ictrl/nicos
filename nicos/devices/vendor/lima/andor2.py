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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import re

from nicos.core import Param, status, oneof, Override, HasLimits, \
    HasPrecision, Moveable
from nicos.devices.tango import PyTangoDevice
from .generic import GenericLimaCCD
from .optional import LimaCooler


class Andor2LimaCCD(GenericLimaCCD):
    """
    This device class is an extension to the GenericLimaCCD that adds the
    hardware specific functionality for all Andor SDK2 based cameras.
    """

    HSSPEEDS = [5, 3, 1, 0.05]  # Values from sdk manual
    VSSPEEDS = [16, 38.55, 76.95]  # Values from sdk manual
    PGAINS = [1, 2, 4]  # Values from sdk manual

    HSSPEED_RE = re.compile(r'ADC0_(\d+\.\d+|\d+)MHZ')
    VSSPEED_RE = re.compile(r'(\d+(?:\.\d+)?)USEC')
    PGAIN_RE = re.compile(r'X(\d)')

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

    def doInfo(self):
        for p in ('hsspeed', 'vsspeed', 'pgain'):
            self._pollParam(p)
        return []

    def doReadHsspeed(self):
        val = float(self.HSSPEED_RE.match(self._hwDev._dev.adc_speed).group(1))
        return val

    def doWriteHsspeed(self, value):
        self._hwDev._dev.adc_speed = 'ADC0_%sMHZ' % value

    def doReadVsspeed(self):
        val = float(self.VSSPEED_RE.match(self._hwDev._dev.vs_speed).group(1))
        return val

    def doWriteVsspeed(self, value):
        self._hwDev._dev.vs_speed = '%gUSEC' % value

    def doReadPgain(self):
        val = float(self.PGAIN_RE.match(self._hwDev._dev.p_gain).group(1))
        return val

    def doWritePgain(self, value):
        self._hwDev._dev.p_gain = 'X%s' % value


class Andor2TemperatureController(PyTangoDevice, HasLimits, HasPrecision,
                                  LimaCooler, Moveable):
    """
    This devices provides access to the cooling feature of Andor2 cameras.
    """

    def doRead(self, maxage=0):
        return self._dev.temperature

    def doStatus(self, maxage=0):
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
            self.cooleron = False
        else:
            self._dev.temperature_sp = value
            self.cooleron = True
