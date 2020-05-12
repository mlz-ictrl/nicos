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
from operator import itemgetter
from string import ascii_lowercase

import pytest

pytest.importorskip('kafka')

from nicos.core import status
from nicos.pycompat import from_utf8

from nicos_ess.devices.forwarder import EpicsKafkaForwarder as DefaultEpicsKafkaForwarder, \
    EpicsKafkaForwarderControl as DefaultEpicsKafkaForwarderControl

try:
    from unittest import mock
except ImportError:
    import mock

session_setup = 'ess_forwarder'


class EpicsKafkaForwarderControl(DefaultEpicsKafkaForwarderControl):
    def doPreinit(self, mode):
        self._producer = mock.Mock()

    def doShutdown(self):
        pass


class EpicsKafkaForwarder(DefaultEpicsKafkaForwarder):
    def doPreinit(self, mode):
        self._producer = mock.Mock()

    def doShutdown(self):
        pass


def create_stream(pv, broker='localhost:9092', topic='TEST_metadata',
                  schema='f142'):
    return {'channel_name': pv, 'converters': [{'broker': broker,
                                                'topic': topic,
                                                'schema': schema}]}


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
    streams = messages[sorted(list(messages.keys()))[-1]]['streams']
    issued = {}
    for stream in streams:
        converter = stream['converters'][0]
        issued[stream['channel_name']] = converter['topic'], converter[
            'schema']
    return issued


def create_pv_details_from_messages(messages):
    streams = messages[sorted(list(messages.keys()))[-1]]['streams']
    pv_details = {}
    for stream in streams:
        converter = stream['converters'][0]
        pv_details[stream['channel_name']] = (converter['topic'],
                                              converter['schema'])
    return pv_details


def create_command_from_messages(messages):
    streams = messages[sorted(list(messages.keys()))[-1]]['streams']
    command = {'cmd': 'add', 'streams': []}

    def get_stream_entry(ch, conv):
        return {"converter":
                    {"topic": "%s/%s" % (conv['broker'], conv['topic']),
                     "schema": conv['schema']},
                "channel_provider_type": "ca", "channel": ch}

    for stream in streams:
        converter = stream['converters'][0]
        channel = stream['channel_name']
        command['streams'].append(get_stream_entry(channel, converter))
    return command


class TestEpicsKafkaForwarderMonitor(object):

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.monitor = self.session.getDevice('KafkaForwarder')

    @pytest.fixture(autouse=True)
    def finalize(self, request):
        def fin():
            self.monitor.curstatus = (0, '')
            self.monitor._forwarded = {}

        request.addfinalizer(fin)

    def set_and_test_status(self, value):
        curstatus = self.monitor.curstatus = value
        self.monitor._status_update_callback({})
        assert self.monitor.curstatus == curstatus

    def test_status_update_callback_doesn_t_change_if_no_messages(self):
        original = self.monitor.curstatus
        for st in [original,
                   (status.OK, 'Forwarding..'),
                   (status.ERROR, 'None forwarded!'),
                   (status.WARN, 'Not forwarded: %d/%d' % (1, 10))]:
            self.set_and_test_status(st)
            self.monitor.curstatus = original

    def test_update_forwarded_pvs(self):
        messages = create_random_messages(10)
        self.monitor._status_update_callback(messages)
        assert self.monitor.forwarded == set(create_issued_from_messages(
            messages).keys())

    def test_update_forwarded_pvs_set_forwarding_status(self):
        assert self.monitor.curstatus == (0, '')
        messages = create_random_messages(10)
        self.monitor._status_update_callback(messages)
        assert self.monitor.curstatus == (status.OK, 'Forwarding..')

    def test_inactive_methods_don_t_fail(self):
        try:
            assert not self.monitor.pv_forwarding_info(None)
            assert not self.monitor.pvs_not_forwarding()
            self.monitor.add(None)
            self.monitor.reissue()
            assert True
        except Exception as e:
            assert False, str(e)

    def test_empty_message_gives_idle_state(self):
        messages = {0: {"service_id": "", "streams": []}}
        self.monitor._status_update_callback(messages)

        assert not self.monitor.forwarded
        assert self.monitor.curstatus == (status.OK, 'idle')


