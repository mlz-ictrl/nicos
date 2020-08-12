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
from os import getpid
from socket import gethostname
from time import time as currenttime

import pytest

pytest.importorskip('streaming_data_types')

from streaming_data_types.logdata_f142 import serialise_f142
from streaming_data_types.status_x5f2 import serialise_x5f2

from nicos.core import BaseDataset

from nicos_ess.devices.datasinks.nexussink import NexusFileWriterStatus

pytest.importorskip('graypy')

try:
    from unittest import mock, TestCase
except ImportError:
    pytestmark = pytest.mark.skip('all tests still WIP')

session_setup = 'ess_filewriter'

start_acknowledge_message = {
    'code': 'START',
    'job_id': '8bacf956-02a3-11e9-af16-64006a47d649',
    'message': 'Start job',
    'service_id': 'kafka-to-nexus--host:SERVERNAME--pid:16055',
    'timestamp': 1551360732952,
    'type': 'filewriter_event',
}

close_message = {
    'code': 'CLOSE',
    'job_id': '8bacf956-02a3-11e9-af16-64006a47d649',
    'message': 'File closed',
    'service_id': 'kafka-to-nexus--host:SERVERNAME--pid:10307',
    'timestamp': 1551344628813,
    'type': 'filewriter_event',
}

error_message = {
    'code': 'ERROR',
    'job_id': '8bacf956-02a3-11e9-af16-64006a47d649',
    'message': 'Configuration Error',
    'service_id': 'kafka-to-nexus--host:SERVERNAME--pid:10307',
    'timestamp': 1551344628813,
    'type': 'filewriter_event',
}

fail_message = {
    "code": "FAIL",
    "job_id": "8bacf956-02a3-11e9-af16-64006a47d649",
    "message": "Unexpected std::exception while handling "
    "command:{\n  "
    '"cmd": "FileWriter_new",\n  "broker": '
    '"127.0.0.1:9092",\n  "job_id": '
    '"8bacf956-02a3-11e9-af16-64006a47d649",'
    '\n  "file_attributes": {\n    "file_name": '
    '"test.nxs"\n '
    ' },\n  "nexus_structure": {\n      '
    '"children": [\n        '
    '  {\n            "type": "group",\n           '
    ' "name": '
    '"my_test_group",\n            "children": [\n '
    "            "
    ' {\n                "type": "stream",\n       '
    "         "
    '"stream": {\n                  "dtype": '
    '"double",'
    '\n                  "writer_module": "f142",'
    "\n            "
    '      "source": "my_test_pv",\n               '
    "   "
    '"topic": "LOQ_sampleEnv"\n                }\n '
    "            "
    ' }\n            ],\n            "attributes": ['
    "\n           "
    '   {\n                "name": "units",\n      '
    "          "
    '"values": "ms"\n              }\n            '
    "]\n          "
    "}\n        ]\n      }\n}\n\nError in "
    "CommandHandler::tryToHandle\n  Failed to "
    "initializeHDF: can "
    "not initialize hdf file /data_files/test.nxs\n    "
    "can not "
    "initialize hdf file "
    "/Users/user/Code/Repos/DMSC/kafka-to-nexus"
    "/cmake-build"
    "-debug/bin/test.nxs\n      The file "
    '"/Users/user/Code/Repos/DMSC/kafka-to'
    "-nexus/cmake"
    '-build-debug/bin/test.nxs" exists already.',
    "service_id": "kafka-to-nexus--host:SERVERNAME--pid:10307",
    "timestamp": 1551344628813,
    "type": "filewriter_event",
}


def create_status_json(message, job_id='1234abcd', code=''):
    return {
        'type': 'filewriter_event',
        'job_id': job_id,
        'code': code,
        'message': message,
    }


def create_x5f2_buffer(status_json, update_interval=5000):
    status_message = serialise_x5f2(
        'Filewriter',
        'version',
        'abcd-1234',
        gethostname(),
        getpid(),
        update_interval,
        json.dumps(status_json),
    )
    return status_message


def create_f142_buffer(value, source_name='mypv'):
    return serialise_f142(value, source_name)


