#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

import json
import time
from collections import Counter

from nicos import session
from nicos.core import Param, Override, status, Attach, tupleof, dictof
from nicos.core.constants import POINT
from nicos.core.data import DataSinkHandler
from nicos.core.errors import NicosError
from nicos.devices.datasinks import FileSink
from nicos.pycompat import iteritems
from nicos_ess.devices.kafka.producer import ProducesKafkaMessages
from nicos_ess.devices.kafka.status_handler import KafkaStatusHandler
from nicos_ess.nexus.converter import NexusTemplateConverter

# File writing status codes for the dataset
UNKNOWN = 'UNKNOWN'
WAITING = 'WAITING'
WRITING = 'WRITING'
FINISHED = 'FINISHED'
ERROR = 'ERROR'


class NexusFileWriterStatus(KafkaStatusHandler):
    """ Device to read the file writing status from the kafka status
    topic. All new messages appearing on the status topic are read
    from a thread and the status is updated accordingly.
    """

    def doInit(self, mode):
        self._active_datasets = {}

    def _status_update_callback(self, messages):
        # This method is called whenever a new status messages appear on
        # the status topic.
        # *messages* is a dict of timestamp and message in JSON format

        # Loop until a valid most recent message is read
        for _, message in sorted(iteritems(messages), reverse=True):
            # A valid message would have files key on the top hierarchy
            if 'files' in message:
                jobs = message['files'].keys()

                # Compare the status of current datasets with the jobs from
                # status message and change the status if necessary
                datasets_finished = []
                for uid, dataset in iteritems(self._active_datasets):
                    state = dataset.info  # Current state of the dataset
                    if state == WRITING and uid not in jobs:
                        # If the dataset was writing and does not exist in
                        # the jobs now that means dataset has finished writing
                        dataset.info = FINISHED
                        datasets_finished.append(dataset)
                    elif state == WAITING and uid in jobs:
                        # If the dataset was waiting and now has appeared in
                        # the jobs would imply that it has started writing
                        dataset.info = WRITING

                # Remove unwanted datasets
                for dataset in datasets_finished:
                    self.remove_dataset(dataset)

                # We need to read only one most recent valid message
                break

        # Gather the currently waiting and writing jobs to be displayed as the
        # device status
        states = Counter([d.info for d in self._active_datasets.values()])
        writing = states.get(WRITING, 0)
        issued = states.get(WAITING, 0)

        # Generate messages using the gathered dataset status
        if issued == 0 and writing == 0:
            stat = status.OK, 'Ok, no active job'
        elif issued == 0 and writing > 0:
            stat = status.BUSY, 'Writing %s files' % writing
        else:
            stat = status.BUSY, 'Writing %s + Waiting %s' % (writing, issued)

        # Finally set the status in cache for it to appear on GUI
        self._setROParam('curstatus', stat)

    def add_dataset(self, dataset):
        dataset.info = WAITING
        if not self.is_process_running():
            self.log.warn('Process is down. Data will not be written..')
            dataset.info = ERROR
        self._active_datasets[str(dataset.uid)] = dataset

    def remove_dataset(self, dataset):
        # Remove the datasets once they finish
        if str(dataset.uid) in self._active_datasets:
            del self._active_datasets[str(dataset.uid)]


class NexusFileWriterSinkHandler(DataSinkHandler):
    """Sink handler for the Nexus File Writer
    """

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._converter = NexusTemplateConverter()
        self.rewriting = False

    def prepare(self):
        # Assign the counter
        session.data.assignCounter(self.dataset)

        # Generate the filenames, only if not set
        if not self.dataset.filepaths:
            session.data.getFilenames(self.dataset, self.sink.filenametemplate,
                                      self.sink.subdir)

        # Update meta information of devices, only if not present
        if not self.dataset.metainfo:
            session.data.updateMetainfo()

    def begin(self):
        # Get the start time
        starttime = int(time.time() * 1000)
        if self.dataset.started:
            starttime = int(self.dataset.started * 1000)

        structure = self._converter.convert(self.sink.template,
                                            self.dataset.metainfo)

        command = {
            "cmd": "FileWriter_new",
            "broker": ','.join(self.sink.brokers),
            "job_id": str(self.dataset.uid),
            "start_time": starttime,
            "use_hdf_swmr": self.sink.useswmr,
            "nexus_structure": structure,
            "file_attributes": {
                "file_name": self.dataset.filepaths[0]
            }
        }

        # Write the stoptime when already known
        if self.dataset.finished:
            stoptime = int(self.dataset.finished * 1000)
            command["stop_time"] = stoptime
            self.rewriting = True

        self.log.debug('Started file writing at: %s', starttime)
        self.sink.send(self.sink.cmdtopic, json.dumps(command))

        # Tell the sink that this dataset has started
        self.sink.dataset_started(self.dataset)

    def end(self):
        # Execute only if not rewriting
        if not self.rewriting:
            stoptime = int(time.time() * 1000)
            if self.dataset.finished:
                stoptime = int(self.dataset.finished * 1000)

            command = {
                "cmd": "FileWriter_stop",
                "job_id": str(self.dataset.uid),
                "stop_time": stoptime
            }

            self.log.debug('Stopped file writing at: %s', stoptime)
            self.sink.send(self.sink.cmdtopic, json.dumps(command))

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
                          type=str, settable=False, preinit=True,
                          mandatory=True),
        'templatesmodule': Param(
            'Python module containing NeXus nexus_templates',
            type=str, mandatory=True),
        'templatename': Param('Template name from the nexus_templates module',
                              type=str, mandatory=True),
        'lastsinked': Param(
            'Saves the counter, start and end time of sinks',
            type=tupleof(int, float, float, dictof(tuple, tuple)),
            settable=True, userparam=False),
        'useswmr': Param('Use SWMR feature when writing HDF files', type=bool,
                         settable=False, userparam=False, default=True)
    }

    parameter_overrides = {
        'settypes': Override(default=[POINT]),
        'filenametemplate': Override(
            default=['%(proposal)s_%(pointcounter)08d.hdf']),
    }

    attached_devices = {
        'status_provider': Attach('Device that provides file writing status',
                                  NexusFileWriterStatus, optional=True),
    }

    handlerclass = NexusFileWriterSinkHandler
    template = None

    def doInit(self, mode):
        self._templates = __import__(self.templatesmodule,
                                     fromlist=[self.templatename])
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
            raise NicosError('Template %s not found in module %s'
                             % (val, self.templatesmodule))

        self.template = getattr(self._templates, val)

        if self.templatename != val:
            self._setROParam('templatename', val)
        self.log.info('Finished setting template')

    @property
    def status_provider(self):
        """ Returns the class that provides status of this sink
        :return: Attached NexusFileWriterStatus
        """
        return self._attached_status_provider

    def dataset_started(self, dataset):
        """ Capture that a dataset has started and change the status
        of the dataset using it's info attribute
        :param dataset: the dataset that has been started
        """
        if self.status_provider:
            self.status_provider.add_dataset(dataset)

    def dataset_ended(self, dataset, rewriting):
        """ Capture the end of the dataset. Record the counter number,
        start and end time of this dataset in cache using the *lastsinked*
        parameter.
        :param dataset: the dataset that was ended
        :param rewriting: Is this dataset being rewritten
        :return:
        """
        # If rewriting, the dataset was already written in the lastsinked
        if not rewriting:
            self.lastsinked = (dataset.counter, dataset.started,
                               dataset.finished, dataset.metainfo)