class TestEpicsKafkaForwarderControl(object):

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.device = self.session.getDevice('KafkaForwarderCommand')

    @pytest.fixture(autouse=True)
    def finalize(self, request):
        def fin():
            self.device._issued = {}
            self.device._notforwarding = {}
            self.device.doStatus()

        request.addfinalizer(fin)

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
        message = list(create_random_messages(1).values())[0]

        self.device.status_update(message)
        assert not self.device._notforwarding
        assert not self.device._issued
        assert self.device.doStatus() == (status.OK, 'None issued')

    def test_status_message_all_forwarded_gives_forwarding(self):
        messages = create_random_messages(1)

        self.device._issued = create_issued_from_messages(messages)
        self.device.status_update(list(messages.values())[0])

        assert not self.device._notforwarding
        assert self.device._issued
        assert self.device.doStatus() == (status.OK, 'Forwarding..')

    def test_status_message_some_not_forwarded_gives_warning(self):
        extra_key = '1234'
        messages = create_random_messages(1)

        self.device._issued = create_issued_from_messages(messages)
        self.device._issued[extra_key] = list(self.device._issued.keys())[-1]
        self.device.status_update(list(messages.values())[0])

        assert self.device._notforwarding == {extra_key}
        message = 'Not forwarded: %d/%d' % (1, len(self.device._issued))
        assert self.device.doStatus() == (status.WARN, message)

    def test_add_pvs(self):
        messages = create_random_messages(1, num_pvs=5)
        pv_details = create_pv_details_from_messages(messages)
        expected_command = create_command_from_messages(messages)

        with mock.patch.object(EpicsKafkaForwarderControl,
                               'send') as mock_send:
            self.device.add(pv_details)

        call_topic, call_command = mock_send.call_args[0]
        assert call_topic == self.device.cmdtopic

        if isinstance(call_command, bytes):
            call_command = json.loads(from_utf8(call_command))
        if isinstance(call_command, str):
            call_command = json.loads(call_command)
        call_entries = sorted(call_command['streams'],
                              key=itemgetter('channel'))
        expected_entries = sorted(expected_command['streams'],
                                  key=itemgetter('channel'))
        assert call_entries == expected_entries
        assert self.device._issued == pv_details

    def test_reissue(self):
        messages = create_random_messages(1, num_pvs=5)
        self.device._issued = create_issued_from_messages(messages)
        pv_details = create_pv_details_from_messages(messages)
        expected_command = create_command_from_messages(messages)

        with mock.patch.object(EpicsKafkaForwarderControl,
                               'send') as mock_send:
            self.device.reissue()

        call_topic, call_command = mock_send.call_args[0]

        assert call_topic == self.device.cmdtopic

        if isinstance(call_command, bytes):
            call_command = json.loads(from_utf8(call_command))
        if isinstance(call_command, str):
            call_command = json.loads(call_command)
        call_entries = sorted(call_command['streams'],
                              key=itemgetter('channel'))
        expected_entries = sorted(expected_command['streams'],
                                  key=itemgetter('channel'))
        assert call_entries == expected_entries
        assert self.device._issued == pv_details


class TestEpicsForwarderMonitorAndControlIntegration(object):

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.monitor = self.session.getDevice('KafkaForwarderIntegration')
        self.control = self.session.getDevice('KafkaForwarderCommand')

    @pytest.fixture(autouse=True)
    def finalize(self, request):
        def fin():
            self.monitor.curstatus = (0, '')
            self.monitor._forwarded = {}
            self.control._issued = {}
            self.control._notforwarding = {}
            self.control.doStatus()

        request.addfinalizer(fin)

    def test_empty_status_update_nothrows_if_no_issued(self):
        try:
            self.monitor._status_update_callback(dict())
            assert True
        except Exception as e:
            assert False, str(e)

    def test_empty_status_update_throws_if_issued(self):
        self.control._issued = {'pv': ()}
        try:
            self.monitor._status_update_callback(dict())
            assert True
        except Exception as e:
            assert False, str(e)

    def test_status_message_on_empty_issued_gives_none_issued(self):
        messages = create_random_messages(10, num_pvs=5)
        self.monitor._status_update_callback(messages)

        assert not self.control._notforwarding
        assert not self.control._issued
        assert self.control.doStatus() == (status.OK, 'None issued')
        assert self.monitor.curstatus == (status.OK, 'None issued')

    def test_status_message_all_forwarded_gives_forwarding(self):
        messages = create_random_messages(10, num_pvs=5)

        self.control._issued = create_issued_from_messages(messages)
        self.monitor._status_update_callback(messages)

        assert not self.control._notforwarding
        assert self.control._issued
        assert self.control.doStatus() == (status.OK, 'Forwarding..')
        assert self.monitor.curstatus == (status.OK, 'Forwarding..')

    def test_status_message_some_not_forwarded_gives_warning(self):
        extra_key = '1234'
        messages = create_random_messages(10, num_pvs=5)

        self.control._issued = create_issued_from_messages(messages)
        self.control._issued[extra_key] = list(self.control._issued.keys())[-1]
        self.monitor._status_update_callback(messages)

        assert self.control._notforwarding == {extra_key}
        message = 'Not forwarded: %d/%d' % (1, len(self.control._issued))
        assert self.control.doStatus() == (status.WARN, message)
        assert self.monitor.curstatus == (status.WARN, message)

    def test_add_pvs(self):
        messages = create_random_messages(10, num_pvs=5)
        pv_details = create_pv_details_from_messages(messages)
        expected_command = create_command_from_messages(messages)

        with mock.patch.object(EpicsKafkaForwarderControl,
                               'send') as mock_send:
            self.monitor.add(pv_details)

        call_topic, call_command = mock_send.call_args[0]
        assert call_topic == self.control.cmdtopic

        if isinstance(call_command, bytes):
            call_command = json.loads(from_utf8(call_command))
        if isinstance(call_command, str):
            call_command = json.loads(call_command)

        call_entries = sorted(call_command['streams'],
                              key=itemgetter('channel'))
        expected_entries = sorted(expected_command['streams'],
                                  key=itemgetter('channel'))
        assert call_entries == expected_entries
        assert self.control._issued == pv_details

    def test_reissue(self):
        messages = create_random_messages(10, num_pvs=5)
        self.control._issued = create_issued_from_messages(messages)
        pv_details = create_pv_details_from_messages(messages)
        expected_command = create_command_from_messages(messages)

        with mock.patch.object(EpicsKafkaForwarderControl,
                               'send') as mock_send:
            self.control.reissue()

        call_topic, call_command = mock_send.call_args[0]

        assert call_topic == self.control.cmdtopic

        if isinstance(call_command, bytes):
            call_command = json.loads(from_utf8(call_command))
        if isinstance(call_command, str):
            call_command = json.loads(call_command)

        call_entries = sorted(call_command['streams'],
                              key=itemgetter('channel'))
        expected_entries = sorted(expected_command['streams'],
                                  key=itemgetter('channel'))
        assert call_entries == expected_entries
        assert self.control._issued == pv_details
