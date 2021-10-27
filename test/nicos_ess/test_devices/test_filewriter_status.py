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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

import json
from datetime import datetime
from unittest import TestCase, mock

import pytest

pytest.importorskip('file_writer_control')
pytest.importorskip('streaming_data_types')

from nicos.core import MASTER

from nicos_ess.devices.datasinks.file_writer import NOT_CURRENTLY_WRITING

from streaming_data_types import serialise_answ, serialise_wrdn, serialise_x5f2
from streaming_data_types.fbschemas.action_response_answ.ActionOutcome import \
    ActionOutcome
from streaming_data_types.fbschemas.action_response_answ.ActionType import \
    ActionType


session_setup = 'ess_filewriter'


def no_op(*args, **kwargs):
    pass


def create_status_message(job_id, start_time=1, stop_time=9999,
                          update_interval=1000):
    status = {'file_being_written': 'filename', 'job_id': job_id,
              'start_time': start_time, 'state': 'writing',
              'stop_time': stop_time}
    return serialise_x5f2('nicos_tests', 'version', 'service_id', 'hostname',
                          12345, update_interval, json.dumps(status))


def create_stop_request_message(job_id, stop_time=None, success=True):
    stop = stop_time if stop_time else datetime.now()
    outcome = ActionOutcome.Success if success else ActionOutcome.Failure
    return serialise_answ('service_id', job_id, 'command_id',
                          ActionType.SetStopTime, outcome,
                          "message", 0, stop)


def create_stop_confirmed_message(job_id):
    return serialise_wrdn('service_id', job_id, False, 'filename')


def create_start_request_message(job_id, start_time=None, success=True):
    start = start_time if start_time else datetime.now()
    outcome = ActionOutcome.Success if success else ActionOutcome.Failure
    return serialise_answ('service_id', job_id, 'command_id',
                          ActionType.StartJob, outcome,
                          "message", 0, start)


def prepare_filewriter_status(filewriter_status):
    filewriter_status.doPreinit(MASTER)
    # Kill the background thread, so we can control timings ourselves
    filewriter_status._stoprequest = True
    # No-op logging
    filewriter_status.log.error = no_op
    filewriter_status.log.warning = no_op


