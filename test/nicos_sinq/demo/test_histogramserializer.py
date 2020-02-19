#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
Tests for EPICS area detector
"""

from __future__ import absolute_import, division, print_function

import time

import numpy
import pytest

pytest.importorskip('kafka')

from nicos_ess.devices.fbschemas.hs00 import Array, EventHistogram
from nicos_ess.devices.kafka.area_detector import \
    HistogramFlatbuffersDeserializer

from .utils import create_hs00

session_setup = "epics_ad_sim_detector"


class TestHistogramDeserializer(object):
    """
    Test for operation of Flatbuffer hs00 deserializer
    """

    decoder = None

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.log = session.log
        self.decoder = HistogramFlatbuffersDeserializer()

    def test_1d_encoded_buffer(self):
        data = numpy.random.randint(1, high=100, size=[10, ], dtype='uint32')
        ts = 1234
        source = 'test_1d_histo'
        buff = create_hs00(data=data, timestamp=ts, source=source)
        histogram = EventHistogram.EventHistogram.GetRootAsEventHistogram(
            buff, 0)
        assert histogram.Source().decode('utf-8') == source
        assert histogram.Timestamp() == ts
        assert histogram.DataType() == Array.Array.ArrayUInt

    def test_decoder_1d_uint(self):
        data = numpy.random.randint(1, high=100, size=[10, ], dtype='uint32')
        ts = 1234
        src = 'test_1d_histo'
        buff = create_hs00(data=data, timestamp=ts, source=src)
        histogram = self.decoder.decode(buff)
        assert histogram is not None
        value, timestamp, source = histogram
        assert (value == data).all()
        assert timestamp == ts
        assert source == src

    @pytest.mark.skip('Not implemented')
    def test_decoder_1d_ulong(self):
        data = numpy.random.randint(1, high=100, size=[10, ], dtype='uint64')
        ts = 1234
        source = 'test_1d_histo'
        buff = create_hs00(data=data, timestamp=ts, source=source)
        histogram = self.decoder.decode(buff)
        assert histogram is not None
        assert (histogram == data).all()

    @pytest.mark.skip('Not implemented')
    def test_decoder_1d_float(self):
        data = numpy.random.random(size=[10, ])
        ts = 1234
        source = 'test_1d_histo'
        buff = create_hs00(data=data.astype('float32'), timestamp=ts,
                           source=source)
        histogram = self.decoder.decode(buff)
        assert histogram is not None
        assert (histogram == data).all()

    @pytest.mark.skip('Not implemented')
    def test_decoder_1d_double(self):
        data = numpy.random.random(size=[10, ])
        ts = 1234
        src = 'test_1d_histo'
        buff = create_hs00(data=data.astype('float64'), timestamp=ts,
                           source=src)
        histogram = self.decoder.decode(buff)
        assert histogram is not None
        assert (histogram == data).all()

    def test_decoder_2d_uint(self):
        data = numpy.random.randint(1, high=100, size=[10, 10, ],
                                    dtype='uint32')
        ts = 5678
        src = 'test_2d_histo'
        buff = create_hs00(data=data, timestamp=ts, source=src)
        histogram = self.decoder.decode(buff)
        assert histogram is not None
        value, timestamp, source = histogram
        assert (value == data).all()
        assert timestamp == ts
        assert source == src

    def test_decoder_3d_uint(self):
        data = numpy.random.randint(1, high=100, size=[12, 8, 4],
                                    dtype='uint32')
        ts = int(time.time() * 1e9)
        src = 'test_3d_histo'
        buff = create_hs00(data=data, timestamp=ts, source=src)
        histogram = self.decoder.decode(buff)
        assert histogram is not None
        value, timestamp, source = histogram
        assert (value == data).all()
        assert timestamp == ts
        assert source == src
