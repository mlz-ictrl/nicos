#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

__version__ = ""

import socket
import select
from time import sleep
from threading import RLock

from RS485Client import RS485Client

from nicos import status
from nicos.taco import TacoDevice
from nicos.utils import intrange, floatrange, oneofdict, oneof, closeSocket, \
     lazy_property, runAsync, usermethod
from nicos.device import Device, Readable, Moveable, Param, Override
from nicos.errors import NicosError, CommunicationError, ProgrammingError, \
    UsageError, TimeoutError
from nicos.abstract import Motor as NicosMotor, Coder as NicosCoder


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
    """Abstract class for IPC protocol communication over RS-485."""


class IPCModBusTaco(TacoDevice, IPCModBus):
    """IPC protocol communication over TACO RS-485 server."""

    taco_class = RS485Client
    taco_errorcodes = {
        537133063: InvalidCommandError,
    }

    parameters = {
        'maxtries': Param('Number of tries for sending and receiving',
                          type=int, default=3, settable=True),
    }

    def send(self, addr, cmd, param=0, length=0):
        self.log.debug('IPCModBusTaco:send: (%d, %d, %d, %d)'
                       % (addr, cmd, param, length))
        #~ return self._taco_multitry('send', self.maxtries, self._dev.genSDA,
                                   #~ addr, cmd-31, length, param)
        return self._taco_multitry('send', self.maxtries, self._dev.SDARaw,
                                   addr, cmd, length, param)

    def get(self, addr, cmd, param=0, length=0):
        self.log.debug('IPCModBusTaco:get: (%d, %d, %d, %d)'
                       % (addr, cmd, param, length))
        #~ res = self._taco_multitry('get', self.maxtries, self._dev.genSRD,
                                  #~ addr, cmd-98, length, param)
        res = self._taco_multitry('get', self.maxtries, self._dev.SRDRaw,
                                  addr, cmd, length, param)
        self.log.debug('IPCModBusTaco:get: result is %d' % res)
        return res

    def ping(self, addr):
        self.log.debug('IPCModBusTaco:ping:%d' % addr)
        return self._taco_multitry('ping', self.maxtries, self._dev.Ping, addr)


class IPCModBusTacoless(IPCModBus):
    """Base class for IPC connections not using the RS485 TACO server."""

    parameters = {
        'commtries': Param('Number of tries for sending and receiving',
                           type=int, default=5, settable=True),
        'roundtime': Param('Maximum time to wait for an answer, set '
                           'this high to slow down everything',
                           type=float, default=0.1, settable=True),
    }

    def doInit(self):
        self._lock = RLock()
        self._connection = None
        try:
            self.doReset()
        except Exception:
            self.log.exception()

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
            except ValueError, err:
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


class IPCModBusTCP(IPCModBusTacoless):
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

            for i in range(self.commtries):
                self.log.debug('waiting for response, try %d/%d' %
                               (i, self.commtries))
                p = select.select([self._connection], [], [self._connection],
                                  self.roundtime)
                if self._connection in p[0]:
                    data = self._connection.recv(20)  # more than enough!
                    if not data:
                        raise CommunicationError(self, 'no reply from recv')
                    response += data
                    if response[-1] in (EOT, DC1, DC2, DC3, ACK, NAK):
                        return response
        except (socket.error, select.error), err:
            if last_try:
                raise CommunicationError(
                    self, 'tcp connection failed: %s' % err)
            # try reopening connection
            self.log.warning('tcp connection failed, retrying', exc=1)
            self.doReset()
            return self._transmit(request, last_try=True)
        else:
            return response


