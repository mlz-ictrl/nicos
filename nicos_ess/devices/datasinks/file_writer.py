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
#   AÜC Hardal <umit.hardal@ess.eu>
#   Ebad Kamil <Ebad.Kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#   Kenan Muric <kenan.muric@ess.eu>
#
# *****************************************************************************
import copy
import json
import threading
import time
from datetime import datetime
from time import time as currenttime

from file_writer_control import JobHandler, WorkerJobPool, WriteJob
from streaming_data_types import deserialise_answ, deserialise_wrdn, \
    deserialise_x5f2
from streaming_data_types.fbschemas.action_response_answ.ActionOutcome import \
    ActionOutcome
from streaming_data_types.fbschemas.action_response_answ.ActionType import \
    ActionType

from nicos import session
from nicos.core import MASTER, Attach, CommunicationError, Device, \
    NicosError, Param, ScanDataset, host, listof, status, usermethod
from nicos.core.constants import INTERRUPTED, POINT
from nicos.core.data.sink import DataSinkHandler
from nicos.core.params import Override, relative_path
from nicos.devices.datasinks.file import FileSink

from nicos_ess.devices.kafka.status_handler import KafkaStatusHandler
from nicos_ess.nexus.converter import NexusTemplateConverter

NOT_CURRENTLY_WRITING = 'not_currently_writing'


class NexusStructureProvider(Device):
    def get_structure(self, dataset, start_time):
        raise NotImplementedError('must implement get_structure method')


class NexusStructureJsonFile(NexusStructureProvider):
    parameters = {
        'nexus_config_path': Param('NeXus configuration filepath',
            type=relative_path, mandatory=True, userparam=True, settable=True),
    }

    def get_structure(self, dataset, start_time):
        with open(self.nexus_config_path, 'r') as file:
            return file.read()


class NexusStructureTemplate(NexusStructureProvider):
    parameters = {
        'templatesmodule': Param(
            'Python module containing NeXus nexus_templates',
            type=str, mandatory=True),
        'templatename': Param('Template name from the nexus_templates module',
            type=str, mandatory=True),
    }

    _templates = []
    _template = None

    def doInit(self, mode):
        self.log.info(self.templatesmodule)
        self._templates = __import__(
            self.templatesmodule, fromlist=[self.templatename]
        )
        self.log.info('Finished importing nexus_templates')
        self.set_template(self.templatename)

    def set_template(self, val):
        """
        Sets the template from the given template modules.
        Parses the template using *parserclass* method parse. The parsed
        root, event kafka streams and device placeholders are then set.
        :param val: template name
        """
        if not hasattr(self._templates, val):
            raise NicosError(
                'Template %s not found in module %s'
                % (val, self.templatesmodule)
            )

        self._template = getattr(self._templates, val)

        if self.templatename != val:
            self._setROParam('templatename', val)

    def _add_start_time(self, dataset, start_time):
        dataset.started = start_time.timestamp()
        start_time_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime(dataset.started))

        # Add start time to metainfo
        if ('dataset', 'starttime') not in dataset.metainfo:
            dataset.metainfo[('dataset', 'starttime')] = (start_time_str,
                                                          start_time_str,
                                                          '', 'general')

    def get_structure(self, dataset, start_time):
        template = copy.deepcopy(self._template)
        self._add_start_time(dataset, start_time)
        converter = NexusTemplateConverter()
        structure = converter.convert(template, dataset.metainfo)
        return json.dumps(structure)


