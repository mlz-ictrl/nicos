# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

from time import sleep

import numpy as np

from nicos.core import Param, Value, floatrange, intrange
from nicos.devices.generic.detector import PassiveChannel
from nicos.devices.tango import PyTangoDevice


class MeasureChannel(PyTangoDevice, PassiveChannel):
    """
    Detector channel to measure a single value multiple times for statistics
    and provide the standard deviation as an error column.
    """

    parameters = {
        'samples':  Param('Number of measurements to take',
                          type=intrange(1, 1e6), default=10, settable=True),
        'interval': Param('Time to wait between measurements',
                          type=floatrange(0), unit='s', settable=True),
    }

    def doRead(self, maxage=0):
        values = [self._dev.value]
        if self.samples == 1:
            return values  # no stdev calculation possible
        for _ in range(self.samples - 1):
            sleep(self.interval)
            values.append(self._dev.value)
        mean = np.mean(values)
        sdev = np.std(values)
        return [mean, sdev]

    def valueInfo(self):
        if self.samples == 1:
            return (Value(self.name, unit=self.unit, fmtstr=self.fmtstr,
                          type='other'),)
        return (Value(self.name, unit=self.unit, fmtstr=self.fmtstr,
                      errors='next', type='other'),
                Value(self.name + '_stdev', unit=self.unit, fmtstr=self.fmtstr,
                      type='error'))
