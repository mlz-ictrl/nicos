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

from nicos.core import Param, intrange
from nicos.devices.tango import DigitalInput, DigitalOutput


class PartialDigitalInput(DigitalInput):
    """Base class for a TANGO DigitalInput with only a part of the full
    bit width accessed.
    """

    parameters = {
        'startbit': Param('Number of the first bit', type=int, default=0),
        'bitwidth': Param('Number of bits', type=int, default=1),
    }

    def doInit(self, mode):
        self._mask = (1 << self.bitwidth) - 1

    def doRead(self, maxage=0):
        raw_value = DigitalInput.doRead(self, maxage)
        return (raw_value >> self.startbit) & self._mask


class PartialDigitalOutput(DigitalOutput):
    """Base class for a TANGO DigitalOutput with only a part of the full
    bit width accessed.
    """

    parameters = {
        'startbit': Param('Number of the first bit', type=int, default=0),
        'bitwidth': Param('Number of bits', type=int, default=1),
    }

    def doInit(self, mode):
        self._mask = (1 << self.bitwidth) - 1
        self.valuetype = intrange(0, self._mask)

    def doRead(self, maxage=0):
        raw_value = DigitalOutput.doRead(self, maxage)
        return (raw_value >> self.startbit) & self._mask

    def doStart(self, target):
        curVal = DigitalOutput.doRead(self)
        newVal = (curVal & ~(self._mask << self.startbit)) | \
                   (target << self.startbit)
        DigitalOutput.doStart(self, newVal)