class FileWriterStatus(KafkaStatusHandler):
    """Monitors Kafka for the status of any file-writing jobs."""
    _lock = None
    _jobs = {}
    _marked_for_stop = set()
    _recently_stopped = {}
    _type_to_handler = {}

    def doPreinit(self, mode):
        KafkaStatusHandler.doPreinit(self, mode)
        self._lock = threading.RLock()
        self._jobs = {}
        self._marked_for_stop = set()
        self._recently_stopped = {}
        self._update_status(status.OK, '')
        self._type_to_handler = {
            b'x5f2': self._on_status_message,
            b'answ': self._on_response_message,
            b'wrdn': self._on_stopped_message,
        }

    def new_messages_callback(self, messages):
        for _, msg in sorted(messages, key=lambda x: x[0]):
            if msg[4:8] in self._type_to_handler:
                with self._lock:
                    self._type_to_handler[msg[4:8]](msg)

    def _on_status_message(self, message):
        result = deserialise_x5f2(message)
        status_info = json.loads(result.status_json)
        job_id = status_info['job_id']
        if job_id == NOT_CURRENTLY_WRITING:
            return
        if job_id in self._recently_stopped:
            # Ignore delayed message
            return
        update_interval = result.update_interval // 1000
        next_update = currenttime() + update_interval
        self._jobs[job_id] = (update_interval, next_update)
        if len(self._jobs) > 1:
            self._update_status(status.BUSY, f'writing {len(self._jobs)} jobs')
        else:
            self._update_status(status.BUSY,
                                f'writing {list(self._jobs.keys())[0]}')

    def _on_stopped_message(self, message):
        result = deserialise_wrdn(message)
        self.log.info(f'stopped writing {result.job_id}')
        if result.job_id in self._jobs:
            del self._jobs[result.job_id]
        if result.job_id in self._marked_for_stop:
            self._marked_for_stop.remove(result.job_id)
        self._recently_stopped[result.job_id] = currenttime()
        if not self._jobs:
            self._update_status(status.OK, '')

    def _on_response_message(self, message):
        result = deserialise_answ(message)
        if result.action == ActionType.StartJob:
            self._on_start_response(result)
        elif result.action == ActionType.SetStopTime:
            self._on_stop_response(result)

    def _on_start_response(self, result):
        if result.outcome == ActionOutcome.Success:
            msg = f'starting to write job {result.job_id}'
            self._update_status(status.BUSY, msg)
            self.log.info(msg)
            self._jobs[result.job_id] = (self.statusinterval,
                                         currenttime() + self.statusinterval)
        else:
            self._update_status(status.ERROR, 'failed to start')
            self.log.error(result.message)

    def _on_stop_response(self, result):
        if result.job_id in self._recently_stopped:
            # Ignore delayed message
            return

        if result.outcome == ActionOutcome.Success:
            self._marked_for_stop.add(result.job_id)
            msg = f'request to stop writing succeeded for job {result.job_id}'
            self.log.info(msg)
        else:
            msg = f'stop writing request failed for job {result.job_id}'
            self._update_status(status.ERROR, msg)
            self.log.error('%s: %s', msg, result.message)

    def no_messages_callback(self):
        with self._lock:
            self._prune_stopped_jobs()
            if not self._jobs:
                return
            self._check_for_lost_jobs()

    def _prune_stopped_jobs(self):
        prune_after_seconds = 60
        self._recently_stopped = {k: v for k, v in
                                  self._recently_stopped.items() if
                                  currenttime() < v + prune_after_seconds}

    def _check_for_lost_jobs(self):
        overdue_jobs = [k for k, v in self._jobs.items() if
                        currenttime() > v[1] + self.timeoutinterval]
        for overdue in overdue_jobs:
            self.log.error(f'lost connection to job {overdue}')
            # Assume it has gone for good...
            del self._jobs[overdue]
        if not self._jobs and self._mode == MASTER:
            self._update_status(status.ERROR, 'lost job(s) - see logs')

    def doInfo(self):
        result = [(f'{self.name}', '', '', '', 'general')]
        for i, job in enumerate(self.jobs):
            result.append((f'job {i + 1}', f'{job}', f'{job}', '', 'general'))
        return result

    def _update_status(self, stat, message):
        if self._mode == MASTER:
            self._setROParam('curstatus', (stat, message))

    @property
    def jobs(self):
        with self._lock:
            return set(self._jobs.keys())

    @property
    def marked_for_stop(self):
        with self._lock:
            return set(self._marked_for_stop)

    def add_marked_for_stop(self, job_id):
        with self._lock:
            self._marked_for_stop.add(job_id)


class FileWriterSinkHandler(DataSinkHandler):
    """Sink handler for the NeXus file-writer"""
    _scan_set = None

    def prepare(self):
        if self.sink._manual_start or self._scan_set:
            return

        self.sink.check_okay_to_start()

        # Assign the counter
        self.manager.assignCounter(self.dataset)

        # Generate the filenames, only if not set
        if not self.dataset.filepaths:
            self.manager.getFilenames(
                self.dataset, self.sink.filenametemplate, self.sink.subdir
            )

        # Update meta information of devices, only if not present
        if not self.dataset.metainfo:
            self.manager.updateMetainfo()
        self._scan_set = self._get_scan_set()

    def begin(self):
        if self.sink._manual_start:
            return

        if self._scan_set and self.dataset.number > 1:
            return

        datetime_now = datetime.now()
        structure = self.sink._attached_nexus.get_structure(self.dataset,
                                                            datetime_now)
        self.sink._start_job(self.dataset.filenames[0], structure, datetime_now)

    def end(self):
        if self.sink._manual_start:
            return

        if self._scan_set and self.dataset.number < self._scan_set.npoints:
            return

        self.sink._stop_job()
        self.sink.end()

    def _get_scan_set(self):
        if not self.sink.one_file_per_scan:
            # User has requested one file per scan point
            return None

        parents = list(self.manager.iterParents(self.dataset))

        if parents and isinstance(parents[~0], ScanDataset):
            return parents[~0]
        return None

    def putResults(self, quality, results):
        if quality == INTERRUPTED:
            # On e-stop let the current file-writing job be stopped
            self._scan_set = None


