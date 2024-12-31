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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import numpy as np

from nicos.core import Attach, Param, Value
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel

from nicos_sinq.devices.imagesink import HistogramDesc, HistogramDimDesc
from nicos_sinq.devices.just_bin_it import JustBinItImage


class RotateCutImage(ImageChannelMixin, PassiveChannel):
    """
    A class which first rotates the source image and then cuts
    a ROI out of it. The SANS-LLB histogrammer delivers the three
    detectors combined in one large data array. Thus it is necessary to
    cut the individual detectors out.
    """

    parameters = {
        'x': Param('start x for cutting', type=int),
        'ntubes': Param('Number of tubes to cut', type=int),
    }

    attached_devices = {
        'raw_image': Attach('image to cut data from', devclass=JustBinItImage),
    }

    def doReadArray(self, quality):
        raw_data = self._attached_raw_image.doReadArray(quality)
        if isinstance(raw_data, np.ndarray):
            rot_data = np.rot90(raw_data, k=3)
            # interchanged axis order after rotation
            result = rot_data[self.x:self.x+self.ntubes, 0:]
            self.readresult = [result.sum()]
            return result
        else:
            self.readresult = [0]
            return np.zeros((self._attached_raw_image.det_width, self.ntubes),
                            dtype=int)

    @property
    def arraydesc(self):
        return HistogramDesc(self.name, 'uint32', [
            HistogramDimDesc(self.ntubes, 'tubes', ''),
            HistogramDimDesc(self._attached_raw_image.det_width,
                             'positions', '')
        ])

    def valueInfo(self):
        return Value(self.name, type='counter', unit=self.unit),


class CutImage(ImageChannelMixin, PassiveChannel):
    """
    A class which cuts a  ROI out of another image. The SANS-LLB histogrammer
    delivers the three detectors combined in one large data array. This is
    necessary to cut the individual detectors out.
    """

    parameters = {
        'x': Param('start x for cutting', type=int),
        'ntubes': Param('Number of tubes to cut', type=int),
    }

    attached_devices = {
        'raw_image': Attach('image to cut data from', devclass=JustBinItImage),
    }

    def doReadArray(self, quality):
        raw_data = self._attached_raw_image.doReadArray(quality)
        if isinstance(raw_data, np.ndarray):
            result = raw_data[0:, self.x:self.x+self.ntubes]
            self.readresult = [result.sum()]
            return result
        else:
            self.readresult = [0]
            return np.zeros((self._attached_raw_image.det_width, self.ntubes),
                            dtype=int)

    @property
    def arraydesc(self):
        return HistogramDesc(self.name, 'uint32', [
            HistogramDimDesc(self._attached_raw_image.det_width,
                             'positions', ''),
            HistogramDimDesc(self.ntubes, 'tubes', '')
        ])

    def shape(self):
        return self._attached_raw_image.det_width, self.ntubes

    def valueInfo(self):
        return Value(self.name, type='counter', unit=self.unit),
