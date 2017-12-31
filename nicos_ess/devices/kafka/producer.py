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

import kafka

from nicos.core import DeviceMixinBase, Param, listof, host


class ProducesKafkaMessages(DeviceMixinBase):
    """ Device to produce messages to kafka. The method *send* can be used
    to produce a timestamped message onto the topic. Kafka brokers
    can be specified using the parameter *brokers*.
    """

    parameters = {
        'brokers': Param('List of kafka hosts to be connected',
                         type=listof(host), default=['localhost:9092'],
                         preinit=True)
    }

    def doPreinit(self, mode):
        self._producer = kafka.KafkaProducer(bootstrap_servers=self.brokers)

    def doShutdown(self):
        self._producer.close()

    def send(self, topic, message, key=None, timestamp=None, partition=None):
        """
        Produces and flushes the provided message
        :param topic: Topic on which the message is to be produced
        :param message: Message
        :param key: key, for a compacted topic
        :param timestamp: message timestamp in milliseconds
        :param partition: partition on which the message is to be produced
        :return:
        """
        self._producer.send(topic, message, key, partition, timestamp)
        self._producer.flush()
