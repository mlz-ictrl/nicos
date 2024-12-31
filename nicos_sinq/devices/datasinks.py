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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
import queue
import socket
from datetime import datetime
from os import path
from time import monotonic as currenttime

import numpy as np
from streaming_data_types import serialise_hs01

from nicos import session
from nicos.core import SIMULATION, Attach, DataSink, DataSinkHandler, \
    Override, Param
from nicos.core.constants import SCAN
from nicos.core.errors import ProgrammingError
from nicos.devices.generic.manual import ManualSwitch
from nicos.nexus.nexussink import NexusSink
from nicos.utils import createThread, readFileCounter, updateFileCounter

from nicos_ess.devices.datasinks.file_writer import FileWriterControlSink, \
    FileWriterSinkHandler
from nicos_ess.devices.datasinks.nexussink import NexusFileWriterSink, \
    NexusFileWriterSinkHandler
from nicos_ess.devices.kafka.producer import ProducesKafkaMessages


def delete_keys_from_dict(dict_del, keys):
    for key in keys:
        if key in dict_del.keys():
            del dict_del[key]

    for val in dict_del.values():
        if isinstance(val, dict):
            delete_keys_from_dict(val, keys)
        if isinstance(val, list):
            for elem in val:
                delete_keys_from_dict(elem, keys)


class SinqNexusFileSinkHandler(NexusFileWriterSinkHandler):
    """Use the SICS counter so that counter is synchronized in all
    user control software.
    """

    def _assignCounter(self):
        # Adapted from DataManager.assignCounter function
        if self.dataset.counter != 0:
            return

        exp = session.experiment
        if not path.isfile(path.join(exp.dataroot, exp.counterfile)):
            session.log.warning('creating new empty file counter file at %s',
                                path.join(exp.dataroot, exp.counterfile))

        if session.mode == SIMULATION:
            raise ProgrammingError('assignCounter should not be called in '
                                   'simulation mode')

        # Read the counter from SICS file
        counter = exp.sicscounter + 1

        # Keep track of which files we have already updated, since the proposal
        # and the sample specific counter might be the same file.
        seen = set()
        for directory, attr in [(exp.dataroot, 'counter'),
                                (exp.proposalpath, 'propcounter'),
                                (exp.samplepath, 'samplecounter')]:
            counterpath = path.normpath(path.join(directory, exp.counterfile))
            readFileCounter(counterpath, self.dataset.countertype)
            if counterpath not in seen:
                updateFileCounter(counterpath, self.dataset.countertype,
                                  counter)
                seen.add(counterpath)

            setattr(self.dataset, attr, counter)

        # Update the counter in SICS file
        exp.updateSicsCounterFile(counter)

        session.experiment._setROParam('lastpoint', self.dataset.counter)

    def _remove_optional_components(self):
        # Remove from the NeXus structure the components not present
        delete_keys = []
        if 'analyser' not in session.loaded_setups:
            delete_keys.append('analyzer:NXfilter')
        if 'polariser' not in session.loaded_setups:
            delete_keys.append('polarizer:NXpolariser')
        if 'slit2' not in session.loaded_setups:
            delete_keys.append('pre_sample_slit2:NXaperture')
        if 'slit3' not in session.loaded_setups:
            delete_keys.append('pre_sample_slit3:NXaperture')
        if 'slit4' not in session.loaded_setups:
            delete_keys.append('after_sample1:NXaperture')
        delete_keys_from_dict(self.template, delete_keys)

    def prepare(self):
        NexusFileWriterSinkHandler.prepare(self)


class SinqNexusFileSink(NexusFileWriterSink):
    parameter_overrides = {'subdir': Override(volatile=True), }

    handlerclass = SinqNexusFileSinkHandler

    def doReadSubdir(self):
        counter = session.experiment.sicscounter
        return ('%3s' % int(counter / 1000)).replace(' ', '0')


class QuieckHandler(DataSinkHandler):
    _startdataset = None

    def begin(self):
        DataSinkHandler.begin(self)
        if not self._startdataset:
            self._startdataset = self.dataset

    def end(self):
        DataSinkHandler.end(self)
        if self._startdataset.finished is not None:
            try:
                message = 'QUIECK/' + self._startdataset.filepaths[0]
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socke:
                    socke.sendto(message.encode(),
                                 (self.sink.host, self.sink.port))
            except Exception:
                # In no event shall the failure to send this message break
                # something
                pass
            self._startdataset = None
            self.sink.end()


