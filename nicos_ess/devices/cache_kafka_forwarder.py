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
#   Matt Clarke <matt.clarke@ess.eu>
#   Ebad Kamil <ebad.kamil@ess.eu>
#
# *****************************************************************************
import queue
import time
from threading import Lock

from streaming_data_types.alarm_al00 import Severity, serialise_al00
from streaming_data_types.logdata_f144 import serialise_f144

from nicos.core import Device, Override, Param, host, listof, status
from nicos.protocols.cache import cache_load
from nicos.services.collector import ForwarderBase
from nicos.utils import createThread
from nicos_ess.devices.kafka.producer import KafkaProducer

nicos_status_to_al00 = {
    status.OK: Severity.OK,
    status.WARN: Severity.MINOR,
    status.ERROR: Severity.MAJOR,
    status.UNKNOWN: Severity.INVALID
}


def convert_status(nicos_status):
    """Convert the NICOS status into the corresponding al00 schema severity.

    Policy decision: treat everything that is not WARN or ERROR as OK.

    :param nicos_status: the NICOS status
    :return: the al00 schema severity
    """
    severity, msg = cache_load(nicos_status)
    return nicos_status_to_al00.get(severity, Severity.OK), msg


def to_f144(dev_name, dev_value, timestamp_ns):
    """Convert the device information into an f144 FlatBuffer.

    :param dev_name: the device name
    :param dev_value: the device's value
    :param timestamp_ns: the associated timestamp in nanoseconds
    :return: FlatBuffer representation of data
    """
    return serialise_f144(dev_name, dev_value, timestamp_ns)


class CacheKafkaForwarder(ForwarderBase, Device):
    parameters = {
        'brokers':
            Param('List of kafka brokers to connect to',
                  type=listof(host(defaultport=9092)),
                  mandatory=True,
                  preinit=True,
                  userparam=False),
        'output_topic':
            Param(
                'The topic to send data to',
                type=str,
                userparam=False,
                settable=False,
                mandatory=True,
            ),
        'dev_ignore':
            Param(
                'Devices to ignore; if empty, all devices are '
                'accepted',
                default=[],
                type=listof(str),
            ),
        'update_interval':
            Param('Time interval (in secs.) to send regular updates',
                  default=10.0,
                  type=float,
                  settable=False),
    }
    parameter_overrides = {
        # Key filters are irrelevant for this collector
        'keyfilters': Override(default=[], settable=False),
    }

    def doInit(self, mode):
        self._dev_to_value_cache = {}
        self._dev_to_status_cache = {}
        self._producer = None
        self._lock = Lock()

        self._initFilters()
        self._queue = queue.Queue(1000)
        self._worker = createThread('cache_to_kafka',
                                    self._processQueue,
                                    start=False)
        self._regular_update_worker = createThread('send_regular_updates',
                                                   self._poll_updates,
                                                   start=False)
        while not self._producer:
            try:
                self._producer = KafkaProducer.create(self.brokers)
            except Exception as error:
                self.log.error(
                    'Could not connect to Kafka - will try again soon: %s',
                    error)
                time.sleep(5)
        self.log.info('Connected to Kafka brokers %s', self.brokers)

    def _startWorker(self):
        self._worker.start()
        self._regular_update_worker.start()

    def _poll_updates(self):
        while True:
            with self._lock:
                for name, (value,
                           timestamp) in self._dev_to_value_cache.items():
                    self._push_to_queue(name, value, timestamp, True)
                for name, (value,
                           timestamp) in self._dev_to_status_cache.items():
                    self._push_to_queue(name, value, timestamp, False)

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
        self.log.debug('_putChange %s %s %s', key, value, timestamp)

        with self._lock:
            timestamp_ns = int(float(timestamp) * 10**9)
            if key.endswith('value'):
                self._dev_to_value_cache[dev_name] = (value, timestamp_ns)
                self._push_to_queue(dev_name, value, timestamp_ns, True)
            else:
                self._dev_to_status_cache[dev_name] = (convert_status(value),
                                                       timestamp_ns)
                self._push_to_queue(dev_name,
                                    *self._dev_to_status_cache[dev_name],
                                    False)

    def _push_to_queue(self, dev_name, value, timestamp, is_value):
        try:
            self._queue.put_nowait((dev_name, value, timestamp, is_value))
        except queue.Full:
            self.log.error('Queue full, so discarding older value(s)')
            self._queue.get()
            self._queue.put((dev_name, value, timestamp, is_value))
            self._queue.task_done()

    def _processQueue(self):
        while True:
            name, value, timestamp, is_value = self._queue.get()
            try:
                if is_value:
                    # Convert value from string to correct type
                    value = cache_load(value)
                    if not isinstance(value, str):
                        # Policy decision: don't send strings via f144
                        buffer = to_f144(name, value, timestamp)
                        self._send_to_kafka(buffer, name)
                else:
                    buffer = serialise_al00(name, timestamp, value[0],
                                            value[1])
                    self._send_to_kafka(buffer, name)
            except Exception as error:
                self.log.error('Could not forward data: %s', error)
            self._queue.task_done()

    def _send_to_kafka(self, buffer, name):
        self._producer.produce(self.output_topic, buffer,
                               key=name.encode('utf-8'))

