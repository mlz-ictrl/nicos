import argparse
import logging
import sys
import time
from os import path
from threading import RLock

from nicos.utils import createThread

sys.path.insert(0, path.dirname(path.dirname(path.realpath(__file__))))

from nicos.devices.cacheclient import CacheClient
from nicos.core.sessions.simple import SingleDeviceSession

# TODO: for f142 only send status/severity if it changes otherwise send NO_CHANGE
# Are only OK, WARN and ERROR relevant? UNKNOWN?


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
            current_status = self.getDeviceParam(dev, 'status')
            current_value = self.getDeviceParam(dev, 'value')
            self._status_value_cache[dev] = [current_status, current_value]
            self.addCallback(dev, 'status', self.changed_value_callback)
            self.addCallback(dev, 'value', self.changed_value_callback)

    def changed_value_callback(self, name, value, timestamp, *args, **kwargs):
        dev_name = name[0:name.index('/')]
        if name.endswith('/status'):
            self.log.info(f'{dev_name} status changed to {value}')
            with self._lock:
                self._status_value_cache[dev_name][0] = value
            # TODO: send value and new status
        elif name.endswith('/value'):
            self.log.info(f'{dev_name} value changed to {value}')
            with self._lock:
                self._status_value_cache[dev_name][1] = value
            # TODO: send value with no change in status

    def doInit(self, mode):
        CacheClient.doInit(self, mode)
        self._status_value_cache = {}
        self._current_devices = set()
        self._lock = RLock()

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
