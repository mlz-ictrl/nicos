#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
FRM-II/JCNS TANGO interface for the respective device classes.
"""

import PyTango

from nicos.core import Param, Override, status, Readable, Moveable, HasLimits, \
    Device, tangodev, DeviceMixinBase, oneof, dictof, intrange, \
    NicosError, CommunicationError, ConfigurationError
from nicos.devices.abstract import Coder, Motor as NicosMotor, CanReference
from nicos.utils import HardwareStub
from nicos.core import SIMULATION

# Only export Nicos devices for 'from nicos.device.tango import *'
__all__ = ['AnalogInput', 'Sensor', 'AnalogOutput', 'Actuator', 'Motor',
           'TemperatureController', 'DigitalInput', 'DigitalOutput', 'StringIO']

DEFAULT_STATUS_MAPPING = {
    PyTango.DevState.ON:     status.OK,
    PyTango.DevState.OFF:    status.PAUSED,
    PyTango.DevState.FAULT:  status.ERROR,
    PyTango.DevState.MOVING: status.BUSY,
}

EXC_MAPPING = {
    PyTango.CommunicationFailed : CommunicationError,
    PyTango.WrongNameSyntax : ConfigurationError,
    PyTango.DevFailed : NicosError,
}


class PyTangoDevice(DeviceMixinBase):
    """
    Basic PyTango device.

    The PyTangoDevice uses an internal PyTango.DeviceProxy but wraps command
    execution and attribute operations with logging and exception mapping.
    """

    parameters = {
        'tangodevice': Param('Tango device name', type=tangodev,
                             mandatory=True, preinit=True)
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

    def doStatus(self, maxage=0, mapping=DEFAULT_STATUS_MAPPING):  # pylint: disable=W0102
        # Query status code and string
        tangoState = self._dev.State()
        tangoStatus = self._dev.Status()

        # Map status
        nicosState = mapping.get(tangoState, status.UNKNOWN)

        return (nicosState, tangoStatus)

    def doVersion(self):
        return [(self.tangodevice, self._dev.version)]

    def doReset(self):
        self._dev.Reset()
        # XXX do we need to "if isOff(): On()" dance?

    def _setMode(self, mode):
        super(PyTangoDevice, self)._setMode(mode)
        # remove the TACO device on entering simulation mode, to prevent
        # accidental access to the hardware
        if mode == SIMULATION:
            self._dev = HardwareStub(self)

    def _getProperty(self, name, dev=None):
        """
        Utility function for getting a property by name easily.
        """
        if dev is None:
            dev = self._dev
        return dev.GetProperties((name, 'device'))[2]

    def _createPyTangoDevice(self, address):  # pylint: disable=E0202
        """
        Creates the PyTango DeviceProxy and wraps command execution and
        attribute operations with logging and exception mapping.
        """
        device = PyTango.DeviceProxy(address)
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
        def wrap(*args, **kwargs):
            # handle different types for better debug output
            if category == 'cmd':
                self.log.debug('[PyTango] command: %s%r' % (args[0], args[1:]))
            elif category == 'attr_read':
                self.log.debug('[PyTango] read attribute: %s' % args[0])
            elif category == 'attr_write':
                self.log.debug('[PyTango] write attribute: %s => %r'
                               % (args[0], args[1:]))
            elif category == 'attr_query':
                self.log.debug('[PyTango] query attribute properties: %s' % args[0])
            elif category == 'constructor':
                self.log.debug('[PyTango] device creation: %s' % args[0])
            elif category == 'internal':
                self.log.debug('[PyTango integration] internal: %s%r'
                               % (func.__name__, args))
            else:
                self.log.debug('[PyTango] call: %s%r'
                               % (func.__name__, args))

            # Try to execute the given func
            try:
                result = func(*args, **kwargs)

                if isinstance(result, PyTango.DeviceAttribute):
                    self.log.debug('\t=> %r' % result.value)
                else:
                    # This line explicitly logs '=> None' for commands which
                    # does not return a value. This indicates that the command
                    # execution ended.
                    self.log.debug('\t=> %r' % (str(result)[:300],))

                return result
            except tuple(EXC_MAPPING.keys()) as e:
                exc = str(e)
                if e.args:
                    exc = e.args[0] # Can be str or DevError

                    if isinstance(exc, PyTango.DevError):
                        exc = '%s: [%s] %s' % (exc.origin, exc.reason, exc.desc)

                self.log.debug('PyTango error: %s' % exc)
                raise EXC_MAPPING.get(type(e), NicosError)(self, exc)

        # hide the wrapping
        wrap.__name__ = func.__name__

        return wrap


class AnalogInput(PyTangoDevice, Readable):
    """
    Represents the client to a TANGO AnalogInput device.
    """

    valuetype = float
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doReadUnit(self):
        attrInfo = self._dev.attribute_query('value')
        return attrInfo.unit

    def doRead(self, maxage=0):
        return self._dev.value


class Sensor(AnalogInput, Coder):
    """
    Represents the client to a TANGO Sensor device.
    """

    def doSetPosition(self, value):
        self._dev.Adjust(value)


class AnalogOutput(PyTangoDevice, HasLimits, Moveable):
    """
    Represents the client to a TANGO AnalogOutput device.
    """

    valuetype = float
    parameter_overrides = {
        'abslimits': Override(mandatory=False),
        'unit':      Override(mandatory=False),
    }

    def doReadUnit(self):
        attrInfo = self._dev.attribute_query('value')
        return attrInfo.unit

    def doReadAbslimits(self):
        absmin = float(self._getProperty('absmin'))
        absmax = float(self._getProperty('absmax'))

        return (absmin, absmax)

    def doRead(self, maxage=0):
        return self._dev.value

    def doStart(self, value):
        self._dev.value = value

    def doStop(self):
        self._dev.Stop()


class Actuator(AnalogOutput, NicosMotor):
    """
    Represents the client to a TANGO Actuator device.
    """

    def doReadSpeed(self):
        return self._dev.speed

    def doWriteSpeed(self, value):
        self._dev.speed = value

    def doSetPosition(self, value):
        self._dev.Adjust(value)


class Motor(CanReference, Actuator):
    """
    Represents the client to a TANGO Motor device.
    """

    parameters = {
        'refpos': Param('Reference position', type=float, unit='main'),
        'accel':  Param('Acceleration', type=float, settable=True),
        'decel':  Param('Decelartion', type=float, settable=True),
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
        self._dev.devel = value

    def doReference(self):
        self._dev.Reference()


class TemperatureController(Actuator):
    """
    Represents the client to a TANGO TemperatureController device.
    """

    parameters = {
        'p':            Param('Proportional control parameter', type=float,
                              settable=True, category='general', chatty=True),
        'i':            Param('Integral control parameter', type=float,
                              settable=True, category='general', chatty=True),
        'd':            Param('Derivative control parameter', type=float,
                              settable=True, category='general', chatty=True),
        'heateroutput': Param('Heater output', type=float, category='general'),
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

    def doReadHeateroutput(self):
        return self._dev.heaterOutput

    def doPoll(self, n):
        if self.speed:
            self._pollParam('heateroutput', 1)
        else:
            self._pollParam('heateroutput', 60)

        self._pollParam('p')
        self._pollParam('i')
        self._pollParam('d')


class DigitalInput(PyTangoDevice, Readable):
    """
    Represents the client to a TANGO DigitalInput device.
    """

    valuetype = int
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doRead(self, maxage=0):
        return self._dev.value


class NamedDigitalInput(DigitalInput):
    """A DigitalInput with numeric values mapped to names."""

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
    """Base class for a TANGO DigitalInput with only a part of the full
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
    Represents the client to a TANGO DigitalOutput device.
    """

    valuetype = int
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doRead(self, maxage=0):
        return self._dev.value

    def doStart(self, value):
        self._dev.value = self.valuetype(value)


class NamedDigitalOutput(DigitalOutput):
    """A DigitalOutput with numeric values mapped to names."""

    parameters = {
        'mapping': Param('A dictionary mapping state names to integer values',
                         type=dictof(str, int), mandatory=True),
    }

    def doInit(self, mode):
        self._reverse = dict((v, k) for (k, v) in self.mapping.items())
        self.valuetype = oneof(*(list(self.mapping.keys()) +
                                 list(self.mapping.values())))

    def doStart(self, target):
        value = self.mapping.get(target, target)
        self._dev.value = self.valuetype(value)

    def doRead(self, maxage=0):
        value = self._dev.value
        return self._reverse.get(value, value)


class PartialDigitalOutput(NamedDigitalOutput):
    """Base class for a TANGO DigitalOutput with only a part of the full
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
    Represents the client to a TANGO StringIO device.
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
