#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS TACO digital input/output definition
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Implementation of TACO DigitalInput and DigitalOutput devices."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from IO import DigitalInput, DigitalOutput

from nicm.device import Readable, Moveable, Param
from nicm.taco.base import TacoDevice


class Input(TacoDevice, Readable):
    """Base class for TACO DigitalInputs."""

    taco_class = DigitalInput


# XXX switchable?
class Output(TacoDevice, Moveable):
    """Base class for TACO DigitalOutputs."""

    taco_class = DigitalOutput

    def doStart(self, value):
        self._taco_guard(self._dev.write, value)


class PartialInput(Input):
    """Base class for a TACO DigitalOutput with only a part of the full
    bit width accessed.
    """

    parameters = {
        'startbit': Param('Number of the first bit', type=int, default=0),
        'bitwidth': Param('Number of bits', type=int, default=1),
    }

    def doInit(self):
        self._mask = ((1 << self.bitwidth) - 1) << self.startbit

    def doRead(self):
        return self._taco_guard(self._dev.read) & self._mask


class PartialOutput(Output):
    """Base class for a TACO DigitalOutput with only a part of the full
    bit width accessed.
    """

    parameters = {
        'startbit': Param('Number of the first bit', type=int, default=0),
        'bitwidth': Param('Number of bits', type=int, default=1),
    }

    def doInit(self):
        self._max = (1 << self.bitwidth) - 1

    def doRead(self):
        return (self._taco_guard(self._dev.read) >> self.startbit) & self._max

    def doStart(self, value):
        curvalue = self._taco_guard(self._dev.read)
        newvalue = (curvalue & ~self._max) & (value << self.startbit)
        self._taco_guard(self._dev.write, newvalue)

    def doIsAllowed(self, value):
        if target < 0 or target > self._max:
            return False, '%d outside range [0, %d]' % (value, self._max)
        return True, ''


class ListOutput(Output):
    """Base class for a TACO DigitalOutput that works with a list of individual
    bits instead of a single integer.
    """

    parameters = {
        'startbit': Param('Number of the first bit', type=int, default=0),
        'bitwidth': Param('Number of bits', type=int, default=1),
    }

    def doInit(self):
        self._max = (1 << self.bitwidth) - 1

    def doRead(self):
        # extract the relevant bit range from the device value
        value = (self._taco_guard(self._dev.read) >> self.startbit) & self._max
        # convert to a list of single bits (big-endian: the first bit is the 1)
        bits = []
        while value:
            bits.append(value & 1)
            value >>= 1
        return bits

    def doStart(self, value):
        # convert list of bits to an integer
        value = sum(bool(bit) << pos for (pos, bit) in enumerate(value))
        # get current value and put new integer at the appropriate position
        curvalue = self._taco_guard(self._dev.read)
        newvalue = (curvalue & ~self._max) & (value << self.startbit)
        self._taco_guard(self._dev.write, newvalue)

    def doIsAllowed(self, value):
        # XXX this will raise TypeError for e.g. ints -- something better?
        if len(target) != self.bitwidth:
            return False, ('value needs to be a list of length %d, not %r' %
                           (self.bitwidth, value))
        return True, ''