class IPCModBusSerial(IPCModBusTacoless):
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
                                         timeout=self.roundtime)

    def doUpdateRoundtime(self, value):
        if self._connection:
            self._connection.timeout = value

    def _transmit(self, request, last_try=False):
        response = ''
        try:
            self._connection.write(request)

            for _ in range(self.commtries):
                data = self._connection.read(20)
                response += data
                if response and response[-1] in (EOT, DC1, DC2, DC3, ACK, NAK):
                    return response
        except IOError, err:
            if last_try:
                raise CommunicationError(self, 'serial line failed: %s' % err)
            # try reopening connection
            self.log.warning('serial line failed, resetting', exc=1)
            self.doReset()
            return self._transmit(request, last_try=True)
        else:
            return response


class Coder(NicosCoder):

    parameters = {
        'addr': Param('Bus address of the coder', type=int, mandatory=True),
        'confbyte': Param('Configuration byte of the coder', type=intrange(0, 256),
                    settable=True),
        'offset': Param('Coder offset', type=float, settable=True),
        'slope': Param('Coder slope', type=float, settable=True, default=1.0),
        'firmware': Param('Firmware version', type=int),
    }

    attached_devices = {
        'bus': IPCModBus,
    }

    def doInit(self):
        bus = self._adevs['bus']
        bus.ping(self.addr)
        self._lasterror = None

    def doVersion(self):
        version = self._adevs['bus'].get(self.addr, 151)
        return [('IPC encoder card', str(version))]

    def doReadFirmware(self):
        return self._adevs['bus'].get(self.addr, 151)

    def doReadConfbyte(self):
        return self._adevs['bus'].get(self.addr, 152)

    def doWriteConfbyte(self, byte):
        self._adevs['bus'].send(self.addr, 154, byte, 3)

    def doUpdateConfbyte(self, byte):
        self._type = self._getcodertype(byte)
        self._resolution = byte & 31

    def _getcodertype(self, byte):
        """Extract coder type from configuration byte."""
        if byte == 44:
            return 'potentiometer'
        proto = byte & 128 and 'endat' or 'ssi'
        coding = byte & 64 and 'gray' or 'binary'
        parity = byte & 32 and 'nopar' or 'evenpar'
        return '%s-%s-%s-%dbit' % (proto, coding, parity, byte & 31)

    def doReset(self):
        self._adevs['bus'].send(self.addr, 153)
        sleep(0.5)

    def _fromsteps(self, value):
        return float((value - self.offset) / self.slope)

    def doRead(self):
        bus = self._adevs['bus']
        try:
            try:
                value = bus.get(self.addr, 150)
            except NicosError:
                self._endatclearalarm()
                sleep(1)
                # try again
                value = bus.get(self.addr, 150)
        except NicosError, e:
            # record last error to return it from doStatus()
            self._lasterror = str(e)
            raise
        self.log.debug('value is %d' % value)
        return self._fromsteps(value)

    def doStatus(self):
        if self._lasterror:
            return status.ERROR, self._lasterror
        return status.OK, 'idle'

    def doSetPosition(self, target):
        raise NicosError('setPosition not implemented for IPC coders')

    def _endatclearalarm(self):
        """Clear alarm for a binary-endat encoder."""
        if not self._type.startswith('endat'):
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


