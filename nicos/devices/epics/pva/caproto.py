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

import numpy as np
from caproto import CaprotoTimeoutError, ChannelType
from caproto.sync.client import read, write
from caproto.threading.client import Context

from nicos.commands import helparglist, hiddenusercommand
from nicos.core import CommunicationError, anytype, status
from nicos.devices.epics import SEVERITY_TO_STATUS

FTYPE_TO_TYPE = {
    ChannelType.STRING: str,
    ChannelType.INT: int,
    ChannelType.FLOAT: float,
    ChannelType.ENUM: int,
    ChannelType.CHAR: bytes,
    ChannelType.LONG: int,
    ChannelType.DOUBLE: float,

    ChannelType.TIME_STRING: str,
    ChannelType.TIME_INT: int,
    ChannelType.TIME_FLOAT: float,
    ChannelType.TIME_ENUM: int,
    ChannelType.TIME_CHAR: bytes,
    ChannelType.TIME_LONG: int,
    ChannelType.TIME_DOUBLE: float,

    ChannelType.CTRL_STRING: str,
    ChannelType.CTRL_INT: int,
    ChannelType.CTRL_FLOAT: float,
    ChannelType.CTRL_ENUM: int,
    ChannelType.CTRL_CHAR: bytes,
    ChannelType.CTRL_LONG: int,
    ChannelType.CTRL_DOUBLE: float,
}

STATUS_TO_MESSAGE = {
    0: 'NO_ALARM',
    1: 'READ',
    2: 'WRITE',
    3: 'HIHI',
    4: 'HIGH',
    5: 'LOLO',
    6: 'LOW',
    7: 'STATE',
    8: 'COS',
    9: 'COMM',
    10: 'TIMED',
    11: 'HWLIMIT',
    12: 'CALC',
    13: 'SCAN',
    14: 'LINK',
    15: 'SOFT',
    16: 'BAD_SUB',
    17: 'UDF',
    18: 'DISABLE',
    19: 'SIMM',
    20: 'READ_ACCESS',
    21: 'WRITE_ACCESS',
}

# Same context can be shared across all devices.
_Context = Context()

@hiddenusercommand
@helparglist('name[, timeout]')
def caget(name, timeout=3.0):
    """ Returns the PV's current value in its raw form via CA.

    :param name: the PV name
    :param timeout: the EPICS timeout
    :return: the PV's raw value
    """
    response = read(name, timeout=timeout)
    return response.data[0] if len(response.data) == 1 else response.data


@hiddenusercommand
@helparglist('name, value[, wait, timeout]')
def caput(name, value, wait=False, timeout=3.0):
    """ Sets a PV's value via CA.

    :param name: the PV name
    :param value: the value to set
    :param wait: whether to wait for completion
    :param timeout: the EPICS timeout
    """
    write(name, value, notify=wait, timeout=timeout)