class TestFileWriterStatus(TestCase):
    def create_patch(self, name):
        patcher = mock.patch(name, spec=True)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def mock_dependencies(self):
        self.consumer = self.create_patch('kafka.KafkaConsumer')
        self.consumer.return_value.topics.return_value = ['TEST_controlTopic',
                                                          'TEST_jobPool']

    def get_status_device(self):
        filewriter_status = self.session.getDevice('FileWriterStatus')
        prepare_filewriter_status(filewriter_status)
        return filewriter_status

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.mock_dependencies()
        self.filewriter_status = self.get_status_device()

    def test_no_messages_after_startup_means_empty_job_list(self):
        assert not self.filewriter_status.jobs

    def test_status_message_received_then_job_added_to_job_list(self):
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1))]

        self.filewriter_status.new_messages_callback(messages)

        assert job_id_1 in self.filewriter_status.jobs

    def test_status_message_received_with_not_writing_placeholder_ignored(self):
        messages = [(123, create_status_message(NOT_CURRENTLY_WRITING))]

        self.filewriter_status.new_messages_callback(messages)

        assert not self.filewriter_status.jobs

    def test_status_messages_received_then_all_jobs_added_to_job_list(self):
        job_id_1 = 'job id 1'
        job_id_2 = 'job id 2'
        job_id_3 = 'job id 3'
        messages = [(123, create_status_message(job_id_1)),
                    (124, create_status_message(job_id_2)),
                    (125, create_status_message(job_id_3))]

        self.filewriter_status.new_messages_callback(messages)

        assert job_id_1 in self.filewriter_status.jobs
        assert job_id_2 in self.filewriter_status.jobs
        assert job_id_3 in self.filewriter_status.jobs

    def test_on_stop_request_message_job_added_to_stop_list(self):
        job_id_1 = 'job id 1'
        status_messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(status_messages)

        stop_request = [(456, create_stop_request_message(job_id_1))]
        self.filewriter_status.new_messages_callback(stop_request)

        assert job_id_1 in self.filewriter_status.marked_for_stop

    def test_on_stop_request_message_correct_job_added_to_stop_list(self):
        job_id_1 = 'job id 1'
        job_id_2 = 'job id 2'
        status_messages = [(123, create_status_message(job_id_1)),
                           (234, create_status_message(job_id_2))]
        self.filewriter_status.new_messages_callback(status_messages)

        stop_request = [(456, create_stop_request_message(job_id_1))]
        self.filewriter_status.new_messages_callback(stop_request)

        assert job_id_1 in self.filewriter_status.marked_for_stop
        assert job_id_2 not in self.filewriter_status.marked_for_stop

    def test_on_stop_confirmed_message_job_removed(self):
        job_id_1 = 'job id 1'
        status_messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(status_messages)
        stop_request = [(456, create_stop_request_message(job_id_1))]
        self.filewriter_status.new_messages_callback(stop_request)

        stop_confirmed = [(789, create_stop_confirmed_message(job_id_1))]
        self.filewriter_status.new_messages_callback(stop_confirmed)

        assert job_id_1 not in self.filewriter_status.marked_for_stop
        assert job_id_1 not in self.filewriter_status.jobs

    def test_on_start_request_message_job_added_to_job_list(self):
        job_id_1 = 'job id 1'

        start_message = [(123, create_start_request_message(job_id_1))]
        self.filewriter_status.new_messages_callback(start_message)

        assert job_id_1 in self.filewriter_status.jobs

    def test_on_start_request_message_error_job_not_added_to_job_list(self):
        job_id_1 = 'job id 1'

        start_message = [(123, create_start_request_message(job_id_1,
                                                            success=False))]
        self.filewriter_status.new_messages_callback(start_message)

        assert job_id_1 not in self.filewriter_status.jobs

    def test_on_stop_request_message_error_job_not_added_to_stop_list(self):
        job_id_1 = 'job id 1'
        status_messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(status_messages)

        stop_request = [(123, create_stop_request_message(job_id_1,
                                                          success=False))]
        self.filewriter_status.new_messages_callback(stop_request)

        assert job_id_1 not in self.filewriter_status.marked_for_stop

    def test_status_message_after_job_stopped_is_ignored(self):
        # There is no guarantee that messages from Kafka are in the order sent
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1)),
                    (125, create_stop_request_message(job_id_1)),
                    (126, create_stop_confirmed_message(job_id_1))
                   ]
        self.filewriter_status.new_messages_callback(messages)

        delayed_status = [(124, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(delayed_status)

        assert job_id_1 not in self.filewriter_status.jobs
        assert job_id_1 not in self.filewriter_status.marked_for_stop

    def test_stopping_message_after_job_stopped_is_ignored(self):
        # There is no guarantee that messages from Kafka are in the order sent
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1)),
                    (126, create_stop_confirmed_message(job_id_1))
                   ]
        self.filewriter_status.new_messages_callback(messages)

        delayed_stop_response = [(124, create_stop_request_message(job_id_1))]
        self.filewriter_status.new_messages_callback(delayed_stop_response)

        assert job_id_1 not in self.filewriter_status.jobs
        assert job_id_1 not in self.filewriter_status.marked_for_stop

    def test_job_considered_lost_when_no_status_messages_for_a_while(self):
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)
        # Hack it so it times out immediately
        old_timeout = self.filewriter_status.timeoutinterval
        self.filewriter_status.timeoutinterval = -10

        self.filewriter_status.no_messages_callback()

        assert job_id_1 not in self.filewriter_status.jobs
        assert job_id_1 not in self.filewriter_status.marked_for_stop

        # Clean up
        self.filewriter_status.timeoutinterval = old_timeout
