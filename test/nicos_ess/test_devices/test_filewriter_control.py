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

from unittest import TestCase, mock

import pytest

pytest.importorskip('streaming_data_types')

from nicos.commands.measure import count
from nicos.commands.scan import scan
from nicos.core import MASTER

from test.nicos_ess.test_devices.test_filewriter_status import \
    create_status_message, create_stop_request_message, no_op, \
    prepare_filewriter_status

session_setup = 'ess_filewriter'


class TestFileWriterControl(TestCase):
    def create_patch(self, name):
        patcher = mock.patch(name, spec=True)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def mock_dependencies(self):
        self.consumer = self.create_patch('kafka.KafkaConsumer')
        self.consumer.return_value.topics.return_value = ['TEST_controlTopic',
                                                          'TEST_jobPool']
        self.job_handler = self.create_patch('file_writer_control.JobHandler')

    def get_filewriter_control_device(self):
        with mock.patch("nicos_ess.devices.datasinks.file_writer.WorkerJobPool.__init__") as pool:
            pool.return_value = None
            filewriter_control = self.session.getDevice('FileWriterControl')
        filewriter_control.one_file_per_scan = True
        # No-op logging
        filewriter_control.log.error = no_op
        filewriter_control.log.warning = no_op
        # Use a mock job handler
        filewriter_control._create_command_channel = lambda: None
        filewriter_control._create_job_handler = lambda x='': self.job_handler
        # Re-initialise
        filewriter_control.doInit(MASTER)
        return filewriter_control

    @pytest.fixture(autouse=True)
    def prepare(self, session):
        self.session = session
        self.mock_dependencies()
        self.filewriter_control = self.get_filewriter_control_device()
        self.filewriter_status = self.filewriter_control._attached_status
        prepare_filewriter_status(self.filewriter_status)

    def test_cannot_start_job_if_job_in_progress(self):
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        with pytest.raises(Exception):
            self.filewriter_control.start_job()

        self.job_handler.start_job.assert_not_called()

    def test_can_start_job_if_no_job_in_progress(self):
        self.filewriter_control.start_job()

        self.job_handler.start_job.assert_called_once()

    def test_can_start_job_if_existing_job_is_stopping(self):
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1)),
                    (125, create_stop_request_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        self.filewriter_control.start_job()

        self.job_handler.start_job.assert_called_once()

    def test_stop_job_ignored_if_no_job_in_progress(self):
        self.filewriter_control.stop_job()

        self.job_handler.stop_now.assert_not_called()

    def test_can_stop_running_job(self):
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        self.filewriter_control.stop_job()

        self.job_handler.set_stop_time.assert_called_once()

    def test_stop_job_ignored_if_existing_job_is_already_stopping(self):
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1)),
                    (125, create_stop_request_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        self.filewriter_control.stop_job()

        self.job_handler.set_stop_time.assert_not_called()

    def test_stop_job_ignored_if_job_id_does_not_match(self):
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        self.filewriter_control.stop_job(job_id='does not match')

        self.job_handler.set_stop_time.assert_not_called()

    def test_can_stop_job_if_job_id_matches(self):
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        self.filewriter_control.stop_job(job_id=job_id_1)

        self.job_handler.set_stop_time.assert_called_once()

    def test_with_multiple_jobs_no_jobs_stopped_if_job_id_not_supplied(self):
        job_id_1 = 'job id 1'
        job_id_2 = 'job id 2'
        status_messages = [(123, create_status_message(job_id_1)),
                           (234, create_status_message(job_id_2))]
        self.filewriter_status.new_messages_callback(status_messages)

        self.filewriter_control.stop_job()

        self.job_handler.set_stop_time.assert_not_called()

    def test_with_multiple_jobs_specified_job_is_stopped(self):
        job_id_1 = 'job id 1'
        job_id_2 = 'job id 2'
        status_messages = [(123, create_status_message(job_id_1)),
                           (234, create_status_message(job_id_2))]
        self.filewriter_status.new_messages_callback(status_messages)

        self.filewriter_control.stop_job(job_id=job_id_1)

        self.job_handler.set_stop_time.assert_called_once()
        assert job_id_1 in self.filewriter_status.marked_for_stop
        assert job_id_2 in self.filewriter_status.jobs

    def test_one_file_for_all_scan_points(self):
        m = self.session.getDevice('motor')
        det = self.session.getDevice('det')
        scan(m, 0, 1, 5, 0., det, 'test scan')

        self.job_handler.start_job.assert_called_once()

    def test_one_file_for_each_scan_point(self):
        self.filewriter_control.one_file_per_scan = False

        m = self.session.getDevice('motor')
        det = self.session.getDevice('det')
        num_points = 5
        scan(m, 0, 1, num_points, 0., det, 'test scan')

        assert self.job_handler.start_job.call_count == 5

    def test_if_manually_started_scan_does_not_send_start_commands(self):
        self.filewriter_control.one_file_per_scan = False
        m = self.session.getDevice('motor')
        det = self.session.getDevice('det')
        self.filewriter_control.start_job()

        scan(m, 0, 1, 5, 0., det, 'test scan')

        self.job_handler.start_job.assert_called_once()

    def test_count_starts_file(self):
        det = self.session.getDevice('det')
        count(det, t=0.)

        self.job_handler.start_job.assert_called_once()

    def test_if_manually_started_count_does_not_send_start_command(self):
        det = self.session.getDevice('det')
        self.filewriter_control.start_job()

        count(det, t=0.)

        self.job_handler.start_job.assert_called_once()

    def test_can_start_writing_after_previous_job_lost(self):
        # Create a lost job
        self.filewriter_control.start_job()
        job_id_1 = 'job id 1'
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)
        old_timeout = self.filewriter_status.timeoutinterval
        self.filewriter_status.timeoutinterval = -10
        self.filewriter_status.no_messages_callback()

        self.filewriter_control.start_job()

        assert self.job_handler.start_job.call_count == 2

        # Clean up
        self.filewriter_status.timeoutinterval = old_timeout
