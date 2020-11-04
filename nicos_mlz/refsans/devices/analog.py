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
#   Matthias Pomm <Matthias.Pomm@hzg.de>
#
# ****************************************************************************
"""
Support code for any encoder with analog signal, like poti laser distance etc
"""

from __future__ import absolute_import, division, print_function

from nicos.core import Readable, oneof, status
from nicos.core.params import Attach, Param, nonemptylistof
from nicos.devices.abstract import Coder


class AnalogPoly(Coder):

    attached_devices = {
        'device': Attach('Sensing device (poti etc)', Readable),
    }

    parameters = {
        'poly': Param('Polynomial coefficients in ascending order',
                      type=nonemptylistof(float), settable=False,
                      mandatory=False, default=[1.]),
    }

    def doRead(self, maxage=0):
        """Return a read analogue signal corrected by a polynom.

        A correcting polynom of at least first order is used.
        Result is then offset + mul * <previously calculated value>
        """
        value = self._attached_device.read(maxage)
        self.log.debug('uncorrected value: %f', value)
        result = sum([ai * (value ** i) for i, ai in enumerate(self.poly)])
        self.log.debug('final result: %f', result)
        return result


class AnalogCalc(Coder):

    attached_devices = {
        'device1': Attach('first value for calculation', Readable),
        'device2': Attach('second value for calculation', Readable),
    }

    parameters = {
        'calc': Param('choose the calculation',
                      type=oneof('mul', 'div', 'add', 'dif'), settable=False,
                      mandatory=True, default='div'),
    }

    def doRead(self, maxage=0):
        """Return a read analogue signal corrected by a polynom.

        A correcting polynom of at least first order is used.
        Result is then offset + mul * <previously calculated value>
        """
        value1 = self._attached_device1.read(maxage)
        value2 = self._attached_device2.read(maxage)

        self.log.info('value 1: %f 2: %f', value1, value2)
        if self.calc == 'mul':
            result = value1 * value2
        elif self.calc == 'div':
            result = value1 / value2
        elif self.calc == 'add':
            result = value1 + value2
        elif self.calc == 'dif':
            result = value1 - value2
        self.log.debug('final result: %f', result)

        return result


class Accuracy(Readable):

    attached_devices = {
        'motor': Attach('moving motor', Readable),
        'analog': Attach('analog encoder maybe poti', Readable),
    }

    parameters = {
        'absolute': Param('Value is absolute or signed.', type=bool,
                          settable=True, default=True),
    }

    def doRead(self, maxage=0):
        dif = self._attached_analog.read(maxage) - \
            self._attached_motor.read(maxage)
        return abs(dif) if self.absolute else dif

    def doStatus(self, maxage=0):
        return status.OK, ''
