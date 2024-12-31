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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

import json
import random
import time
from os import getpid
from socket import gethostname
from string import ascii_lowercase

import pytest

pytest.importorskip('streaming_data_types')
pytest.importorskip('confluent_kafka')

from streaming_data_types.logdata_f142 import serialise_f142
from streaming_data_types.status_x5f2 import serialise_x5f2

from nicos.core import status

from nicos_ess.devices.forwarder import EpicsKafkaForwarder

try:
    from unittest import TestCase, mock
except ImportError:
    pytestmark = pytest.mark.skip('all tests still WIP')

pytest.importorskip('kafka')
pytest.importorskip('graypy')

# Set to None because we load the setup after the mocks are in place.
session_setup = None


def create_stream(
    pv, protocol='ca', topic='TEST_metadata', schema='f142'
):
    return {
        'channel_name': pv,
        "protocol": protocol,
        "output_topic": topic,
        "schema": schema,
    }


def create_x5f2_buffer(streams_json, update_interval=5000):
    streams_message = serialise_x5f2(
        'Forwarder',
        'version',
        'abcd-1234',
        gethostname(),
        getpid(),
        update_interval,
        json.dumps(streams_json),
    )
    return streams_message


def random_string(length):
    letters = ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def create_random_messages(num_messages, num_pvs=10):
    start = int(1000 * time.time())
    pvs = [random_string(4) for _ in range(num_pvs)]
    streams = {'streams': [create_stream(pv) for pv in pvs]}
    times = [start + random.randint(0, 1000) for _ in range(num_messages)]
    return {t: streams for t in times}


def create_issued_from_messages(messages):
    _, message = sorted(messages, key=lambda m: m[0])[~0]
    streams = message.get('streams', [])
    issued = {}
    for stream in streams:
        issued[stream['channel_name']] = (
            stream['output_topic'],
            stream['schema'],
        )
    return issued


def create_f142_buffer(value, source_name='mypv'):
    return serialise_f142(value, source_name)


def create_pv_details_from_messages(messages):
    _, message = sorted(messages, key=lambda m: m[0])[~0]
    streams = message.get('streams', [])
    pv_details = {}
    for stream in streams:
        pv_details[stream['channel_name']] = (
            stream['output_topic'],
            stream['schema'],
        )
    return pv_details


class TestEpicsKafkaForwarderStatus(TestCase):
    def create_patch(self, name):
        patcher = mock.patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.mock = self.create_patch('nicos_ess.devices.kafka.consumer.KafkaConsumer')
        self.mock.return_value.topics.return_value = 'TEST_forwarderStatus'
        self.session.unloadSetup()
        self.session.loadSetup('ess_forwarder', {})
        self.device = self.session.getDevice('KafkaForwarder')
        self.device._setROParam('curstatus', (0, ''))

    def test_update_forwarded_pv(self):
        pvname = 'mypv'
        message_json = {'streams': [create_stream(pvname)]}
        update_interval = 5000
        message_fb = create_x5f2_buffer(message_json, update_interval)
        with mock.patch.object(
            EpicsKafkaForwarder, '_status_update_callback'
        ) as mock_method:
            self.device.new_messages_callback([(123456, message_fb)])
            mock_method.assert_called_once()
            messages = mock_method.call_args[0]

        message_json.update({'update_interval': update_interval})
        assert messages == ({123456: message_json},)

        self.device.new_messages_callback([(12345, message_fb)])
        assert self.device.forwarded == {pvname}

    def test_update_forwarded_many_pvs(self):
        assert self.device.curstatus == (0, '')
        pvnames = {f'mypv{d}' for d in range(10)}
        message_json = {'streams': [create_stream(pv) for pv in pvnames]}
        message_fb = create_x5f2_buffer(message_json)
        self.device.new_messages_callback([(12345, message_fb)])
        self.device.new_messages_callback([(12345, message_fb)])
        assert self.device.forwarded == pvnames

    def test_update_forwarded_pv_sets_forwarding_status(self):
        assert self.device.curstatus == (0, '')
        pvname = 'mypv'
        message_json = {'streams': [create_stream(pvname)]}
        message_fb = create_x5f2_buffer(message_json)
        self.device.new_messages_callback([(12345, message_fb)])
        assert self.device.curstatus == (status.OK, 'Forwarding..')

    def test_update_forwarded_many_pvs_set_forwarding_status(self):
        assert self.device.curstatus == (0, '')
        pvnames = {f'mypv{d}' for d in range(10)}
        message_json = {'streams': [create_stream(pv) for pv in pvnames]}
        message_fb = create_x5f2_buffer(message_json)
        self.device.new_messages_callback([(12345, message_fb)])
        assert self.device.curstatus == (status.OK, 'Forwarding..')

    def test_empty_message_gives_idle_state(self):
        message_json = {'streams': []}
        message_fb = create_x5f2_buffer(message_json)
        self.device.new_messages_callback([(12345, message_fb)])
        assert not self.device.forwarded
        assert self.device.curstatus == (status.OK, 'idle')

    def test_next_update_flatbuffers(self):
        message_json = {'streams': []}
        for update_interval in [1000, 2000]:
            message_fb = create_x5f2_buffer(message_json, update_interval)
            self.device.new_messages_callback([(123456, message_fb)])
            assert self.device.statusinterval == update_interval // 1000
