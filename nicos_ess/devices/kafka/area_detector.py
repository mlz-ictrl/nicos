#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

import kafka
import numpy

from nicos.core import Attach, status
from nicos.core.constants import LIVE
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel

from nicos_ess.devices.epics.area_detector import ADKafkaPlugin
from nicos_ess.devices.kafka.consumer import KafkaSubscriber

try:
    from nicos_ess.devices.fbschemas.hs00 import Array, ArrayUInt, \
        EventHistogram

except ImportError:
    EventHistogram = None
    Array = None
    ArrayUInt = None


class ADKafkaImageDetector(KafkaSubscriber, ImageChannelMixin, PassiveChannel):
    """
    Class for reading images from the stream associated with the ADPluginKafka
    """
    attached_devices = {
        'kafka_plugin': Attach('NICOS device for the ADPluginKafka',
                               ADKafkaPlugin, optional=False)
    }

    def doPreinit(self, mode):
        broker = getattr(self._attached_kafka_plugin, 'broker')
        if not broker:
            raise Exception('Can\'t find broker address in ADPluginKafka')
        self._consumer = kafka.KafkaConsumer(
            bootstrap_servers=[broker],
            auto_offset_reset='latest'  # start at latest offset
        )

        # Settings for thread to fetch new message
        self._stoprequest = True
        self._updater_thread = None
        self._lastmessage = None

    def doInit(self, mode):
        topic = getattr(self._attached_kafka_plugin, 'topic')
        if not topic:
            raise Exception('Can\'t find topic in ADPluginKafka')
        self._consumer.subscribe([topic])

    def doReadArray(self, quality=LIVE):
        deserializer = HistogramFlatbuffersDeserializer()
        try:
            data, _, _ = deserializer.decode(self._lastmessage[1])
        except Exception as e:
            self.log.error(e)
            return []
        self.readresult = []
        return data.tolist()

    def new_messages_callback(self, messages):
        if not messages:
            return
        lastkey = sorted(list(messages.keys()))[-1]
        self._lastmessage = (lastkey, messages[lastkey])

    def doStatus(self, maxage=0):
        st = self._attached_kafka_plugin.doStatus()
        if st[0] != status.OK:
            return st
        if not self._consumer:
            return status.ERROR, 'Broker failure'
        if not self._consumer.subscription():
            return status.WARN, 'No topic subscribed'
        return status.OK, ''

    def valueInfo(self):
        return ()


class HistogramFlatbuffersDeserializer(object):
    """
    Decode the histogram using the flatbuffers schema hs00
    """
    file_identifier = "hs00"

    @staticmethod
    def _read_as_numpy(histogram, dtype=ArrayUInt.ArrayUInt):
        result = dtype()
        result.Init(histogram.Data().Bytes, histogram.Data().Pos)
        return result.ValueAsNumpy()

    @staticmethod
    def _read_current_shape(histogram):
        result = ArrayUInt.ArrayUInt()
        result.Init(histogram.CurrentShape().Bytes,
                    histogram.CurrentShape().Pos)
        return result.ValueAsNumpy()

    def decode(self, buff):
        histogram = EventHistogram.EventHistogram().GetRootAsEventHistogram(
            buff, 0)
        data_type = histogram.DataType()
        value = []
        if data_type == Array.Array.ArrayUInt:
            value = self._read_as_numpy(histogram=histogram)
        if data_type == Array.Array.ArrayULong:
            raise NotImplementedError('This data type is not yet implemented.')
            # value = self._read_as_numpy(histogram=histogram,
            # dtype=ArrayULong.ArrayULong)
        if data_type == Array.Array.ArrayFloat:
            raise NotImplementedError('This data type is not yet implemented.')
            # value = self._read_as_numpy(histogram=histogram,
            # dtype=ArrayFloat.ArrayFloat)
        if data_type == Array.Array.ArrayDouble:
            raise NotImplementedError('This data type is not yet implemented.')
            # value = self._read_as_numpy(histogram=histogram,
            # dtype=ArrayDouble.ArrayDouble)

        value = numpy.reshape(value, histogram.CurrentShapeAsNumpy())
        return value, histogram.Timestamp(), histogram.Source().decode('utf-8')
