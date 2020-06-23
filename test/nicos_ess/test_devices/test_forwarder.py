# -*- coding: utf-8 -*-
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

from __future__ import absolute_import, division, print_function

import json
import random
import time
from os import getpid
from socket import gethostname
from string import ascii_lowercase

import pytest

pytest.importorskip('streaming_data_types')

from streaming_data_types.forwarder_config_update_rf5k import UpdateType, \
    deserialise_rf5k
from streaming_data_types.logdata_f142 import serialise_f142
from streaming_data_types.status_x5f2 import serialise_x5f2

from nicos.core import status

from nicos_ess.devices.forwarder import EpicsKafkaForwarder, \
    EpicsKafkaForwarderControl

try:
    from unittest import mock, TestCase
except ImportError:
    pytestmark = pytest.mark.skip('all tests still WIP')

pytest.importorskip('kafka')
pytest.importorskip('graypy')

session_setup = 'ess_forwarder'


def create_stream(
    pv, broker='localhost:9092', topic='TEST_metadata', schema='f142'
):
    return {
        'channel_name': pv,
        'converters': [{'broker': broker, 'topic': topic, 'schema': schema}],
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
    streams = messages[sorted(list(messages.keys()))[-1]].get('streams', [])
    issued = {}
    for stream in streams:
        converter = stream['converters'][0]
        issued[stream['channel_name']] = (
            converter['topic'],
            converter['schema'],
        )
    return issued


def create_f142_buffer(value, source_name='mypv'):
    return serialise_f142(value, source_name)


def create_pv_details_from_messages(messages):
    streams = messages[sorted(list(messages.keys()))[-1]].get('streams', [])
    pv_details = {}
    for stream in streams:
        converter = stream['converters'][0]
        pv_details[stream['channel_name']] = (
            converter['topic'],
            converter['schema'],
        )
    return pv_details


def create_command_from_messages(messages):
    streams = messages[sorted(list(messages.keys()))[-1]].get('streams', [])
    command = {'cmd': 'add', 'streams': []}

    def get_stream_entry(ch, conv):
        return {
            'converter': {
                'topic': f'{conv["broker"]}/{conv["topic"]}',
                'schema': conv['schema'],
            },
            'channel_provider_type': 'ca',
            'channel': ch,
        }

    for stream in streams:
        converter = stream['converters'][0]
        channel = stream['channel_name']
        command['streams'].append(get_stream_entry(channel, converter))
    return command


class TestEpicsKafkaForwarderStatus(TestCase):
    def create_patch(self, name):
        patcher = mock.patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.mock = self.create_patch('kafka.KafkaConsumer')
        self.mock.return_value.topics.return_value = 'TEST_forwarderStatus'
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
            self.device.new_messages_callback({123456: message_fb})
            mock_method.assert_called_once()
            messages = mock_method.call_args[0]

        message_json.update({'update_interval': update_interval})
        assert messages == ({123456: message_json},)

        self.device.new_messages_callback({12345: message_fb})
        assert self.device.forwarded == {pvname}

    def test_update_forwarded_many_pvs(self):
        assert self.device.curstatus == (0, '')
        pvnames = {f'mypv{d}' for d in range(10)}
        message_json = {'streams': [create_stream(pv) for pv in pvnames]}
        message_fb = create_x5f2_buffer(message_json)
        self.device.new_messages_callback({12345: message_fb})
        self.device.new_messages_callback({12345: message_fb})
        assert self.device.forwarded == pvnames

    def test_update_forwarded_pv_sets_forwarding_status(self):
        assert self.device.curstatus == (0, '')
        pvname = 'mypv'
        message_json = {'streams': [create_stream(pvname)]}
        message_fb = create_x5f2_buffer(message_json)
        self.device.new_messages_callback({12345: message_fb})
        assert self.device.curstatus == (status.OK, 'Forwarding..')

    def test_update_forwarded_many_pvs_set_forwarding_status(self):
        assert self.device.curstatus == (0, '')
        pvnames = {f'mypv{d}' for d in range(10)}
        message_json = {'streams': [create_stream(pv) for pv in pvnames]}
        message_fb = create_x5f2_buffer(message_json)
        self.device.new_messages_callback({12345: message_fb})
        assert self.device.curstatus == (status.OK, 'Forwarding..')

    def test_update_forwarded_many_pvs_set_forwarding_status_json(self):
        assert self.device.curstatus == (0, '')
        pvnames = {f'mypv{d}' for d in range(10)}
        message_json = {'streams': [create_stream(pv) for pv in pvnames]}
        self.device.new_messages_callback({12345: json.dumps(message_json)})
        assert self.device.curstatus == (status.OK, 'Forwarding..')

    def test_empty_message_gives_idle_state(self):
        message_json = {'streams': []}
        message_fb = create_x5f2_buffer(message_json)
        self.device.new_messages_callback({12345: message_fb})
        assert not self.device.forwarded
        assert self.device.curstatus == (status.OK, 'idle')

    def test_inactive_methods_don_t_fail(self):
        try:
            assert not self.device.pv_forwarding_info(None)
            assert not self.device.pvs_not_forwarding()
            self.device.add(None)
            self.device.reissue()
            assert True
        except Exception as e:
            assert False, str(e)

    def test_next_update_flatbuffers(self):
        message_json = {'streams': []}
        for update_interval in [1000, 2000]:
            message_fb = create_x5f2_buffer(message_json, update_interval)
            self.device.new_messages_callback({123456: message_fb})
            assert self.device.statusinterval == update_interval // 1000

    def test_next_update_json(self):
        message_json = {'streams': []}
        for update_interval in [1000, 2000]:
            message_json['update_interval'] = update_interval
            self.device.new_messages_callback(
                {123456: json.dumps(message_json)}
            )
            assert self.device.statusinterval == update_interval // 1000


class TestEpicsKafkaForwarderControl(TestCase):
    def create_patch(self, name):
        patcher = mock.patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.mock = self.create_patch('kafka.KafkaProducer')
        self.mock.return_value.topics.return_value = [
            'TEST_forwarderStatus',
            'TEST_forwarderCommands',
            'TEST_metadata',
        ]
        self.device = self.session.getDevice('KafkaForwarderCommand')
        self.device._issued = {}
        self.device._notforwarding = {}

    def test_initial_status(self):
        assert self.device.doStatus() == (status.OK, 'None issued')

    def test_empty_status_update_nothrows_if_no_issued(self):
        try:
            self.device.status_update(dict())
            assert True
        except Exception as e:
            assert False, str(e)

    def test_empty_status_update_throws_if_issued(self):
        self.device._issued = {'pv': ()}
        with pytest.raises(KeyError):
            assert self.device.status_update(dict())

    def test_status_message_on_empty_issued_gives_none_issued(self):
        message = {'streams': [create_stream('pv')]}
        self.device.status_update(message)
        assert not self.device._notforwarding
        assert not self.device._issued
        assert self.device.doStatus() == (status.OK, 'None issued')

    def test_status_message_all_forwarded_gives_forwarding(self):
        pvnames = {f'mypv{i}' for i in range(10)}
        message = {'streams': [create_stream(pv) for pv in pvnames]}
        self.device._issued = create_issued_from_messages({12345: message})
        self.device.status_update(message)

        assert not self.device._notforwarding
        assert self.device._issued
        assert self.device.doStatus() == (status.OK, 'Forwarding..')

    def test_status_message_some_not_forwarded_gives_warning(self):
        extra_key = '1234'
        pvnames = {f'mypv{i}' for i in range(10)}
        message = {'streams': [create_stream(pv) for pv in pvnames]}
        self.device._issued = create_issued_from_messages({12345: message})
        self.device._issued[extra_key] = list(self.device._issued.keys())[-1]
        self.device.status_update(message)

        assert self.device._notforwarding == {extra_key}
        message = f'Not forwarded: 1/{len(self.device._issued)}'
        assert self.device.doStatus() == (status.WARN, message)

    def test_add_pvs(self):
        pvnames = {f'mypv{i}' for i in range(10)}
        message = {'streams': [create_stream(pv) for pv in pvnames]}
        pv_details = create_pv_details_from_messages({1236: message})

        with mock.patch.object(
            EpicsKafkaForwarderControl, 'send'
        ) as mock_send:
            self.device.add(pv_details)
            call_topic, call_command = mock_send.call_args[0]
            assert call_topic == self.device.cmdtopic

        entry = deserialise_rf5k(call_command)
        assert entry.config_change == UpdateType.UpdateType.ADD
        topics = set()
        for stream in entry.streams:
            assert stream.schema == 'f142'
            assert stream.topic == 'TEST_metadata'
            topics.add(stream.channel)
        assert topics == set(pv_details.keys())

    def test_reissue(self):
        pvnames = {f'mypv{i}' for i in range(10)}
        message = {'streams': [create_stream(pv) for pv in pvnames]}
        pv_details = create_pv_details_from_messages({1236: message})
        self.device.add(pv_details)

        with mock.patch.object(
            EpicsKafkaForwarderControl, 'send'
        ) as mock_send:
            self.device.reissue()
            mock_send.assert_called_once()

        assert self.device._issued == pv_details


class TestEpicsForwarderStatusAndControl(TestCase):
    def create_patch(self, name):
        patcher = mock.patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.mock_consumer = self.create_patch('kafka.KafkaConsumer')
        self.mock_producer = self.create_patch('kafka.KafkaProducer')
        self.mock_consumer.return_value.topics.return_value = (
            'TEST_forwarderStatus'
        )
        self.mock_producer.return_value.topics.return_value = [
            'TEST_forwarderCommands',
            'TEST_metadata',
        ]
        self.device = self.session.getDevice('KafkaForwarderIntegration')
        self.control = self.session.getDevice('KafkaForwarderCommand')
        self.device.curstatus = (0, '')
        self.device._forwarded = {}
        self.control._issued = {}
        self.control._notforwarding = {}

    def test_empty_messages_are_ignored(self):
        message_json = {'streams': [create_stream('pv')]}
        create_pv_details_from_messages({1234: message_json})
        self.device._issued = create_pv_details_from_messages(
            {1234: message_json}
        )
        with mock.patch.object(
            EpicsKafkaForwarder, '_status_update_callback'
        ) as mock_method:
            self.device.new_messages_callback({})
            assert not mock_method.called, 'method should not have been called'

    def test_status_message_on_empty_issued_gives_none_issued(self):
        pvs = {f'pv{i}' for i in range(5)}
        message_json = {'streams': [create_stream(pv) for pv in pvs]}
        message_fb = create_x5f2_buffer(message_json)
        self.device.new_messages_callback({12346: message_fb})

        assert not self.control._notforwarding
        assert not self.control._issued
        assert self.control.doStatus() == (status.OK, 'None issued')

    def test_status_message_all_forwarded_gives_forwarding(self):
        pvs = {f'pv{i}' for i in range(5)}
        message_json = {'streams': [create_stream(pv) for pv in pvs]}
        message_fb = create_x5f2_buffer(message_json)

        self.control._issued = create_issued_from_messages(
            {12346: message_json}
        )
        self.device.new_messages_callback({12346: message_fb})

        assert not self.control._notforwarding
        assert self.control._issued
        assert self.control.doStatus() == (status.OK, 'Forwarding..')

    def test_status_message_some_not_forwarded_gives_warning(self):
        pvs = {f'pv{i}' for i in range(5)}
        message_json = {'streams': [create_stream(pv) for pv in pvs]}
        message_fb = create_x5f2_buffer(message_json)
        extra_pv = {
            'new_pv': ('TEST_metadata', 'f142'),
        }

        self.control._issued = create_issued_from_messages(
            {12346: message_json}
        )
        self.device.new_messages_callback({12346: message_fb})
        self.control._issued.update(extra_pv)
        self.control.status_update(message_json)
        assert self.control._notforwarding == set(extra_pv)
        message = f'Not forwarded: {1}/{len(self.control._issued)}'
        assert self.control.doStatus() == (status.WARN, message)

    def test_add_pvs(self):
        pvs = {f'pv{i}' for i in range(5)}
        message_json = {'streams': [create_stream(pv) for pv in pvs]}
        pv_details = create_pv_details_from_messages({1234: message_json})

        with mock.patch.object(
            EpicsKafkaForwarderControl, 'send'
        ) as mock_send:
            self.device.add(pv_details)
            call_topic, call_command = mock_send.call_args[0]

        assert call_topic == self.control.cmdtopic

        entry = deserialise_rf5k(call_command)
        assert entry.config_change == UpdateType.UpdateType.ADD
        topics = set()
        for stream in entry.streams:
            assert stream.schema == 'f142'
            assert stream.topic == 'TEST_metadata'
            topics.add(stream.channel)
        assert topics == set(pv_details.keys())
        assert self.control._issued == pv_details

    def test_reissue(self):
        pvs = {f'pv{i}' for i in range(5)}
        message_json = {'streams': [create_stream(pv) for pv in pvs]}

        pv_details = create_pv_details_from_messages({1234: message_json})
        self.control._issued = create_issued_from_messages(
            {1234: message_json}
        )

        with mock.patch.object(
            EpicsKafkaForwarderControl, 'send'
        ) as mock_send:
            self.control.reissue()
            call_topic, call_command = mock_send.call_args[0]

        assert call_topic == self.control.cmdtopic
        entry = deserialise_rf5k(call_command)
        assert entry.config_change == UpdateType.UpdateType.ADD
        topics = set()
        for stream in entry.streams:
            assert stream.schema == 'f142'
            assert stream.topic == 'TEST_metadata'
            topics.add(stream.channel)
        assert topics == set(pv_details.keys())
