#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

All NICOS - TANGO devices only support devices which fulfill the official
MLZ TANGO interface for the respective device classes.
"""

import re
import socket
import os

import PyTango
import numpy

from nicos import session
from nicos.core import Param, Override, status, Readable, Moveable, \
    HasLimits, Device, tangodev, HasCommunication, oneofdict, oneof, \
    dictof, intrange, nonemptylistof, listof, NicosError, CommunicationError, \
    ConfigurationError, ProgrammingError, HardwareError, InvalidValueError, \
    HasTimeout, HasPrecision, ArrayDesc, Value, floatrange
from nicos.devices.abstract import Coder, Motor as NicosMotor, CanReference
from nicos.utils import HardwareStub, tcpSocket, closeSocket
from nicos.core import SIMULATION
from nicos.core.mixins import HasWindowTimeout
from nicos.devices.generic.detector import ActiveChannel, CounterChannelMixin, \
    ImageChannelMixin, TimerChannelMixin, PassiveChannel

# Only export Nicos devices for 'from nicos.device.tango import *'
__all__ = [
    'AnalogInput', 'Sensor', 'AnalogOutput', 'Actuator', 'RampActuator',
    'Motor', 'TemperatureController', 'PowerSupply', 'DigitalInput',
    'NamedDigitalInput', 'PartialDigitalInput', 'DigitalOutput',
    'NamedDigitalOutput', 'PartialDigitalOutput', 'StringIO', 'DetectorChannel',
    'TimerChannel', 'CounterChannel', 'ImageChannel', 'TOFChannel',
    'WindowTimeoutAO'
]

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
FATAL_REASONS = set((
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
))


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
        m = re.search(r'connect to device ([\w/]+)', fulldesc)
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
        closeSocket(tcpSocket(tango_host, 10000, timeout=timeout))
    except socket.error as e:
        raise CommunicationError(str(e))


class PyTangoDevice(HasCommunication):
    """
    Basic PyTango device.

    The PyTangoDevice uses an internal PyTango.DeviceProxy but wraps command
    execution and attribute operations with logging and exception mapping.
    """

    hardware_access = True

    parameters = {
        'tangodevice': Param('Tango device name', type=tangodev,
                             mandatory=True, preinit=True),
        'tangotimeout': Param('TANGO network timeout for this process',
                             unit='s', type=floatrange(0.0, 1200), default=3,
                             settable=True, preinit=True),
    }

    tango_status_mapping = {
        PyTango.DevState.ON:     status.OK,
        PyTango.DevState.ALARM:  status.WARN,
        PyTango.DevState.OFF:    status.ERROR,
        PyTango.DevState.FAULT:  status.ERROR,
        PyTango.DevState.MOVING: status.BUSY,
    }

    def doPreinit(self, mode):
        # Wrap PyTango client creation (so even for the ctor, logging and
        # exception mapping is enabled).
        self._createPyTangoDevice = self._applyGuardToFunc(
            self._createPyTangoDevice, 'constructor')

        self._dev = None

        # Don't create PyTango device in simulation mode
        if mode != SIMULATION:
            self._dev = self._createPyTangoDevice(self.tangodevice)

    def doStatus(self, maxage=0):
        # Query status code and string
        tangoState = self._dev.State()
        tangoStatus = self._dev.Status()

        # Map status
        nicosState = self.tango_status_mapping.get(tangoState, status.UNKNOWN)

        return (nicosState, tangoStatus)

    def _hw_wait(self):
        """Wait until hardware status is not BUSY."""
        while PyTangoDevice.doStatus(self, 0)[0] == status.BUSY:
            session.delay(self._base_loop_delay)

    def doVersion(self):
        return [(self.tangodevice, self._dev.version)]

    def doReset(self):
        self._dev.Reset()

    def _setMode(self, mode):
        super(PyTangoDevice, self)._setMode(mode)
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
        # Entangle and later API
        if dev.command_query('GetProperties').in_type == PyTango.DevVoid:
            props = dev.GetProperties()
            return props[props.index(name) + 1] if name in props else None
        # old (pre-Entangle) API
        return dev.GetProperties([name, 'device'])[2]

    def _createPyTangoDevice(self, address):  # pylint: disable=E0202
        """
        Creates the PyTango DeviceProxy and wraps command execution and
        attribute operations with logging and exception mapping.
        """
        check_tango_host_connection(self.tangodevice, self.tangotimeout)
        device = PyTango.DeviceProxy(address)
        device.set_timeout_millis(int(self.tangotimeout * 1000))
        # detect not running and not exported devices early, because that
        # otherwise would lead to attribute errors later
        try:
            device.State
        except AttributeError:
            raise NicosError(self, 'connection to Tango server failed, '
                             'is the server running?')
        return self._applyGuardsToPyTangoDevice(device)

    def _applyGuardsToPyTangoDevice(self, dev):
        """
        Wraps command execution and attribute operations of the given
        device with logging and exception mapping.
        """
        dev.command_inout = self._applyGuardToFunc(dev.command_inout)
        dev.write_attribute = self._applyGuardToFunc(dev.write_attribute,
                                                     'attr_write')
        dev.read_attribute = self._applyGuardToFunc(dev.read_attribute,
                                                    'attr_read')
        dev.attribute_query = self._applyGuardToFunc(dev.attribute_query,
                                                     'attr_query')
        return dev

    def _applyGuardToFunc(self, func, category='cmd'):
        """
        Wrap given function with logging and exception mapping.
        """
        def wrap(*args, **kwds):
            info = category + ' ' + args[0] if args else category

            # handle different types for better debug output
            if category == 'cmd':
                self.log.debug('[PyTango] command: %s%r', args[0], args[1:])
            elif category == 'attr_read':
                self.log.debug('[PyTango] read attribute: %s', args[0])
            elif category == 'attr_write':
                self.log.debug('[PyTango] write attribute: %s => %r',
                               args[0], args[1:])
            elif category == 'attr_query':
                self.log.debug('[PyTango] query attribute properties: %s',
                               args[0])
            elif category == 'constructor':
                self.log.debug('[PyTango] device creation: %s', args[0])
                try:
                    result = func(*args, **kwds)
                    return self._com_return(result, info)
                except Exception as err:
                    self._com_raise(err, info)

            elif category == 'internal':
                self.log.debug('[PyTango integration] internal: %s%r',
                               func.__name__, args)
            else:
                self.log.debug('[PyTango] call: %s%r', func.__name__, args)

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
        self.log.debug('PyTango error: %s', fulldesc)
        raise exclass(self, fulldesc)


class AnalogInput(PyTangoDevice, Readable):
    """
    The AnalogInput handles all devices only delivering an analogue value.
    """

    valuetype = float
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doReadUnit(self):
        attrInfo = self._dev.attribute_query('value')
        # prefer configured unit if nothing is set on the Tango device
        if attrInfo.unit == 'No unit' and 'unit' in self._config:
            return self._config['unit']
        return attrInfo.unit

    def doRead(self, maxage=0):
        return self._dev.value


class Sensor(AnalogInput, Coder):
    """
    The sensor interface describes all analog read only devices.

    The difference to AnalogInput is that the “value” attribute can be
    converted from the “raw value” to a physical value with an offset and a
    formula.
    """

    def doSetPosition(self, value):
        self._dev.Adjust(value)


class AnalogOutput(PyTangoDevice, HasLimits, Moveable):
    """
    The AnalogOutput handles all devices which set an analogue value.

    The main application field is the output of any signal which may be
    considered as continously in a range. The values may have nearly any
    value between the limits. The compactness is limited by the resolution of
    the hardware.

    This class should be considered as a base class for motors, temperature
    controllers, ...
    """

    valuetype = float
    parameter_overrides = {
        'abslimits': Override(mandatory=False, volatile=True),
        'unit':      Override(mandatory=False),
    }

    def doReadUnit(self):
        attrInfo = self._dev.attribute_query('value')
        # prefer configured unit if nothing is set on the Tango device
        if attrInfo.unit == 'No unit' and 'unit' in self._config:
            return self._config['unit']
        return attrInfo.unit

    def doReadAbslimits(self):
        absmin = float(self._getProperty('absmin'))
        absmax = float(self._getProperty('absmax'))

        return (absmin, absmax)

    def doRead(self, maxage=0):
        return self._dev.value

    def doStart(self, value):
        try:
            self._dev.value = value
        except NicosError:
            # changing target value during movement is not allowed by the
            # Tango base class state machine. If we are moving, stop first.
            if self.status(0)[0] == status.BUSY:
                self.stop()
                self._hw_wait()
                self._dev.value = value
            else:
                raise

    def doStop(self):
        self._dev.Stop()


class WindowTimeoutAO(HasWindowTimeout, AnalogOutput):
    """
    AnalogOutput with window timeout.
    """
    pass


class Actuator(AnalogOutput, NicosMotor):
    """
    The actuator interface describes all analog devices which DO something in a
    defined way.

    The difference to AnalogOutput is that there is a speed attribute, and the
    value attribute is converted from the “raw value” with a formula and
    offset.
    """

    parameter_overrides = {
        'speed':  Override(volatile=True),
    }

    def doReadSpeed(self):
        return self._dev.speed

    def doWriteSpeed(self, value):
        self._dev.speed = value

    def doSetPosition(self, value):
        self._dev.Adjust(value)


class Motor(CanReference, Actuator):
    """
    This class implements a motor device (in a sense of a real motor
    (stepper motor, servo motor, ...)).

    It has the ability to move a real object from one place to another place.
    """

    parameters = {
        'refpos': Param('Reference position', type=float, unit='main'),
        'accel':  Param('Acceleration', type=float, settable=True,
                        volatile=True, unit='main/s^2'),
        'decel':  Param('Deceleration', type=float, settable=True,
                        volatile=True, unit='main/s^2'),
    }

    def doReadRefpos(self):
        return float(self._getProperty('refpos'))

    def doReadAccel(self):
        return self._dev.accel

    def doWriteAccel(self, value):
        self._dev.accel = value

    def doReadDecel(self):
        return self._dev.decel

    def doWriteDecel(self, value):
        self._dev.decel = value

    def doReference(self):
        self._setROParam('target', None)  # don't check target in wait() below
        self._dev.Reference()
        self.wait()

    def doTime(self, start, end):
        s, v, a, d = abs(start - end), self.speed, self.accel, self.decel
        if v <= 0 or a <= 0 or d <= 0:
            return 0
        if s > v ** 2 / a:  # do we reach nominal speed?
            return s / v + 0.5 * (v / a + v / d)
        return 2 * (s / a) ** 0.5


class RampActuator(HasPrecision, AnalogOutput):
    """
    A class wrapping the Tango Actuator interface that does not inherit the
    NICOS motor interface.

    It treats the value changing speed in terms of the "ramp" attribute
    (set in units/minute), not the "speed" attribute (set in units/second)
    that the `Actuator` class uses.
    """

    parameters = {
        'ramp': Param('Ramp of the main value', unit='main/min',
                      type=float, settable=True, volatile=True),
    }

    def doReadRamp(self):
        return self._dev.ramp

    def doWriteRamp(self, value):
        self._dev.ramp = value


class TemperatureController(HasWindowTimeout, RampActuator):
    """
    A temperature control loop device.
    """

    parameters = {
        'p':            Param('Proportional control parameter', type=float,
                              settable=True, category='general', chatty=True,
                              volatile=True),
        'i':            Param('Integral control parameter', type=float,
                              settable=True, category='general', chatty=True,
                              volatile=True),
        'd':            Param('Derivative control parameter', type=float,
                              settable=True, category='general', chatty=True,
                              volatile=True),
        'setpoint':     Param('Current setpoint', type=float,
                              category='general', volatile=True),
        'heateroutput': Param('Heater output', type=float, category='general',
                              volatile=True),
    }

    parameter_overrides = {
        # We want this to be freely user-settable, and not produce a warning
        # on startup, so select a usually sensible default.
        'precision':    Override(mandatory=False, default=0.1),
    }

    def doReadP(self):
        return self._dev.p

    def doWriteP(self, value):
        self._dev.p = value

    def doReadI(self):
        return self._dev.i

    def doWriteI(self, value):
        self._dev.i = value

    def doReadD(self):
        return self._dev.d

    def doWriteD(self, value):
        self._dev.d = value

    def doReadSetpoint(self):
        return self._dev.setpoint

    def doReadHeateroutput(self):
        return self._dev.heaterOutput

    def doPoll(self, n, maxage):
        if self.ramp:
            self._pollParam('setpoint', 1)
            self._pollParam('heateroutput', 1)
        if n % 30 == 0:
            self._pollParam('setpoint', 30)
            self._pollParam('heateroutput', 30)
            self._pollParam('p')
            self._pollParam('i')
            self._pollParam('d')


class PowerSupply(HasTimeout, RampActuator):
    """
    A power supply (voltage and current) device.
    """

    parameters = {
        'voltage': Param('Actual voltage', unit='V',
                         type=float, settable=False, volatile=True),
        'current': Param('Actual current', unit='A',
                         type=float, settable=False, volatile=True),
    }

    def doReadVoltage(self):
        return self._dev.voltage

    def doReadCurrent(self):
        return self._dev.current

    def doPoll(self, n, maxage):
        if n % 5 == 0:
            self._pollParam('voltage', 1)
            self._pollParam('current', 1)


class DigitalInput(PyTangoDevice, Readable):
    """
    A device reading a bitfield.
    """

    valuetype = int
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doRead(self, maxage=0):
        return self._dev.value


class NamedDigitalInput(DigitalInput):
    """
    A DigitalInput with numeric values mapped to names.
    """

    parameters = {
        'mapping': Param('A dictionary mapping state names to integers',
                         type=dictof(str, int)),
    }

    def doInit(self, mode):
        self._reverse = dict((v, k) for (k, v) in self.mapping.items())

    def doRead(self, maxage=0):
        value = self._dev.value
        return self._reverse.get(value, value)


class PartialDigitalInput(NamedDigitalInput):
    """
    Base class for a TANGO DigitalInput with only a part of the full
    bit width accessed.
    """

    parameters = {
        'startbit': Param('Number of the first bit', type=int, default=0),
        'bitwidth': Param('Number of bits', type=int, default=1),
    }

    def doInit(self, mode):
        NamedDigitalInput.doInit(self, mode)
        self._mask = (1 << self.bitwidth) - 1

    def doRead(self, maxage=0):
        raw_value = self._dev.value
        value = (raw_value >> self.startbit) & self._mask
        return self._reverse.get(value, value)


class DigitalOutput(PyTangoDevice, Moveable):
    """
    A devices that can set and read a digital value corresponding to a
    bitfield.
    """

    valuetype = int
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doRead(self, maxage=0):
        return self._dev.value

    def doStart(self, value):
        self._dev.value = value


class NamedDigitalOutput(DigitalOutput):
    """
    A DigitalOutput with numeric values mapped to names.
    """

    parameters = {
        'mapping': Param('A dictionary mapping state names to integer values',
                         type=dictof(str, int), mandatory=True),
    }

    def doInit(self, mode):
        self._reverse = dict((v, k) for (k, v) in self.mapping.items())
        # oneofdict: allows both types of values (string/int), but normalizes
        # them into the string form
        self.valuetype = oneofdict(self._reverse)

    def doStart(self, target):
        value = self.mapping.get(target, target)
        self._dev.value = value

    def doRead(self, maxage=0):
        value = self._dev.value
        return self._reverse.get(value, value)


class PartialDigitalOutput(NamedDigitalOutput):
    """
    Base class for a TANGO DigitalOutput with only a part of the full
    bit width accessed.
    """

    parameters = {
        'startbit': Param('Number of the first bit', type=int, default=0),
        'bitwidth': Param('Number of bits', type=int, default=1),
    }

    def doInit(self, mode):
        NamedDigitalOutput.doInit(self, mode)
        self._mask = (1 << self.bitwidth) - 1
        self.valuetype = intrange(0, self._mask)

    def doRead(self, maxage=0):
        raw_value = self._dev.value
        value = (raw_value >> self.startbit) & self._mask
        return self._reverse.get(value, value)

    def doStart(self, target):
        value = self.mapping.get(target, target)
        curvalue = self._dev.value
        newvalue = (curvalue & ~(self._mask << self.startbit)) | \
                   (value << self.startbit)
        self._dev.value = self.valuetype(newvalue)

    def doIsAllowed(self, target):
        value = self.mapping.get(target, target)
        if value < 0 or value > self._mask:
            return False, '%d outside range [0,%d]' % (value, self._mask)
        return True, ''


class StringIO(PyTangoDevice, Device):
    """
    StringIO abstracts communication over a hardware bus that sends and
    receives strings.
    """

    parameters = {
        'bustimeout':  Param('Communication timeout', type=float,
                             settable=True, unit='s'),
        'endofline':   Param('End of line', type=str, settable=True),
        'startofline': Param('Start of line', type=str, settable=True),
    }

    def doReadBustimeout(self):
        return self._dev.communicationTimeout

    def doWriteBustimeout(self, value):
        self._dev.communicationTimeout = value

    def doReadEndofline(self):
        return self._dev.endOfLine

    def doWriteEndofline(self, value):
        self._dev.endOfLine = value

    def doReadStartofline(self):
        return self._dev.startOfLine

    def doWriteStartofline(self, value):
        self._dev.startOfLine = value

    def communicate(self, value):
        return self._dev.Communicate(value)

    def flush(self):
        self._dev.Flush()

    def read(self, value):
        return self._dev.Read(value)

    def write(self, value):
        return self._dev.Write(value)

    def readLine(self):
        return self._dev.ReadLine()

    def writeLine(self, value):
        return self._dev.WriteLine(value)

    def multiCommunicate(self, value):
        return self._dev.MultiCommunicate(value)

    @property
    def availablechars(self):
        return self._dev.availableChars

    @property
    def availablelines(self):
        return self._dev.availableLines


class DetectorChannel(PyTangoDevice, ActiveChannel):
    """
    Base class for detector channels.
    """

    def valueInfo(self):
        # no readresult by default
        return ()

    def doReadIsmaster(self):
        # if the channel is passive, it will always return False here
        return self._dev.active

    def doWriteIsmaster(self, value):
        self._dev.active = value

    def doReadPreselection(self):
        return self._dev.preselection

    def doWritePreselection(self, preselectionvalue):
        self._dev.preselection = preselectionvalue

    def doPrepare(self):
        self._dev.Prepare()

    def doStart(self):
        self._dev.Start()

    def doStop(self):
        self._dev.Stop()

    def doClear(self):
        self._dev.Clear()

    def doResume(self):
        self._dev.Resume()

    def doPause(self):
        self.doStop()
        return True

    def doFinish(self):
        self._dev.Stop()


class TimerChannel(TimerChannelMixin, DetectorChannel):
    """
    Detector channel to measure time.
    """
    def doRead(self, maxage=0):
        return self._dev.value


class CounterChannel(CounterChannelMixin, DetectorChannel):
    """
    Detector channel to count events.
    """
    def doRead(self, maxage=0):
        return self._dev.value


class ImageChannel(ImageChannelMixin, DetectorChannel):
    """
    Detector channel for delivering images.
    """

    parameters = {
        'size':      Param('Full detector size', type=nonemptylistof(int),
                           settable=False, mandatory=False, volatile=True),
        'roioffset': Param('ROI offset', type=nonemptylistof(int),
                           mandatory=False, volatile=True, settable=True),
        'roisize':   Param('ROI size', type=nonemptylistof(int),
                           mandatory=False, volatile=True, settable=True),
        'binning':   Param('Binning', type=nonemptylistof(int),
                           mandatory=False, volatile=True, settable=True),
        'zeropoint': Param('Zero point', type=nonemptylistof(int),
                           settable=False, mandatory=False, volatile=True),
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            shape = tuple(self._dev.roiSize)
        else:
            shape = (256, 256)  # select some arbitrary shape
        self.arraydesc = ArrayDesc('data', shape=shape, dtype='<u4')

    def doReadSize(self):
        return self._dev.detectorSize.tolist()

    def doReadRoioffset(self):
        return self._dev.roiOffset.tolist()

    def doWriteRoioffset(self, value):
        self._dev.roiOffset = value

    def doReadRoisize(self):
        return self._dev.roiSize.tolist()

    def doWriteRoisize(self, value):
        self._dev.roiSize = value

    def doReadBinning(self):
        return self._dev.binning.tolist()

    def doWriteBinning(self, value):
        self._dev.binning = value

    def doReadZeropoint(self):
        return self._dev.zeroPoint.tolist()

    def doReadArray(self, quality):
        self.arraydesc = ArrayDesc('data', shape=tuple(self._dev.roiSize),
                                   dtype='<u4')
        return self._dev.value.reshape(self.arraydesc.shape)


class TOFChannel(ImageChannel):
    """
    Image channel with Time-of-flight related attributes.
    """

    parameters = {
        'delay':        Param('Delay from start pulse to first time channel',
                              type=int, settable=True, unit='ns',
                              mandatory=False, volatile=True),
        'timechannels': Param('Number of time channels', settable=True,
                              type=int, mandatory=False, volatile=True),
        'timeinterval': Param('Time for each time channel', type=int,
                              settable=True, unit='ns', mandatory=False,
                              volatile=True),
    }

    def doReadTimechannels(self):
        return self._dev.timeChannels

    def doWriteTimechannels(self, value):
        self._dev.timeChannels = value

    def doReadDelay(self):
        return self._dev.delay

    def doWriteDelay(self, value):
        self._dev.delay = value

    def doReadTimeinterval(self):
        return self._dev.timeInterval

    def doWriteTimeinterval(self, value):
        self._dev.timeInterval = value


class ReadableChannel(PyTangoDevice, PassiveChannel):
    """Pseudochannel for a single readable tango device. Usable e.g. to get a
    readable value into the scan plot."""

    parameters = {
        'valuenames': Param('Name(s) of provided value(s)',
                            type=listof(str), settable=True, mandatory=False,
                            default=[]),
    }

    def doRead(self, maxage=0):
        val = self._dev.value
        return val.tolist() if isinstance(val, numpy.ndarray) else val

    def valueInfo(self):
        names = self.valuenames if self.valuenames else [self.name]
        return tuple(Value(entry, unit=self.unit, fmtstr=self.fmtstr)
                     for entry in names)


class OnOffSwitch(PyTangoDevice, Moveable):
    """The OnOffSwitch is a generic devices that is capable of switching
    the desired Tango device on or off via the On()/Off commands."""

    valuetype = oneof('on', 'off')
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    tango_status_mapping = PyTangoDevice.tango_status_mapping.copy()
    tango_status_mapping[PyTango.DevState.OFF] = status.OK
    tango_status_mapping[PyTango.DevState.ALARM] = status.OK
    tango_status_mapping[PyTango.DevState.MOVING] = status.OK

    def doRead(self, maxage=0):
        if self._dev.State() == PyTango.DevState.OFF:
            return 'off'
        return 'on'

    def doStart(self, value):
        if value == 'on':
            self._dev.On()
        else:
            self._dev.Off()
