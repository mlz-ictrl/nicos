#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from nicos.core import SIMULATION, CommunicationError, Device, \
    HasCommunication, Override, Param, ProgrammingError
from nicos.utils import HardwareStub, closeSocket

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
    # second element: None or a tuple (numdigits, minvalue, maxvalue)
    # third element: number of bytes in response
    31:  ['Reset motor card', None, 1],                    # ### ######
    32:  ['Start motor', None, 1],                         # ### ######
    33:  ['Stop motor immediately', None, 1],              # ### ######
    34:  ['Switch forward direction', None, 1],            # ### ######
    35:  ['Switch backward direction', None, 1],           # ### ######
    36:  ['Switch fullstep', None, 1],                     #
    37:  ['Switch halfstep', None, 1],                     #
    38:  ['Switch relay on', None, 1],                     #
    39:  ['Switch relay off', None, 1],                    #
    40:  ['Write values to EEPROM', None, 1],              # ### ######
    41:  ['Set speed', (3, 0, 255), 1],                    # ### ######
    42:  ['Set acceleration', (3, 0, 255), 1],             # ### ######
    43:  ['Set current position', (6, 0, 999999), 1],      # ### ######
    44:  ['Set maximum position', (6, 0, 999999), 1],      # ### ######
    45:  ['Set minimum position', (6, 0, 999999), 1],      # ### ######
    46:  ['Set multisteps and start', (6, 0, 999999), 1],  # ### ######
    # ... with given speed and switch back
    47:  ['Find reference switch', (3, 0, 255), 1],        #
    48:  ['Check motor connection', None, 1],              #
    49:  ['Save config byte to EEPROM', (3, 0, 255), 1],   #
    50:  ['Select ramp shape', (3, 1, 4), 1],              #
    51:  ['Save user value to EEPROM', (6, 0, 999999), 1], # ### ######
    52:  ['Stop motor using ramp', None, 1],               #
    53:  ['Switch driver off', None, 1],                   # ### ######
    54:  ['Switch driver on', None, 1],                    # ### ######
    55:  ['Set inhibit delay', (3, 0, 255), 1],            #
    56:  ['Set target position', (6, 0, 999999), 1],         ### ######
    57:  ['Set microsteps', (3, 0, 4), 1],                   ### ######
    58:  ['Set stop delay', (3, 0, 255), 1],               #
    60:  ['Set clock divider', (3, 1, 7), 1],                ###
    128: ['Read speed', None, 10],                         # ### ######
    129: ['Read accel', None, 10],                         # ### ######
    130: ['Read position', None, 13],                      # ### ######
    131: ['Read maximum', None, 13],                       # ### ######
    132: ['Read minimum', None, 13],                       # ### ######
    133: ['Read multisteps', None, 13],                    #
    134: ['Read status', None, 13],                        # ### ######
    135: ['Read config byte', None, 10],                   #
    136: ['Read ramp shape', None, 10],                    #
    137: ['Read version number', None, 10],                # ### ######
    138: ['Read user value', None, 13],                    # ### ######
    139: ['Read inhibit delay', None, 10],                 #
    140: ['Read target position', None, 13],                 ### ######
    141: ['Read microsteps', None, 10],                      ### ######
    142: ['Read load indicator', None, 10],                  ### ######
    143: ['Read stop delay', None, 10],                    #
    144: ['Read clock divider', None, 10],                   ###
    # encoder/potentiometer (abs enc=#, inc enc=##, poti=###)
    150: ['Read encoder value', None, 15],                 # ## ###
    151: ['Read encoder version', None, 10],               # ## ###
    152: ['Read encoder configuration', None, 10],         # ## ###
    153: ['Reset encoder', None, 1],                       # ## ###
    154: ['Set encoder configuration', (3, 0, 255), 1],    # ##
    155: ['Select endat memory range', (3, 161, 185), 1],  #
    # 156 is used DIFFERENTLY for resolvers and endat-coders !!!
    # 156: ['Read statusbyte', None, 10],                  #
    # 156: ['Read endat parameter', (3, 0, 15), 15],       #
    157: ['Write endat parameter', (3, 0, 15), 1],         #
    # 4-wing slits
    160: ['Set bottom target position', (4, 0, 4095), 1],
    161: ['Set top target position', (4, 0, 4095), 1],
    162: ['Set right target position', (4, 0, 4095), 1],
    163: ['Set left target position', (4, 0, 4095), 1],
    164: ['Read status', None, 10],
    165: ['Read version number', None, 10],
    166: ['Read bottom target position', None, 11],
    167: ['Read top target position', None, 11],
    168: ['Read right target position', None, 11],
    169: ['Read left target position', None, 11],
    170: ['Write user value to EEPROM', (4, 0, 9999), 1],
    171: ['Read user value', None, 11],
    # digital input
    180: ['Read digital bits 0-7', None, 10],
    181: ['Read digital bits 8-15', None, 10],
    182: ['Save user value to EEPROM', (6, 0, 999999), 1],
    183: ['Read user value', None, 13],
    184: ['Read digital input version number', None, 10],
    185: ['Read digital bits 0-15', None, 13],
    # digital output
    190: ['Set digital output bits', (3, 0, 255), 1],
    191: ['Read digital output bits', None, 10],
    192: ['Save user value to EEPROM', (6, 0, 999999), 1],
    193: ['Read user value', None, 13],
    194: ['Read digital output version number', None, 10],
    195: ['Read status', None, 10],
}


