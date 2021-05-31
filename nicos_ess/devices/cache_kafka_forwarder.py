#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
#   Ebad Kamil <ebad.kamil@ess.eu>
#
# *****************************************************************************
import queue
import time
from threading import Lock

from kafka import KafkaProducer
from streaming_data_types.fbschemas.logdata_f142.AlarmSeverity import \
    AlarmSeverity
from streaming_data_types.fbschemas.logdata_f142.AlarmStatus import AlarmStatus
from streaming_data_types.logdata_f142 import serialise_f142

from nicos.core import Device, Override, Param, host, listof, status
from nicos.protocols.cache import cache_load
from nicos.services.collector import ForwarderBase
from nicos.utils import createThread

nicos_status_to_f142 = {
    status.OK: AlarmSeverity.NO_ALARM,
    status.WARN: AlarmSeverity.MINOR,
    status.ERROR: AlarmSeverity.MAJOR,
}


def convert_status(nicos_status):
    """Convert the NICOS status into the corresponding f142 schema severity.

    Policy decision: treat everything that is not WARN or ERROR as OK.

    :param nicos_status: the NICOS status
    :return: the f142 schema severity
    """
    return nicos_status_to_f142.get(nicos_status, AlarmSeverity.NO_ALARM)


def to_f142(dev_name, dev_value, dev_severity, timestamp_ns):
    """Convert the device information in to an f142 FlatBuffer.

    :param dev_name: the device name
    :param dev_value: the device's value
    :param dev_severity: the device's status
    :param timestamp_ns: the associated timestamp in nanoseconds
    :return: FlatBuffer representation of data
    """
    # Alarm status is not relevant for NICOS but we have to send something
    return serialise_f142(dev_value, dev_name, timestamp_ns,
                          AlarmStatus.NO_ALARM, dev_severity)


class CacheKafkaForwarder(ForwarderBase, Device):
    parameters = {
        'brokers': Param('List of kafka hosts to be connected',
                         type=listof(host(defaultport=9092)),
                         mandatory=True, preinit=True, userparam=False
                         ),
        'output_topic': Param('The topic to send data to',
                              type=str, userparam=False, settable=False,
                              mandatory=True,
                              ),
        'dev_ignore': Param('Devices to ignore; if empty, all devices are '
                            'accepted', default=[],
                            type=listof(str),
                            ),
        'update_interval': Param('Time interval (in secs.) to send regular updates',
                                 default=10.0, type=float, settable=False)

    }
    parameter_overrides = {
        # Key filters are irrelevant for this collector
        'keyfilters': Override(default=[], settable=False),
    }

    def doInit(self, mode):
        self._dev_to_value_cache = {}
        self._dev_to_status_cache = {}
        self._dev_to_timestamp_cache = {}
        self._producer = None
        self._lock = Lock()

        self._initFilters()
        self._queue = queue.Queue(1000)
        self._worker = createThread('cache_to_kafka', self._processQueue,
                                    start=False)
        self._regular_update_worker = createThread(
            'send_regular_updates', self._poll_updates, start=False)
        while not self._producer:
            try:
                self._producer = \
                    KafkaProducer(bootstrap_servers=self._config['brokers'])
            except Exception as error:
                self.log.error(
                    'Could not connect to Kafka - will try again soon: %s',
                    error)
                time.sleep(5)
        self.log.info('Connected to Kafka brokers %s', self._config['brokers'])

    def _startWorker(self):
        self._worker.start()
        self._regular_update_worker.start()

    def _poll_updates(self):
        while True:
            with self._lock:
                for dev_name in set(self._dev_to_value_cache.keys()).union(
                        self._dev_to_status_cache.keys()):
                    if self._relevant_properties_available(dev_name):
                        self._push_to_queue(
                            dev_name,
                            self._dev_to_value_cache[dev_name],
                            self._dev_to_status_cache[dev_name],
                            self._dev_to_timestamp_cache[dev_name])

            time.sleep(self.update_interval)

    def _checkKey(self, key):
        if key.endswith('/value') or key.endswith('/status'):
            return True
        return False

    def _checkDevice(self, name):
        if name not in self.dev_ignore:
            return True
        return False

    def _putChange(self, timestamp, ttl, key, value):
        if value is None:
            return
        dev_name = key[0:key.index('/')]
        if not self._checkKey(key) or not self._checkDevice(dev_name):
            return
        self.log.debug('_putChange %s %s %s', key, value, time)

        with self._lock:
            if key.endswith('value'):
                self._dev_to_value_cache[dev_name] = value
            else:
                self._dev_to_status_cache[dev_name] = convert_status(value)

            timestamp_ns = int(float(timestamp) * 10 ** 9)
            self._dev_to_timestamp_cache[dev_name] = timestamp_ns
            # Don't send until have at least one reading for both value and status
            if self._relevant_properties_available(dev_name):
                self._push_to_queue(
                    dev_name,
                    self._dev_to_value_cache[dev_name],
                    self._dev_to_status_cache[dev_name],
                    timestamp_ns,)

    def _relevant_properties_available(self, dev_name):
        return dev_name in self._dev_to_value_cache \
            and dev_name in self._dev_to_status_cache \
            and dev_name in self._dev_to_timestamp_cache

    def _push_to_queue(self, dev_name, value, status, timestamp):
        try:
            self._queue.put_nowait((dev_name, value, status, timestamp))
        except queue.Full:
            self.log.error('Queue full, so discarding older value(s)')
            self._queue.get()
            self._queue.put((dev_name, value, status, timestamp))
            self._queue.task_done()

    def _processQueue(self):
        while True:
            name, value, status, timestamp = self._queue.get()
            try:
                # Convert value from string to correct type
                value = cache_load(value)
                if not isinstance(value, str):
                    # Policy decision: don't send strings via f142
                    buffer = to_f142(name, value, status, timestamp)
                    self._send_to_kafka(buffer)
            except Exception as error:
                self.log.error('Could not forward data: %s', error)
            self._queue.task_done()

    def doShutdown(self):
        self._producer.close()

    def _send_to_kafka(self, buffer):
        self._producer.send(self.output_topic, buffer)
        self._producer.flush(timeout=3)
