# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
import time
import uuid

from confluent_kafka import OFFSET_END, Consumer, KafkaException, \
    TopicPartition

from nicos.core import DeviceMixinBase, Param, host, listof
from nicos.core.constants import SIMULATION
from nicos.core.errors import ConfigurationError
from nicos.utils import createThread

from nicos_ess.devices.kafka.utils import create_sasl_config


class KafkaConsumer:
    """Class for wrapping the Confluent Kafka consumer."""

    @staticmethod
    def create(brokers, starting_offset='latest', **options):
        """Factory method for creating a consumer.

        Will automatically apply SSL settings if they are defined in the
        nicos.conf file.

        :param brokers: The broker addresses to connect to.
        :param starting_offset: Either 'latest' (default) or 'earliest'.
        :param options: Extra configuration options. See the Confluent Kafka
            documents for the full list of options.
        """
        options = {**options, **create_sasl_config()}
        return KafkaConsumer(brokers, starting_offset, **options)

    def __init__(self, brokers, starting_offset='latest', **options):
        """
        :param brokers: The broker addresses to connect to.
        :param starting_offset: Either 'latest' (default) or 'earliest'.
        :param options: Extra configuration options. See the Confluent Kafka
            documents for the full list of options.
        """
        config = {
            'bootstrap.servers': ','.join(brokers),
            'group.id': uuid.uuid4(),
            'auto.offset.reset': starting_offset,
        }
        self._consumer = Consumer({**config, **options})

    def subscribe(self, topic_name, partitions=None):
        """Subscribe to a topic.

        :param topic_name: The topic to subscribe to.
        :param partitions: Which partitions to subscribe to. Optional, defaults
            to all partitions.
        """
        try:
            metadata = self._consumer.list_topics(topic_name, timeout=5)
        except KafkaException as exc:
            raise ConfigurationError('could not obtain metadata for topic '
                                     f'{topic_name}') from exc

        if topic_name not in metadata.topics:
            raise ConfigurationError(f'provided topic {topic_name} does '
                                     'not exist')

        partitions = partitions if partitions \
            else metadata.topics[topic_name].partitions
        topic_partitions = [
            TopicPartition(topic_name, p) for p in partitions
        ]

        self._consumer.assign(topic_partitions)

    def unsubscribe(self):
        """Remove any existing subscriptions."""
        self._consumer.unsubscribe()

    def poll(self, timeout_ms=5):
        """Poll for messages.

        Note: returns at most one message.

        :param timeout_ms: The poll timeout
        :return: A message or None if no message received within the
            timeout.
        """
        return self._consumer.poll(timeout_ms // 1000)

    def close(self):
        """Close the consumer."""
        self._consumer.close()

    def topics(self):
        """
        :return: A list of topics.
        """
        return self._consumer.list_topics()

    def seek(self, topic_name, partition, offset, timeout_s=5):
        """Seek to a particular offset on a partition.

        :param topic_name: The topic name.
        :param partition: The partition to seek on.
        :param offset: The required offset.
        :param timeout_s: The timeout in seconds.
        """
        topic_partition = TopicPartition(topic_name, partition)
        topic_partition.offset = offset
        self._seek([topic_partition], timeout_s)

    def _seek(self, partitions, timeout_s):
        # Seek will fail if called too soon after assign.
        # Therefore, try a few times.
        start = time.monotonic()
        while time.monotonic() < start + timeout_s:
            for part in partitions:
                try:
                    self._consumer.seek(part)
                except KafkaException:
                    time.sleep(0.1)
            return
        raise RuntimeError('failed to seek offset')

    def assignment(self):
        """
        :return: A list of assigned topic partitions.
        """
        return self._consumer.assignment()

    def seek_to_end(self, timeout_s=5):
        """Move the consumer to the end of the partition(s).

        :param timeout_s: The timeout in seconds.
        """
        partitions = self._consumer.assignment()
        for tp in partitions:
            tp.offset = OFFSET_END
        self._seek(partitions, timeout_s)


class KafkaSubscriber(DeviceMixinBase):
    """ Receives messages from Kafka, can subscribe to a topic and get all
    new messages from the topic if required via a callback method
    *new_message_callback*.
    """

    parameters = {
        'brokers':
            Param('List of kafka brokers to connect to',
                  type=listof(host(defaultport=9092)),
                  mandatory=True,
                  preinit=True,
                  userparam=False)
    }
    _updater_thread = None

    def doPreinit(self, mode):
        if mode != SIMULATION:
            self._consumer = KafkaConsumer.create(self.brokers)
        else:
            self._consumer = None

        # Settings for thread to fetch new message
        self._stoprequest = True

    def doShutdown(self):
        if self._updater_thread is not None:
            self._stoprequest = True
            if self._updater_thread.is_alive():
                self._updater_thread.join()
            if self._consumer:
                self._consumer.close()

    @property
    def consumer(self):
        return self._consumer

    def subscribe(self, topic):
        """ Create the thread that provides call backs on new messages
        """
        # Remove all the assigned topics
        self._consumer.unsubscribe()

        self._consumer.subscribe(topic)

        self._stoprequest = False
        self._updater_thread = createThread('updater_' + topic,
                                            self._get_new_messages)
        self.log.debug('subscribed to updates from topic: %s' % topic)

    def _get_new_messages(self):
        while not self._stoprequest:
            time.sleep(self._long_loop_delay)

            messages = []
            data = self._consumer.poll(timeout_ms=5)
            if data:
                messages.append((data.timestamp(), data.value()))

            if messages:
                self.new_messages_callback(messages)
            else:
                self.no_messages_callback()
        self.log.debug("KafkaSubscriber thread finished")

    def new_messages_callback(self, messages):
        """This method is called whenever a new messages appear on
        the topic. The subclasses should define this method if
        a callback is required when new messages appear.
        :param messages: list of tuples of timestamp and raw message
        """

    def no_messages_callback(self):
        """This method is called if no messages are on the topic.
        Subclasses should define this method if they are interested
        in this.
        """
