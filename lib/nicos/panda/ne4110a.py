#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
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
# *****************************************************************************

from __future__ import with_statement

"""Moxa NE 4110a RS-485 interface for IPC stepper/coder/IO cards."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"


import socket
import select
from threading import RLock

import serial

from nicos.ipc import IPCModBus, InvalidCommandError
from nicos.device import Device, Param
from nicos.errors import NicosError, CommunicationError, ProgrammingError

STX = chr(2)
EOT = chr(4)
ACK = chr(6)
NAK = chr(0x15)
DC1 = chr(0x11)
DC2 = chr(0x12)
DC3 = chr(0x13)

IPC_MAGIC = {
    # motor cards
    31:  ['Do Reset Motorcard', None], 
    32:  ['Do Motor Start', None],
    33:  ['Do Motor Stop Immediately', None],
    34:  ['Switch Forward Direction', None],
    35:  ['Switch Backward Direction', None],
    36:  ['Switch Fullstep', None],
    37:  ['Switch Halfstep', None],
    38:  ['Switch Relay On', None],
    39:  ['Switch Relay Off', None],
    40:  ['Save Values to EEPROM', None],
    41:  ['Set Speed', (3, 0, 255)],                # numdigits, minvalue, maxvalue
    42:  ['Set Acceleration', (3, 0, 255)],
    43:  ['Set Current Position', (6, 0, 999999)],
    44:  ['Set Maximum Position', (6, 0, 999999)],
    45:  ['Set Minimum Position', (6, 0, 999999)],
    46:  ['Set Multisteps', (6, 0, 999999)],
    47:  ['Do find Reference Switch', (3, 0, 255)], # ... with given speed and switch back
    48:  ['Check motor connection', None],
    49:  ['Save config byte to EEPROM', (3, 0, 63)],
    50:  ['Select ramp shape', (3, 1, 4)],
    51:  ['Save user value to EEPROM', (6, 0, 999999)],
    52:  ['Stop motor using ramp', None],
    53:  ['Switch driver off', None],
    54:  ['Switch driver on', None],
    55:  ['Set inhibit delay', (3, 0, 255)],
    56:  ['Set target position', (6, 0, 999999)],
    57:  ['Set microsteps', (3, 0, 4)],
    58:  ['Set stop delay', (3, 0, 255)],
    60:  ['Set clock divider', (3, 1, 7)],
    128: ['Read speed', None],
    129: ['Read accel', None],
    130: ['Read position', None],
    131: ['Read maximum', None],
    132: ['Read minimum', None],
    133: ['Read multisteps', None],
    134: ['Read status', None],
    135: ['Read config byte', None],
    136: ['Read ramp shape', None],
    137: ['Read version number', None],
    138: ['Read user value', None],
    139: ['Read inhibit delay', None],
    140: ['Read target position', None],
    141: ['Read microsteps', None],
    142: ['Read load indicator', None],	
    143: ['Read stop delay', None],
    144: ['Read clock divider', None],
    # encoder/potentiometer
    150: ['Read encoder value', None],
    151: ['Read encoder version', None],
    152: ['Read encoder configuration', None],
    153: ['Reset encoder', None],
    154: ['Set encoder configuration', (3, 0, 255)],
    155: ['Select endat memory range', (3, 161, 185)],
    156: ['Read endat parameter', (3, 0, 15)],
    157: ['Write endat parameter', (3, 0, 15)],
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


class ne4110_bus(IPCModBus):
    """IPC protocol communication bus over network to serial adapter using tcp-connection."""

    parameters = {
        'commtries':  Param('Number of tries for sending and receiving',
                           type=int, default=5, settable=True),
        'roundtime': Param('Maximum time to wait for an answer, set '
                           'this high to slow down everything',
                           type=float, default=0.01, settable=True),
        'host':      Param('Hostname (or IP) of network2serial converter',
                           type=str, settable=True, mandatory=True),
        'port':      Param('TCP Port on network2serial converter',
                           type=int, default=4001),
    }

    def doInit(self):
        self._lock = RLock()
        self._mysock = None
        try:
            self.doReset()
        except Exception:
            self.printexception()
    
    def doReset(self):
        if self._mysock:
            try:
                self._mysock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self._mysock.close()
            except Exception:
                pass
        self._mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._mysock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._mysock.connect((self.host, self.port))

    def _crc_ipc( self, String ):
        crc = 255
        if String:
            if String[0] == STX and String[-1] == EOT:
                String = String[1:-1]  # if present, kill STX and EOT for calculating CRC
            for i in range(len(String)):
                byte = ord(String[i])
                crc ^= byte
                for j in range(8):
                    temp = crc % 2
                    crc = int(crc / 2)
                    if temp != 0:
                        crc ^= 161  # 0xA1
        return '%03d' % crc

    # TODO: check status of tcp-connection before trying to communicate and reopen if neccessary
    def _comm(self, orig_request, ping=False, last_try=False):
        request = orig_request
        if not ping:
            request += self._crc_ipc(request)
        request = STX + request + EOT
        self.printdebug('sending %r' % request)
        with self._lock:
            try:
                while request:
                    request = request[self._mysock.send(request):]

                for i in range(self.commtries):
                    p = select.select([self._mysock], [], [self._mysock], self.roundtime)
                    if self._mysock in p[0]:
                        n = self._mysock.recv(20)  # more than enough!
                        if not n:
                            raise CommunicationError(self, 'no reply from recv')
                        request += n
                        if request.endswith(EOT):
                            break
                        if request in (DC1, DC2, DC3, ACK, NAK):
                            break
            except (socket.error, select.error), err:
                if last_try:
                    raise CommunicationError(self, 'tcp connection failed: %s' % err)
                # try reopening connection
                self.printwarning('tcp connection failed, resetting', exc=1)
                self.doReset()
                return self._comm(orig_request, ping, True)
        # now check data
        self.printdebug('received %r' % request)
        if not request: 
            raise CommunicationError(self, 'no answer')
        if request == ACK:
            return 0
        elif request == NAK: 
            if ping:
                return 1
            raise CommunicationError(self, 'CRC error')
        elif request == DC1:
            raise InvalidCommandError(self, 'invalid command number')
        elif request == DC2:
            raise ProgrammingError(self, 'invalid command parameter')
        elif request == DC3:
            raise CommunicationError(self, 'command failed, e.g. hardware error')
        elif len(request) < 3:
            raise CommunicationError(self, 'response too short')
        elif request[0] != STX:
            raise CommunicationError(self, 'response should start with STX')
        elif request[-1] != EOT:
            raise CommunicationError(self, 'response should end with EOT')
        else:  # good response!
            request = request[1:-1]  # remove STX/EOT
            if len(request) > 2:  # try to check CRC
                if request[-3:] != self._crc_ipc(request[:-3]):
                    raise CommunicationError(self, 'wrong CRC on response')
            return int(request[2:-3])

    def ping(self, addr):
        if 32 <= addr <= 255:
            if self._comm(chr(addr), ping=True):
                return addr
            else: 
                return -1
        else:
            return -1

    def send(self, addr, cmd, param=0, len=0):
        try:
            cmdname, limits = IPC_MAGIC[cmd]
        except KeyError:
            raise ProgrammingError(self, 'Command %s not supported' % cmd)
        if limits:
            if len != limits[0] or not limits[1] <= param <= limits[2]:
                raise ProgrammingError(self, 'Parameter %s outside allowed '
                    'values %s for cmd %s' % (param, limits, cmdname))
        elif len or param:
            raise ProgrammingError(self, 'Sending parameters is not allowed '
                                    'for cmd %s' % cmdname)
        s = chr(addr) + chr(cmd)
        if len > 0:
            s += '%0*d' % (len, param)
        self.printdebug('sending %s to card %s' % (cmdname, addr))
        return self._comm(s)

    def get(self, addr, cmd, param=0, len=0):
        return self.send(addr, cmd, param, len)


class serial_bus(ne4110_bus):
    def doReset(self):
        if self._mysock:
            try:
                self._mysock.close()
            except Exception:
                pass
        self._mysock = serial.Serial(self.host, baudrate=19200, timeout=self.roundtime)

    def _comm(self, orig_request, ping=False, last_try=False):
        request = orig_request
        if not ping:
            request += self._crc_ipc(request)
        request = STX + request + EOT
        self.printdebug('sending %r' % request)
        with self._lock:
            try:
                self._mysock.write(request)
                request = ''

                for i in range(self.commtries):
                    n = self._mysock.read(20)
                    #if not n:
                     #   raise CommunicationError(self, 'no reply from read')
                    request += n
                    if request.endswith(EOT):
                        break
                    if request in (DC1, DC2, DC3, ACK, NAK):
                        break
            except IOError, err:
                if last_try:
                    raise CommunicationError(self, 'tcp connection failed: %s' % err)
                # try reopening connection
                self.printwarning('tcp connection failed, resetting', exc=1)
                self.doReset()
                return self._comm(orig_request, ping, True)
        # now check data
        self.printdebug('received %r' % request)
        if not request: 
            raise CommunicationError(self, 'no answer')
        if request == ACK:
            return 0
        elif request == NAK: 
            if ping:
                return 1
            raise CommunicationError(self, 'CRC error')
        elif request == DC1:
            raise InvalidCommandError(self, 'invalid command number')
        elif request == DC2:
            raise ProgrammingError(self, 'invalid command parameter')
        elif request == DC3:
            raise CommunicationError(self, 'command failed, e.g. hardware error')
        elif len(request) < 3:
            raise CommunicationError(self, 'response too short')
        elif request[0] != STX:
            raise CommunicationError(self, 'response should start with STX')
        elif request[-1] != EOT:
            raise CommunicationError(self, 'response should end with EOT')
        else:  # good response!
            request = request[1:-1]  # remove STX/EOT
            if len(request) > 2:  # try to check CRC
                if request[-3:] != self._crc_ipc(request[:-3]):
                    raise CommunicationError(self, 'wrong CRC on response')
            return int(request[2:-3])
