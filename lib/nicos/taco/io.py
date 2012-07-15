#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""Implementation of TACO I/O devices."""

__version__ = "$Revision$"

import IO

from nicos.core import dictof, Readable, Moveable, HasLimits, Param, Override, \
     NicosError, waitForStatus
from nicos.taco.core import TacoDevice


class AnalogInput(TacoDevice, Readable):
    """Base class for TACO AnalogInput devices.

    This class can be used for concrete devices, or other more specific device
    classes can be derived from it.
    """

    taco_class = IO.AnalogInput


class AnalogOutput(TacoDevice, HasLimits, Moveable):
    """Base class for TACO AnalogOutput devices.

    This class can be used for concrete devices, or other more specific device
    classes can be derived from it.
    """

    parameters = {
        'loopdelay': Param('Wait loop delay', unit='s', default=0.3),
    }

    taco_class = IO.AnalogOutput

    def doStart(self, value):
        self._taco_guard(self._dev.write, value)

    def doWait(self):
        # XXX add a timeout?
        waitForStatus(self, self.loopdelay)


class DigitalInput(TacoDevice, Readable):
    """Base class for TACO DigitalInput devices.  The values are plain integers.

    This class can be used for concrete devices, or other more specific device
    classes can be derived from it.
    """

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
    }

    taco_class = IO.DigitalInput


class NamedDigitalInput(DigitalInput):
    """A DigitalInput with numeric values mapped to names."""

    parameters = {
        'mapping': Param('A dictionary mapping integer values to names',
                         type=dictof(int, str)),
    }

    def doRead(self, maxage=0):
        value = self._taco_guard(self._dev.read)
        return self.mapping.get(value, value)


class PartialDigitalInput(NamedDigitalInput):
    """Base class for a TACO DigitalOutput with only a part of the full
    bit width accessed.
    """

    parameters = {
        'startbit': Param('Number of the first bit', type=int, default=0),
        'bitwidth': Param('Number of bits', type=int, default=1),
    }

    def doInit(self, mode):
        self._mask = ((1 << self.bitwidth) - 1) << self.startbit

    def doRead(self, maxage=0):
        value = self._taco_guard(self._dev.read) & self._mask
        return self.mapping.get(value, value)


class DigitalOutput(TacoDevice, Moveable):
    """Base class for TACO DigitalOutputs.

    This class can be used for concrete devices, or other more specific device
    classes can be derived from it.
    """

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
    }

    taco_class = IO.DigitalOutput

    def doStart(self, target):
        self._taco_guard(self._dev.write, target)


class NamedDigitalOutput(DigitalOutput):
    """A DigitalOutput with numeric values mapped to names."""

    parameters = {
        'mapping': Param('A dictionary mapping integer values to names',
                         type=dictof(int, str)),
    }

    def doInit(self, mode):
        self._reverse = dict((v, k) for (k, v) in self.mapping.iteritems())

    def doStart(self, target):
        value = self._reverse.get(target, target)
        self._taco_guard(self._dev.write, value)

    def doRead(self, maxage=0):
        value = self._taco_guard(self._dev.read)
        return self.mapping.get(value, value)


class PartialDigitalOutput(NamedDigitalOutput):
    """Base class for a TACO DigitalOutput with only a part of the full
    bit width accessed.
    """

    parameters = {
        'startbit': Param('Number of the first bit', type=int, default=0),
        'bitwidth': Param('Number of bits', type=int, default=1),
    }

    def doInit(self, mode):
        NamedDigitalOutput.doInit(self, mode)
        self._max = (1 << self.bitwidth) - 1

    def doRead(self, maxage=0):
        value = int(self._taco_guard(self._dev.read))
        value = (value >> self.startbit) & self._max
        return self.mapping.get(value, value)

    def doStart(self, target):
        value = self._reverse.get(target, target)
        curvalue = self._taco_guard(self._dev.read)
        newvalue = (curvalue & ~(self._max << self.startbit)) | \
                   (value << self.startbit)
        self._taco_guard(self._dev.write, newvalue)

    def doIsAllowed(self, target):
        value = self._reverse.get(target, target)
        if value < 0 or value > self._max:
            return False, '%d outside range [0, %d]' % (value, self._max)
        return True, ''


class BitsDigitalOutput(DigitalOutput):
    """Base class for a TACO DigitalOutput that works with a tuple of individual
    bits instead of a single integer.
    """

    parameters = {
        'startbit': Param('Number of the first bit', type=int, default=0),
        'bitwidth': Param('Number of bits', type=int, default=1),
    }

    def doInit(self, mode):
        self._max = (1 << self.bitwidth) - 1

    def doReadFmtstr(self):
        return '{ ' + ' '.join(['%s'] * self.bitwidth) + ' }'

    def doRead(self, maxage=0):
        # extract the relevant bit range from the device value
        value = (self._taco_guard(self._dev.read) >> self.startbit) & self._max
        # convert to a list of single bits (big-endian: the first bit is the 1)
        bits = []
        while value:
            bits.append(int(value & 1))
            value >>= 1
        bits += [0] * (self.bitwidth - len(bits))
        return tuple(bits)

    def doStart(self, target):
        # convert list of bits to an integer
        value = sum(bool(bit) << pos for (pos, bit) in enumerate(target))
        # get current value and put new integer at the appropriate position
        curvalue = self._taco_guard(self._dev.read)
        newvalue = (curvalue & ~self._max) | (value << self.startbit)
        self._taco_guard(self._dev.write, newvalue)

    def doIsAllowed(self, target):
        try:
            if len(target) != self.bitwidth:
                return False, ('value needs to be a sequence of length %d, '
                               'not %r' % (self.bitwidth, target))
        except TypeError:
            return False, 'invalid value for device: %r' % target
        return True, ''


class MultiDigitalOutput(Moveable):
    """Writes the same value to multiple digital outputs at once."""

    attached_devices = {
        'outputs': ([DigitalOutput], 'A list of digital outputs to '
                    'switch simultaneously'),
    }

    def doStart(self, target):
        for dev in self._adevs['outputs']:
            dev.start(target)

    def doRead(self, maxage=0):
        values = []
        for dev in self._adevs['outputs']:
            values.append(dev.read(maxage))
        if len(set(values)) != 1:
            devnames = [dev.name for dev in self._adevs['outputs']]
            raise NicosError(self,
                'outputs have different read values: '
                + ', '.join('%s=%s' % x for x in zip(devnames, values)))
        return values[0]
