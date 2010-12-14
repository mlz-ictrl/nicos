#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Toni-protocol device classes
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Toni-protocol device classes."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import serial
import threading
from time import sleep, time

from nicm.utils import intrange
from nicm.device import Device, Switchable, Param
from nicm.errors import CommunicationError


class ModBus(Device):

    # XXX this should be rewritten as a TACO device using the RS-232 server

    parameters = {
        'port':     Param('Serial port device file', type=str, mandatory=True),
        'baudrate': Param('Baud rate', type=int, default=19200),
        'bytesize': Param('Byte size', type=int, default=8),
        'parity':   Param('Parity', type=int, default=0),
        'stopbits': Param('Stop bits', type=int, default=1),
        'timeout':  Param('Timeout', type=int, default=1, unit='s'),
        'xonxoff':  Param('XON/XOFF flow control', type=bool, default=False),
        'rtscts':   Param('RTS/CTS flow control', type=bool, default=False),
        'maxtries': Param('Maximum tries before raising', type=int, default=5),
    }

    def doInit(self):
        self._dev = serial.Serial(self.port, self.baudrate, self.bytesize,
                                  self.parity, self.stopbits, self.timeout,
                                  self.xonxoff, self.rtscts)
        self._dev.setRTS(0)
        self._lock = threading.RLock()
        self._buffer = []
        self._source = 0  # XXX should this be configurable?

    def _crc(self, str):
        crc = ord(str[0])
        for i in str[1:]:
            crc ^= ord(i)
        return crc

    def read(self, dest):
        self._lock.acquire()
        try:
            ret = self._r(dest)
        finally:
            self._lock.release()
        return ret[5:-3]

    def write(self, msg, dest):
        self._lock.acquire()
        try:
            ret = self._w(msg, dest)
        finally:
            self._lock.release()
        return ret[5:-3]

    def _r(self, dest, echo=0):
        tries = self.maxtries
        errnum = ''
        if echo:
            source = dest
            dest = self._source
        else:
            source = self._source
            for msg in self._buffer:
                if int(msg[3:5], 16) == dest:
                    # got a message for the correct destination
                    del self._buffer[self._buffer.index(msg)]
                    return msg
        input = ''
        inp = 'x'
        while tries:
            inp1 = ''
            # wait for start of message (0x2)
            while inp and inp != chr(2):
                inp = self._dev.read()
                inp1 = inp
            if not inp:
                tries -= 1
                input = ''
                errnum += '1'
                continue
            input += inp1
            inp = 'x'
            # read until end of message (0x3)
            while inp and inp != chr(3) and inp != chr(2):
                inp = self._dev.read()
                input += inp
            # did not receive end of message
            if not inp:
                tries -= 1
                errnum += '2'
                continue
            # did receive start of new message before end of message
            elif inp == chr(2):
                tries -= 1
                errnum += '3'
                continue
            # check for message length: should be at least 8 characters
            if len(input) < 8:
                tries -= 1
                inp = 'x'
                input = ''
                errnum += '4'
            # okay, we got something that looks like a valid message, check CRC
            checksum = self._crc(input[:-3])
            if checksum.upper() != input[-3:-1].upper():
                tries -= 1
                inp = 'x'
                input = ''
                errnum += '5'
                continue
            # check for valid source
            if int(input[1:3], 16) != source:
                inp = 'x'
                input = ''
                continue
            # check if we are the destination
            if int(input[3:5], 16) == dest:
                return input
            else:
                self._buffer.append(input)
                inp = 'x'
                input = ''
                continue
        self._dev.setRTS(0)
        # XXX error here?
        return ''

    def _w(self, msg, dest):
        self._dev.setRTS(0)
        tries = self.maxtries
        msg = '\x02%02x%02x%s' % (dest, self._source, msg)
        checksum = self._crc(msg)
        msg += checksum + '\x03'
        while True:
            self._dev.setRTS(1)
            sleep(0.001)
            self._dev.write('\x03' + msg)
            while True:
                echo = self._r(dest, echo=True)
                self._dev.setRTS(0)
                if echo == msg:
                    return self._r(dest)
                elif self._dev.inWaiting() < 8:
                    tries -= 1
                    if tries == 0:
                        raise CommunicationError(self, 'Modbus write error')
                    break


class Valve(Switchable):

    attached_devices = {
        'bus': ModBus,
    }

    parameters = {
        'addr':    Param('Bus address of the valve control', type=int,
                         mandatory=True),
        'channel': Param('Channel of the valve', type=intrange(0, 8),
                         mandatory=True),
        'states':  Param('Names for the closed/open states', type=listof(str),
                         default=['off', 'on']),
    }

    def doInit(self):
        if len(self.states) != 2:
            raise ConfigurationError(self, 'Valve states must be a list of '
                                     'two strings for closed/open state')
        off, on = self.states
        self.__dict__['switchlist'] = {off: 0, on: 1}
        self._timer = 0

    def doStart(self, value):
        self.doWait()
        self._timer = time()
        msg = '%s=%02x' % (value and 'O' or 'C', 1 << self.channel)
        ret = self._adevs['bus'].write(msg, self.addr)
        if ret != 'OK':
            raise CommunicationError(self, 'ModBus read error: %r' % ret)

    def doRead(self):
        self.doWait()
        ret = self._adevs['bus'].write('R?', self.addr)
        if not ret:
            raise CommunicationError(self, 'ModBus read error: %r' % ret)
        return bool(int(ret, 16) & (1 << self.channel))

    def doStatus(self):
        self.doWait()
        ret = self._adevs['bus'].write('I?', self.addr)
        if not ret:
            raise CommunicationError(self, 'ModBus read error: %r' % ret)
        # XXX what return values?
        return int(ret), ''

    def doWait(self):
        if self._timer:
            # wait 5 seconds after last write action
            while time() - self._timer < 5:
                sleep(0.1)
            self._timer = 0
