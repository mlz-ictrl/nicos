#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
from threading import Event

import pytest

pytest.importorskip('streaming_data_types', minversion='0.16.0')
pytest.importorskip('streaming_data_types.deserialise_hs01',
                    'streaming_data_types.serialise_hs01')
import numpy as np
from streaming_data_types import deserialise_hs01
from streaming_data_types.utils import get_schema

from nicos_sinq.devices.datasinks import ImageForwarderSink, \
    ImageForwarderSinkHandler

session_setup = 'sinq_devices'


class MockImageForwarderSink(ImageForwarderSink):

    def doPreinit(self, mode):
        self._expected_number_of_messages = 1
        self._producer = None
        self._sent = []
        self._append_event = Event()

    def send(self, topic, message, key=None, timestamp=None, partition=None):
        self._sent.append((topic, message))
        if len(self._sent) >= self._expected_number_of_messages:
            self._append_event.set()


class MockImageForwarderSinkHandler(ImageForwarderSinkHandler):
    def __init__(self, sink, dataset, detector):
        # pylint: disable=W0231
        pass


# test that getReadResult puts data into the queue
def test_consume_message_from_empty_queue(session):
    sink = session.getDevice('image_forwarder_sink')
    sink._append_event.wait(timeout=5)
    assert sink._queue.empty()
    assert not sink._sent


# test that getReadResult puts data into the queue
def test_consume_message_from_queue(session):
    sink = session.getDevice('image_forwarder_sink')
    message = 'dummy_data'
    sink._queue.put(message)
    sink._append_event.wait(timeout=5)
    assert sink._queue.empty()

    assert sink._sent
    assert sink._sent[0] == (sink.output_topic, message)


def make_sink_data(detector_name, values):
    return {detector_name: [[], values]}


def test_histogram_is_hs01(session):
    # test the correct serialisation
    sink = session.getDevice('image_forwarder_sink')
    handler = MockImageForwarderSinkHandler(None, None, 'det')
    handler.sink = sink
    data = np.random.randint(1024, size=(128, 128))
    handler.putResults(0, make_sink_data('det', [data]))

    sink._append_event.wait(timeout=5)
    assert sink._queue.empty()

    assert sink._sent
    assert sink._sent[0][0] == sink.output_topic
    assert get_schema(sink._sent[0][1]) == 'hs01'


# test the histogram boundaries metadata
def test_histogram_metadata(session):
    sink = session.getDevice('image_forwarder_sink')
    handler = MockImageForwarderSinkHandler(None, None, 'det')
    handler.sink = sink

    shape = [2 * 128, 128]
    data = np.random.randint(1024, size=shape)
    handler.putResults(0, make_sink_data('det', [data]))

    sink._append_event.wait(timeout=5)
    assert sink._queue.empty()

    histogram = deserialise_hs01(sink._sent[0][1])

    assert np.array_equal(histogram['data'], data)
    assert histogram['current_shape'] == shape
    assert histogram['source'] == 'det'


# test the histogram boundaries metadata
def test_histogram_metadata_with_multiple_arrays(session):
    sink = session.getDevice('image_forwarder_sink')
    sink._expected_number_of_messages = 2
    handler = MockImageForwarderSinkHandler(None, None, 'det')
    handler.sink = sink

    shape0 = [2 * 128, 128]
    shape1 = [2 * 16, 16]
    data0 = np.random.randint(1024, size=shape0)
    data1 = np.random.randint(1024, size=shape1)

    handler.putResults(0, make_sink_data('det', [data0, data1]))

    sink._append_event.wait(timeout=5)

    assert sink._queue.empty()
    assert len(sink._sent) == sink._expected_number_of_messages

    histogram = deserialise_hs01(sink._sent[0][1])
    assert np.array_equal(histogram['data'], data0)
    assert histogram['current_shape'] == shape0
    assert histogram['source'] == 'det_0'

    histogram = deserialise_hs01(sink._sent[1][1])
    assert np.array_equal(histogram['data'], data1)
    assert histogram['current_shape'] == shape1
    assert histogram['source'] == 'det_1'


# test the histogram boundaries metadata
def test_histogram_with_multiple_detectors(session):
    sink = session.getDevice('image_forwarder_sink')
    sink._expected_number_of_messages = 2
    handler0 = MockImageForwarderSinkHandler(None, None, 'det0')
    handler1 = MockImageForwarderSinkHandler(None, None, 'det1')
    handler0.sink = sink
    handler1.sink = sink

    shape0 = [2 * 128, 128]
    shape1 = [2 * 16, 16]
    data0 = np.random.randint(1024, size=shape0)
    data1 = np.random.randint(1024, size=shape1)

    handler0.putResults(0, make_sink_data('det0', [data0]))
    handler1.putResults(0, make_sink_data('det1', [data1]))

    sink._append_event.wait(timeout=5)

    assert sink._queue.empty()
    assert len(sink._sent) == sink._expected_number_of_messages

    histogram = deserialise_hs01(sink._sent[0][1])
    assert np.array_equal(histogram['data'], data0)
    assert histogram['current_shape'] == shape0
    assert histogram['source'] == 'det0'

    histogram = deserialise_hs01(sink._sent[1][1])
    assert np.array_equal(histogram['data'], data1)
    assert histogram['current_shape'] == shape1
    assert histogram['source'] == 'det1'
