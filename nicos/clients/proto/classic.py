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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

import socket
import uuid

from nicos.protocols.daemon import DAEMON_EVENTS, \
    ClientTransport as BaseClientTransport, ProtocolError
from nicos.protocols.daemon.classic import ACK, ENQ, LENGTH, NAK, \
    READ_BUFSIZE, SERIALIZERS, STX, code2event, command2code
from nicos.utils import closeSocket, tcpSocket


class ClientTransport(BaseClientTransport):

    def __init__(self, serializer=None):
        self.serializer = serializer

        self.sock = None
        self.event_sock = None

        self.client_id = b''

    def connect(self, conndata):
        self.client_id = uuid.uuid1().bytes
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

        if not self.serializer:  # determine serializer class automatically
            for serializercls in SERIALIZERS.values():
                try:
                    candidate = serializercls()
                    candidate.deserialize_reply(buf, start[0:1] == STX)
                except Exception:
                    continue
                self.serializer = candidate
                break
            else:  # no serializer found
                raise ProtocolError('no serializer found for this connection')
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
        buf = bytearray(length)
        buf_view = memoryview(buf)
        while got < length:
            read = self.event_sock.recv_into(buf_view[got:], length - got)
            if not read:
                raise ProtocolError('read: event connection broken')
            got += read
        # XXX: error handling
        event = code2event[start[1:3]]
        # serialized or raw event data?
        if DAEMON_EVENTS[event][0]:
            data = self.serializer.deserialize_event(buf, event)
        else:
            data = event, buf_view
        return data
