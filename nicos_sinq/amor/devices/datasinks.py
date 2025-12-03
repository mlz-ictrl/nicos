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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

import copy
import json
import time
from os import path

import numpy

from nicos import session
from nicos.core import FINAL, LIVE
from nicos.core.data import DataSink, DataSinkHandler
from nicos.utils import byteBuffer, safeName

from nicos_ess.devices.datasinks.nexus_structure import NexusStructureTemplate
from nicos_ess.nexus.converter import NexusTemplateConverter
from nicos_sinq.amor.commands import synchronize_daq
from nicos_sinq.devices.datasinks import SinqNexusFileSink
from nicos_sinq.devices.imagesink import ImageKafkaDataSink, \
    ImageKafkaDataSinkHandler


class ImageKafkaWithLiveViewDataSinkHandler(ImageKafkaDataSinkHandler):

    def prepare(self):
        # Reset the counts to 0 in the Live View
        arrays = []
        for desc in self.detector.arrayInfo():
            # Empty byte array representing 0 of type uint32
            arrays.append(numpy.zeros(numpy.prod(desc.shape), dtype='uint32'))
        self.putResults(LIVE, {self.detector.name: (None, arrays)})

    def putResults(self, quality, results):
        ImageKafkaDataSinkHandler.putResults(self, quality, results)

        if quality not in [FINAL, LIVE]:
            return

        if self.detector.name not in results:
            return

        _, arrays = results[self.detector.name]
        nx = []
        ny = []
        nz = []
        tags = []
        data = []
        for desc, array in zip(self.detector.arrayInfo(), arrays):
            if array is None:
                continue
            if len(desc.shape) == 1:
                nx.append(desc.shape[0])
                ny.append(1)
                nz.append(1)
                tags.append(desc.name)
                data.append(byteBuffer(array))
            elif len(desc.shape) == 2:
                nx.append(desc.shape[1])
                ny.append(desc.shape[0])
                nz.append(1)
                tags.append(desc.name)
                data.append(byteBuffer(array))
            elif len(desc.shape) == 3:
                # X-Axis summed up
                arrayX = numpy.sum(array.reshape(desc.shape),
                                   axis=0, dtype='uint32')[::-1].flatten()
                nx.append(desc.shape[2])
                ny.append(desc.shape[1])
                nz.append(1)
                tags.append('X-Integrated - Area Detector')
                data.append(byteBuffer(arrayX))

                # TOF summed up
                arrayT = numpy.sum(array.reshape(desc.shape),
                                   axis=2, dtype='uint32').flatten()
                nx.append(desc.shape[1])
                ny.append(desc.shape[0])
                nz.append(1)
                tags.append('TOF Integrated - Area Detector')
                data.append(byteBuffer(arrayT))
            else:
                continue

        session.updateLiveData(
            dict(tag=LIVE,
                 uid=self.dataset.uid,
                 detector=self.detector.name,
                 filenames=tags,
                 dtypes=['<u4'],
                 shapes=list(zip(nx, ny, nz)),
                 time=time.time() - self.dataset.started),
            data)


class ImageKafkaWithLiveViewDataSink(ImageKafkaDataSink):
    handlerclass = ImageKafkaWithLiveViewDataSinkHandler


def to_snake(s):
    return safeName(''.join(['_'+c.lower() if c.isupper() else c for c in
                             s]).lstrip('_'))


class AmorNexusFileSink(SinqNexusFileSink):
    def get_output_file_dir(self):
        return path.join(self.file_output_dir,
                         to_snake(session.experiment.title))


class AmorStructureTemplate(NexusStructureTemplate):
    """
    A template provider which massages the template in an AMOR
    specific way:

    1) Remove optional components from the template
    2) Puts the distances offset in
    """

    def _delete_keys_from_dict(self, dict_del, keys):
        for key in list(keys):
            if key in dict_del.keys():
                del dict_del[key]

        for val in dict_del.values():
            if isinstance(val, dict):
                self._delete_keys_from_dict(val, keys)
            if isinstance(val, list):
                for elem in val:
                    self._delete_keys_from_dict(elem, keys)

    def _remove_optional_components(self, template):
        # Remove from the NeXus structure the components not present
        delete_keys = []
        if 'deflector' not in session.loaded_setups:
            delete_keys.append('deflector:NXmirror')
        if 'polarizer' not in session.loaded_setups:
            delete_keys.append('polarizer:NXpolariser')
        if 'diaphragm2' not in session.loaded_setups:
            delete_keys.append('diaphragm2:NXslit')
        if 'diaphragm3' not in session.loaded_setups:
            delete_keys.append('diaphragm3:NXslit')
        if 'diaphragm4' not in session.loaded_setups:
            delete_keys.append('diaphragm4:NXslit')
        if 'stz_table' not in session.loaded_setups:
            delete_keys.append('height_offset')
        self._delete_keys_from_dict(template, delete_keys)
        return template

    def get_structure(self, dataset, start_time):
        template = copy.deepcopy(self._template)
        template = self._remove_optional_components(template)
        self._add_start_time(dataset)

        converter = NexusTemplateConverter()
        structure = converter.convert(template, dataset.metainfo)
        return json.dumps(structure)


class SyncDaqHandler(DataSinkHandler):

    def prepare(self):
        synchronize_daq()

    def begin(self):
        DataSinkHandler.begin(self)

    def end(self):
        DataSinkHandler.end(self)


class SyncDaqSink(DataSink):
    """
    A simple DataSink which calls the synchronize_daq user command at the start
    of each measurement.
    """

    handlerclass = SyncDaqHandler
    _handlerObj = None

    def createHandlers(self, dataset):
        if not self._handlerObj:
            self._handlerObj = self.handlerclass(self, dataset, None)
        else:
            self._handlerObj.dataset = dataset
        return [self._handlerObj]

    def end(self):
        self._handlerObj = None