class TestStatus(TestCase):
    def create_patch(self, name):
        patcher = mock.patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.messages_processed = False
        self.mock = self.create_patch('kafka.KafkaConsumer')
        self.mock.return_value.topics.return_value = 'TEST_writerStatus'
        self.session = session
        self.device = self.session.getDevice('KafkaFileWriter')
        self.device._started = []

    def test_process_not_running_if_no_message_within_timeout_interval(self):
        expected_update = currenttime() + self.device.timeoutinterval
        self.device._setROParam('nextupdate', expected_update - 10)
        assert not self.device.is_process_running()

    def test_process_is_running_if_message_is_within_timeout_interval(self):
        expected_update = currenttime() + self.device.timeoutinterval
        self.device._setROParam('nextupdate', expected_update + 10)
        assert self.device.is_process_running()

    def test_json_status_is_processed(self):
        message_json = {'a': 1}
        with mock.patch.object(
            NexusFileWriterStatus, '_status_update_callback'
        ) as mock_method:
            self.device.new_messages_callback(
                {12345: json.dumps(message_json)}
            )
            mock_method.assert_called_once()
            messages = mock_method.call_args[0]
            assert messages == ({12345: message_json},)

    def test_x5f2_status_is_processed(self):
        message_json = {'a': 1}
        update_interval = 1111
        message_fb = create_x5f2_buffer(
            message_json, update_interval=update_interval
        )
        with mock.patch.object(
            NexusFileWriterStatus, '_status_update_callback'
        ) as mock_method:
            self.device.new_messages_callback({12345: message_fb})
            mock_method.assert_called_once()
            messages = mock_method.call_args[0]
            # warning: during processing the `update_interval` is added to
            # the JSON content
            message_json.update({'update_interval': update_interval})
            assert messages == ({12345: message_json},)

    def test_not_x5f2_status_is_not_processed(self):
        message_fb = create_f142_buffer(123.4)
        with mock.patch.object(
            NexusFileWriterStatus, '_status_update_callback'
        ) as mock_method:
            self.device.new_messages_callback({12345: message_fb})
            assert mock_method.call_args is None

    @pytest.mark.skip(
        reason='functionality removed from filewriter, will be '
        'restored in the future'
    )
    def test_json_start_message(self):
        jobid = '1234-abcd'
        message_json = dict(start_acknowledge_message)
        message_json['job_id'] = jobid

        with mock.patch.object(
            NexusFileWriterStatus, '_on_start'
        ) as mock_method:
            self.device._tracked_datasets[jobid] = BaseDataset()
            self.device.new_messages_callback(
                {12345: json.dumps(message_json)}
            )
            mock_method.assert_called_once()

        self.device.new_messages_callback({12345: json.dumps(message_json)})
        assert len(self.device._started) == 1 and jobid in self.device._started

    @pytest.mark.skip(
        reason='functionality removed from filewriter, will be '
        'restored in the future'
    )
    def test_flatbuffer_start_message(self):
        jobid = '1235-abcd'
        message_json = dict(start_acknowledge_message)
        message_json['job_id'] = jobid
        message_serialised = create_x5f2_buffer(message_json)

        with mock.patch.object(
            NexusFileWriterStatus, '_on_start'
        ) as mock_method:
            self.device._tracked_datasets[jobid] = BaseDataset()
            self.device.new_messages_callback({12345: message_serialised})
            mock_method.assert_called_once()

        self.device.new_messages_callback({12345: message_serialised})
        assert len(self.device._started) == 1 and jobid in self.device._started

    @pytest.mark.skip(
        reason='functionality removed from filewriter, will be '
        'restored in the future'
    )
    def test_json_close_message(self):
        jobid = '1234-abcd'
        message_json = dict(close_message)
        message_json['job_id'] = jobid

        with mock.patch.object(
            NexusFileWriterStatus, '_on_close'
        ) as mock_method:
            self.device._tracked_datasets[jobid] = BaseDataset()
            self.device.new_messages_callback(
                {12345: json.dumps(message_json)}
            )
            mock_method.assert_called_once()

        self.device._tracked_datasets[jobid] = BaseDataset()
        self.device._started = [jobid]
        self.device.new_messages_callback({12345: json.dumps(message_json)})
        assert jobid not in self.device._started
        assert jobid not in self.device._tracked_datasets
