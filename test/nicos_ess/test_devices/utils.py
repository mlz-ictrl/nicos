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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""
Utilities for serializing a hs00 flatbuffer
"""

import time
from unittest.mock import patch

import flatbuffers
import numpy

from nicos.core import UsageError

from nicos_ess.devices.datasinks.imagesink.histogramdesc import HistogramDesc, \
    HistogramDimDesc
from nicos_ess.devices.datasinks.imagesink.serializer import \
    HistogramFlatbuffersSerializer
from nicos_ess.devices.fbschemas.hs00 import ArrayDouble, ArrayFloat, \
    ArrayULong

uint32_bytes = flatbuffers.number_types.Float32Flags.bytewidth
float_bytes = flatbuffers.number_types.Float32Flags.bytewidth
double_bytes = flatbuffers.number_types.Float32Flags.bytewidth
ulong_bytes = flatbuffers.number_types.Uint64Flags.bytewidth


class HistogramFlatbuffersSerializerFloat(HistogramFlatbuffersSerializer):
    def _encodeArray(self, builder, array, l_elements):
        # Serialize the data array
        ArrayFloat.ArrayFloatStartValueVector(builder, l_elements)

        if not isinstance(array, bytearray):
            array = bytearray(array.flatten('C').astype('float32'))

        # Directly copy the bytes array
        l_bytes = l_elements * float_bytes  # Number of bytes in hist

        # Recalculate the head position of the buffer
        head = flatbuffers.number_types.UOffsetTFlags.py_type(
            builder.Head() - l_bytes)
        builder.head = head

        # Copy the bytes from histogram bytearray
        builder.Bytes[head:head + l_bytes] = array[0:l_bytes]

        pos_val = builder.EndVector(l_elements)
        ArrayFloat.ArrayFloatStart(builder)
        ArrayFloat.ArrayFloatAddValue(builder, pos_val)
        return ArrayFloat.ArrayFloatEnd(builder)


class HistogramFlatbuffersSerializerDouble(HistogramFlatbuffersSerializer):
    def _encodeArray(self, builder, array, l_elements):
        # Serialize the data array
        ArrayDouble.ArrayDoubleStartValueVector(builder, l_elements)

        if not isinstance(array, bytearray):
            array = bytearray(array.flatten('C').astype('float64'))

        # Directly copy the bytes array
        l_bytes = l_elements * float_bytes  # Number of bytes in hist

        # Recalculate the head position of the buffer
        head = flatbuffers.number_types.UOffsetTFlags.py_type(
            builder.Head() - l_bytes)
        builder.head = head

        # Copy the bytes from histogram bytearray
        builder.Bytes[head:head + l_bytes] = array[0:l_bytes]

        pos_val = builder.EndVector(l_elements)
        ArrayDouble.ArrayDoubleStart(builder)
        ArrayDouble.ArrayDoubleAddValue(builder, pos_val)
        return ArrayDouble.ArrayDoubleEnd(builder)


class HistogramFlatbuffersSerializerULong(HistogramFlatbuffersSerializer):
    def _encodeArray(self, builder, array, l_elements):
        # Serialize the data array
        ArrayULong.ArrayULongStartValueVector(builder, l_elements)

        if not isinstance(array, bytearray):
            array = bytearray(array.flatten('C').astype('uint64'))

        # Directly copy the bytes array
        l_bytes = l_elements * float_bytes  # Number of bytes in hist

        # Recalculate the head position of the buffer
        head = flatbuffers.number_types.UOffsetTFlags.py_type(
            builder.Head() - l_bytes)
        builder.head = head

        # Copy the bytes from histogram bytearray
        builder.Bytes[head:head + l_bytes] = array[0:l_bytes]

        pos_val = builder.EndVector(l_elements)
        ArrayULong.ArrayULongStart(builder)
        ArrayULong.ArrayULongAddValue(builder, pos_val)
        return ArrayULong.ArrayULongEnd(builder)


def create_histogram_dim_desc(dims, labels):
    description = []
    for dim, label in zip(dims, labels):
        description.append(HistogramDimDesc(dim, label))
    return description


def create_histogram_desc(name, dims, labels, dtype=numpy.uint32):
    dims_description = create_histogram_dim_desc(dims=dims, labels=labels)
    return HistogramDesc(name, dtype, dims_description)


def create_hs00(data=None, timestamp=None, source='test_device'):
    dims = list(data.shape)
    ts = timestamp or int(time.time() * 1e9)
    labels = list('xyzwijklm')
    if len(data.shape) > len(labels):
        raise UsageError('Too many dimensions.')
    encoder = None
    if data.dtype.type == numpy.float32:
        encoder = HistogramFlatbuffersSerializerFloat()
    if data.dtype.type == numpy.float64:
        encoder = HistogramFlatbuffersSerializerDouble()
    if data.dtype.type == numpy.uint32:
        encoder = HistogramFlatbuffersSerializer()
    if data.dtype.type == numpy.uint64:
        encoder = HistogramFlatbuffersSerializerULong()

    arraydesc = create_histogram_desc(name='hs00_test', dims=dims,
                                      labels=labels,
                                      dtype=data.dtype.type)
    return encoder.encode(ts, arraydesc, data, source)


def create_patch(obj, name):
    patcher = patch(name)
    thing = patcher.start()
    obj.addCleanup(patcher.stop)
    return thing


def create_method_patch(reason, obj, name, replacement):
    patcher = patch.object(obj, name, replacement)
    thing = patcher.start()
    reason.addCleanup(patcher.stop)
    return thing


def return_value_wrapper(value):
    def return_value(*args, **kwargs):
        return value
    return return_value
