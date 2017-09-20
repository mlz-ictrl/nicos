#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import

from time import sleep, time as currenttime

from kafka import KafkaConsumer, KafkaProducer, TopicPartition

from nicos.core import Param, Attach, listof, host
from nicos.core.errors import ConfigurationError
from nicos.protocols.cache import OP_TELL, OP_TELLOLD, FLAG_NO_STORE
from nicos.pycompat import iteritems
from nicos.services.cache.database.base import CacheDatabase
from nicos.services.cache.database.entry import CacheEntry, \
    CacheEntrySerializer
from nicos.utils import createThread


class KafkaCacheDatabase(CacheDatabase):
    """ Cache database that stores cache in Kafka topics without History.

    Current key and value pairs are stored in Kafka using log compaction.
    The `CacheEntry` values can be serialized using the attached device. This
    is then used to encode and decode entry instances while producing to
    the Kafka topic and while consuming from it.

    The data is stored in the Kafka topics using log compaction. Log
    compaction ensures that Kafka will always retain at least the last
    known value for each message key within the log of data for a single
    topic partition.

    The keys for partitioning are the keys received from cache server and
    the timestamp of the message is same as the time of the cache entry.
    If the provided `topic` does not exist, the cache database will not
    be able to proceed. Use the command line kafka tool to create the topic.

    This database will connect to the kafka and zookeeper services so
    they should be running in background on the provided `hosts`. For
    a basic getting started with kafka one can use the following guide:
    https://kafka.apache.org/quickstart

    Note that the minimum kafka broker version required for this
    database to run properly is 0.11.0. Before this version timestamps
    for messages could not be set.

    The default behavior of Kafka does not ensure that the topic will
    be cleaned up using the log compaction policy. For this to happen
    one of the following two is to be done:

    * Create topic by CLI Kafka tools using --config cleanup.policy=compact
    * Set in server.properties log.cleanup.policy=compact

    History is NOT supported with this database.
    """
    parameters = {
        'currenttopic': Param(
            'Kafka topic where the current values of cache are streamed',
            type=str, mandatory=True),
        'brokers': Param('List of Kafka bootstrap servers.',
                         type=listof(host), default=['localhost:9092']),
    }

    attached_devices = {
        'serializer': Attach('Device to serialize the cache entry values',
                             CacheEntrySerializer, optional=False)
    }

    def doInit(self, mode):
        CacheDatabase.doInit(self, mode)

        self._db = {}  # Dict holding current values in memory

        # Create the producer
        self._producer = KafkaProducer(bootstrap_servers=self.brokers)

        # Create the consumer
        self._consumer = KafkaConsumer(
            bootstrap_servers=self.brokers,
            auto_offset_reset='earliest'  # start at earliest topic
        )

        # Give up if the topic does not exist
        if self.currenttopic not in self._consumer.topics():
            raise ConfigurationError(
                'Topic "%s" does not exit. Create this topic and restart.'
                % self.currenttopic)

        # Assign the partitions
        partitions = self._consumer.partitions_for_topic(self.currenttopic)
        self._consumer.assign(
            [TopicPartition(self.currenttopic, p) for p in partitions])

        # Cleanup thread configuration
        self._stoprequest = False
        self._cleaner = createThread('cleaner', self._clean)

    def doShutdown(self):
        self._consumer.close()
        self._producer.close()

        # Stop the cleaner thread
        self._stoprequest = True
        self._cleaner.join()

    def initDatabase(self):
        self.log.info('Reading messages from kafka topic - %s',
                      self.currenttopic)
        now = currenttime()
        message_count = 0
        end = self._consumer.end_offsets(list(self._consumer.assignment()))
        for partition in self._consumer.assignment():
            while self._consumer.position(partition) < end[partition]:
                msg = next(self._consumer)
                message_count += 1
                if msg.value is not None:
                    _, entry = self._attached_serializer.decode(msg.value)
                    if entry is not None:
                        # self.log.debug('%s (%s): %s -> %s', msg.offset,
                        #               msg.timestamp, msg.key, entry)
                        if entry.ttl and entry.time + entry.ttl < now:
                            entry.expired = True

                        self._db[msg.key] = entry

        self.log.info('Processed %i messages.', message_count)

    def ask(self, key, ts, time, ttl):
        # self.log.info('Ask: %s' % key)
        if key not in self._db:
            return [key + OP_TELLOLD + '\n']

        entry = self._db[key]
        if entry.ttl and entry.time + entry.ttl < currenttime():
            entry.expired = True

        # check for removed keys
        if entry.value is None:
            return [key + OP_TELLOLD + '\n']

        # check for expired keys
        op = entry.expired and OP_TELLOLD or OP_TELL

        # Write the correct value
        if entry.ttl:
            if ts:
                return ['%r+%s@%s%s%s\n' % (entry.time, entry.ttl,
                                            key, op, entry.value)]
            else:
                return [key + op + entry.value + '\n']
        if ts:
            return ['%r@%s%s%s\n' % (entry.time, key, op, entry.value)]
        else:
            return [key + op + entry.value + '\n']

    def ask_wc(self, key, ts, time, ttl):
        # self.log.info('Ask WC: %s' % key)
        ret = set()
        for k in self._db:
            if key in k:
                entry = self._db[k]
                if entry.ttl and entry.time + entry.ttl < currenttime():
                    entry.expired = True

                # check for removed keys
                if entry.value is None:
                    continue

                # check for expired keys
                op = entry.expired and OP_TELLOLD or OP_TELL
                if entry.ttl:
                    if ts:
                        ret.add('%r+%s@%s%s%s\n' %
                                (entry.time, entry.ttl, k,
                                 op, entry.value))
                    else:
                        ret.add(k + op + entry.value + '\n')
                elif ts:
                    ret.add('%r@%s%s%s\n' % (entry.time, k,
                                             op, entry.value))
                else:
                    ret.add(k + op + entry.value + '\n')
        return [''.join(ret)]

    def ask_hist(self, key, fromtime, totime):
        return []

    def _clean(self):
        def cleanonce():
            for key, entry in iteritems(self._db):
                if not entry.value or entry.expired:
                    continue
                time = currenttime()
                if entry.ttl and (entry.time + entry.ttl < time):
                    entry.expired = True
                    for client in self._server._connected.values():
                        client.update(key, OP_TELLOLD, entry.value, time, None)

        while not self._stoprequest:
            sleep(self._long_loop_delay)
            cleanonce()

    def _update_topic(self, key, entry):
        # This method is responsible to communicate and update all the
        # topics that should be updated. Subclasses can (re)implement it
        # if there are messages to be produced to other topics
        # self.log.info('Writing: %s -> %s', key, entry.value)
        self._producer.send(
            topic=self.currenttopic,
            value=self._attached_serializer.encode(entry, key),
            key=bytes(key),
            timestamp_ms=entry.time * 1000)
        # clear all local buffers and produce pending messages
        self._producer.flush()

    def tell(self, key, value, time, ttl, from_client):
        # self.log.info('Updating: %s=%s' % (key, value))
        now = currenttime()
        if time is None:
            time = now

        store_on_disk = True
        if key.endswith(FLAG_NO_STORE):
            key = key[:-len(FLAG_NO_STORE)]
            store_on_disk = False

        category = '/'.join(key.split('/')[:-1])
        subkey = key.split('/')[-1]
        newcats = [category]
        if category in self._rewrites:
            newcats.extend(self._rewrites[category])

        for newcat in newcats:
            newkey = '/'.join((newcat, subkey))
            update = True
            if newkey in self._db:
                entry = self._db[newkey]
                if entry.value == value and not entry.expired:
                    # existing entry with the same value: update the TTL
                    # but don't write an update to the history file
                    entry.time = time
                    entry.ttl = ttl
                    update = not store_on_disk
                elif value is None and entry.expired:
                    # do not delete old value, it is already expired
                    update = not store_on_disk

            if update:
                entry = CacheEntry(time, ttl, value)
                self._db[newkey] = entry
                if store_on_disk:
                    self._update_topic(newkey, entry)

            if update and (not ttl or time + ttl > now):
                for client in self._server._connected.values():
                    if client is not from_client:
                        client.update(newkey, OP_TELL, value or '', time, ttl)