def crc_ipc(string):
    crc = 255
    for byte in string:
        byte = ord(byte)
        crc ^= byte
        for _ in range(8):
            temp = crc % 2
            crc = crc // 2
            if temp != 0:
                crc ^= 0xA1
    return '%03d' % crc


class InvalidCommandError(ProgrammingError):
    """Error raised for "invalid command" response of IPC cards."""


class IPCModBus(Device):
    """Abstract class for IPC protocol communication over RS-485.

    A device of this type is needed as the ``.bus`` parameter of the other IPC
    devices.

    Concrete implementations are `IPCModBusTaco`, `IPCModBusTCP`,
    `IPCModBusSerial`.
    """


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
        'comtries': Override(default=5),
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

    def _comm(self, request, retlen, ping=False):
        if not ping:
            request += crc_ipc(request)
        request = STX + request + EOT
        self.log.debug('sending %r', convert(request))
        with self._lock:
            response = self._transmit(request, retlen)
        # now check data
        self.log.debug('received %r', convert(response))
        if not response:
            raise CommunicationError(self, 'no response')
        elif response == ACK:
            return 0
        elif response == NAK:
            if ping:
                return 1
            raise CommunicationError(self, 'CRC error: %r' % convert(request))
        elif response == DC1:
            raise InvalidCommandError(self, 'invalid command number: %r' %
                                      convert(request))
        elif response == DC2:
            raise ProgrammingError(self, 'invalid command parameter: %r' %
                                   convert(request))
        elif response == DC3:
            raise CommunicationError(self, 'command failed, e.g. limit '
                                     'switch reached or hardware error')
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
                    self, 'invalid response: missing value (%s)' % err
                ) from err

    def ping(self, addr):
        if 32 <= addr <= 255:
            if self._comm(chr(addr), 1, ping=True):
                return addr
            else:
                return -1
        else:
            return -1

    def send(self, addr, cmd, param=0, length=0):
        try:
            cmdname, limits, retlen = IPC_MAGIC[cmd]
        except KeyError as err:
            raise ProgrammingError(
                self, 'Command %s not supported' % cmd) from err
        if limits:
            if length != limits[0] or not limits[1] <= param <= limits[2]:
                raise ProgrammingError(
                    self, 'Parameter %s outside allowed values %s for cmd '
                    '%s' % (param, limits, cmdname))
        elif length or param:
            raise ProgrammingError(self, 'Sending parameters is not allowed '
                                   'for cmd %s' % cmdname)
        s = chr(addr) + chr(cmd)
        if length > 0:
            s += '%0*d' % (length, param)
        self.log.debug('sending %s to card %s', cmdname, addr)
        for i in range(self.comtries, 0, -1):
            try:
                return self._comm(s, retlen)
            except (CommunicationError, ProgrammingError):
                if i == 1:
                    raise

    def get(self, addr, cmd, param=0, length=0):
        return self.send(addr, cmd, param, length)


class IPCModBusTCP(IPCModBusRS232):
    """IPC protocol communication bus over network to serial adapter
    using TCP connection.
    """

    parameters = {
        'host': Param('Hostname (or IP) of network2serial converter',
                      type=str, settable=True, mandatory=True),
        'port': Param('TCP Port on network2serial converter',
                      type=int, default=4001),
    }

    def doReset(self):
        if self._connection:
            closeSocket(self._connection)
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._connection.connect((self.host, self.port))

    def doShutdown(self):
        if self._connection:
            closeSocket(self._connection)

    def _transmit(self, request, retlen, last_try=False):
        response = ''
        try:
            self._connection.sendall(request)
            self.log.debug('request sent')

            for i in range(self.comtries):
                self.log.debug('waiting for response, try %d/%d',
                               i, self.comtries)
                p = select.select([self._connection], [], [], self.bustimeout)
                if self._connection in p[0]:
                    data = self._connection.recv(20)  # more than enough!
                    if not data:
                        raise CommunicationError(self, 'no reply from recv')
                    response += data
                    if response[-1] in (EOT, DC1, DC2, DC3, ACK, NAK):
                        return response
        except OSError as err:
            if last_try:
                raise CommunicationError(
                    self, 'tcp connection failed: %s' % err) from err
            # try reopening connection
            self.log.warning('tcp connection failed, retrying', exc=1)
            self.doReset()
            return self._transmit(request, retlen, last_try=True)
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

    def _transmit(self, request, retlen, last_try=False):
        response = ''
        try:
            self._connection.write(request)

            for _ in range(self.comtries):
                data = self._connection.read(20)
                response += data
                if response and response[-1] in (EOT, DC1, DC2, DC3, ACK, NAK):
                    return response
        except OSError as err:
            if last_try:
                raise CommunicationError(
                    self, 'serial line failed: %s' % err) from err
            # try reopening connection
            self.log.warning('serial line failed, resetting', exc=1)
            self.doReset()
            return self._transmit(request, retlen, last_try=True)
        else:
            return response