class Motor(NicosMotor):

    parameters = {
        'addr':       Param('Bus address of the motor', type=int, mandatory=True),
        'timeout':    Param('Waiting timeout', type=int, unit='s', default=360),
        'unit':       Param('Motor unit', type=str, default='steps'),
        'offset':     Param('Motor offset', type=float, settable=True),
        'slope':      Param('Motor slope', type=float, settable=True,
                            default=1.0),
        # those parameters come from the card
        'firmware':   Param('Firmware version', type=int),
        'steps':      Param('Last position in steps', settable=True,
                            type=intrange(0, 1000000)),
        'speed':      Param('Motor speed (0..255)', settable=True,
                            type=intrange(0, 256)),
        'accel':      Param('Motor acceleration (0..255)', settable=True,
                            type=intrange(0, 256)),
        'confbyte':   Param('Configuration byte', type=intrange(0, 256),
                            settable=True),
        'ramptype':   Param('Ramp type', settable=True, type=intrange(1, 5)),
        'microstep':  Param('Microstepping mode', unit='steps', settable=True,
                            type=oneof(int, 1, 2, 4, 8, 16)),
        'min':        Param('Lower motorlimit', settable=True,
                            type=intrange(0, 1000000), unit='steps'),
        'max':        Param('Upper motorlimit', settable=True,
                            type=intrange(0, 1000000), unit='steps'),
        'startdelay': Param('Start delay', type=floatrange(0, 25), unit='s',
                            settable=True),
        'stopdelay':  Param('Stop delay', type=floatrange(0, 25), unit='s',
                            settable=True),
        'divider':    Param('Speed divider', settable=True,
                            type=intrange(0, 8)),
        # volatile parameters to read/switch card features
        'inhibit':    Param('Inhibit input', default='off', volatile=True,
                            type=oneofdict({0: 'off', 1: 'on'})),
        'relay':      Param('Relay switch', type=oneofdict({0: 'off', 1: 'on'}),
                            settable=True, default='off', volatile=True),
        'power':      Param('Internal power stage switch', default='on',
                            type=oneofdict({0: 'off', 1: 'on'}), settable=True,
                            volatile=True),
    }

    attached_devices = {
        'bus': IPCModBus,
    }

    def doInit(self):
        bus = self._adevs['bus']
        bus.ping(self.addr)
        # make sure that the card has the right "last steps"
        if self.steps != self.doReadSteps():
            self.doWriteSteps(self.steps)
            self.log.warning('Resetting stepper position to last known good '
                             'value %d' % self.steps)

    def doVersion(self):
        try:
            version = self._adevs['bus'].get(self.addr, 137)
        except InvalidCommandError:
            return []
        else:
            return [('IPC motor card', str(version))]

    def _tosteps(self, value):
        return int(float(value) * self.slope + self.offset)

    def _fromsteps(self, value):
        return float((value - self.offset) / self.slope)

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
            raise UsageError(self, 'ramp type not supported by card')
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadDivider(self):
        try:
            return self._adevs['bus'].get(self.addr, 144)
        except InvalidCommandError:
            return -1

    def doWriteDivider(self, value):
        try:
            self._adevs['bus'].send(self.addr, 60, value, 3)
        except InvalidCommandError:
            raise UsageError(self, 'divider not supported by card')
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
                raise UsageError(self, 'microsteps > 2 not supported by card')
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
            raise UsageError(self, 'confbyte not supported by card')
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
            raise UsageError(self, 'startdelay not supported by card')
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
            raise UsageError(self, 'stopdelay not supported by card')
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
        self.log.debug('target is %d' % target)
        bus = self._adevs['bus']
        self.doWait()
        pos = self._tosteps(self.doRead())
        self.log.debug('pos is %d' % pos)
        diff = target - pos
        if diff == 0:
            return
        elif diff < 0:
            bus.send(self.addr, 35)
        else:
            bus.send(self.addr, 34)
        # XXX handle limit switch touch (???)
        bus.send(self.addr, 46, abs(diff), 6)

    def doReset(self):
        def rewind():
            bus = self._adevs['bus']
            # remember current state
            actpos  = bus.get(self.addr, 130)
            speed   = bus.get(self.addr, 128)
            accel   = bus.get(self.addr, 129)
            minstep = bus.get(self.addr, 132)
            maxstep = bus.get(self.addr, 131)
            bus.send(self.addr, 31)  # reset card
            sleep(0.2)
            # update state
            bus.send(self.addr, 41, speed, 3)
            bus.send(self.addr, 42, accel, 3)
            bus.send(self.addr, 45, minstep, 6)
            bus.send(self.addr, 44, maxstep, 6)
            bus.send(self.addr, 43, actpos, 6)
        @runAsync
        def stopandrewind():
            bus = self._adevs['bus']
            bus.send(self.addr, 33)  # stop
            try:
                self.doWait()        # this might take a while, ignore errors
            except:
                pass
            rewind()
        if self.doStatus()[0] != status.OK:  # busy or error
            stopandrewind()
        else:
            rewind()

    def doWait(self):
        timeleft = self.timeout
        sleep(0.1)
        while timeleft >= 0:
            sleep(0.2)
            timeleft -= 0.2
            if self.poll()[0][0] != status.BUSY:
                #~ self.doRead()
                #~ sleep(1.0)   # triple crds have status idle before they
                                # are really stopped. reading position directly
                                # after becoming idle yields not the final value
                #~ self.doRead()
                break
        else:
            raise TimeoutError(self, 'movement timed out (timeout %.1f s)'
                               % self.timeout)

    def doStop(self):
        if self._hwtype == 'single':
            self._adevs['bus'].send(self.addr, 52)
        else:
            self._adevs['bus'].send(self.addr, 33)
        sleep(0.2)

    def doRead(self):
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

    def doStatus(self):
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

        # if it's moving, it's not in error state!
        if state & 1:
            st = status.BUSY
            msg = ', moving' + msg
        self.log.debug('status is %d:%s' % (st, msg[2:]))
        return st, msg[2:]

    def doSetPosition(self, target):
        self.log.debug('setPosition: %s' % target)
        steps = self._adevs['bus'].get(self.addr, 130)
        self.offset = steps - target * self.slope

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
    """Makes the relay of an IPC stepper available as switch."""

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    attached_devices = {
        'stepper': Motor,
    }

    def doStart(self, target):
        self._adevs['stepper'].relay = target

    def doRead(self):
        return self._adevs['stepper'].relay

    def doStatus(self):
        return status.OK, 'relay is ' + str(self.doRead())


