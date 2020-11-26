import sys
import time
from dataclasses import dataclass
from os import path
from threading import RLock
from time import time_ns
from typing import Any, Tuple

from nicos.core import status

sys.path.insert(0, path.dirname(path.dirname(path.realpath(__file__))))

from kafka import KafkaProducer
from nicos.core.sessions.simple import SingleDeviceSession
from nicos.devices.cacheclient import CacheClient
from nicos.utils import createThread
from streaming_data_types.logdata_f142 import serialise_f142
from streaming_data_types.fbschemas.logdata_f142.AlarmSeverity import AlarmSeverity


# Treat everything that is not WARN or ERROR as OK
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
    _lock = RLock()

    def start(self, *args):
        self._device_watcher = createThread('device watcher', self.device_thread,
                                            start=False)
        self._device_watcher.start()

    def device_thread(self):
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
            except Exception:
                self.log.exception('exception in device watcher thread')
                if self._stoprequest:
                    break  # ensure we do not restart during shutdown

    def remove_current_callbacks(self):
        for dev in self._current_devices:
            self.removeCallback(dev, 'status', self.changed_value_callback)
            self.removeCallback(dev, 'value', self.changed_value_callback)

    def create_callbacks(self, devices):
        for dev in devices:
            self.log.info(f'Added {dev}')
            current_status = self._convert_status(self.getDeviceParam(dev, 'status'))
            current_value = self.getDeviceParam(dev, 'value')
            # TODO: send initial values to kafka
            self._status_value_cache[dev] = \
                DeviceState(current_status, current_value)
            self.addCallback(dev, 'status', self.change_status_callback)
            self.addCallback(dev, 'value', self.changed_value_callback)

    @staticmethod
    def _convert_status(nicos_status):
        return nicos_status_to_f142.get(nicos_status[0], AlarmSeverity.NO_ALARM)

    def changed_value_callback(self, name, new_value, timestamp_s, *args, **kwargs):
        dev_name = name[0:name.index('/')]
        self.log.info(f'{dev_name} value changed to {new_value}')
        with self._lock:
            self._status_value_cache[dev_name].value = new_value
        buffer = self._to_f142(dev_name, new_value, int(timestamp_s * 10 ** 9),
                               AlarmSeverity.NO_CHANGE)
        self.send_to_kafka(buffer)

    def change_status_callback(self, name, new_status, timestamp_s, *args, **kwargs):
        dev_name = name[0:name.index('/')]
        self.log.info(f'{dev_name} status changed to {new_status}')
        new_status = self._convert_status(new_status)
        with self._lock:
            if new_status == self._status_value_cache[dev_name].status:
                # No change so nothing to do
                return
            self._status_value_cache[dev_name].status = new_status
            value = self._status_value_cache[dev_name].value
        buffer = self._to_f142(dev_name, value, int(timestamp_s * 10 ** 9),
                               new_status)
        # self.send_to_kafka(buffer)

    @staticmethod
    def _to_f142(name, value, timestamp, severity):
        return serialise_f142(value, name, timestamp, alarm_severity=severity)

    def send_to_kafka(self, buffer):
        self._producer.send("nicos_forwarder_test", buffer)
        self._producer.flush()

    def doInit(self, mode):
        CacheClient.doInit(self, mode)
        self._status_value_cache = {}
        self._current_devices = set()
        self._lock = RLock()
        self._producer = KafkaProducer(bootstrap_servers=["localhost:9092"])

        # Wait until connected
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


if __name__ == '__main__':
    SingleDeviceSession.run('forwarder', ForwarderApp,
                        {'prefix': 'nicos', 'cache': 'localhost'},
                        pidfile=False)
