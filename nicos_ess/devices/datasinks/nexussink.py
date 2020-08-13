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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

import copy
import json
import os
import time

from nicos.core import Attach, Override, Param, dictof, status, tupleof
from nicos.core.constants import POINT
from nicos.core.data import DataSinkHandler
from nicos.core.errors import NicosError
from nicos.devices.datasinks import FileSink
from nicos_ess.devices.kafka.producer import ProducesKafkaMessages
from nicos_ess.devices.kafka.status_handler import KafkaStatusHandler
from nicos_ess.nexus.converter import NexusTemplateConverter

from streaming_data_types.run_start_pl72 import serialise_pl72
from streaming_data_types.run_stop_6s4t import serialise_6s4t


class NexusFileWriterStatus(KafkaStatusHandler):
    """ Device to read the file writing status from the kafka status
    topic. All new messages appearing on the status topic are read
    from a thread and the status is updated accordingly.

    In the context of file writing, dataset goes through following life-cycle:

    ISSUED: The job has been issued to the file writer (notified from sink)
    START: File writer has started writing the file (notified from FileWriter)
    (may be) FAIL: File writer failed to write (notified from FileWriter)
    (may be) ERROR: File writer had error but is still writing the file
    STOP: The measurement stopped (using preset/user) (notified from sink)
    CLOSE: File writer closed the file (notified from sink)
    """

    parameters = {
        'timeout': Param(
            'Maximum waiting time for a job to start/close (sec)',
            type=int,
            default=30,
        ),
    }

    def doInit(self, mode):
        self._tracked_datasets = {}
        self._issued = []
        self._started = []
        self._stopped = []
        self._job_in_progress = ''

    def _on_issue(self, jobid, dataset):
        # Called when a dataset started and job was issued to the file writer
        if not self.is_process_running():
            self.log.error('File Writer is down. Data will not be written!!')
            return
        self._tracked_datasets[jobid] = dataset
        self._issued.append(jobid)

    def _on_start(self, jobid, dataset):
        # Called when a file writer actually starts to write
        if jobid in self._issued:
            self._issued.remove(jobid)
        self._started.append(jobid)

    def _on_error(self, jobid, dataset, message=''):
        # Called when an error appears in writing the dataset
        self.log.error('Unexpected error while writing %d %s', dataset.counter,
                       ' - ' + message if message else message)

    def _on_fail(self, jobid, dataset, message=''):
        # Called when the writing failed
        self.log.error('Failed to write #%d - %s', dataset.counter, message)
        if jobid in self._tracked_datasets:
            self._tracked_datasets.pop(jobid)
        if jobid in self._issued:
            self._issued.remove(jobid)
        if jobid in self._started:
            self._started.remove(jobid)
        if jobid in self._stopped:
            self._stopped.remove(jobid)

    def _on_stop(self, jobid, dataset):
        # Called when the measurement stopped
        if jobid in self._tracked_datasets:
            self._stopped.append(jobid)

    def _on_close(self, jobid, dataset):
        # Called when the file writer finishes and closes the file
        if jobid in self._tracked_datasets:
            self._tracked_datasets.pop(jobid)
        if jobid in self._started:
            self._started.remove(jobid)
        if jobid in self._stopped:
            self._stopped.remove(jobid)

    def _check_timeouts(self):
        # Check if timeout occurred for issued or stopped datasets
        if self._job_in_progress in self._issued:
            self._issued.remove(self._job_in_progress)
        else:
            for jobid in self._issued:
                dset = self._tracked_datasets.get(jobid)
                now = time.time()
                if dset and now > dset.started + self.timeout:
                    msg = 'Timeout while waiting for file writer to start ' \
                          'writing'
                    self._on_fail(jobid, dset, msg)

        if not self._job_in_progress and self._stopped:
            self._stopped.clear()
        else:
            for jobid in self._stopped:
                dset = self._tracked_datasets.get(jobid)
                now = time.time()
                if dset and now > dset.finished + self.timeout:
                    msg = 'Timeout while waiting for file writer to close ' \
                          'the file'
                    self._on_fail(jobid, dset, msg)

    def new_messages_callback(self, messages):
        self._check_timeouts()
        KafkaStatusHandler.new_messages_callback(self, messages)

    def no_messages_callback(self):
        self._check_timeouts()
        KafkaStatusHandler.no_messages_callback(self)

    def _status_update_callback(self, messages):
        """
        :param messages: dict of timestamp and JSON in the form
        {
            "file_being_written": "some_file.nxs",
            "job_id": "1234",
            "start_time": 1580460273162,
            "stop_time": 0,
            "update_interval": 2000
        }
        """

        def get_latest_message(message_list):
            message_list_sorted = sorted(message_list.items(), reverse=True)
            # makes sure that the message comes from the filewriter
            gen = (
                msg
                for _, msg in message_list_sorted
                if 'file_being_written' in msg
            )
            return next(gen, None)

        message = get_latest_message(messages)
        if not message:
            return

        self._set_next_update(message)
        self._job_in_progress = message.get('job_id', '')
        file_name = message.get('file_being_written', '')
        if file_name:
            self._setROParam(
                'curstatus', (status.BUSY, 'Writing %s' % file_name)
            )
            return
        self._setROParam('curstatus', (status.OK, 'Idle'))


