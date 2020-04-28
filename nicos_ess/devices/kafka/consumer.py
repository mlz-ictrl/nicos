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

from time import sleep

import kafka

from nicos.core import DeviceMixinBase, Param, host, listof
from nicos.core.errors import ConfigurationError
from nicos.utils import createThread


class KafkaSubscriber(DeviceMixinBase):
    """ Receives messages from Kafka, can subscribe to a topic and get all
    new messages from the topic if required via a callback method
    *new_message_callback*.
    """

    parameters = {
        'brokers': Param('List of kafka hosts to be connected',
                         type=listof(host(defaultport=9092)),
                         default=['localhost'], preinit=True, userparam=False)
    }

    def doPreinit(self, mode):
        self._consumer = kafka.KafkaConsumer(
            bootstrap_servers=self.brokers,
            auto_offset_reset='latest'  # start at latest offset
        )

        # Settings for thread to fetch new message
        self._stoprequest = True
        self._updater_thread = None

    def doShutdown(self):
        if self._updater_thread is not None:
            self._stoprequest = True
            if self._updater_thread.is_alive():
                self._updater_thread.join()
            self._consumer.close()

    @property
    def consumer(self):
        return self._consumer

    def subscribe(self, topic):
        """ Create the thread that provides call backs on new messages
        """
        # Remove all the assigned topics
        self._consumer.unsubscribe()

        topics = self._consumer.topics()
        if topic not in topics:
            raise ConfigurationError('Provided topic %s does not exist' % topic)

        # Assign the partitions
        partitions = self._consumer.partitions_for_topic(topic)
        if not partitions:
            raise ConfigurationError('Cannot query partitions for %s' % topic)

        self._consumer.assign([kafka.TopicPartition(topic, p)
                               for p in partitions])
        self._stoprequest = False
        self._updater_thread = createThread('updater_' + topic,
                                            self._get_new_messages)
        self.log.debug('subscribed to updates from topic: %s' % topic)

    def _get_new_messages(self):
        while not self._stoprequest:
            sleep(self._long_loop_delay)

            messages = {}
            data = self._consumer.poll(5)
            for records in data.values():
                for record in records:
                    messages[record.timestamp] = record.value

            if messages:
                self.new_messages_callback(messages)
            else:
                self.no_messages_callback()

    def new_messages_callback(self, messages):
        """This method is called whenever a new messages appear on
        the topic. The subclasses should define this method if
        a callback is required when new messages appear.
        :param messages: dict of timestamp and raw message
        """
        pass

    def no_messages_callback(self):
        """This method is called if no messages are on the topic.
        Subclasses should define this method if they are interested
        in this.
        """
        pass