class CaprotoWrapper:
    """ Class that wraps the caproto module that provides EPICS Channel Access
    (CA) support.
    """

    def __init__(self, timeout=3.0):
        self._pvs = {}
        self._choices = {}
        self._callbacks = set()
        self._timeout = timeout

    def connect_pv(self, pvname):
        if pvname in self._pvs:
            return

        value = self._create_pv(pvname)
        # Do some prep work for enum types
        if hasattr(value.metadata, 'enum_strings'):
            self._choices[pvname] = self.get_value_choices(pvname)

    def _create_pv(self, pvname, connection_callback=None):
        try:
            pv, *_ = _Context.get_pvs(
                pvname,
                connection_state_callback=connection_callback,
                timeout=self._timeout
            )
            self._pvs[pvname] = pv
            # Do a read to force a connection
            return pv.read(timeout=self._timeout, data_type='control')
        except CaprotoTimeoutError:
            raise CommunicationError(
                f'could not connect to PV {pvname}') from None

    def get_pv_value(self, pvname, as_string=False):
        try:
            result = self._pvs[pvname].read(timeout=self._timeout,
                                            data_type='control')
            return self._convert_value(pvname, result, as_string)
        except CaprotoTimeoutError:
            raise TimeoutError(f"getting {pvname} timed out") from None

    def _convert_value(self, pvname, raw_value, as_string=False):
        if len(raw_value.data) == 1:
            value = raw_value.data[0]
            if pvname in self._choices:
                return self._choices[pvname][value] if as_string else value
            elif isinstance(value, bytes):
                return value.decode()
            return str(value) if as_string else value

        # waveforms and arrays are ndarrays
        if isinstance(raw_value.data, np.ndarray):
            val_type = FTYPE_TO_TYPE[self._pvs[pvname].channel.native_data_type]
            if val_type == bytes or as_string:
                return raw_value.data.tobytes().decode()

        return str(raw_value.data) if as_string else raw_value.data

    def put_pv_value(self, pvname, value, wait=False):
        if pvname in self._choices:
            value = self._choices[pvname].index(value)
        try:
            self._pvs[pvname].write(value, wait=wait, timeout=self._timeout)
        except CaprotoTimeoutError:
            raise TimeoutError(f"setting {pvname} timed out") from None

    def put_pv_value_blocking(self, pvname, value, block_timeout=60):
        if pvname in self._choices:
            value = self._choices[pvname].index(value)
        try:
            self._pvs[pvname].write(value, wait=True, timeout=block_timeout)
        except CaprotoTimeoutError:
            raise TimeoutError(f"setting {pvname} timed out") from None

    def get_pv_type(self, pvname):
        data_type = self._pvs[pvname].channel.native_data_type
        return FTYPE_TO_TYPE.get(data_type, anytype)

    def get_alarm_status(self, pvname):
        values = self.get_control_values(pvname)
        return self._extract_alarm_info(values)

    def get_units(self, pvname, default=''):
        values = self.get_control_values(pvname)
        return self._get_units(values, default)

    def _get_units(self, values, default):
        if hasattr(values, 'units'):
            return values.units.decode()
        return default

    def get_limits(self, pvname, default_low=-1e308, default_high=1e308):
        values = self.get_control_values(pvname)
        if hasattr(values, 'lower_warning_limit'):
            default_low = values.lower_warning_limit
            default_high = values.upper_warning_limit
        return default_low, default_high

    def get_control_values(self, pvname):
        try:
            result = self._pvs[pvname].read(timeout=self._timeout,
                                            data_type='control')
            return result.metadata
        except CaprotoTimeoutError:
            raise TimeoutError(
                f"getting control values for {pvname} timed out") from None

    def get_value_choices(self, pvname):
        # Only works for enum types like MBBI and MBBO
        value = self.get_control_values(pvname)
        return self._extract_choices(value)

    def _extract_choices(self, value):
        if hasattr(value, 'enum_strings'):
            return [x.decode() for x in value.enum_strings]
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
        conn_callback = self._create_connection_callback(pvname, pvparam,
                                                         connection_callback)
        self._create_pv(pvname, conn_callback)

        value_callback = self._create_value_callback(pvname, pvparam,
                                                     change_callback, as_string)
        sub = self._pvs[pvname].subscribe(data_type='control')
        sub.add_callback(value_callback)
        return sub

    def _create_value_callback(self, pvname, pvparam, change_callback,
                               as_string):
        callback = partial(self._callback, pvname, pvparam, change_callback,
                           as_string)
        self._store_callback(callback)
        return callback

    def _create_connection_callback(self, pvname, pvparam, connection_callback):
        callback = partial(self._conn_callback, pvname, pvparam,
                           connection_callback)
        self._store_callback(callback)
        return callback

    def _store_callback(self, callback):
        # Must keep a reference to callbacks to avoid garbage collection!
        self._callbacks.add(callback)

    def _callback(self, pvname, pvparam, change_callback, as_string, sub,
                  response):
        value = self._convert_value(pvname, response, as_string)
        units = self._get_units(response.metadata, '')
        severity, message = self._extract_alarm_info(response)
        change_callback(pvname, pvparam, value, units, severity, message)

    def _conn_callback(self, pvname, pvparam, connection_callback, pv, state):
        connection_callback(pvname, pvparam, state == 'connected')

    def _extract_alarm_info(self, values):
        # The EPICS 'severity' matches to the NICOS `status` and the message has
        # a short description of the alarm details.
        if hasattr(values, 'severity'):
            severity = SEVERITY_TO_STATUS[values.severity]
            message = STATUS_TO_MESSAGE[values.status]
            return severity, '' if message == 'NO_ALARM' else message
        return status.UNKNOWN, 'alarm information unavailable'

    def close_subscription(self, subscription):
        subscription.clear()
