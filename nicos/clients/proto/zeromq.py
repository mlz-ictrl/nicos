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
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

import zmq

from nicos.protocols.daemon import DAEMON_EVENTS, \
    ClientTransport as BaseClientTransport, ProtocolError
from nicos.pycompat import from_utf8, to_utf8


class ClientTransport(BaseClientTransport):

    def __init__(self, serializer):
        self.serializer = serializer

        self.sock = None
        self.event_sock = None

    def connect(self, conndata):
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.REQ)
        self.sock.connect('tcp://%s:%s' % (conndata.host, conndata.port))
        self.sock.send_multipart([b'getbanner', b'', b''])

    def connect_events(self, conndata):
        self.event_sock = self.context.socket(zmq.SUB)
        self.event_sock.connect('tcp://%s:%s' % (conndata.host,
                                                 conndata.port + 1))
        self.event_sock.setsockopt(zmq.SUBSCRIBE, b'ALL')

    def disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        if self.event_sock:
            self.event_sock.close()
        self.context.destroy()

    def send_command(self, cmdname, args):
        data = self.serializer.serialize_cmd(cmdname, args)
        self.sock.send_multipart([to_utf8(cmdname), '', data])

    def get_reply(self):
        item = self.sock.recv_multipart()
        if len(item) < 3:
            raise ProtocolError('invalid frames received')
        return self.serializer.deserialize_reply(item[2], item[0] == b'ok')

    def get_event(self):
        item = self.event_sock.recv_multipart()
        if len(item) < 3:
            raise ProtocolError('invalid frames received')
        event = from_utf8(item[1])
        # serialized or raw event data?
        if DAEMON_EVENTS[event][0]:
            return self.serializer.deserialize_event(item[2], item[1])
        else:
            return item[2]
