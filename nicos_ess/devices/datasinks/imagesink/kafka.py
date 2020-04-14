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

from time import time as currenttime

from nicos.core import FINAL, INTERMEDIATE, DataSink, DataSinkHandler, \
    Override, Param, dictof, tupleof
from nicos.core.constants import POINT

from nicos_ess.devices.datasinks.imagesink.serializer import \
    HistogramFlatbuffersSerializer
from nicos_ess.devices.kafka.producer import ProducesKafkaMessages


class ImageKafkaDataSinkHandler(DataSinkHandler):
    """ Data sink handler for sending the image data to Kafka.
    This class handles the periodic sending of arrays to Kafka.
    The frequency can be set in the detector where this sink
    is used from.
    """

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._lastmetadata = 0

    def prepare(self):
        self._lastmetadata = 0

    def _sendArray(self, timestamp, desc, array):
        if desc.name not in self.sink.channeltostream:
            return

        topic, source = self.sink.channeltostream[desc.name]

        # Serialize the message
        msg = self.sink.serializer.encode(timestamp, desc, array, source,
                                          self._lastmetadata)

        # Send the message to Kafka
        self.log.debug('%d bytes sent to %s', len(msg), topic)
        self.sink.send(topic, msg)

    def putResults(self, quality, results):
        # This method is called while measuring after specific time
        # periods that can be controlled by the detector.
        if self.detector.name not in results:
            return

        if quality not in [INTERMEDIATE, FINAL]:
            return

        timestamp = currenttime() * 1E9
        _, arrays = results[self.detector.name]
        for desc, array in zip(self.detector.arrayInfo(), arrays):
            self._sendArray(timestamp, desc, array)

        # If metadata was sent this time, set this information
        if self._lastmetadata == 0:
            self._lastmetadata = timestamp

    def end(self):
        # Reset the last metadata timestamp, so that it can be
        # sent again in the next measurement
        self._lastmetadata = 0


class ImageKafkaDataSink(ProducesKafkaMessages, DataSink):
    """ Data sink which writes images to Kafka after serializing
    them. The parameter *channeltostream* provides a dict of all
    the image channels from which the data is to be be forwarded
    mapped to a tuple of (kafka topic, message source name)
    """

    parameters = {
        'maximagesize': Param('Expected max array size of the image',
                              type=int, default=5e7),
        'channeltostream': Param(
            'Dict of image channel name(to be forwarded) -> (topic, source)',
            type=dictof(str, tupleof(str, str)), mandatory=True),
    }

    parameter_overrides = {
        'settypes': Override(default=[POINT]),
    }

    handlerclass = ImageKafkaDataSinkHandler
    serializer = HistogramFlatbuffersSerializer()

    def doInit(self, mode):
        # Increase the maximum message size that the producer can send
        self._setProducerConfig(max_request_size=self.maximagesize)
