# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Alexander Söderqvist <alexander.soederqvist@psi.ch>
#
# *****************************************************************************
import numpy as np

from nicos.core import Attach, Value
from nicos.devices.abstract import MappedMoveable
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel

from nicos_sinq.devices.imagesink.histogramdesc import HistogramDesc, \
    HistogramDimDesc
from nicos_sinq.devices.just_bin_it import JustBinItImage
from nicos_sinq.poldi.devices.epics_no_stop import EpicsDigitalMoveableNoStop


class PoldiFold(ImageChannelMixin, PassiveChannel):
    """
    For POLDI we sum up 4 segments of time bins in the histogram memory.
    These come from the fact that the chopper's 4 quadrants each share the same
    pattern, data generated should be interpreted summed together and not
    individually. This implementation is sort of a hack, as the
    histogram memory is configured to have 4 times as many ToF bins than
    actual, this NICOS device corrects this.
    """
    attached_devices = {
        'rawimage': Attach('Raw data where to get data from',
                           ImageChannelMixin)
    }

    def doReadArray(self, quality):
        # Get raw histogram memory data
        raw = self._attached_rawimage.readArray(quality)
        # Split, stack, reduce, return
        return np.add.reduce(
            np.stack(np.split(raw, 4, axis=1), axis=1), axis=1)

    @property
    def arraydesc(self):
        rawshape = self._attached_rawimage.readArray(0).shape
        return HistogramDesc(self.name, 'uint32', [
            HistogramDimDesc(rawshape[0], 'x', ''),
            HistogramDimDesc(rawshape[1] / 4, 'y', '')
        ])

    def valueInfo(self):
        return [Value(self.name, type='counter', unit=self.unit)]


class MappedChopperTimebinModes(MappedMoveable):
    """
    A device that applies common chopper speed and timebin configuration pairs.
    """
    attached_devices = {
        'chopper_speed': Attach('Device on where to set chopper speed',
                                EpicsDigitalMoveableNoStop),
        'just_bin_it_image': Attach('JustBinItImage device to manipulate',
                                    JustBinItImage)
    }

    def doInit(self, mode):
        super().doInit(mode)
        # Update value on init
        self.read()

    def doRead(self, maxage=0):
        return self._attached_chopper_speed.read(maxage)

    def doStatus(self, maxage=0):
        return self._attached_chopper_speed.status(maxage)

    def doStart(self, target):
        """
        target :: The target speed to configure
        """
        nbins = self.mapping[target]
        if target == '0':
            tof_max = 480000
        else:
            # tof_max = chopper_period (in rpm) / fpga_clock_cycle period(25ns)
            tof_max = 60 / int(target) // (25 * 10**-9) + 1
        self._attached_just_bin_it_image.num_bins = nbins
        self._attached_just_bin_it_image.tof_range = (1, tof_max)
        self._attached_chopper_speed.move(target)
        # Set value to chopper speed, bins and tof are presented elsewhere
        self.read()
