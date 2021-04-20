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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""
This module contains the NICOS - TANGO integration.
"""

import os
import re

import PyTango

from nicos import session
from nicos.core import SIMULATION, CommunicationError, ConfigurationError, \
    HardwareError, HasCommunication, InvalidValueError, NicosError, Override, \
    Param, ProgrammingError, floatrange, status, tangodev
from nicos.utils import HardwareStub, tcpSocketContext

EXC_MAPPING = {
    PyTango.CommunicationFailed: CommunicationError,
    PyTango.WrongNameSyntax: ConfigurationError,
    PyTango.DevFailed: NicosError,
}

REASON_MAPPING = {
    'Entangle_ConfigurationError': ConfigurationError,
    'Entangle_WrongAPICall': ProgrammingError,
    'Entangle_CommunicationFailure': CommunicationError,
    'Entangle_InvalidValue': InvalidValueError,
    'Entangle_ProgrammingError': ProgrammingError,
    'Entangle_HardwareFailure': HardwareError,
}

# Tango DevFailed reasons that should not cause a retry
FATAL_REASONS = {
    'Entangle_ConfigurationError',
    'Entangle_UnrecognizedHardware',
    'Entangle_WrongAPICall',
    'Entangle_InvalidValue',
    'Entangle_NotSupported',
    'Entangle_ProgrammingError',
    'DB_DeviceNotDefined',
    'API_DeviceNotDefined',
    'API_CantConnectToDatabase',
    'API_TangoHostNotSet',
    'API_ServerNotRunning',
    'API_DeviceNotExported',
}


def describe_dev_error(exc):
    """Return a better description for a Tango exception.

    Most Tango exceptions are quite verbose and not suitable for user
    consumption.  Map the most common ones, that can also happen during normal
    operation, to a bit more friendly ones.
    """
    # general attributes
    reason = exc.reason.strip()
    fulldesc = reason + ': ' + exc.desc.strip()
    # reduce Python tracebacks
    if '\n' in exc.origin and 'File ' in exc.origin:
        origin = exc.origin.splitlines()[-2].strip()
    else:
        origin = exc.origin.strip()

    # we don't need origin info for Tango itself
    if origin.startswith(('DeviceProxy::', 'DeviceImpl::', 'Device_3Impl::',
                          'Device_4Impl::', 'Connection::', 'TangoMonitor::')):
        origin = None

    # now handle specific cases better
    if reason == 'API_AttrNotAllowed':
        m = re.search(r'to (read|write) attribute (\w+)', fulldesc)
        if m:
            if m.group(1) == 'read':
                fulldesc = 'reading %r not allowed in current state'
            else:
                fulldesc = 'writing %r not allowed in current state'
            fulldesc %= m.group(2)
    elif reason == 'API_CommandNotAllowed':
        m = re.search(r'Command (\w+) not allowed when the '
                      r'device is in (\w+) state', fulldesc)
        if m:
            fulldesc = 'executing %r not allowed in state %s' \
                % (m.group(1), m.group(2))
    elif reason == 'API_DeviceNotExported':
        m = re.search(r'Device ([\w/]+) is not', fulldesc)
        if m:
            fulldesc = 'Tango device %s is not exported, is the server ' \
                'running?' % m.group(1)
    elif reason == 'API_CorbaException':
        if 'TRANSIENT_CallTimedout' in fulldesc:
            fulldesc = 'Tango client-server call timed out'
        elif 'TRANSIENT_ConnectFailed' in fulldesc:
            fulldesc = 'connection to Tango server failed, is the server ' \
                'running?'
    elif reason == 'API_CantConnectToDevice':
        m = re.search(r'connect to device ([\w/-]+)', fulldesc)
        if m:
            fulldesc = 'connection to Tango device %s failed, is the server ' \
                'running?' % m.group(1)
    elif reason == 'API_CommandTimedOut':
        if 'acquire serialization' in fulldesc:
            fulldesc = 'Tango call timed out waiting for lock on server'

    # append origin if wanted
    if origin:
        fulldesc += ' in %s' % origin
    return fulldesc


def check_tango_host_connection(address, timeout=3.0):
    """Check pure network connection to the tango host."""
    tango_host = os.environ.get('TANGO_HOST', 'localhost:10000')

    if address.startswith('tango://'):
        tango_host = address.split('/')[2]

    try:
        with tcpSocketContext(tango_host, 10000, timeout=timeout):
            pass
    except OSError as e:
        raise CommunicationError(str(e)) from None


class PyTangoDevice(HasCommunication):
    """
    Basic PyTango device.

    The PyTangoDevice uses an internal PyTango.DeviceProxy but wraps command
    execution and attribute operations with logging and exception mapping.
    """

    hardware_access = True

    parameters = {
        'tangodevice':  Param('Tango device name', type=tangodev,
                              mandatory=True, preinit=True),
        'tangotimeout': Param('TANGO network timeout for this process',
                              unit='s', type=floatrange(0.0, 1200), default=3,
                              settable=True, preinit=True),
    }
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    tango_status_mapping = {
        PyTango.DevState.ON:     status.OK,
        PyTango.DevState.ALARM:  status.WARN,
        PyTango.DevState.OFF:    status.DISABLED,
        PyTango.DevState.FAULT:  status.ERROR,
        PyTango.DevState.MOVING: status.BUSY,
    }

    # Since each DeviceProxy leaks a few Python objects, we can't just
    # drop them when the device fails to initialize, and create another one.
    # It is also not required since they reconnect automatically.
    proxy_cache = {}

    def doPreinit(self, mode):
        # Wrap PyTango client creation (so even for the ctor, logging and
        # exception mapping is enabled).
        self._createPyTangoDevice = self._applyGuardToFunc(
            self._createPyTangoDevice, 'constructor')

        self._dev = None

        # Don't create PyTango device in simulation mode
        if mode != SIMULATION:
            self._dev = self._createPyTangoDevice(self.tangodevice)
        else:
            self._dev = HardwareStub(self)

    def doStatus(self, maxage=0):
        # Map Tango state to NICOS status
        nicosState = self.tango_status_mapping.get(self._dev.State(),
                                                   status.UNKNOWN)
        return (nicosState, self._dev.Status())

    def _hw_wait(self):
        """Wait until hardware status is not BUSY."""
        while PyTangoDevice.doStatus(self, 0)[0] == status.BUSY:
            session.delay(self._base_loop_delay)

    def doVersion(self):
        return [(self.tangodevice, self._dev.version)]

    def doReset(self):
        self._dev.Reset()
        while self._dev.State() == PyTango.DevState.INIT:
            session.delay(self._base_loop_delay)

    def _setMode(self, mode):
        super()._setMode(mode)
        # remove the Tango device on entering simulation mode, to prevent
        # accidental access to the hardware
        if mode == SIMULATION:
            self._dev = HardwareStub(self)

    def _getProperty(self, name, dev=None):
        """
        Utility function for getting a property by name easily.
        """
        if dev is None:
            dev = self._dev
        # return value is: [name, value, name, value, ...]
        props = dev.GetProperties()
        propnames = props[::2]
        return props[2 * propnames.index(name) + 1] \
            if name in propnames else None

    def doReadUnit(self):
        """For devices with a unit attribute."""
        attrInfo = self._dev.attribute_query('value')
        # prefer configured unit if nothing is set on the Tango device
        if attrInfo.unit == 'No unit':
            return self._config.get('unit', '')
        return attrInfo.unit

    def _createPyTangoDevice(self, address):  # pylint: disable=method-hidden
        """
        Creates the PyTango DeviceProxy and wraps command execution and
        attribute operations with logging and exception mapping.
        """
        check_tango_host_connection(self.tangodevice, self.tangotimeout)
        proxy_key = (self._name, address)
        if proxy_key not in PyTangoDevice.proxy_cache:
            PyTangoDevice.proxy_cache[proxy_key] = PyTango.DeviceProxy(address)
        device = PyTangoDevice.proxy_cache[proxy_key]
        device.set_timeout_millis(int(self.tangotimeout * 1000))
        # detect not running and not exported devices early, because that
        # otherwise would lead to attribute errors later
        try:
            device.State
        except AttributeError:
            raise NicosError(self, 'connection to Tango server failed, '
                             'is the server running?') from None
        return self._applyGuardsToPyTangoDevice(device)

    def _applyGuardsToPyTangoDevice(self, dev):
        """
        Wraps command execution and attribute operations of the given
        device with logging and exception mapping.
        """
        # if the device is in the proxy cache, and has already been
        # successfully created once, skip it
        if getattr(dev, '_nicos_proxies_applied', False):
            return dev
        dev.command_inout = self._applyGuardToFunc(dev.command_inout)
        dev.write_attribute = self._applyGuardToFunc(dev.write_attribute,
                                                     'attr_write')
        dev.read_attribute = self._applyGuardToFunc(dev.read_attribute,
                                                    'attr_read')
        dev.attribute_query = self._applyGuardToFunc(dev.attribute_query,
                                                     'attr_query')
        dev._nicos_proxies_applied = True
        return dev

    def _applyGuardToFunc(self, func, category='cmd'):
        """
        Wrap given function with logging and exception mapping.
        """
        def wrap(*args, **kwds):
            info = category + ' ' + args[0] if args else category

            # handle different types for better debug output
            if category == 'cmd':
                self.log.debug('[Tango] command: %s%r', args[0], args[1:])
            elif category == 'attr_read':
                self.log.debug('[Tango] read attribute: %s', args[0])
            elif category == 'attr_write':
                self.log.debug('[Tango] write attribute: %s => %r',
                               args[0], args[1:])
            elif category == 'attr_query':
                self.log.debug('[Tango] query attribute properties: %s',
                               args[0])
            elif category == 'constructor':
                self.log.debug('[Tango] device creation: %s', args[0])
                try:
                    result = func(*args, **kwds)
                    return self._com_return(result, info)
                except Exception as err:
                    self._com_raise(err, info)

            elif category == 'internal':
                self.log.debug('[Tango integration] internal: %s%r',
                               func.__name__, args)
            else:
                self.log.debug('[Tango] call: %s%r', func.__name__, args)

            return self._com_retry(info, func, *args, **kwds)

        # hide the wrapping
        wrap.__name__ = func.__name__

        return wrap

    def _com_return(self, result, info):
        # explicit check for loglevel to avoid expensive reprs
        if self.loglevel == 'debug':
            if isinstance(result, PyTango.DeviceAttribute):
                the_repr = repr(result.value)[:300]
            else:
                # This line explicitly logs '=> None' for commands which
                # does not return a value. This indicates that the command
                # execution ended.
                the_repr = repr(result)[:300]
            self.log.debug('\t=> %s', the_repr)
        return result

    def _tango_exc_desc(self, err):
        exc = str(err)
        if err.args:
            exc = err.args[0]  # Can be str or DevError
            if isinstance(exc, PyTango.DevError):
                return describe_dev_error(exc)
        return exc

    def _tango_exc_reason(self, err):
        if err.args and isinstance(err.args[0], PyTango.DevError):
            return err.args[0].reason.strip()
        return ''

    def _com_warn(self, retries, name, err, info):
        if self._tango_exc_reason(err) in FATAL_REASONS:
            self._com_raise(err, info)
        if retries == self.comtries - 1:
            self.log.warning('%s failed, retrying up to %d times: %s',
                             info, retries, self._tango_exc_desc(err))

    def _com_raise(self, err, info):
        reason = self._tango_exc_reason(err)
        exclass = REASON_MAPPING.get(
            reason, EXC_MAPPING.get(type(err), NicosError))
        fulldesc = self._tango_exc_desc(err)
        self.log.debug('[Tango] error: %s', fulldesc)
        raise exclass(self, fulldesc)