class QuieckSink(DataSink):
    """
    A simple DataSink which sends a UDP message at a specified port
    when a file is closed. At SINQ, there is a separate Java server which
    listens to these messages and initiates the synchronisation of data
    files from the local disk to backuped network storage.

    NICOS created a datasink for every intermediate dataset. This class
    contains logic that in a scan, a handler is created only for the
    first datset received.
    """

    parameters = {
        'port': Param('Port to which UDP Messages are sent', type=int,
                      default=2108),
        'host': Param('Host to which to send messages', type=str,
                      default='127.0.0.1'), }

    handlerclass = QuieckHandler
    _handlerObj = None

    def createHandlers(self, dataset):
        if not self._handlerObj:
            self._handlerObj = self.handlerclass(self, dataset, None)
        else:
            self._handlerObj.dataset = dataset
        return [self._handlerObj]

    def end(self):
        self._handlerObj = None


class SwitchableNexusSink(NexusSink):
    """"
    This allows file writing to be switched on/off through a ManualSwitch
    """
    attached_devices = {
        'file_switch': Attach('Switch for switching file writing on/off',
                              ManualSwitch),
    }

    def createHandlers(self, dataset):
        if self._attached_file_switch.read(0) == 'on':
            return NexusSink.createHandlers(self, dataset)
        else:
            session.log.warning(
                'NeXus file writing suppressed on user request')
            return []


class ImageForwarderSinkHandler(DataSinkHandler):

    def serialise(self, prefix, arr, index=0, num_images=1):
        shape = arr.shape
        dim_metadata = [
            {'bin_boundaries': np.array(range(shape[0])) - .5,
             'length': shape[0]},
            {'bin_boundaries': np.array(range(shape[1])) - .5,
             'length': shape[1]},
        ]
        data = {
            'source': f'{prefix}_{index}' if num_images > 1 else prefix,
            'timestamp': int(currenttime() * 1e3),
            'current_shape': shape,
            'dim_metadata': dim_metadata,
            'data': arr,
        }
        return serialise_hs01(data)

    def putResults(self, quality, results):
        for source_prefix, value in results.items():
            num_images = len(value[1])
            for index, arr in enumerate(value[1]):
                message = self.serialise(source_prefix, arr, index, num_images)
                self.sink._queue.put(message)


class ImageForwarderSink(ProducesKafkaMessages, DataSink):
    parameters = {
        'output_topic': Param('The topic to send data to',
                              type=str, userparam=False, settable=False,
                              mandatory=True,
                              ),
    }

    handlerclass = ImageForwarderSinkHandler

    def doInit(self, mode):
        self._queue = queue.Queue(1000)
        self._worker = createThread('det_image_to_kafka', self._processQueue,
                                    start=True)

    def _processQueue(self):
        while True:
            value = self._queue.get()
            self.send(self.output_topic, value)
            self._queue.task_done()


class SinqFileWriterSinkHandler(FileWriterSinkHandler):

    def prepare(self):
        # At SINQ counter assignement works only for scan
        oldtype = self.dataset.countertype
        if oldtype != SCAN and self.sink.one_file_per_scan:
            self.dataset.countertype = 'scan'
            FileWriterSinkHandler.prepare(self)
            self.dataset.countertype = oldtype
            return
        FileWriterSinkHandler.prepare(self)

    def begin(self):
        if self.sink._manual_start:
            return

        if self._scan_set and self.dataset.number > 1:
            return

        _, filepaths = self.manager.getFilenames(
            self.dataset, self.sink.filenametemplate, self.sink.subdir
        )
        filename = filepaths[0]
        if hasattr(self.dataset, 'replay_info'):
            # Replaying previous job
            self.sink._start_job(filename,
                                 self.dataset.counter,
                                 self.dataset.replay_info['structure'],
                                 self.dataset.replay_info['start_time'],
                                 self.dataset.replay_info['stop_time'],
                                 self.dataset.replay_info['replay_of'])
            return

        datetime_now = datetime.now()
        structure = self.sink._attached_nexus.get_structure(self.dataset,
                                                            datetime_now)
        self.sink._start_job(filename, self.dataset.counter,
                             structure, datetime_now)


class SinqFileWriterControlSink(FileWriterControlSink):
    parameters = {
        'file_output_dir': Param('The directory where data files are written',
                                 type=str, settable=False, default=None,
                                 userparam=False),
    }

    handlerclass = SinqFileWriterSinkHandler

    def get_output_file_dir(self):
        return path.join(self.file_output_dir, str(datetime.now().year),
                         str(session.experiment.proposal))
