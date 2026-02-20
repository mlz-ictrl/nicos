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
#   Mark Koennecke <mark.koennecke@psi.ch>
#   Alexis Chennevierre <alexis.chenneviere@cea.fr>
#
# *****************************************************************************
import numpy as np

from nicos.core import Attach, Param, Value
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel

from nicos_sinq.devices.imagesink.histogramdesc import HistogramDesc, \
    HistogramDimDesc


class XSummedImageChannel(ImageChannelMixin, PassiveChannel):
    """
    For SANS-LLB we need to sum detector channels together along the
    first axis in order to get similar resolutions in x and y.
    """
    parameters = {
        'sumstep': Param('numbers of detectors to sum in x',
                         type=int),
    }

    attached_devices = {
        'rawimage': Attach('Raw data where to get data from',
                           ImageChannelMixin),
    }

    def doReadArray(self, quality):
        raw = self._attached_rawimage.readArray(quality)
        result = np.empty((int(raw.shape[0]/self.sumstep), raw.shape[1]),
                          dtype='int32')
        k = 0
        for x in range(0, raw.shape[0], self.sumstep):
            data = np.zeros(raw.shape[1], dtype='int32')
            for i in range(0, self.sumstep):
                data += raw[x+i]
            result[k] = data
            k += 1
        return result

    @property
    def arraydesc(self):
        rawshape = self._attached_rawimage.readArray(0).shape
        return HistogramDesc(self.name, 'uint32', [
            HistogramDimDesc(rawshape[0]/self.sumstep, 'x', ''),
            HistogramDimDesc(rawshape[1], 'y', '')
        ])

    def shape(self):
        rawshape = self._attached_rawimage.readArray(0).shape
        return rawshape[0]/self.sumstep, rawshape[1]

    def valueInfo(self):
        return [Value(self.name, type='counter', unit=self.unit)]


class LLBCalibratedImage(ImageChannelMixin, PassiveChannel):
    """
    This class performs the LLB detector calibration at
    SANS-LLB.
    """

    attached_devices = {
        'rawimage': Attach('Raw data where to get data from',
                           ImageChannelMixin),
    }

    parameters = {
        'calibration_file': Param('calibration file to use',
                                  type=str, mandatory=True),
    }

    _calib = None

    def doInit(self, mode):
        self._calib = np.loadtxt('nicos_sinq/sans-llb/' + self.calibration_file)

    @property
    def arraydesc(self):
        return HistogramDesc(self.name, 'uint32', [
                HistogramDimDesc(128, 'x', ''),
                HistogramDimDesc(128, 'y', '')
        ])

    def shape(self):
        return 128, 128

    def valueInfo(self):
        return [Value(self.name, type='counter', unit=self.unit)]

    def doReadArray(self, quality):
        raw = self._attached_rawimage.readArray(quality)
        raw = raw.reshape(128, 256)

        # Apply calibration
        x = np.arange(256)
        xp = (x - self._calib[:, 1, np.newaxis]) /\
             (self._calib[:, 2, np.newaxis])
        calibMat = np.zeros((128, 256))
        for i in range(128):
            for j in range(256):
                if j <= xp[i, j] < j + 1:
                    calibMat[i, j] += raw[i, j]
                elif j > xp[i, j] > j - 1:
                    calibMat[i, j] += raw[i, j - 1] * (xp[i, j] - (j - 1))
                elif xp[i, j] >= j + 1 > xp[i, j]:
                    calibMat[i, j] += raw[i, j + 1] * (xp[i, j] - (j - 1))
                else:
                    pass

        # Perform the summing in y
        result = np.empty((128, 128),
                          dtype='int32')
        for x in range(0, 128):
            k = 0
            for y in range(0, 256, 2):
                result[x, k] = calibMat[x, y] + calibMat[x, y + 1]
                k += 1
        return result
