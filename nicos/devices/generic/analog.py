#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
Devices to support calculations between device values
"""

from nicos.core import Readable
from nicos.core.errors import ConfigurationError
from nicos.core.params import Attach, Override, Param, oneof


class CalculatedReadable(Readable):
    """Calculates the sum, difference, product, or quotient of 2 devices."""

    attached_devices = {
        'device1': Attach('first device for calculation', Readable),
        'device2': Attach('second device for calculation', Readable),
    }

    parameters = {
        'op': Param('Operation between the device values',
                    type=oneof('mul', '*', 'div', '/', 'add', '+', 'dif', '-'),
                    settable=False, mandatory=True, default='div'),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, settable=True),
    }

    def doInit(self, mode):
        if self._attached_device1.unit != self._attached_device2.unit:
            raise ConfigurationError(
                self, 'different units for device1 and device2 (%s vs %s)' %
                (self._attached_device1.unit, self._attached_device2.unit))

    def doRead(self, maxage=0):
        """Return the calculated value of to readable devices."""
        value1 = self._attached_device1.read(maxage)
        value2 = self._attached_device2.read(maxage)

        self.log.debug('value 1: %f 2: %f', value1, value2)
        if self.op in ['add', '+']:
            result = value1 + value2
        elif self.op in ['dif', '-']:
            result = value1 - value2
        elif self.op in ['mul', '*']:
            result = value1 * value2
        elif self.op in ['div', '/']:
            result = value1 / value2
        self.log.debug('final result: %f', result)
        return result

    def doReadUnit(self):
        unit = self._params.get('unit')
        if unit is None:
            if self.op in ['div', '/']:
                unit = ''
            elif self.op in ['mul', '*']:
                unit = '%s^2' % self._attached_device1.unit
            else:
                unit = self._attached_device1.unit
        return unit
