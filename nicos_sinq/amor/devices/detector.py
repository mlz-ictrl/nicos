# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#  Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

import time

import streaming_data_types
from confluent_kafka import TopicPartition

from nicos import session
from nicos.core import status
from nicos.core.constants import POLLER
from nicos.core.device import Readable
from nicos.core.params import Override, Param

from nicos_sinq.devices.kafka.consumer import KafkaSubscriber


class DetectorRate(KafkaSubscriber, Readable):
    """
    A device to read the detector event rate from the corresponding Kafka topic.

    This device polls the latest message from an ev44-encoded Kafka topic
    every self._long_loop_delay seconds and calculates the current detector
    event rate. The message frequency itself is defined by the chopper speed,
    which is made available as an attached device.
    """

    parameters = {
        'topic': Param('Detector message topic',
                  type=str,
                  settable=False,
                  preinit=True,
                  mandatory=True,
                  userparam=False),
        'error_msg': Param('Error message',
                  type=str,
                  settable=False,
                  userparam=False,
                  default='')
    }

    parameter_overrides = {
        'unit': Override(default='1/s'),
    }

    def doPreinit(self, mode):
        KafkaSubscriber.doPreinit(self, mode)
        if session.sessiontype == POLLER:
            self.subscribe(self.topic)

    def _get_new_messages(self):
        # The entire loop is wrapped in a try-except so it can forward any
        # issues to the doStatus method.

        # Delete any leftover error messages
        self._cache.put(self._name, 'error_msg', '', time.time())
        try:
            consumer = self._consumer._consumer
            tp = TopicPartition(self.topic, 0)
            while not self._stoprequest:
                session.delay(self._long_loop_delay)

                low, high = consumer.get_watermark_offsets(tp)
                last_offset = high - 1

                if last_offset > low:
                    consumer.seek(TopicPartition(self.topic, 0, last_offset))

                    # A new update should be available after 5 seconds latest.
                    data = consumer.poll(5)

                    if data is not None:
                        rate = streaming_data_types.deserialise_f144(data.value())

                        # Force fast cache updates
                        self._cache.put(self._name, 'value', rate.value, time.time())
                        continue

                # In case no new information is available on Kafka, assume that
                # the detector rate is currently zero.
                self._cache.put(self._name, 'value', 0, time.time())

        except Exception as e:
            self._cache.put(self._name, 'error_msg', str(e), time.time())

    def doRead(self, maxage=0):
        return self._cache.get(self._name, 'value', None)

    def doStatus(self, maxage=0):
        if self.error_msg:
            return status.ERROR, self.error_msg
        return status.OK, ''

    def doReset(self):
        """
        Restarts the Kafka messages poller thread, if it has crashed.
        """
        if self.error_msg:
            self._cache.put(self._name, 'error_msg', '', time.time())
            self.subscribe(self.topic)
