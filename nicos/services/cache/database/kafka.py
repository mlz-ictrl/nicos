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
#
# *****************************************************************************

from time import sleep, time as currenttime

from kafka import KafkaConsumer, KafkaProducer, TopicPartition

from nicos.core import Attach, Param, host, listof
from nicos.core.errors import ConfigurationError
from nicos.protocols.cache import OP_TELLOLD
from nicos.services.cache.database.memory import MemoryCacheDatabase
from nicos.services.cache.entry.serializer import CacheEntrySerializer
from nicos.utils import createThread


class KafkaCacheDatabase(MemoryCacheDatabase):
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
                         type=listof(host(defaultport=9092)),
                         default=['localhost']),
    }

    attached_devices = {
        'serializer': Attach('Device to serialize the cache entry values',
                             CacheEntrySerializer, optional=False)
    }

    def doInit(self, mode):
        MemoryCacheDatabase.doInit(self, mode)

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
                'Topic "%s" does not exist. Create this topic and restart.'
                % self.currenttopic)

        # Assign the partitions
        partitions = self._consumer.partitions_for_topic(self.currenttopic)
        self._consumer.assign(
            [TopicPartition(self.currenttopic, p) for p in partitions])

        # Cleanup thread configuration
        self._stoprequest = False
        self._cleaner = createThread('cleaner', self._clean, start=False)

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
                    msgkey, entry = self._attached_serializer.decode(msg.value)
                    if entry is not None and entry.value is not None:
                        if entry.ttl and entry.time + entry.ttl < now:
                            entry.expired = True

                        self._db[msgkey] = [entry]
        self._cleaner.start()
        self.log.info('Processed %i messages.', message_count)

    def _clean(self):
        def cleanonce():
            with self._db_lock:
                for key, entries in self._db.items():
                    entry = entries[-1]
                    if not entry.value or entry.expired:
                        continue
                    time = currenttime()
                    if entry.ttl and (entry.time + entry.ttl < time):
                        entry.expired = True
                        for client in self._server._connected.values():
                            client.update(key, OP_TELLOLD, entry.value, time,
                                          None)

        while not self._stoprequest:
            sleep(self._long_loop_delay)
            cleanonce()

    def _update_topic(self, key, entry):
        # This method is responsible to communicate and update all the
        # topics that should be updated. Subclasses can (re)implement it
        # if there are messages to be produced to other topics
        self.log.debug('writing: %s -> %s', key, entry.value)

        # For the log-compacted topic key deletion happens when None is
        # passed as the value for the key
        value = None
        if entry.value is not None:
            # Only when the key deletion is not required
            value = self._attached_serializer.encode(key, entry)

        self._producer.send(
            topic=self.currenttopic,
            value=value,
            key=key.encode(),
            timestamp_ms=int(entry.time * 1000))

        # clear all local buffers and produce pending messages
        self._producer.flush()

    def updateEntries(self, categories, subkey, no_store, entry):
        real_update = True
        for cat in categories:
            with self._db_lock:
                entries = self._db.setdefault((cat, subkey), [])
                if entries:
                    lastent = entries[-1]
                    if lastent.value == entry.value and not lastent.expired:
                        # not a real update
                        real_update = False
                entries[:] = [entry]
                if real_update:
                    self._update_topic(f'{cat}/{subkey}', entry)
        return real_update


class KafkaCacheDatabaseWithHistory(KafkaCacheDatabase):
    """ Cache database that stores cache in Kafka topics with History.

    The current values from cache are stored in a log compacted kafka topic
    with key -> value (CacheEntry) pairs. The history is saved in different
    topic without log compaction just as messages. This is done as no deletion
    is required in the history topic and log compaction would not help.
    The encoded messages have key stored in them along with the CacheEntry
    instances.
    """

    parameters = {
        'historytopic': Param(
            'Kafka topic where the history values are stored',
            type=str, mandatory=True),
    }

    def doInit(self, mode):
        KafkaCacheDatabase.doInit(self, mode)

        if self.historytopic not in self._consumer.topics():
            raise ConfigurationError(
                'Topic "%s" does not exist. Create this topic and restart.'
                % self.historytopic)

        # Create the history consumer
        self._history_consumer = KafkaConsumer(bootstrap_servers=self.brokers)

        # Give up if the topic does not exist
        if self.historytopic not in self._history_consumer.topics():
            raise ConfigurationError(
                'Topic "%s" does not exist. Create this topic and restart.'
                % self.historytopic)

        # Assign the partitions
        partitions = self._history_consumer.partitions_for_topic(
            self.historytopic)
        self._history_consumer.assign(
            [TopicPartition(self.historytopic, p) for p in partitions])

    def doShutdown(self):
        self._history_consumer.close()
        KafkaCacheDatabase.doShutdown(self)

    def queryHistory(self, dbkey, fromtime, totime, interval):
        # TODO: implement cache queries with interval here if possible
        _ = interval
        key = f'{dbkey[0]}/{dbkey[1]}'
        self.log.debug('hist for %s in (%s, %s)', dbkey, fromtime, totime)
        buffer_time = 10

        # Get the assignment
        assignment = self._history_consumer.assignment()

        # Reset the offset to match fromtime
        offsets = self._history_consumer.offsets_for_times(
            {p: fromtime * 1000 for p in assignment})

        # The partitions should be in correct location before starting to
        # consume
        for partition in offsets:
            self._history_consumer.seek(partition, offsets[partition].offset)

        end = self._consumer.end_offsets(list(assignment))
        found_some = False
        for partition in assignment:
            while self._history_consumer.position(partition) < end[partition]:
                # pylint: disable=stop-iteration-return
                msg = next(self._history_consumer)
                time = msg.timestamp

                # As the messages are not strictly arranged in the order of
                # timestamp, we read extra messages written in buffer time
                # and try to find if there is something which we need in those
                # messages.
                if time > (totime + buffer_time) * 1000:
                    break

                if msg.value is not None:
                    msgkey, entry = self._attached_serializer.decode(msg.value)
                    if (msgkey == key and not entry.expired and
                            fromtime <= entry.time <= totime and
                            entry.value is not None):
                        self.log.info('%s -> %s', msgkey, entry)
                        found_some = True
                        yield entry

        # Return at least the last value, if none match the range
        if not found_some and dbkey in self._db:
            entry = self._db[dbkey][-1]
            self.log.debug('not found in provided range, fetching current')
            yield entry

    def _update_topic(self, key, entry):
        KafkaCacheDatabase._update_topic(self, key, entry)
        # Send the message to the history topic
        self._producer.send(
            topic=self.historytopic,
            value=self._attached_serializer.encode(key, entry),
            timestamp_ms=int(entry.time * 1000))
        self._producer.flush()