class NexusFileWriterSinkHandler(DataSinkHandler):
    """Sink handler for the Nexus File Writer
    """

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._converter = NexusTemplateConverter()
        self.rewriting = False

    def _remove_optional_components(self):
        pass

    def prepare(self):
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

    def begin(self):
        # A deep copy is ABSOLUTELY required here!
        self.template = copy.deepcopy(self.sink.template)
        self._remove_optional_components()

        # Get the start time
        if not self.dataset.started:
            self.dataset.started = time.time()

        start_time = int(self.dataset.started * 1000)
        start_time_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime(self.dataset.started))

        metainfo = self.dataset.metainfo
        # Put the start time in the metainfo
        if ('dataset', 'starttime') not in metainfo:
            metainfo[('dataset', 'starttime')] = (start_time_str,
                                                  start_time_str,
                                                  '', 'general')

        structure = self._converter.convert(self.template,
                                            self.dataset.metainfo)
        job_id = str(self.dataset.uid)

        filename = os.path.basename(self.dataset.filepaths[0])
        if self.sink.file_output_dir:
            filename = os.path.join(self.sink.file_output_dir, filename)

        # Write the stop time if already known
        stop_time = 0
        if self.dataset.finished:
            stop_time = int(self.dataset.finished * 1000)
            self.rewriting = True

        start_message = serialise_pl72(job_id=job_id, filename=filename,
                                       start_time=start_time,
                                       stop_time=stop_time,
                                       nexus_structure=json.dumps(structure),
                                       broker=','.join(self.sink.brokers))

        self.log.info('Started file writing at: %s (%s)', start_time_str,
                      start_time)
        self.sink.send(self.sink.cmdtopic, start_message)

        # Tell the sink that this dataset has started
        self.sink.dataset_started(self.dataset)

    def end(self):
        # Execute only if not rewriting
        if not self.rewriting:
            if not self.dataset.finished:
                self.dataset.finished = time.time()
            stop_time = int(self.dataset.finished * 1000)

            stop_message = serialise_6s4t(job_id=str(self.dataset.uid),
                                          stop_time=stop_time)

            self.log.info('Stopped file writing at: %s', stop_time)
            self.sink.send(self.sink.cmdtopic, stop_message)

        # Tell the sink that this dataset has ended
        self.sink.dataset_ended(self.dataset, self.rewriting)