class IPCInhibit(Readable):
    """Makes the inhibit of an IPC stepper available as an input.

    Returns 'on' if inhibit is active, 'off' otherwise.
    """

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    attached_devices = {
        'stepper': Motor,
    }

    def doRead(self):
        return 'on' if self._adevs['stepper'].inhibit else 'off'

    def doStatus(self):
        return status.OK, 'inhibit is ' + str(self.doRead())


class Input(Readable):
    """IPC I/O card digital input class."""

    parameters = {
        'addr':  Param('Bus address of the card', type=int, mandatory=True),
        'first': Param('First bit to read', type=intrange(0, 16),
                       mandatory=True),
        'last':  Param('Last bit to read', type=intrange(0, 16),
                       mandatory=True),
    }

    attached_devices = {
        'bus': IPCModBus,
    }

    def doInit(self):
        self._mask = ((1 << (self.last - self.first + 1)) - 1) << self.first

    def doRead(self):
        high = self._adevs['bus'].get(self.addr, 181)
        low  = self._adevs['bus'].get(self.addr, 180)
        return ((high + low) & self._mask) >> self.first

    def doStatus(self):
        return status.OK, 'idle'


class Output(Input, Moveable):
    """
    IPC I/O card digital output class.

    Shares parameters and doInit with Input.
    """

    def doVersion(self):
        version = self._adevs['bus'].get(self.addr, 194)
        return [('IPC digital output card', str(version))]

    def doRead(self):
        ioval = self._adevs['bus'].get(self.addr, 191)
        return (ioval & self._mask) >> self.first

    def doStatus(self):
        st = self._adevs['bus'].get(self.addr, 195)
        if st == 1:
            return status.ERROR, 'power stage overheat'
        return status.OK, 'idle'

    def doIsAllowed(self, pos):
        maxval = self._mask >> self.first
        if not 0 <= pos <= maxval:
            return False, 'outside range [0, %d] of digital output' % maxval
        return True, ''

    def doStart(self, pos):
        curval = self._adevs['bus'].get(self.addr, 191)
        newval = (pos << self.first) | (curval & ~self._mask)
        self._adevs['bus'].send(self.addr, 190, newval, 3)
