#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

import os
import socket
import hashlib
from time import time as currenttime

import numpy as np

from nicos.protocols.daemon.classic import ENQ, ACK, NAK, STX, LENGTH, \
    READ_BUFSIZE, command2code, code2event
from nicos.protocols.daemon import DAEMON_EVENTS, ProtocolError, \
    ClientTransport as BaseClientTransport
from nicos.utils import closeSocket, tcpSocket
from nicos.pycompat import to_utf8


class ClientTransport(BaseClientTransport):

    def __init__(self, serializer):
        self.serializer = serializer

        self.sock = None
        self.event_sock = None

        unique_id = to_utf8(str(currenttime()) + str(os.getpid()))
        # spurious warning due to hashlib magic # pylint: disable=E1121
        self.client_id = hashlib.md5(unique_id).digest()

    def connect(self, conndata):
        self.sock = tcpSocket(conndata.host, conndata.port, timeout=30.0)
        # write client identification: we are a new client
        self.sock.sendall(self.client_id)

    def connect_events(self, conndata):
        # connect to event port
        try:
            self.event_sock = tcpSocket(conndata.host, conndata.port)
        except socket.error as err:
            msg = err.args[1]
            self.signal('failed', 'Event connection failed: %s.' % msg, err)
            return

        # write client id to ensure we get registered as event connection
        self.event_sock.sendall(self.client_id)

    def disconnect(self):
        closeSocket(self.sock)
        closeSocket(self.event_sock)
        self.sock = None

    def send_command(self, cmdname, args):
        data = self.serializer.serialize_cmd(cmdname, args)
        self.sock.sendall(ENQ + command2code[cmdname] +
                          LENGTH.pack(len(data)) + data)

    def recv_reply(self):
        # receive first byte + (possibly) length
        start = b''
        while len(start) < 5:
            data = self.sock.recv(5 - len(start))
            if not data:
                raise ProtocolError('connection broken')
            start += data
            if start == ACK:
                return True, None
        if start[0:1] not in (NAK, STX):
            raise ProtocolError('invalid response %r' % start)
        # it has a length...
        length, = LENGTH.unpack(start[1:])
        buf = b''
        while len(buf) < length:
            read = self.sock.recv(READ_BUFSIZE)
            if not read:
                raise ProtocolError('connection broken')
            buf += read
        # XXX: handle errors
        return self.serializer.deserialize_reply(buf, start[0:1] == STX)

    def recv_event(self):
        # receive STX (1 byte) + eventcode (2) + length (4)
        start = b''
        while len(start) < 7:
            data = self.event_sock.recv(7 - len(start))
            if not data:
                raise ProtocolError('read: event connection broken')
            start += data
        if start[0:1] != STX:
            raise ProtocolError('wrong event header')
        length, = LENGTH.unpack(start[3:])
        got = 0
        # read into a pre-allocated buffer to avoid copying lots of data
        # around several times
        buf = np.zeros(length, 'c')  # Py3: replace with bytearray+memoryview
        while got < length:
            read = self.event_sock.recv_into(buf[got:], length - got)
            if not read:
                raise ProtocolError('read: event connection broken')
            got += read
        # XXX: error handling
        event = code2event[start[1:3]]
        # serialized or raw event data?
        if DAEMON_EVENTS[event][0]:
            data = self.serializer.deserialize_event(buf.tostring(), event)
        else:
            data = event, buffer(buf)
        return data
