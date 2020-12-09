from functools import partial
from threading import RLock

import numpy as np
from p4p.client.thread import Context

from nicos.core import CommunicationError, status

# Same context can be shared across all devices.
# nt=False tells p4p not to try to map types itself
# we want to do this manually to avoid information loss
from nicos.devices.epics import SEVERITY_TO_STATUS

_CONTEXT = Context('pva', nt=False)


class PvaWrapper:
    def __init__(self):
        self.disconnected = set()
        self.lock = RLock()

    @staticmethod
    def connect_pv(pvname, timeout):
        # Check pv is available
        try:
            _CONTEXT.get(pvname, timeout=timeout)
        except TimeoutError:
            raise CommunicationError('could not connect to PV %r' % pvname)
        return pvname

    @staticmethod
    def get_control_values(pv, timeout):
        raw_result = _CONTEXT.get(pv, timeout=timeout)
        if 'display' in raw_result:
            return raw_result['display']
        return raw_result['control'] if 'control' in raw_result else {}

    @staticmethod
    def get_value_choices(pv, timeout):
        # Only works for enum types like MBBI and MBBO
        raw_result = _CONTEXT.get(pv, timeout=timeout)
        if 'choices' in raw_result['value']:
            return raw_result['value']['choices']
        return []

    def get_pv_value(self, pv, timeout, as_string=False):
        result = _CONTEXT.get(pv, timeout=timeout)
        return self._convert_value(result['value'], as_string)

    @staticmethod
    def _convert_value(value, as_string=False):
        try:
            # Enums are complicated
            if value.getID() == 'enum_t':
                index = value['index']
                if as_string:
                    return value['choices'][index]
                return index
        except AttributeError:
            # getID() doesn't (currently) exist for scalar
            # and scalar-array types
            pass

        if as_string:
            # waveforms and arrays are already ndarrays
            if isinstance(value, np.ndarray):
                return value.tostring().decode()
            else:
                str(value)

        return value

    @staticmethod
    def put_pv_value(pv, value, wait, timeout):
        _CONTEXT.put(pv, value, timeout=timeout, wait=wait)

    @staticmethod
    def put_pv_value_blocking(pv, value, update_rate=0.1, timeout=60):
        # if wait is set p4p will block until the value is set or it
        # times out
        _CONTEXT.put(pv, value, timeout=timeout, wait=True)

    @staticmethod
    def get_pv_type(pv, timeout):
        # TODO: handle more complex types?
        result = _CONTEXT.get(pv, timeout=timeout)
        try:
            if result['value'].getID() == 'enum_t':
                # Treat enums as ints
                return int
        except AttributeError:
            # getID() doesn't (currently) exist for scalar
            # and scalar-array types
            pass

        return type(result["value"])

    def get_alarm_status(self, pv, timeout):
        result = _CONTEXT.get(pv, timeout=timeout)
        return self._extract_alarm_info(result)

    @staticmethod
    def get_units(pv, timeout, default=''):
        result = _CONTEXT.get(pv, timeout=timeout)
        try:
            return result['display']['units']
        except KeyError:
            return default

    @staticmethod
    def get_limits(pv, timeout, default_low=-1e308, default_high=1e308):
        result = _CONTEXT.get(pv, timeout=timeout)
        try:
            default_low = result['display']['limitLow']
            default_high = result['display']['limitHigh']
        except KeyError:
            pass
        return default_low, default_high

    def subscribe(self, pvname, pvparam, change_callback,
                  connection_callback=None, as_string=False):
        self.disconnected.add(pvname)

        request = _CONTEXT.makeRequest(
            "field(value,timeStamp,alarm,control,display)")

        callback = partial(self._callback, pvname, pvparam, change_callback,
                           connection_callback, as_string)
        subscription = _CONTEXT.monitor(pvname, callback, request=request,
                                        notify_disconnect=True)
        return subscription

    def _callback(self, name, pvparam, change_callback, connection_callback,
                  as_string, result):
        if isinstance(result, Exception):
            # Only callback on disconnection if was previously connected
            if connection_callback and name not in self.disconnected:
                connection_callback(name, pvparam, False)
                self.disconnected.add(name)
            return

        if name in self.disconnected:
            # Only callback if it is a new connection
            if connection_callback:
                connection_callback(name, pvparam, True)
            with self.lock:
                if name in self.disconnected:
                    self.disconnected.remove(name)

        if change_callback:
            value = self._convert_value(result['value'], as_string)
            severity, message = self._extract_alarm_info(result)
            change_callback(name, pvparam, value, severity, message)

    @staticmethod
    def _extract_alarm_info(value):
        # The EPICS 'severity' matches to the NICOS `status`.
        # p4p doesn't give anything useful for the status, but the message has
        # a short description of the alarm details.
        try:
            severity = SEVERITY_TO_STATUS[value['alarm']['severity']]
            return severity, value['alarm']['message']
        except KeyError as err:
            # Information not available
            return status.UNKNOWN, 'alarm information unavailable'


