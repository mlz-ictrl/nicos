# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

import numpy

try:
    from nicos_sinq.devices.fbschemas.hs00 import Array, ArrayUInt, \
        EventHistogram
except ImportError:
    EventHistogram = None
    Array = None
    ArrayUInt = None


class HistogramFlatbuffersDeserializer:
    """
    Decode the histogram using the flatbuffers schema hs00
    """
    file_identifier = "hs00"

    @staticmethod
    def _read_as_numpy(histogram, dtype=ArrayUInt.ArrayUInt):
        result = dtype()
        result.Init(histogram.Data().Bytes, histogram.Data().Pos)
        return result.ValueAsNumpy()

    @staticmethod
    def _read_current_shape(histogram):
        result = ArrayUInt.ArrayUInt()
        result.Init(histogram.CurrentShape().Bytes,
                    histogram.CurrentShape().Pos)
        return result.ValueAsNumpy()

    def decode(self, buff):
        histogram = EventHistogram.EventHistogram().GetRootAsEventHistogram(
            buff, 0)
        data_type = histogram.DataType()
        value = []
        if data_type == Array.Array.ArrayUInt:
            value = self._read_as_numpy(histogram=histogram)
        if data_type == Array.Array.ArrayULong:
            raise NotImplementedError('This data type is not yet implemented.')
            # value = self._read_as_numpy(histogram=histogram,
            # dtype=ArrayULong.ArrayULong)
        if data_type == Array.Array.ArrayFloat:
            raise NotImplementedError('This data type is not yet implemented.')
            # value = self._read_as_numpy(histogram=histogram,
            # dtype=ArrayFloat.ArrayFloat)
        if data_type == Array.Array.ArrayDouble:
            raise NotImplementedError('This data type is not yet implemented.')
            # value = self._read_as_numpy(histogram=histogram,
            # dtype=ArrayDouble.ArrayDouble)

        value = numpy.reshape(value, histogram.CurrentShapeAsNumpy())
        return value, histogram.Timestamp(), histogram.Source().decode()
