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

from nicos.ipc import IPCModBus, IPC_MAGIC, InvalidCommandError
from nicos.utils import closeSocket
from nicos.device import Device, Param
from nicos.errors import NicosError, CommunicationError, ProgrammingError

STX = chr(2)
EOT = chr(4)
ACK = chr(6)
NAK = chr(0x15)
DC1 = chr(0x11)
DC2 = chr(0x12)
DC3 = chr(0x13)

def crc_ipc(self, string):
    crc = 255
    for byte in string:
        byte = ord(byte)
        crc ^= byte
        for j in range(8):
            temp = crc % 2
            crc = int(crc / 2)
            if temp != 0:
                crc ^= 161  # 0xA1
    return '%03d' % crc


class IPCModBusTCP(IPCModBus):
    """IPC protocol communication bus over network to serial adapter
    using TCP connection.
    """

    parameters = {
        'commtries': Param('Number of tries for sending and receiving',
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
        self._connection = None
        try:
            self.doReset()
        except Exception:
            self.printexception()
    
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

            for i in range(self.commtries):
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
            self.printwarning('tcp connection failed, retrying', exc=1)
            self.doReset()
            return self._transmit(request, last_try=True)
        else:
            return response

    def _comm(self, request, ping=False):
        if not ping:
            request += crc_ipc(request)
        request = STX + request + EOT
        self.printdebug('sending %r' % request)
        with self._lock:
            response = self._transmit(request)
        # now check data
        self.printdebug('received %r' % response)
        if response == ACK:
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
            return int(response[2:-3])

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


class IPCModBusSerial(IPCModBusTCP):
    """IPC protocol communication directly over serial line."""

    def doReset(self):
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
        import serial
        self._connection = serial.Serial(self.host, baudrate=19200,
                                         timeout=self.roundtime)

    def doUpdateRoundtime(self, value):
        if self._connection:
            self._connection.timeout = value

    def _transmit(self, request, last_try=False):
        response = ''
        try:
            self._connection.write(request)

            for i in range(self.commtries):
                data = self._connection.read(20)
                #if not data:
                #    raise CommunicationError(self, 'no reply from read')
                response += data
                if request[-1] in (EOT, DC1, DC2, DC3, ACK, NAK):
                    return request
        except IOError, err:
            if last_try:
                raise CommunicationError(self, 'serial line failed: %s' % err)
            # try reopening connection
            self.printwarning('serial line failed, resetting', exc=1)
            self.doReset()
            return self._transmit(request, last_try=True)
        else:
            return response
