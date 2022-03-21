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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

from pathlib import Path
from unittest import TestCase, mock

import pytest

from test.utils import ErrorLogged

pytest.importorskip('streaming_data_types', minversion='0.16.0')
pytest.importorskip('confluent_kafka')

from nicos.commands.measure import count
from nicos.commands.scan import scan
from nicos.core import SIMULATION

from nicos_ess.devices.datasinks.file_writer import FileWriterController, \
    JobRecord

from nicos_ess.test.test_devices.test_filewriter_status import \
    create_status_message, create_stop_message_with_error, no_op, \
    prepare_filewriter_status

# Set to None because we load the setup after the mocks are in place.
session_setup = None


class TestFileWriterControl(TestCase):
    def create_patch(self, name):
        patcher = mock.patch(name, spec=True)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def mock_dependencies(self):
        self.consumer = self.create_patch('nicos_ess.devices.kafka.consumer.KafkaConsumer')
        self.consumer.return_value.topics.return_value = ['TEST_controlTopic',
                                                          'TEST_jobPool']
        self.mock_controller = mock.create_autospec(FileWriterController)

    def get_filewriter_control_device(self):
        filewriter_control = self.session.getDevice('FileWriterControl')
        filewriter_control.one_file_per_scan = True
        # No-op logging
        filewriter_control.log.error = no_op
        filewriter_control.log.warning = no_op
        # Re-initialise
        filewriter_control.doInit(SIMULATION)
        # Use a mock controller
        filewriter_control._controller = self.mock_controller
        return filewriter_control

    def _add_job(self, job_id, counter):
        job = JobRecord(job_id, counter, 0, 0)
        self.filewriter_status.add_job(job)

    @pytest.fixture(autouse=True)
    def prepare(self, session, log):
        self.session = session
        self.log = log
        self.mock_dependencies()
        self.session.unloadSetup()
        self.session._setup_info = {}
        p = Path(__file__).parent
        while p.match('test_*'):
            p = p.parent
        self.session.setSetupPath(*(self.session.getSetupPath() +
                                    ['%s' % p.joinpath('setups')]))
        self.session.loadSetup('filewriter', {})
        self.session.experiment.propinfo['proposal'] = '123456'
        self.filewriter_control = self.get_filewriter_control_device()
        self.filewriter_status = self.filewriter_control._attached_status
        prepare_filewriter_status(self.filewriter_status)

    def test_cannot_start_job_if_job_in_progress(self):
        job_id_1 = 'job id 1'
        self._add_job(job_id_1, 42)
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        with pytest.raises(Exception):
            self.filewriter_control.start_job()

    def test_can_start_job_if_no_job_in_progress(self):
        job_id = 'job id 1'
        self.mock_controller.request_start.return_value = (job_id, '')

        self.filewriter_control.start_job()

        assert job_id in self.filewriter_status.jobs_in_progress

    def test_can_start_job_if_existing_job_is_stopped(self):
        stopping_job_id = 'job id 1'
        self._add_job(stopping_job_id, 42)
        self.filewriter_status.mark_for_stop(stopping_job_id, stop_time=12345678)
        new_job_id = 'job id 2'
        self.mock_controller.request_start.return_value = (new_job_id, '')

        self.filewriter_control.start_job()

        assert new_job_id in self.filewriter_status.jobs_in_progress

    def test_stop_job_ignored_if_no_job_in_progress(self):
        self.filewriter_control.stop_job()

        self.mock_controller.request_stop.assert_not_called()

    def test_can_stop_running_job(self):
        self.mock_controller.request_start.return_value = ('job id 1', '')
        self.filewriter_control.start_job()

        self.filewriter_control.stop_job()

        self.mock_controller.request_stop.assert_called_once()
        assert self.filewriter_status.jobs_in_progress
        assert self.filewriter_status.marked_for_stop

    def test_stop_job_ignored_if_existing_job_is_already_stopping(self):
        self.mock_controller.request_start.return_value = ('job id 1', '')
        self.filewriter_control.start_job()
        self.filewriter_control.stop_job()

        self.filewriter_control.stop_job()

        self.mock_controller.request_stop.assert_called_once()

    def test_stop_job_ignored_if_job_id_does_not_match(self):
        job_id_1 = 'job id 1'
        job_number = 42
        self._add_job(job_id_1, job_number)
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        self.filewriter_control.stop_job(job_number='does not match')

        self.mock_controller.request_stop.assert_not_called()

    def test_can_stop_job_if_job_id_matches(self):
        job_id_1 = 'job id 1'
        job_number = 42
        self._add_job(job_id_1, job_number)
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        self.filewriter_control.stop_job(job_number=job_number)

        self.mock_controller.request_stop.assert_called_once()

    def test_with_multiple_jobs_no_jobs_stopped_if_job_id_not_supplied(self):
        job_id_1 = 'job id 1'
        job_id_2 = 'job id 2'
        self._add_job(job_id_1, 42)
        self._add_job(job_id_2, 42)
        status_messages = [(123, create_status_message(job_id_1)),
                           (234, create_status_message(job_id_2))]
        self.filewriter_status.new_messages_callback(status_messages)

        self.filewriter_control.stop_job()

        self.mock_controller.request_stop.assert_not_called()

    def test_with_multiple_jobs_specified_job_is_stopped(self):
        job_id_1 = 'job id 1'
        job_number_1 = 42
        job_id_2 = 'job id 2'
        job_number_2 = 43
        self._add_job(job_id_1, job_number_1)
        self._add_job(job_id_2, job_number_2)
        status_messages = [(123, create_status_message(job_id_1)),
                           (234, create_status_message(job_id_2))]
        self.filewriter_status.new_messages_callback(status_messages)

        self.filewriter_control.stop_job(job_number=job_number_1)

        self.mock_controller.request_stop.assert_called_once()
        assert job_id_1 in self.filewriter_status.marked_for_stop
        assert job_id_2 in self.filewriter_status.jobs_in_progress

    def test_one_file_for_all_scan_points(self):
        self.mock_controller.request_start.return_value = ('job id 1', '')
        m = self.session.getDevice('motor')
        det = self.session.getDevice('det')
        scan(m, 0, 1, 5, 0., det, 'test scan')

        self.mock_controller.request_start.assert_called_once()
        self.mock_controller.request_stop.assert_called_once()

    def test_one_file_for_each_scan_point(self):
        self.mock_controller.request_start.return_value = ('job id 1', '')
        self.filewriter_control.one_file_per_scan = False

        m = self.session.getDevice('motor')
        det = self.session.getDevice('det')
        num_points = 5
        scan(m, 0, 1, num_points, 0., det, 'test scan')

        assert self.mock_controller.request_start.call_count == 5
        assert self.mock_controller.request_stop.call_count == 5

    def test_if_manually_started_scan_does_not_send_start_stop_commands(self):
        self.mock_controller.request_start.return_value = ('job id 1', '')
        self.filewriter_control.one_file_per_scan = False
        m = self.session.getDevice('motor')
        det = self.session.getDevice('det')
        self.filewriter_control.start_job()

        scan(m, 0, 1, 5, 0., det, 'test scan')

        self.mock_controller.request_start.assert_called_once()
        self.mock_controller.request_stop.assert_not_called()

    def test_count_starts_and_stops_file(self):
        self.mock_controller.request_start.return_value = ('job id 1', '')
        det = self.session.getDevice('det')
        count(det, t=0.)

        self.mock_controller.request_start.assert_called_once()
        self.mock_controller.request_stop.assert_called_once()

    def test_if_manually_started_count_does_not_send_start_command(self):
        self.mock_controller.request_start.return_value = ('job id 1', '')
        det = self.session.getDevice('det')
        self.filewriter_control.start_job()

        count(det, t=0.)

        self.mock_controller.request_start.assert_called_once()
        self.mock_controller.request_stop.assert_not_called()

    def test_lost_job_still_considered_in_progress(self):
        # Simulate a file-writer crash by forcing the job to time out.
        job_id_1 = 'job id 1'
        self.mock_controller.request_start.return_value = (job_id_1, '')
        self.filewriter_control.start_job()
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)
        old_timeout = self.filewriter_status.timeoutinterval
        self.filewriter_status.timeoutinterval = -10
        self.filewriter_status.no_messages_callback()

        assert job_id_1 in self.filewriter_status.jobs_in_progress

        # Clean up
        self.filewriter_status.timeoutinterval = old_timeout

    def test_can_stop_writing_even_if_job_lost(self):
        # Simulate a file-writer crash by forcing the job to time out.
        job_id_1 = 'job id 1'
        self.mock_controller.request_start.return_value = (job_id_1, '')
        self.filewriter_control.start_job()
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)
        old_timeout = self.filewriter_status.timeoutinterval
        self.filewriter_status.timeoutinterval = -10
        self.filewriter_status.no_messages_callback()

        with self.log.allow_errors():
            self.filewriter_control.stop_job()

        # Clean up
        self.filewriter_status.timeoutinterval = old_timeout

    def test_unacknowledged_start_still_considered_in_progress(self):
        # For example: all file-writers are busy
        job_id_1 = 'job id 1'
        self.mock_controller.request_start.return_value = (job_id_1,
                                                      'not acknowledged')
        self.filewriter_control.start_job()

        assert job_id_1 in self.filewriter_status.jobs_in_progress

    def test_if_kafka_data_topics_not_present_still_considered_in_progress(self):
        # If the topics containing the data do not exist then the file-writer
        # will stop writing almost immediately.
        job_id_1 = 'job id 1'
        self.mock_controller.request_start.return_value = (job_id_1, '')
        self.filewriter_control.start_job()
        # First the file-writer sends a message to say it is writing
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)
        # file-writer sends a message to say it has stopped itself due to error
        messages = [(124, create_stop_message_with_error(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        assert job_id_1 in self.filewriter_status.jobs_in_progress

    def test_if_job_lost_then_on_stopping_logs_error(self):
        job_id_1 = 'job id 1'
        self.mock_controller.request_start.return_value = (job_id_1, 0)
        # Hack it so it times out immediately
        old_timeout = self.filewriter_status.timeoutinterval
        self.filewriter_status.timeoutinterval = -10
        self.filewriter_control.start_job()
        messages = [(123, create_status_message(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)
        self.filewriter_status.no_messages_callback()

        with pytest.raises(ErrorLogged):
            self.filewriter_control.stop_job()

        # Clean up
        self.filewriter_status.timeoutinterval = old_timeout

    def test_if_job_fails_because_invalid_topic_then_on_stopping_logs_error(self):
        job_id_1 = 'job id 1'
        self.mock_controller.request_start.return_value = (job_id_1, 0)
        self.filewriter_control.start_job()
        messages = [(123, create_status_message(job_id_1)),
                    (124, create_stop_message_with_error(job_id_1))]
        self.filewriter_status.new_messages_callback(messages)

        with pytest.raises(ErrorLogged):
            self.filewriter_control.stop_job()