class FileWriterControlSink(FileSink):
    """Sink for the NeXus file-writer"""

    parameters = {
        'brokers': Param('List of kafka hosts to be connected',
                         type=listof(host(defaultport=9092)),
                         mandatory=True, preinit=True, userparam=False),
        'pool_topic': Param(
            'Kafka topic where start messages are sent',
            type=str, settable=False, preinit=True, mandatory=True,
            userparam=False,
        ),
        'timeoutinterval': Param(
            'Time to wait (secs) before communication is considered failed',
            type=int, default=5, settable=True, userparam=False,
        ),
        'one_file_per_scan': Param(
            'Whether to write all scan points to one file or a file per point',
            type=bool, default=True, settable=True, userparam=False,
        ),
    }

    parameter_overrides = {
        'settypes': Override(default=[POINT]),
        'filenametemplate': Override(
            default=['%(proposal)s_%(pointcounter)08d.hdf']
        ),
    }

    attached_devices = {
        'status': Attach('The file-writer status device', FileWriterStatus),
        'nexus': Attach('Supplies the NeXus file structure',
                        NexusStructureProvider),
    }

    handlerclass = FileWriterSinkHandler

    def doInit(self, mode):
        self._statustopic = self._attached_status.statustopic
        self._manual_start = False
        self._handler = None
        self._command_channel = self._create_command_channel()

    def _create_command_channel(self):
        try:
            return WorkerJobPool(f'{self.brokers[0]}/{self.pool_topic}',
                                 f'{self.brokers[0]}/{self._statustopic}')
        except Exception as error:
            raise CommunicationError(
                f'could not connect to job pool: {error}') from error

    def _create_job_handler(self, job_id=''):
        return JobHandler(self._command_channel, job_id)

    @usermethod
    def start_job(self):
        """Start a new file-writing job."""
        self.check_okay_to_start()
        self._manual_start = False

        # Begin a point but remove it from the stack immediately to avoid an
        # orphaned point.
        # File-writing won't stop though.
        session.experiment.data.beginPoint()
        self._manual_start = True
        session.experiment.data.finishPoint()

    def _start_job(self, filename, structure, start_time=None, stop_time=None):
        self.check_okay_to_start()

        # Initialise the write job.
        write_job = WriteJob(
            nexus_structure=structure,
            file_name=filename,
            broker=self.brokers[0],
            start_time=start_time if start_time else datetime.now(),
            stop_time=stop_time,
            control_topic=self._statustopic
        )

        job_handler = self._create_job_handler()
        start_handler = job_handler.start_job(write_job)
        timeout = int(currenttime()) + self.timeoutinterval

        while not start_handler.is_done():
            if int(currenttime()) > timeout:
                raise Exception('request to start writing job not acknowledged')

    @usermethod
    def stop_job(self, job_id=''):
        """Stop a file-writing job.

        :param job_id: the particular job to stop. Only required if there is
            more than one job running.
        """
        self._stop_job(job_id)
        self._handler = None
        self._manual_start = False

    def _stop_job(self, job_id=''):
        if job_id and job_id in self._attached_status.marked_for_stop:
            # Already stopping so ignore
            return

        active_jobs = self.get_active_jobs()
        if not active_jobs:
            self.log.warning('all jobs have already stopped or are stopping')
            return

        if job_id and job_id not in active_jobs:
            self.log.error('supplied job ID is not recognised. '
                           'Already stopped or perhaps a typo?')
            return

        if len(active_jobs) == 1:
            job_id = list(active_jobs)[0]
        elif len(active_jobs) > 1 and not job_id:
            self.log.error('more than one job being written, rerun the command '
                           'with the job ID specified in quotes')
            return

        job_handler = self._create_job_handler(job_id)
        stop_handler = job_handler.set_stop_time(datetime.now())
        timeout = int(currenttime()) + self.timeoutinterval

        while not stop_handler.is_done() and not job_handler.is_done():
            if int(currenttime()) > timeout:
                self.log.error('request to stop writing job not'
                               'acknowledged by filewriter')
                return
        self._attached_status.add_marked_for_stop(job_id)

    def check_okay_to_start(self):
        active_jobs = self.get_active_jobs()
        if active_jobs:
            raise Exception('cannot start file-writing as following job(s) '
                            f'already in progress: {",".join(active_jobs)}')

    def get_active_jobs(self):
        jobs = self._attached_status.jobs
        active_jobs = \
            self._attached_status.marked_for_stop.symmetric_difference(jobs)
        return active_jobs

    def doInfo(self):
        return self._attached_status.doInfo()

    def createHandlers(self, dataset):
        if self._handler is None:
            self._handler = self.handlerclass(self, dataset, None)
        else:
            self._handler.dataset = dataset
        return [self._handler]

    def end(self):
        self._handler = None
