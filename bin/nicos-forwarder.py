import argparse
import sys
import time
from dataclasses import dataclass
from os import path
from threading import RLock
from time import time_ns
from typing import Any

from kafka import KafkaProducer
from streaming_data_types.logdata_f142 import serialise_f142
from streaming_data_types.fbschemas.logdata_f142.AlarmSeverity import \
    AlarmSeverity
from streaming_data_types.fbschemas.logdata_f142.AlarmStatus import AlarmStatus

sys.path.insert(0, path.dirname(path.dirname(path.realpath(__file__))))

from nicos.core import status
from nicos.core.sessions.simple import SingleDeviceSession
from nicos.devices.cacheclient import CacheClient
from nicos.utils import createThread


# Policy decision: treat everything that is not WARN or ERROR as OK
nicos_status_to_f142 = {
    status.OK: AlarmSeverity.NO_ALARM,
    status.WARN: AlarmSeverity.MINOR,
    status.ERROR: AlarmSeverity.MAJOR,
}


@dataclass
class DeviceState:
    value: Any
    status: int


class ForwarderApp(CacheClient):
    _status_value_cache = {}
    _current_devices = set()
    _device_watcher = None
    _producer = None
    _lock = RLock()

    def doInit(self, mode):
        CacheClient.doInit(self, mode)
        self._status_value_cache = {}
        self._current_devices = set()
        self._lock = RLock()

        while not self._producer:
            try:
                self._producer = \
                    KafkaProducer(bootstrap_servers=self._config['brokers'])
            except Exception as error:
                self.log.error(
                    f'Could not connect to Kafka - will try again soon: {error}'
                )
                time.sleep(5)
        self.log.info(f'Connected to Kafka brokers {self._config["brokers"]}')

        # Wait until connected to nicos
        while not self.getDeviceList():
            time.sleep(0.1)

    def getDeviceList(self, only_explicit=True, special_clause=None):
        devlist = [key[:-6] for (key, _) in self.query_db('')
                   if key.endswith('/value')]
        if special_clause:
            devlist = [dn for dn in devlist
                       if eval(special_clause, {'dn': dn})]
        return sorted(devlist)

    def getDeviceParam(self, devname, parname):
        return self.get(devname, parname)

    def start(self, *args):
        self._device_watcher = createThread('device list watcher',
                                            self.monitor_device_list,
                                            start=False)
        self._device_watcher.start()

    def monitor_device_list(self):
        while True:
            try:
                devices = set(self.getDeviceList())
                if devices != self._current_devices:
                    self.log.info('Device list changed')
                    with self._lock:
                        self.remove_current_callbacks()
                        self._status_value_cache.clear()
                        self.create_callbacks(devices)
                        self._current_devices = devices
                time.sleep(0.1)
            except Exception as error:
                self.log.exception(
                    f'exception in device watcher thread {error}')
                if self._stoprequest:
                    break  # ensure we do not restart during shutdown

    def remove_current_callbacks(self):
        for dev in self._current_devices:
            self.removeCallback(dev, 'status', self.changed_value_callback)
            self.removeCallback(dev, 'value', self.changed_value_callback)

    def create_callbacks(self, devices):
        for dev_name in devices:
            self.log.info(f'Added {dev_name}')
            current_status = self._convert_status(self.getDeviceParam(dev_name,
                                                                      'status'))
            current_value = self.getDeviceParam(dev_name, 'value')
            self._status_value_cache[dev_name] = \
                DeviceState(current_status, current_value)
            self._send_device_info(dev_name, current_value, time_ns(),
                                   current_status)
            self.addCallback(dev_name, 'status', self.change_status_callback)
            self.addCallback(dev_name, 'value', self.changed_value_callback)

    @staticmethod
    def _convert_status(nicos_status):
        return nicos_status_to_f142.get(nicos_status[0], AlarmSeverity.NO_ALARM)

    def changed_value_callback(self, name, new_value, timestamp_s, *args,
                               **kwargs):
        dev_name = name[0:name.index('/')]
        self.log.info(f'{dev_name} value changed to {new_value}')
        with self._lock:
            self._status_value_cache[dev_name].value = new_value
        self._send_device_info(dev_name, new_value,
                               int(timestamp_s * 10 ** 9),
                               AlarmSeverity.NO_CHANGE)

    def change_status_callback(self, name, new_status, timestamp_s, *args,
                               **kwargs):
        dev_name = name[0:name.index('/')]
        self.log.info(f'{dev_name} status changed to {new_status}')
        new_status = self._convert_status(new_status)
        with self._lock:
            if new_status == self._status_value_cache[dev_name].status:
                # No change so nothing to do
                return
            self._status_value_cache[dev_name].status = new_status
            value = self._status_value_cache[dev_name].value
        self._send_device_info(dev_name, value, int(timestamp_s * 10 ** 9),
                               new_status)

    def _send_device_info(self, dev_name, dev_value, timestamp_ns,
                          dev_status):
        if isinstance(dev_value, str):
            # Policy decision: don't send strings via f142
            return

        try:
            buffer = self._to_f142(dev_name, dev_value, timestamp_ns,
                                   dev_status)
            self.send_to_kafka(buffer)
        except Exception as error:
            self.log.error(f'Could not send device status: {error}')

    @staticmethod
    def _to_f142(name, value, timestamp, severity):
        # Alarm status is not relevant for NICOS but we have to send something
        return serialise_f142(value, name, timestamp, AlarmStatus.NO_ALARM,
                              severity)

    def send_to_kafka(self, buffer):
        self._producer.send(self._config['topic'], buffer)
        self._producer.flush(timeout=3)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-b', '--brokers', type=str, nargs='+',
                               help='the Kafka broker addresses',
                               required=True,)

    required_args.add_argument('-t', '--topic', type=str,
                               help='the topic to write device data to',
                               required=True)

    parser.add_argument('-c', '--cache', action='store',
                        help='the server:port for the cache',
                        default='localhost:14869')

    args = parser.parse_args()

    SingleDeviceSession.run('forwarder', ForwarderApp,
                            {'prefix': 'nicos', 'cache': args.cache,
                             'brokers': args.brokers, 'topic': args.topic},
                            pidfile=False)
