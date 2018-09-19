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

import numpy
from time import time as currenttime

from nicos import session
from nicos.core import FINAL, LIVE
from nicos.pycompat import memory_buffer

from nicos_ess.devices.datasinks.imagesink import ImageKafkaDataSinkHandler, \
    ImageKafkaDataSink


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
                data.append(memory_buffer(array))
            elif len(desc.shape) == 2:
                nx.append(desc.shape[1])
                ny.append(desc.shape[0])
                nz.append(1)
                tags.append(desc.name)
                data.append(memory_buffer(array))
            elif len(desc.shape) == 3:
                # X-Axis summed up
                arrayX = numpy.sum(array.reshape(desc.shape),
                                   axis=0, dtype='uint32')[::-1].flatten()
                nx.append(desc.shape[2])
                ny.append(desc.shape[1])
                nz.append(1)
                tags.append('X-Integrated - Area Detector')
                data.append(memory_buffer(arrayX))

                # TOF summed up
                arrayT = numpy.sum(array.reshape(desc.shape),
                                   axis=2, dtype='uint32').flatten()
                nx.append(desc.shape[1])
                ny.append(desc.shape[0])
                nz.append(1)
                tags.append('TOF Integrated - Area Detector')
                data.append(memory_buffer(arrayT))
            else:
                continue

        session.updateLiveData('Live', self.dataset.uid, self.detector.name,
                               tags, '<u4', nx, ny, nz,
                               currenttime() - self.dataset.started, data)


class ImageKafkaWithLiveViewDataSink(ImageKafkaDataSink):
    handlerclass = ImageKafkaWithLiveViewDataSinkHandler
