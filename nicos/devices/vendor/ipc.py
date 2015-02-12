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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""IPC (Institut für Physikalische Chemie, Göttingen) hardware classes."""

import select
import socket
from threading import RLock
from time import sleep

from IO import StringIO
from RS485Client import RS485Client  # pylint: disable=F0401

from nicos.core import status, intrange, floatrange, oneofdict, oneof, \
    none_or, usermethod, Device, Readable, Moveable, Param, Override, \
    NicosError, CommunicationError, ProgrammingError, InvalidValueError, \
    defaultIsCompleted, HasTimeout, HasCommunication, SIMULATION
from nicos.devices.abstract import Coder as NicosCoder, Motor as NicosMotor
from nicos.devices.taco.core import TacoDevice
from nicos.utils import HardwareStub, closeSocket, lazy_property


STX = chr(2)
EOT = chr(4)
ACK = chr(6)
NAK = chr(0x15)
DC1 = chr(0x11)
DC2 = chr(0x12)
DC3 = chr(0x13)

PRINTABLES = {
    STX: '<STX>',
    EOT: '<EOT>',
    ACK: '<ACK>',
    NAK: '<NAK>',
    DC1: '<DC1>',
    DC2: '<DC2>',
    DC3: '<DC3>',
}

def convert(string):
    return ''.join(PRINTABLES.get(c, c) for c in string)

IPC_MAGIC = {
    # motor cards
    # # only works for single cards, ### only works for triple cards
    # ###### only works for sixfold cards
    # limits is None or a tuple (numdigits, minvalue, maxvalue)
    31:  ['Reset motor card', None],                    # ### ######
    32:  ['Start motor', None],                         # ### ######
    33:  ['Stop motor immediately', None],              # ### ######
    34:  ['Switch forward direction', None],            # ### ######
    35:  ['Switch backward direction', None],           # ### ######
    36:  ['Switch fullstep', None],                     #
    37:  ['Switch halfstep', None],                     #
    38:  ['Switch relay on', None],                     #
    39:  ['Switch relay off', None],                    #
    40:  ['Write values to EEPROM', None],              # ### ######
    41:  ['Set speed', (3, 0, 255)],                    # ### ######
    42:  ['Set acceleration', (3, 0, 255)],             # ### ######
    43:  ['Set current position', (6, 0, 999999)],      # ### ######
    44:  ['Set maximum position', (6, 0, 999999)],      # ### ######
    45:  ['Set minimum position', (6, 0, 999999)],      # ### ######
    46:  ['Set multisteps and start', (6, 0, 999999)],  # ### ######
    # ... with given speed and switch back
    47:  ['Find reference switch', (3, 0, 255)],        #
    48:  ['Check motor connection', None],              #
    49:  ['Save config byte to EEPROM', (3, 0, 63)],    #
    50:  ['Select ramp shape', (3, 1, 4)],              #
    51:  ['Save user value to EEPROM', (6, 0, 999999)], # ### ######
    52:  ['Stop motor using ramp', None],               #
    53:  ['Switch driver off', None],                   # ### ######
    54:  ['Switch driver on', None],                    # ### ######
    55:  ['Set inhibit delay', (3, 0, 255)],            #
    56:  ['Set target position', (6, 0, 999999)],         ### ######
    57:  ['Set microsteps', (3, 0, 4)],                   ### ######
    58:  ['Set stop delay', (3, 0, 255)],               #
    60:  ['Set clock divider', (3, 1, 7)],                ###
    128: ['Read speed', None],                          # ### ######
    129: ['Read accel', None],                          # ### ######
    130: ['Read position', None],                       # ### ######
    131: ['Read maximum', None],                        # ### ######
    132: ['Read minimum', None],                        # ### ######
    133: ['Read multisteps', None],                     #
    134: ['Read status', None],                         # ### ######
    135: ['Read config byte', None],                    #
    136: ['Read ramp shape', None],                     #
    137: ['Read version number', None],                 # ### ######
    138: ['Read user value', None],                     # ### ######
    139: ['Read inhibit delay', None],                  #
    140: ['Read target position', None],                  ### ######
    141: ['Read microsteps', None],                       ### ######
    142: ['Read load indicator', None],                   ### ######
    143: ['Read stop delay', None],                     #
    144: ['Read clock divider', None],                    ###
    # encoder/potentiometer (abs enc=#, inc enc=##, poti=###)
    150: ['Read encoder value', None],                  # ## ###
    151: ['Read encoder version', None],                # ## ###
    152: ['Read encoder configuration', None],          # ## ###
    153: ['Reset encoder', None],                       # ## ###
    154: ['Set encoder configuration', (3, 0, 255)],    # ##
    155: ['Select endat memory range', (3, 161, 185)],  #
    156: ['Read endat parameter', (3, 0, 15)],          #
    157: ['Write endat parameter', (3, 0, 15)],         #
    # 4-wing slits
    160: ['Set bottom target position', (4, 0, 4095)],
    161: ['Set top target position', (4, 0, 4095)],
    162: ['Set right target position', (4, 0, 4095)],
    163: ['Set left target position', (4, 0, 4095)],
    164: ['Read status', None],
    165: ['Read version number', None],
    166: ['Read bottom target position', None],
    167: ['Read top target position', None],
    168: ['Read right target position', None],
    169: ['Read left target position', None],
    170: ['Write user value to EEPROM', (4, 0, 9999)],
    171: ['Read user value', None],
    # digital input
    180: ['Read digital bits 0-7', None],
    181: ['Read digital bits 8-15', None],
    182: ['Save user value to EEPROM', (6, 0, 999999)],
    183: ['Read user value', None],
    184: ['Read digital input version number', None],
    185: ['Read digital bits 0-15', None],
    # digital output
    190: ['Set digital output bits', (3, 0, 255)],
    191: ['Read digital output bits', None],
    192: ['Save user value to EEPROM', (6, 0, 999999)],
    193: ['Read user value', None],
    194: ['Read digital output version number', None],
    195: ['Read status', None],
}


def crc_ipc(string):
    crc = 255
    for byte in string:
        byte = ord(byte)
        crc ^= byte
        for _ in range(8):
            temp = crc % 2
            crc = int(crc / 2)
            if temp != 0:
                crc ^= 0xA1
    return '%03d' % crc


class InvalidCommandError(ProgrammingError):
    """Error raised for "invalid command" response of IPC cards."""


class IPCModBus(Device):
    """Abstract class for IPC protocol communication over RS-485.

    A device of this type is needed as the `.bus` parameter of the other IPC
    devices.

    Concrete implementations are `IPCModBusTaco`, `IPCModBusTCP`,
    `IPCModBusSerial`.
    """


class IPCModBusTaco(TacoDevice, IPCModBus):
    """IPC protocol communication over TACO RS-485 server."""

    taco_class = RS485Client
    taco_errorcodes = {
        537133063: InvalidCommandError,
    }

    parameters = {
        'bustimeout': Param('Communication timeout for this device',
                            type=floatrange(0.1, 1200), default=0.5, settable=True),
    }

    def send(self, addr, cmd, param=0, length=0):
        return self._taco_guard(self._dev.SDARaw, addr, cmd, length, param)

    def get(self, addr, cmd, param=0, length=0):
        return self._taco_guard(self._dev.SRDRaw, addr, cmd, length, param)

    def ping(self, addr):
        return self._taco_guard(self._dev.Ping, addr)

    def doReadBustimeout(self):
        if self._dev and hasattr(self._dev, 'timeout'):
            return float(self._taco_guard(self._dev.timeout))
        raise ProgrammingError(self, "TacoDevice has no 'timeout'!")

    def doUpdateBustimeout(self, value):
        if self._dev:
            self._taco_update_resource('timeout', str(value))


class IPCModBusRS232(HasCommunication, IPCModBus):
    """Base class for IPC connections not using the RS485 TACO server.

    This is an abstract class; use one of `IPCModBusTacoSerial`,
    `IPCModBusTCP` or `IPCModBusSerial`.
    """

    parameters = {
        'bustimeout': Param('Maximum time to wait for an answer, set '
                            'this high to slow down everything', unit='s',
                            type=float, default=0.1, settable=True),
    }

    parameter_overrides = {
        'comtries':   Override(default=5),
    }

    def doInit(self, mode):
        self._lock = RLock()
        self._connection = None
        if mode != SIMULATION:
            try:
                self.doReset()
            except Exception:
                self.log.exception('IPC: exception during init')

    def _setMode(self, mode):
        IPCModBus._setMode(self, mode)
        if mode == SIMULATION:
            self._connection = HardwareStub(self)

    def _comm(self, request, ping=False):
        if not ping:
            request += crc_ipc(request)
        request = STX + request + EOT
        self.log.debug('sending %r' % convert(request))
        with self._lock:
            response = self._transmit(request)
        # now check data
        self.log.debug('received %r' % convert(response))
        if not response:
            raise CommunicationError(self, 'no response')
        elif response == ACK:
            return 0
        elif response == NAK:
            if ping:
                return 1
            raise CommunicationError(self, 'CRC error')
        elif response == DC1:
            raise InvalidCommandError(self, 'invalid command number')
        elif response == DC2:
            raise ProgrammingError(self, 'invalid command parameter')
        elif response == DC3:
            raise CommunicationError(self, 'command failed, e.g. hardware error')
        elif len(response) < 3:
            raise CommunicationError(self, 'response too short')
        elif response[0] != STX:
            raise CommunicationError(self, 'response should start with STX')
        elif response[-1] != EOT:
            raise CommunicationError(self, 'response should end with EOT')
        else:  # good response!
            response = response[1:-1]  # remove STX/EOT
            if len(response) > 2:  # try to check CRC
                if response[-3:] != crc_ipc(response[:-3]):
                    raise CommunicationError(self, 'wrong CRC on response')
            # return response integer (excluding address and command number)
            try:
                # command might fail if no value was transmitted
                return int(response[2:-3])
            except ValueError as err:
                raise CommunicationError(
                    self, 'invalid response: missing value (%s)' % err)

    def ping(self, addr):
        if 32 <= addr <= 255:
            if self._comm(chr(addr), ping=True):
                return addr
            else:
                return -1
        else:
            return -1

    def send(self, addr, cmd, param=0, length=0):
        try:
            cmdname, limits = IPC_MAGIC[cmd]
        except KeyError:
            raise ProgrammingError(self, 'Command %s not supported' % cmd)
        if limits:
            if length != limits[0] or not limits[1] <= param <= limits[2]:
                raise ProgrammingError(self, 'Parameter %s outside allowed '
                    'values %s for cmd %s' % (param, limits, cmdname))
        elif length or param:
            raise ProgrammingError(self, 'Sending parameters is not allowed '
                                    'for cmd %s' % cmdname)
        s = chr(addr) + chr(cmd)
        if length > 0:
            s += '%0*d' % (length, param)
        self.log.debug('sending %s to card %s' % (cmdname, addr))
        return self._comm(s)

    def get(self, addr, cmd, param=0, length=0):
        return self.send(addr, cmd, param, length)


class IPCModBusTacoSerial(TacoDevice, IPCModBusRS232):
    taco_class = StringIO

    def _transmit(self, request, last_try=False):
        response = ''
        self._dev.write(request)
        for _i in range(self.comtries):
            sleep(self.bustimeout)
            try:
                data = self._dev.read()
            except Exception:
                data = ''
            if not data:
                continue
            response += data
            if response[-1] in (EOT, DC1, DC2, DC3, ACK, NAK):
                return response
        raise CommunicationError(self, 'no response')

    def doReset(self):
        TacoDevice.doReset(self)


class IPCModBusTCP(IPCModBusRS232):
    """IPC protocol communication bus over network to serial adapter
    using TCP connection.
    """

    parameters = {
        'host':      Param('Hostname (or IP) of network2serial converter',
                           type=str, settable=True, mandatory=True),
        'port':      Param('TCP Port on network2serial converter',
                           type=int, default=4001),
    }

    def doReset(self):
        if self._connection:
            closeSocket(self._connection)
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._connection.connect((self.host, self.port))

    def _transmit(self, request, last_try=False):
        response = ''
        try:
            self._connection.sendall(request)
            self.log.debug('request sent')

            for i in range(self.comtries):
                self.log.debug('waiting for response, try %d/%d' %
                               (i, self.comtries))
                p = select.select([self._connection], [], [], self.bustimeout)
                if self._connection in p[0]:
                    data = self._connection.recv(20)  # more than enough!
                    if not data:
                        raise CommunicationError(self, 'no reply from recv')
                    response += data
                    if response[-1] in (EOT, DC1, DC2, DC3, ACK, NAK):
                        return response
        except (socket.error, select.error) as err:
            if last_try:
                raise CommunicationError(
                    self, 'tcp connection failed: %s' % err)
            # try reopening connection
            self.log.warning('tcp connection failed, retrying', exc=1)
            self.doReset()
            return self._transmit(request, last_try=True)
        else:
            return response


class IPCModBusSerial(IPCModBusRS232):
    """IPC protocol communication directly over serial line."""

    parameters = {
        'port': Param('Device file name of the serial port to use',
                      type=str, settable=True, mandatory=True),
    }

    _connection = None

    def doReset(self):
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
        import serial
        self._connection = serial.Serial(self.port, baudrate=19200,
                                         timeout=self.bustimeout)

    def doUpdateBustimeout(self, value):
        if self._connection:
            self._connection.timeout = value

    def _transmit(self, request, last_try=False):
        response = ''
        try:
            self._connection.write(request)

            for _ in range(self.comtries):
                data = self._connection.read(20)
                response += data
                if response and response[-1] in (EOT, DC1, DC2, DC3, ACK, NAK):
                    return response
        except IOError as err:
            if last_try:
                raise CommunicationError(self, 'serial line failed: %s' % err)
            # try reopening connection
            self.log.warning('serial line failed, resetting', exc=1)
            self.doReset()
            return self._transmit(request, last_try=True)
        else:
            return response


class Coder(NicosCoder):
    """This class supports both IPC absolute and incremental coder cards.

    It can be used with the `nicos.devices.generic.Axis` class.
    """

    parameters = {
        'addr':      Param('Bus address of the coder', type=int,
                           mandatory=True),
        'confbyte':  Param('Configuration byte of the coder', settable=True,
                           type=intrange(0, 255), prefercache=False),
        'zerosteps': Param('Coder steps for physical zero', type=float,
                           unit='steps', settable=True),
        'slope':     Param('Coder slope', type=float, default=1.0,
                           unit='steps/main', settable=True),
        'firmware':  Param('Firmware version', type=int),
        'steps':     Param('Current coder position in steps', type=int,
                           settable=False),
        'circular':  Param('Wrap-around value for circular coders, if negative '
                           'use it as +/-, else as 0..value, None disables this',
                           type=none_or(float), settable=True, default=None),
        'readings':  Param('Number of readings to average over '
                           'when determining current position', type=int,
                           default=1, settable=True),
    }

    attached_devices = {
        'bus': (IPCModBus, 'The communication bus'),
    }

    def doInit(self, mode):
        bus = self._adevs['bus']
        if mode != SIMULATION:
            bus.ping(self.addr)
            try:
                actual_confbyte = self.doReadConfbyte()
            except NicosError:
                actual_confbyte = -1
            if self.confbyte != actual_confbyte:
                self.doWriteConfbyte(self.confbyte)
                self.log.warning('Confbyte mismatch between setup and card, '
                                 'overriding card value to 0x%02x' %
                                 self.confbyte)
        self._lasterror = None

    def doVersion(self):
        version = self._adevs['bus'].get(self.addr, 151)
        return [('IPC encoder card, %s' % self._hwtype, str(version))]

    def doReadFirmware(self):
        return self._adevs['bus'].get(self.addr, 151)

    def doReadConfbyte(self):
        return self._adevs['bus'].get(self.addr, 152)

    def doWriteConfbyte(self, byte):
        self._adevs['bus'].send(self.addr, 154, byte, 3)

    def doUpdateConfbyte(self, byte):
        try:
            self._type = self._getcodertype(byte)
            self._resolution = byte & 31
        except Exception:
            self._type = None
            self._resolution = None

    @lazy_property
    def _hwtype(self):
        """Returns 'analog' or 'digital', used for features that only one of the
        card types supports. 'analog' type is for potis and 'digital' is for
        rotary encoders.
        """
        firmware = self._adevs['bus'].get(self.addr, 151)
        confbyte = self._adevs['bus'].get(self.addr, 152)
        if confbyte < 4:
            return 'digital'
        if confbyte & 0xe0 == 0x20:
            if firmware < 20:  # wild guess, but seems to work...
                return 'analog'
        return 'digital'

    def _getcodertype(self, byte):
        """Extract coder type from configuration byte."""
        if byte < 4:
            return 'incremental encoder, 24bit, ' + \
                ['no reset', 'reset once', 'reset always',
                 'reset once to halfrange'][byte]
        if self._hwtype == 'analog':
            return 'potentiometer, %dbit' % (byte & 0x1F)
        proto = byte & 128 and 'endat' or 'ssi'
        coding = byte & 64 and 'gray' or 'binary'
        parity = byte & 32 and 'no parity' or 'even parity'
        return 'absolute encoder, %s-protocol, %s-coded, %s, %dbit' % \
            (proto, coding, parity, byte & 31)

    def doReset(self):
        try:
            self._adevs['bus'].send(self.addr, 153)
        except NicosError:
            pass
        else:
            sleep(0.5)

    def _fromsteps(self, value):
        return float((value - self.zerosteps) / self.slope)

    def doReadSteps(self):
        bus = self._adevs['bus']
        try:
            try:
                value = bus.get(self.addr, 150)
            except NicosError:
                self._endatclearalarm()
                sleep(1)
                # try again
                value = bus.get(self.addr, 150)
        except NicosError as e:
            # record last error to return it from doStatus()
            self._lasterror = str(e)
            raise
        self.log.debug('value is %d steps' % value)
        return value

    def doRead(self, maxage=0):
        # make sure to ask hardware, don't use cached value of steps
        steps = sum(self.doReadSteps() for _ in range(self.readings))
        steps = int(steps / float(self.readings))
        self._params['steps'] = steps
        if self._cache:  # save last valid position in cache
            self._cache.put(self, 'steps', steps)
        pos = self._fromsteps(steps)
        if self.circular is not None:
            # make it wrap around
            pos = pos % abs(self.circular)
            # if we want +/- instead of 0 to x and value is >x/2
            if self.circular < 0 and pos > -0.5*self.circular:
                # subtract x to make it -x/2..0..x/2 (circular is negative here)
                pos += self.circular
        self.log.debug('position is ' + self.format(pos))
        return pos

    def doStatus(self, maxage=0):
        if self._lasterror:
            return status.ERROR, self._lasterror
        return status.OK, ''

    def doSetPosition(self, target):
        raise NicosError('setPosition not implemented for IPC coders')

    def _endatclearalarm(self):
        """Clear alarm for a binary-endat encoder."""
        if self._type is not None and 'endat-protocol' not in self._type:
            return
        bus = self._adevs['bus']
        try:
            bus.send(self.addr, 155, 185, 3)
            sleep(0.5)
            bus.send(self.addr, 157, 0, 3)
            sleep(0.5)
            self.doReset()
        except Exception:
            raise CommunicationError(self, 'cannot clear alarm for encoder')


class Motor(HasTimeout, NicosMotor):
    """This class supports IPC 6-fold, 3-fold and single motor cards.

    It can be used with the `nicos.devices.generic.Axis` class.
    """

    parameters = {
        'addr':       Param('Bus address of the motor', type=int, mandatory=True),
        'unit':       Param('Motor unit', type=str, default='steps'),
        'zerosteps':  Param('Motor steps for physical zero', type=float,
                            unit='steps', settable=True),
        'slope':      Param('Motor slope', type=float, settable=True,
                            unit='steps/main', default=1.0),
        # those parameters come from the card
        'firmware':   Param('Firmware version', type=int),
        'steps':      Param('Last position in steps', settable=True,
                            type=intrange(0, 999999), prefercache=False),
        'speed':      Param('Motor speed (0..255)', settable=True,
                            type=intrange(0, 255)),
        'accel':      Param('Motor acceleration (0..255)', settable=True,
                            type=intrange(0, 255)),
        'confbyte':   Param('Configuration byte', type=intrange(-1, 255),
                            settable=True),
        'ramptype':   Param('Ramp type', settable=True, type=intrange(1, 4)),
        'microstep':  Param('Microstepping mode', unit='steps', settable=True,
                            type=oneof(1, 2, 4, 8, 16)),
        'min':        Param('Lower motorlimit', settable=True,
                            type=intrange(0, 999999), unit='steps'),
        'max':        Param('Upper motorlimit', settable=True,
                            type=intrange(0, 999999), unit='steps'),
        'startdelay': Param('Start delay', type=floatrange(0, 25), unit='s',
                            settable=True),
        'stopdelay':  Param('Stop delay', type=floatrange(0, 25), unit='s',
                            settable=True),
        'divider':    Param('Speed divider', settable=True,
                            type=intrange(-1, 7)),
        # volatile parameters to read/switch card features
        'inhibit':    Param('Inhibit input', default='off', volatile=True,
                            type=oneofdict({0: 'off', 1: 'on'})),
        'relay':      Param('Relay switch', type=oneofdict({0: 'off', 1: 'on'}),
                            settable=True, default='off', volatile=True),
        'power':      Param('Internal power stage switch', default='on',
                            type=oneofdict({0: 'off', 1: 'on'}), settable=True,
                            volatile=True),
    }

    parameter_overrides = {
        'timeout': Override(mandatory=False, default=360),
    }

    attached_devices = {
        'bus': (IPCModBus, 'The communication bus'),
    }

    def doInit(self, mode):
        bus = self._adevs['bus']
        if mode != SIMULATION:
            bus.ping(self.addr)
            if self._hwtype == 'single':
                if self.confbyte != self.doReadConfbyte():
                    self.doWriteConfbyte(self.confbyte)
                    self.log.warning('Confbyte mismatch between setup and card,'
                                     ' overriding card value to 0x%02x' %
                                     self.confbyte)
            # make sure that the card has the right "last steps"
            if self.steps != self.doReadSteps():
                self.doWriteSteps(self.steps)
                self.log.warning('Resetting stepper position to last known '
                                 'good value %d' % self.steps)
            self._type = 'stepper motor, ' + self._hwtype
        else:
            self._type = 'simulated stepper'

    def doVersion(self):
        try:
            version = self._adevs['bus'].get(self.addr, 137)
        except InvalidCommandError:
            return []
        else:
            return [('IPC motor card', str(version))]

    def _tosteps(self, value):
        return int(float(value) * self.slope + self.zerosteps)

    def _fromsteps(self, value):
        return float((value - self.zerosteps) / self.slope)

    @lazy_property
    def _hwtype(self):
        """Returns 'single' or 'triple', used for features that only one of the
        card types supports.
        """
        return self.doReadDivider() == -1 and 'single' or 'triple'

    def doReadUserlimits(self):
        if self.slope < 0:
            return (self._fromsteps(self.max), self._fromsteps(self.min))
        else:
            return (self._fromsteps(self.min), self._fromsteps(self.max))

    def doWriteUserlimits(self, limits):
        NicosMotor.doWriteUserlimits(self, limits)
        if self.slope < 0:
            self.min = self._tosteps(limits[1])
            self.max = self._tosteps(limits[0])
        else:
            self.min = self._tosteps(limits[0])
            self.max = self._tosteps(limits[1])

    def doReadSpeed(self):
        return self._adevs['bus'].get(self.addr, 128)

    def doWriteSpeed(self, value):
        self._adevs['bus'].send(self.addr, 41, value, 3)

    def doReadAccel(self):
        return self._adevs['bus'].get(self.addr, 129)

    def doWriteAccel(self, value):
        if self._hwtype != 'single' and value > 31:
            raise ValueError(self, 'acceleration value %d too big for '
                             'non-single cards' % value)
        self._adevs['bus'].send(self.addr, 42, value, 3)
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadRamptype(self):
        try:
            return self._adevs['bus'].get(self.addr, 136)
        except InvalidCommandError:
            return 1

    def doWriteRamptype(self, value):
        try:
            self._adevs['bus'].send(self.addr, 50, value, 3)
        except InvalidCommandError:
            raise InvalidValueError(self, 'ramp type not supported by card')
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadDivider(self):
        if self._mode == SIMULATION:
            return -1   # can't determine value in simulation mode!
        try:
            return self._adevs['bus'].get(self.addr, 144)
        except InvalidCommandError:
            return -1

    def doWriteDivider(self, value):
        try:
            self._adevs['bus'].send(self.addr, 60, value, 3)
        except InvalidCommandError:
            raise InvalidValueError(self, 'divider not supported by card')
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadMicrostep(self):
        try:
            # microstepping cards
            return [1, 2, 4, 8, 16][self._adevs['bus'].get(self.addr, 141)]
        except InvalidCommandError:
            # sinple cards only support full or half steps
            return [1, 2][(self._adevs['bus'].get(self.addr, 134) & 4) >> 2]

    def doWriteMicrostep(self, value):
        if self._hwtype == 'single':
            if value == 1:
                self._adevs['bus'].send(self.addr, 36)
            elif value == 2:
                self._adevs['bus'].send(self.addr, 37)
            else:
                raise InvalidValueError(self,
                                        'microsteps > 2 not supported by card')
        else:
            self._adevs['bus'].send(self.addr, 57,
                                    [1, 2, 4, 8, 16].index(value), 3)
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadMax(self):
        return self._adevs['bus'].get(self.addr, 131)

    def doWriteMax(self, value):
        self._adevs['bus'].send(self.addr, 44, value, 6)

    def doReadMin(self):
        return self._adevs['bus'].get(self.addr, 132)

    def doWriteMin(self, value):
        self._adevs['bus'].send(self.addr, 45, value, 6)

    def doReadStepsize(self):
        return bool(self._adevs['bus'].get(self.addr, 134) & 4)

    def doReadConfbyte(self):
        try:
            return self._adevs['bus'].get(self.addr, 135)
        except InvalidCommandError:
            return -1

    def doWriteConfbyte(self, value):
        if self._hwtype == 'single':
            self._adevs['bus'].send(self.addr, 49, value, 3)
        else:
            raise InvalidValueError(self, 'confbyte not supported by card')
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadStartdelay(self):
        if self.firmware > 40:
            try:
                return self._adevs['bus'].get(self.addr, 139) / 10.0
            except InvalidCommandError:
                return 0.0
        else:
            return 0.0

    def doWriteStartdelay(self, value):
        if self._hwtype == 'single':
            self._adevs['bus'].send(self.addr, 55, int(value * 10), 3)
        else:
            raise InvalidValueError(self, 'startdelay not supported by card')
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadStopdelay(self):
        if self.firmware > 44:
            try:
                return self._adevs['bus'].get(self.addr, 143) / 10.0
            except InvalidCommandError:
                return 0.0
        else:
            return 0.0

    def doWriteStopdelay(self, value):
        if self._hwtype == 'single':
            self._adevs['bus'].send(self.addr, 58, int(value * 10), 3)
        else:
            raise InvalidValueError(self, 'stopdelay not supported by card')
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadFirmware(self):
        return self._adevs['bus'].get(self.addr, 137)

    def doReadSteps(self):
        return self._adevs['bus'].get(self.addr, 130)

    def doWriteSteps(self, value):
        self.log.debug('setting new steps value: %s' % value)
        self._adevs['bus'].send(self.addr, 43, value, 6)

    def doStart(self, target):
        target = self._tosteps(target)
        self.log.debug('target is %d steps' % target)
        bus = self._adevs['bus']
        self.wait()
        pos = self._tosteps(self.read(0))
        self.log.debug('pos is %d steps' % pos)
        diff = target - pos
        if diff == 0:
            return
        elif diff < 0:
            bus.send(self.addr, 35)
        else:
            bus.send(self.addr, 34)
        bus.send(self.addr, 46, abs(diff), 6)
        sleep(0.1)  # moved here from doWait.

    def doReset(self):
        bus = self._adevs['bus']
        if self.status(0)[0] != status.OK:  # busy or error
            bus.send(self.addr, 33)  # stop
            try:
                self.wait()        # this might take a while, ignore errors
            except Exception:
                pass
        # remember current state
        actpos  = bus.get(self.addr, 130)
        speed   = bus.get(self.addr, 128)
        accel   = bus.get(self.addr, 129)
        minstep = bus.get(self.addr, 132)
        maxstep = bus.get(self.addr, 131)
        bus.send(self.addr, 31)  # reset card
        sleep(0.2)
        if self._hwtype == 'triple':
            # triple cards need a LONG time for resetting
            sleep(2)
        # update state
        bus.send(self.addr, 41, speed, 3)
        bus.send(self.addr, 42, accel, 3)
        bus.send(self.addr, 45, minstep, 6)
        bus.send(self.addr, 44, maxstep, 6)
        bus.send(self.addr, 43, actpos, 6)

    def doIsCompleted(self):
        return defaultIsCompleted(self, errorstates=())

    def doStop(self):
        if self._hwtype == 'single':
            self._adevs['bus'].send(self.addr, 52)
        else:
            self._adevs['bus'].send(self.addr, 33)
        sleep(0.2)

    def doRead(self, maxage=0):
        value = self._adevs['bus'].get(self.addr, 130)
        self._params['steps'] = value  # save last valid position in cache
        if self._cache:
            self._cache.put(self, 'steps', value)
        self.log.debug('value is %d' % value)
        return self._fromsteps(value)

    def doReadRelay(self):
        return 'on' if self._adevs['bus'].get(self.addr, 134) & 8 else 'off'

    def doWriteRelay(self, value):
        if value in [0, 'off']:
            self._adevs['bus'].send(self.addr, 39)
        elif value in [1, 'on']:
            self._adevs['bus'].send(self.addr, 38)

    def doReadInhibit(self):
        return (self._adevs['bus'].get(self.addr, 134) & 16) == 16

    def doReadPower(self):
        return 'on' if self._adevs['bus'].get(self.addr, 134) & 16384 else 'off'

    def doWritePower(self, value):
        if value in [0, 'off']:
            self._adevs['bus'].send(self.addr, 53)
        elif value in [1, 'on']:
            self._adevs['bus'].send(self.addr, 54)

    def doStatus(self, maxage=0):
        state = self._adevs['bus'].get(self.addr, 134)
        st = status.OK

        msg = ''
        #msg += (state & 2) and ', backward' or ', forward'
        #msg += (state & 4) and ', halfsteps' or ', fullsteps'
        if state & 16:
            msg += ', inhibit active'
        if state & 128:
            msg += ', reference switch active'
        if state & 256:
            msg += ', software limit - reached'
        if state & 512:
            msg += ', software limit + reached'
        if state & 16384 == 0:
            msg += ', external power stage enabled'
        if state & 32:
            msg += ', limit switch - active'
        if state & 64:
            msg += ', limit switch + active'
        if self._hwtype == 'single':
            msg += (state & 8) and ', relais on' or ', relais off'
            if state & 8:
                # on single cards, if relay is ON, card is supposedly BUSY
                st = status.BUSY
        if state & 32768:
            st = status.BUSY
            msg += ', waiting for start/stopdelay'

        # check error states last
        if state & 32 and state & 64:
            st = status.ERROR
            msg = msg.replace('limit switch - active, limit switch + active',
                'EMERGENCY STOP pressed or both limit switches broken')
        if state & 1024:
            st = status.ERROR
            msg += ', device overheated'
        if state & 2048:
            st = status.ERROR
            msg += ', motor undervoltage'
        if state & 4096:
            st = status.ERROR
            msg += ', motor not connected or leads broken'
        if state & 8192:
            st = status.ERROR
            msg += ', hardware failure or device not reset after power-on'

        # if it's moving, it's not in error state! (except if the emergency stop
        # is active)
        if state & 1 and (state & 96 != 96):
            st = status.BUSY
            msg = ', moving' + msg
        self.log.debug('status is %d:%s' % (st, msg[2:]))
        return st, msg[2:]

    def doSetPosition(self, target):
        """Adjust the current stepper position of the IPC-stepper card to match
        the given position.

        This is in contrast to the normal behaviour which just adjusts the
        zerosteps, but IPC cards have a limited range, so it is crucial to stay
        within that.  So we 'set' the position of the card instead of adjusting
        our zerosteps.
        """
        self.log.debug('setPosition: %s' % target)
        value = self._tosteps(target)
        self.doWriteSteps(value)
        self._params['steps'] = value  # save last valid position in cache
        if self._cache:
            self._cache.put(self, 'steps', value)

    @usermethod
    def _store(self):
        self._adevs['bus'].send(self.addr, 40)
        self.log.info('parameters stored to EEPROM')

    @usermethod
    def _printconfig(self):
        byte = self.confbyte
        c = ''

        if byte & 1: c += 'limit switch 1:  high = active\n'
        else: c += 'limit switch 1:  low = active\n'
        if byte & 2: c += 'limit switch 2:  high = active\n'
        else: c += 'limit switch 2:  low = active\n'
        if byte & 4: c += 'inhibit entry:  high = active\n'
        else: c += 'inhibit entry:  low = active\n'
        if byte & 8: c += 'reference switch:  high = active\n'
        else: c += 'reference switch:  low = active\n'
        if byte & 16: c += 'use external powerstage\n'
        else: c += 'use internal powerstage\n'
        if byte & 32: c += 'leads testing disabled\n'
        else: c += 'leads testing enabled\n'
        if byte & 64: c += 'reversed limit switches\n'
        else: c += 'normal limit switch order\n'
        if byte & 128: c += 'freq-range: 8-300Hz\n'
        else: c += 'freq-range: 90-3000Hz\n'

        self.log.info(c)


class IPCRelay(Moveable):
    """Makes the relay of an IPC single stepper card available as switch."""

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    attached_devices = {
        'stepper': (Motor, 'The stepper card whose relay is controlled'),
    }

    valuetype = oneofdict({0: 'off', 1: 'on'})

    def doStart(self, target):
        self._adevs['stepper'].relay = target

    def doRead(self, maxage=0):
        return self._adevs['stepper'].relay

    def doStatus(self, maxage=0):
        return status.OK, 'relay is %s' % self._adevs['stepper'].relay


class IPCInhibit(Readable):
    """Makes the inhibit of an IPC single stepper card available as an input.

    Returns 'on' if inhibit is active, 'off' otherwise.
    """

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    attached_devices = {
        'stepper': (Motor, 'The stepper card whose inhibit is read out'),
    }

    def doRead(self, maxage=0):
        return 'on' if self._adevs['stepper'].inhibit else 'off'

    def doStatus(self, maxage=0):
        return status.OK, 'inhibit is ' + self.doRead()


class Input(Readable):
    """IPC I/O card digital input class."""

    parameters = {
        'addr':  Param('Bus address of the card', type=int, mandatory=True),
        'first': Param('First bit to read', type=intrange(0, 15),
                       mandatory=True),
        'last':  Param('Last bit to read', type=intrange(0, 15),
                       mandatory=True),
    }

    parameter_overrides = {
        'unit':  Override(mandatory=False, default=''),
        'fmtstr': Override(default='%d'),
    }

    attached_devices = {
        'bus': (IPCModBus, 'The communication bus'),
    }

    def doInit(self, mode):
        self._mask = ((1 << (self.last - self.first + 1)) - 1) << self.first

    def doRead(self, maxage=0):
        high = self._adevs['bus'].get(self.addr, 181) << 8
        low  = self._adevs['bus'].get(self.addr, 180)
        return ((high + low) & self._mask) >> self.first

    def doStatus(self, maxage=0):
        return status.OK, ''

class IPCSwitches(Input):
    """ IPC motor card read out for the limit switches and reference switch """

    parameter_overrides = {
         'first' : Override(mandatory=False, default=5, settable=False),
         'last' : Override(mandatory=False, default=7, settable=False),
    }

    def doInit(self, mode):
        Input.doInit(self, mode)        # init _mask
        if mode != SIMULATION:
            self._adevs['bus'].ping(self.addr)

    def doStatus(self, maxage=0):
        try:
            _ = self._adevs['bus'].get(self.addr, 134)
            return status.OK, ''
        except NicosError:
            return status.ERROR, 'Hardware not found'

    def doRead(self, maxage=0):
        """ returns 0 if no switch is set
                    1 if the lower limit switch is set
                    2 if the upper limit switch is set
                    4 if the reference switch is set
        """
        try:
#           temp & 32 'low limit switch'
#           temp & 64 'high limit switch'
#           temp & 128 'ref switch'
            temp = self._adevs['bus'].get(self.addr, 134)
            return (temp & self._mask) >> self.first
        except Exception:
            raise NicosError(self, 'cannot evaluate status byte of stepper')

class Output(Input, Moveable):
    """
    IPC I/O card digital output class.

    Shares parameters and doInit with `Input`.
    """

    valuetype = int

    def doVersion(self):
        version = self._adevs['bus'].get(self.addr, 194)
        return [('IPC digital output card', str(version))]

    def doRead(self, maxage=0):
        ioval = self._adevs['bus'].get(self.addr, 191)
        return (ioval & self._mask) >> self.first

    def doStatus(self, maxage=0):
        st = self._adevs['bus'].get(self.addr, 195)
        if st == 1:
            return status.ERROR, 'power stage overheat'
        return status.OK, ''

    def doIsAllowed(self, pos):
        maxval = self._mask >> self.first
        if not 0 <= pos <= maxval:
            return False, 'outside range [0, %d] of digital output' % maxval
        return True, ''

    def doStart(self, pos):
        curval = self._adevs['bus'].get(self.addr, 191)
        newval = (pos << self.first) | (curval & ~self._mask)
        self._adevs['bus'].send(self.addr, 190, newval, 3)


class SlitMotor(HasTimeout, NicosMotor):
    """Class for one axis of a IPC 4-wing slit.

    Use this together with `nicos.devices.generic.Axis` to create a single slit axis,
    and combine four of them using `nicos.devices.generic.Slit` to create a 4-wing slit
    device.
    """

    parameters = {
        'addr':       Param('Bus address of the slit', type=int, mandatory=True),
        'side':       Param('Side of axis', type=int, mandatory=True),
        'unit':       Param('Axis unit', type=str, default='mm'),
        'zerosteps':  Param('Motor steps for physical zero', type=int,
                            unit='steps', settable=True),
        'slope':      Param('Motor slope', type=float, settable=True,
                            unit='steps/mm', default=1.0),
        'resetpos':   Param('Value to move to for reset', type=float,
                            unit='main', mandatory=True),
    }

    parameter_overrides = {
        'speed':      Override(settable=False),
        'timeout':    Override(mandatory=False, default=40),
    }

    attached_devices = {
        'bus': (IPCModBus, 'The communication bus'),
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            self._adevs['bus'].ping(self.addr)

    def doVersion(self):
        return [('IPC slit axis', str(self._adevs['bus'].get(self.addr, 165)))]

    def _tosteps(self, value):
        return int(float(value) * self.slope + self.zerosteps)

    def _fromsteps(self, value):
        return float((value - self.zerosteps) / self.slope)

    def doRead(self, maxage=0):
        steps = self._adevs['bus'].get(self.addr, self.side + 166)
        if steps == 9999:
            raise NicosError(self, 'could not read, please reset')
        return self._fromsteps(steps)

    def doStart(self, target):
        target = self._tosteps(target)
        self._adevs['bus'].send(self.addr, self.side+160, target, 4)

    def doReset(self):
        if self._adevs['bus'].get(self.addr, self.side + 166) != 9999 and \
           self.doStatus()[0] != status.ERROR:
            return
        self.log.info('blade is blocked or not initialized, moving to reset '
                      'position %s' % self.format(self.resetpos, unit=True))
        steps = self._tosteps(self.resetpos)
        self._adevs['bus'].send(self.addr, self.side+160, steps, 4)
        sleep(0.3)
        self.wait()

    def doStop(self):
        pass

    def doSetPosition(self, pos):
        pass

    def doStatus(self, maxage=0):
        temp = self._adevs['bus'].get(self.addr, 164)
        temp = (temp >> (2*self.side)) & 3
        if temp == 1:
            return status.OK, 'idle'
        elif temp == 0:
            return status.BUSY, 'moving'
        else:
            return status.ERROR, 'blocked'
