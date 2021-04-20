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
This module contains NICOS devices for each MLZ Tango (Entangle) base class,
and a few that add NICOS mixin features, like `WindowTimeoutAO`.

For a list of the base classes and their required Tango API, see
https://forge.frm2.tum.de/entangle/defs/entangle-master/
"""

import ast

import numpy

from nicos.core import SIMULATION, ArrayDesc, CanDisable, Device, HasLimits, \
    HasPrecision, HasTimeout, Moveable, NicosError, Override, Param, \
    Readable, Value, dictof, intrange, listof, nonemptylistof, oneof, \
    oneofdict, status, waitForCompletion
from nicos.core.constants import FINAL, SLAVE
from nicos.core.mixins import HasOffset, HasWindowTimeout
from nicos.devices.abstract import CanReference, Coder, Motor as NicosMotor
from nicos.devices.generic.detector import ActiveChannel, \
    CounterChannelMixin, ImageChannelMixin, PassiveChannel, \
    TimerChannelMixin
from nicos.devices.tango import PyTango, PyTangoDevice
from nicos.utils import squeeze

# Only export Nicos devices for 'from nicos.device.entangle import *'
__all__ = [
    'AnalogInput', 'Sensor', 'AnalogOutput', 'Actuator', 'RampActuator',
    'Motor', 'TemperatureController', 'PowerSupply', 'DigitalInput',
    'NamedDigitalInput', 'PartialDigitalInput', 'DigitalOutput',
    'NamedDigitalOutput', 'PartialDigitalOutput', 'StringIO', 'DetectorChannel',
    'TimerChannel', 'CounterChannel', 'ImageChannel', 'TOFChannel',
    'WindowTimeoutAO', 'VectorInput', 'VectorInputElement', 'VectorOutput',
    'OnOffSwitch',
]


class AnalogInput(PyTangoDevice, Readable):
    """
    The AnalogInput handles all devices only delivering an analogue value.
    """

    valuetype = float

    def doRead(self, maxage=0):
        return self._dev.value


class Sensor(AnalogInput, Coder):
    """
    The sensor interface describes all analog read only devices.

    The difference to AnalogInput is that the “value” attribute can be
    converted from the “raw value” to a physical value with an offset and a
    formula.
    """

    def doSetPosition(self, pos):
        self._dev.Adjust(pos)


class AnalogOutput(PyTangoDevice, HasLimits, CanDisable, Moveable):
    """
    The AnalogOutput handles all devices which set an analogue value.

    The main application field is the output of any signal which may be
    considered as continously in a range. The values may have nearly any
    value between the limits. The compactness is limited by the resolution of
    the hardware.

    This class should be considered as a base class e.g. for motors or
    temperature controllers.
    """

    valuetype = float
    parameter_overrides = {
        'abslimits': Override(mandatory=False, volatile=True),
    }

    def doReadAbslimits(self):
        absmin = float(self._getProperty('absmin'))
        absmax = float(self._getProperty('absmax'))

        return (absmin, absmax)

    def doRead(self, maxage=0):
        return self._dev.value

    def doStart(self, target):
        try:
            self._dev.value = target
        except NicosError:
            # changing target value during movement is not allowed by the
            # Tango base class state machine. If we are moving, stop first.
            if self.status(0)[0] == status.BUSY:
                self.stop()
                self._hw_wait()
                self._dev.value = target
            else:
                raise

    def doStop(self):
        self._dev.Stop()

    def doEnable(self, on):
        if on:
            self._dev.On()
        else:
            self._dev.Off()


class WindowTimeoutAO(HasWindowTimeout, AnalogOutput):
    """
    AnalogOutput with window timeout.
    """


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
        return self._dev.speed

    def doSetPosition(self, pos):
        self._dev.Adjust(pos)


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
        return self._dev.accel

    def doReadDecel(self):
        return self._dev.decel

    def doWriteDecel(self, value):
        self._dev.decel = value
        return self._dev.decel

    def doReference(self):
        self._setROParam('target', None)  # don't check target in wait() below
        self._dev.Reference()
        self.wait()

    def doTime(self, old_value, target):
        s, v, a, d = abs(old_value - target), self.speed, self.accel, self.decel
        if v <= 0:
            return 0
        if d <= 0:  # decel can be =0 to mean the same as accel
            d = a
        if a <= 0:
            return s / v
        if s > v ** 2 / a:  # do we reach nominal speed?
            return s / v + 0.5 * (v / a + v / d)
        return (a / d + 1) * (s / a)**0.5


class MotorAxis(HasOffset, Motor):
    """Tango motor with offset.

    This class is provided for motors which do not need any other features
    of the NICOS axis except the user offset.
    """

    def doRead(self, maxage=0):
        return Motor.doRead(self, maxage) - self.offset

    def doStart(self, target):
        return Motor.doStart(self, target + self.offset)

    def doSetPosition(self, pos):
        return Motor.doSetPosition(self, pos + self.offset)


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
        return self._dev.ramp


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
                              settable=True, category='general', unit='main',
                              volatile=True),
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

    def doWriteSetpoint(self, value):
        raise NicosError(self, 'To change the setpoint, use move(%s, %s)' %
                         (self, value))

    def doReadHeateroutput(self):
        return self._dev.heaterOutput

    def doPoll(self, n, maxage):
        if self.ramp:
            self._pollParam('setpoint', 1)
        if n % 5 == 0:
            self._pollParam('heateroutput', 5)
        if n % 30 == 0:
            self._pollParam('setpoint', 30)
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


def parse_mapping(mapping):
    """Parse the "mapping" property of digital devices."""
    reverse = {}
    forward = {}
    mapping = ast.literal_eval(mapping or '[]')
    for entry in mapping:
        parts = entry.split(':')
        if len(parts) < 2:
            continue
        try:
            val = int(parts[0].strip())
        except ValueError:
            continue
        label = parts[1].strip()
        reverse[val] = label
        if len(parts) == 2 or 'ro' not in parts[2]:
            forward[label] = val
    return reverse, forward


class DigitalInput(PyTangoDevice, Readable):
    """
    A device reading a bitfield.
    """

    valuetype = int

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
    }

    def doRead(self, maxage=0):
        return self._dev.value


class NamedDigitalInput(DigitalInput):
    """
    A DigitalInput with numeric values mapped to names.
    """

    parameters = {
        'mapping': Param('A dictionary mapping state names to integers - '
                         'if not given, read the mapping from the Tango '
                         'device if possible',
                         type=dictof(str, int), mandatory=False),
    }

    def doInit(self, mode):
        if self.mapping:
            self._reverse = {v: k for (k, v) in self.mapping.items()}
            return
        try:
            self._reverse = parse_mapping(self._getProperty('mapping'))[0]
        except Exception:
            self.log.warning('could not parse value mapping from Tango', exc=1)
            self._reverse = {}

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
        'unit': Override(default='', mandatory=False),
    }

    def doRead(self, maxage=0):
        return self._dev.value

    def doStart(self, target):
        self._dev.value = target


class NamedDigitalOutput(DigitalOutput):
    """
    A DigitalOutput with numeric values mapped to names.
    """

    parameters = {
        'mapping': Param('A dictionary mapping state names to integers - '
                         'if not given, read the mapping from the Tango '
                         'device if possible',
                         type=dictof(str, int), mandatory=False),
    }

    def doInit(self, mode):
        if self.mapping:
            self._reverse = {v: k for (k, v) in self.mapping.items()}
            # oneofdict: allows both types of values (string/int), but
            # normalizes them into the string form
            self.valuetype = oneofdict(self._reverse)
            self._forward = self.mapping
            return
        try:
            self._reverse, self._forward = \
                parse_mapping(self._getProperty('mapping'))
            # we don't build the valuetype from self._reverse since it should
            # only contain the write-able values
            self.valuetype = oneofdict({v: k for (k, v)
                                        in self._forward.items()})
        except Exception:
            self.log.warning('could not parse value mapping from Tango', exc=1)
            self._reverse = self._forward = {}

    def doStart(self, target):
        self._dev.value = self._forward.get(target, target)

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
        self._dev.Clear()
        self._dev.Prepare()

    def doStart(self):
        self._dev.Start()

    def doStop(self):
        self._dev.Stop()

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


class BaseImageChannel(ImageChannelMixin, DetectorChannel):
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
            shape = self._shape
        else:
            shape = (256, 256)  # select some arbitrary shape
        self.arraydesc = ArrayDesc('data', shape=shape, dtype='<u4')

    @property
    def _shape(self):
        return squeeze(tuple(self.roisize), 2)[::-1]

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
        self.arraydesc = ArrayDesc(
            'data', shape=self._shape, dtype='<u4')
        return self._dev.value.reshape(self.arraydesc.shape)


class ImageChannel(BaseImageChannel):
    """Image channel that automatically returns the sum of all counts."""

    def doInit(self, mode):
        BaseImageChannel.doInit(self, mode)
        if mode != SLAVE:
            self.readArray(FINAL)  # update readresult at startup

    def doReadArray(self, quality):
        # on quality FINAL wait for entangle ImageChannel finishing readout
        if quality == FINAL:
            waitForCompletion(self)
        narray = BaseImageChannel.doReadArray(self, quality)
        self.readresult = [narray.sum()]
        return narray

    def valueInfo(self):
        return Value(name=self.name, type='counter', fmtstr='%d',
                     errors='sqrt', unit='cts'),


class TOFChannel(BaseImageChannel):
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
    """Pseudochannel for a single readable entangle device. Usable e.g. to get a
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

    tango_status_mapping = PyTangoDevice.tango_status_mapping.copy()
    tango_status_mapping[PyTango.DevState.OFF] = status.OK
    tango_status_mapping[PyTango.DevState.ALARM] = status.OK
    tango_status_mapping[PyTango.DevState.MOVING] = status.OK

    def doReadUnit(self):
        return ''

    def doRead(self, maxage=0):
        if self._dev.State() == PyTango.DevState.OFF:
            return 'off'
        return 'on'

    def doStart(self, target):
        if target == 'on':
            self._dev.On()
        else:
            self._dev.Off()


class VectorInput(AnalogInput):
    """Returns all components of a VectorInput as a list."""

    valuetype = listof(float)

    def doRead(self, maxage=0):
        return list(self._dev.value)


class VectorInputElement(AnalogInput):
    """Returns a single component of a VectorInput."""

    parameters = {
        'index': Param('The index of the component to return', type=int,
                       mandatory=True),
    }

    def doRead(self, maxage=0):
        return self._dev.value[self.index]


class VectorOutput(PyTangoDevice, Moveable):
    """Returns and sets all components of a VectorOutput as a list."""
    # NOTE: does not inherit from AnalogOutput because we don't want HasLimits

    valuetype = listof(float)

    def doRead(self, maxage=0):
        return list(self._dev.value)

    def doStart(self, target):
        try:
            self._dev.value = target
        except NicosError:
            if self.status(0)[0] == status.BUSY:
                self.stop()
                self._hw_wait()
                self._dev.value = target
            else:
                raise

    def doStop(self):
        self._dev.Stop()
