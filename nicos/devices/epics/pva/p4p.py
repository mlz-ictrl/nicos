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
#
# *****************************************************************************
from functools import partial
from threading import Lock

import numpy as np
from p4p.client.thread import Context

from nicos.core import CommunicationError, status
from nicos.devices.epics import SEVERITY_TO_STATUS

# Same context can be shared across all devices.
# nt=False tells p4p not to try to map types itself
# we want to do this manually to avoid information loss
_CONTEXT = Context('pva', nt=False)


class P4pWrapper:
    """ Class that wraps the p4p module that provides EPICS PVA Access (PVA)
    support.
    """

    def __init__(self, timeout=3.0):
        self.disconnected = set()
        self.lock = Lock()
        self._timeout = timeout
        self._units = {}
        self._values = {}
        self._alarms = {}
        self._choices = {}

    def connect_pv(self, pvname):
        # Check pv is available
        try:
            _CONTEXT.get(pvname, timeout=self._timeout)
        except TimeoutError:
            raise CommunicationError(
                f'could not connect to PV {pvname}') from None

    def get_pv_value(self, pvname, as_string=False):
        result = _CONTEXT.get(pvname, timeout=self._timeout)
        return self._convert_value(pvname, result['value'], as_string)

    def _convert_value(self, pvname, value, as_string=False):
        try:
            # Enums are complicated
            if value.getID() == 'enum_t':
                index = value['index']
                if as_string:
                    if pvname not in self._choices:
                        self.get_value_choices(pvname)
                    return self._choices[pvname][index]
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
                return str(value)
        return value

    def put_pv_value(self, pvname, value, wait=False):
        _CONTEXT.put(pvname, value, timeout=self._timeout, wait=wait)

    def put_pv_value_blocking(self, pvname, value, block_timeout=60):
        _CONTEXT.put(pvname, value, timeout=block_timeout, wait=True)

    def get_pv_type(self, pvname):
        result = _CONTEXT.get(pvname, timeout=self._timeout)
        try:
            if result['value'].getID() == 'enum_t':
                # Treat enums as ints
                return int
        except AttributeError:
            # getID() doesn't (currently) exist for scalar
            # and scalar-array types
            pass

        return type(result["value"])

    def get_alarm_status(self, pvname):
        result = _CONTEXT.get(pvname, timeout=self._timeout)
        return self._extract_alarm_info(result)

    def get_units(self, pvname, default=''):
        result = _CONTEXT.get(pvname, timeout=self._timeout)
        return self._get_units(result, default)

    def _get_units(self, result, default):
        try:
            return result['display']['units']
        except KeyError:
            return default

    def get_limits(self, pvname, default_low=-1e308, default_high=1e308):
        result = _CONTEXT.get(pvname, timeout=self._timeout)
        try:
            default_low = result['display']['limitLow']
            default_high = result['display']['limitHigh']
        except KeyError:
            pass
        return default_low, default_high

    def get_control_values(self, pvname):
        raw_result = _CONTEXT.get(pvname, timeout=self._timeout)
        if 'display' in raw_result:
            return raw_result['display']
        return raw_result['control'] if 'control' in raw_result else {}

    def get_value_choices(self, pvname):
        # Only works for enum types like MBBI and MBBO
        raw_result = _CONTEXT.get(pvname, timeout=self._timeout)
        if 'choices' in raw_result['value']:
            self._choices[pvname] = raw_result['value']['choices']
            return self._choices[pvname]
        return []

    def subscribe(self, pvname, pvparam, change_callback,
                  connection_callback=None, as_string=False):
        """
        Create a monitor subscription to the specified PV.

        :param pvname: The PV name.
        :param pvparam: The associated NICOS parameter
            (e.g. readpv, writepv, etc.).
        :param change_callback: The function to call when the value changes.
        :param connection_callback: The function to call when the connection
            status changes.
        :param as_string: Whether to return the value as a string.
        :return: the subscription object.
        """
        with self.lock:
            self.disconnected.add(pvname)

        request = _CONTEXT.makeRequest(
            "field(value,timeStamp,alarm,control,display)")

        callback = partial(self._callback, pvname, pvparam, change_callback,
                           connection_callback, as_string)
        subscription = _CONTEXT.monitor(pvname, callback, request=request,
                                        notify_disconnect=True)
        return subscription

    def _callback(self, pvname, pvparam, change_callback, connection_callback,
                  as_string, result):
        if isinstance(result, Exception):
            # Only callback on disconnection if was previously connected
            if connection_callback and pvname not in self.disconnected:
                connection_callback(pvname, pvparam, False)
                with self.lock:
                    self.disconnected.add(pvname)
            return

        if pvname in self.disconnected:
            # Only callback if it is a new connection
            if connection_callback:
                connection_callback(pvname, pvparam, True)
            with self.lock:
                if pvname in self.disconnected:
                    self.disconnected.remove(pvname)
                    if pvname in self._values:
                        del self._values[pvname]
                    if pvname in self._choices:
                        del self._choices[pvname]

        if change_callback:
            # PVA only sends a delta of what has changed
            change_set = result.changedSet()

            if 'value' in change_set or 'value.index' in change_set:
                self._values[pvname] = self._convert_value(pvname,
                                                           result['value'],
                                                           as_string)
            if 'display.units' in change_set:
                self._units[pvname] = self._get_units(result, '')
            if 'alarm.status' in change_set or 'alarm.severity' in change_set:
                self._alarms[pvname] = self._extract_alarm_info(result)

            if pvname in self._values:
                severity, msg = self._alarms.get(pvname, (status.UNKNOWN, ''))
                change_callback(pvname, pvparam, self._values[pvname],
                                self._units.get(pvname, ''), severity, msg)

    def _extract_alarm_info(self, value):
        # The EPICS 'severity' matches to the NICOS `status` and the message has
        # a short description of the alarm details.
        try:
            severity = SEVERITY_TO_STATUS[value['alarm']['severity']]
            message = value['alarm']['message']
            return severity, '' if message == 'NO_ALARM' else message
        except KeyError:
            return status.UNKNOWN, 'alarm information unavailable'

    def close_subscription(self, subscription):
        subscription.close()