class NexusFileWriterSink(ProducesKafkaMessages, FileSink):
    """ Sink for writing NeXus files using the FileWriter. The file
    writer accepts commands on a Kafka topic. This command is in the
    form of a JSON object which contains properties such as start
    time, brokers and the nexus structure. The details are provided
    in the github repository of the FileWriter:
    https://github.com/ess-dmsc/kafka-to-nexus

    Topic on which the FileWriter accepts the commands is given by the
    parameter *cmdtopic*. The module containing various nexus templates
    is provided using the parameter *templatesmodule*. A default template
    can be chosen from these nexus templates using the parameter *templatename*

    Rules for the template:
    * Groups should be represented as: <group_name>:<NX_class> in the keys
    * NX_class should be one of the standard NeXus groups
    * Datasets should be represented as: <dataset_name> in the keys
    * Dataset value should be a instance of class NXDataset.
    * Attribute value can either be numerical or instance of class NXattribute
    * Detector event streams are marked using the class EventStream
    * Device values that are to be streamed are marked with DeviceStream

    Example template:
    template = {
        "entry1:NXentry": {
            "INST:NXinstrument": {
                "name": NXDataset("Instrument"),
                "detector:NXdetector": {
                    "data": EventStream(topic="EventTopic", source="SrcName")
                },
            },
            "sample:NXsample": {
                "height": DeviceDataset('dev'),
                "property": DeviceDataset('dev', 'param', unit='K'),
            },
        }
    }
    """

    parameters = {
        'cmdtopic': Param('Kafka topic where status commands are written',
            type=str, settable=False, preinit=True, mandatory=True),
        'templatesmodule': Param(
            'Python module containing NeXus nexus_templates',
            type=str, mandatory=True),
        'templatename': Param('Template name from the nexus_templates module',
            type=str, mandatory=True),
        'lastsinked': Param(
            'Saves the counter, start and end time of sinks',
            type=tupleof(int, float, float, dictof(tuple, tuple)),
            settable=True, internal=True),
        'useswmr': Param('Use SWMR feature when writing HDF files', type=bool,
            settable=False, userparam=False, default=True),
        'file_output_dir': Param('The directory where data files are written',
            type=str, settable=False, default=None, userparam=False),
        'title': Param('Title to set in NeXus file', type=str,
            settable=True, userparam=True, default=''),
        'cachetopic': Param('Kafka topic for cache messages', type=str),
    }

    parameter_overrides = {
        'settypes': Override(default=[POINT]),
        'filenametemplate': Override(
            default=['%(proposal)s_%(pointcounter)08d.hdf']
        ),
    }

    attached_devices = {
        'status_provider': Attach(
            'Device that provides file writing status',
            NexusFileWriterStatus,
            optional=True,
        ),
    }

    handlerclass = NexusFileWriterSinkHandler
    template = None

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

        self.template = getattr(self._templates, val)

        if self.templatename != val:
            self._setROParam('templatename', val)

    @property
    def status_provider(self):
        """ Returns the class that provides status of this sink
        :return: Attached NexusFileWriterStatus
        """
        return self._attached_status_provider

    def dataset_started(self, dataset):
        """ Capture that a dataset has started and change the status
        of the dataset
        :param dataset: the dataset that has been started
        """
        if self.status_provider:
            jobid = str(dataset.uid)
            self.status_provider._on_issue(jobid, dataset)

    def dataset_ended(self, dataset, rewriting):
        """ Capture the end of the dataset. Record the counter number,
        start and end time of this dataset in cache using the *lastsinked*
        parameter.
        :param dataset: the dataset that was ended
        :param rewriting: Is this dataset being rewritten
        """
        if self.status_provider:
            jobid = str(dataset.uid)
            self.status_provider._on_stop(jobid, dataset)

        # If rewriting, the dataset was already written in the lastsinked
        if not rewriting:
            self.lastsinked = (
                dataset.counter,
                dataset.started,
                dataset.finished,
                dataset.metainfo,
            )
