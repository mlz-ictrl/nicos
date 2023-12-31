# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

from confluent_kafka import Producer

from nicos.core import DeviceMixinBase, Param, host, listof
from nicos.core.constants import SIMULATION

from nicos_ess.devices.kafka.utils import create_sasl_config


MAX_MESSAGE_SIZE = 209_715_200


class KafkaProducer:
    """Class for wrapping the Confluent Kafka producer."""

    @staticmethod
    def create(brokers, **options):
        """Factory method for creating a producer.

        Will automatically apply SSL settings if they are defined in the
        nicos.conf file.

        :param brokers: The broker addresses to connect to.
        :param options: Extra configuration options. See the Confluent Kafka
            documents for the full list of options.
        """
        options = {**options, **create_sasl_config()}
        return KafkaProducer(brokers, **options)

    def __init__(self, brokers, **options):
        """
        :param brokers: The broker addresses to connect to.
        :param options: Extra configuration options. See the Confluent Kafka
            documents for the full list of options.
        """
        config = {
            'bootstrap.servers': ','.join(brokers),
            'message.max.bytes': MAX_MESSAGE_SIZE,
        }
        self._producer = Producer({**config, **options})

    def produce(self, topic_name, message, partition=-1, key=None,
                on_delivery_callback=None):
        """Send a message to Kafka.

        :param topic_name: The topic to send to.
        :param message: The message.
        :param partition: Which partition to send to. Optional.
        :param key: The key to assign. Optional
        :param on_delivery_callback: The delivery callback. Optional.
        """
        self._producer.produce(topic_name, message, partition=partition,
                               key=key, on_delivery=on_delivery_callback)
        self._producer.flush()


class ProducesKafkaMessages(DeviceMixinBase):
    """ Device to produce messages to kafka. The method *send* can be used
    to produce a timestamped message onto the topic. Kafka brokers
    can be specified using the parameter *brokers*.
    """

    parameters = {
        'brokers':
            Param('List of kafka brokers to connect to',
                  type=listof(host(defaultport=9092)),
                  mandatory=True,
                  preinit=True,
                  userparam=False),
        'max_request_size':
            Param('Maximum size of kafka message',
                  type=int,
                  default=16000000,
                  preinit=True,
                  userparam=False),
    }

    def doPreinit(self, mode):
        if mode != SIMULATION:
            self._producer = self._create_producer(
                max_request_size=self.max_request_size)
        else:
            self._producer = None

    def _create_producer(self, **options):
        return KafkaProducer.create(self.brokers, **options)

    def _setProducerConfig(self, **configs):
        self._producer = self._create_producer(**configs)

    def send(self, topic, message):
        """
        Produces and flushes the provided message
        :param topic: Topic on which the message is to be produced
        :param message: Message
        :return:
        """
        self._producer.produce(topic, message)
        self._producer.flush()
