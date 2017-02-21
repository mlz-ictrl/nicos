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

"""Implementation of the daemon protocol over ZMQ."""

from __future__ import print_function

import threading

import zmq

from nicos.services.daemon.handler import ConnectionHandler
from nicos.protocols.daemon import CloseConnection, ProtocolError, \
    DAEMON_EVENTS, Server as BaseServer, ServerTransport as BaseServerTransport
from nicos.utils import createThread
from nicos.utils.messaging import nicos_zmq_ctx
from nicos.pycompat import queue, from_utf8, to_utf8


# Framing for commands:
#
# [id, '', verb, object, data]
#
# Id and empty frame come from the ROUTER socket.
#
# The verb is the protocol command or event.
# The object is empty for now.
# The data is serialized payload.
#
# Framing for events:
#
# [id, verb, data]
#
# The id is the client id for subscription purposes, or 'ALL' (XXX).
# The verb is the event name.
# The data is (maybe) serialized payload.


class Server(BaseServer):

    def __init__(self, daemon, address, serializer):
        BaseServer.__init__(self, daemon, address, serializer)
        self.sock = nicos_zmq_ctx.socket(zmq.ROUTER)
        self.sock.bind('tcp://%s:%s' % (address[0], address[1]))
        self.event_queue = queue.Queue()
        self.event_sock = nicos_zmq_ctx.socket(zmq.PUB)
        self.event_sock.bind('tcp://%s:%s' % (address[0], address[1] + 1))
        self.handlers = {}
        self.handler_ident = 0
        self.handler_lock = threading.Lock()
        self._stoprequest = False

    def start(self, interval):
        createThread('daemon event sender', self.event_sender)
        # TODO:
        # * clean up unused handlers (when?)
        # * more zmq inproc sockets and proxies instead of queues?
        # * useful and comprehensive error handling
        reply_collect = nicos_zmq_ctx.socket(zmq.PULL)
        reply_collect.bind('inproc://daemon_reply')

        poller = zmq.Poller()
        poller.register(self.sock, zmq.POLLIN)
        poller.register(reply_collect, zmq.POLLIN)

        # ZeroMQ expects a poll timeout given in msec. interval is passed through in seconds.
        interval_ms = interval * 1000

        while not self._stoprequest:
            for (sock, _) in poller.poll(interval_ms):
                # reply? pass it through
                if sock is reply_collect:
                    self.sock.send_multipart(reply_collect.recv_multipart())
                    continue
                # otherwise, must be message from a client
                msg = self.sock.recv_multipart()
                client_id = msg[0]
                if client_id in self.handlers:
                    self.handlers[client_id].command_queue.put(msg)
                elif msg[2] == b'getbanner':
                    # new connection, create a handler
                    self.handler_ident += 1
                    handler = ServerTransport(client_id, self)
                    with self.handler_lock:
                        self.handlers[client_id] = handler
                    createThread('handler %d' % self.handler_ident,
                                 handler.handle_loop)
                else:
                    # all other messages: client must initiate connection first
                    self.sock.send_multipart([client_id, b'', b'error', b'',
                                              b'"session expired"'])

    def clear_handler(self, client_id):
        with self.handler_lock:
            self.handlers.pop(client_id, None)

    def emit(self, event, data, handler=None):
        if DAEMON_EVENTS[event][0]:
            data = self.serializer.serialize_event(event, data)
        self.event_queue.put([handler.client_id if handler else b'ALL',
                              to_utf8(event), data])

    def stop(self):
        self._stoprequest = True

    def close(self):
        self.sock.close()
        self.event_sock.close()

    def event_sender(self):
        while not self._stoprequest:
            try:
                item = self.event_queue.get()
                self.event_sock.send_multipart(item)
            except zmq.ZMQError as err:
                if not self._stoprequest:
                    self.daemon.log.warning('error sending event: %s', err)
                    # XXX should we sleep here for a bit?


class ServerTransport(ConnectionHandler, BaseServerTransport):

    def __init__(self, client_id, server):
        self.client_id = client_id
        self.ident = server.handler_ident  # only for logging purposes
        self.unregister = server.clear_handler
        self.command_queue = queue.Queue()
        self.reply_sender = nicos_zmq_ctx.socket(zmq.PUSH)
        self.reply_sender.connect('inproc://daemon_reply')
        self.serializer = server.serializer
        self.clientnames = []
        ConnectionHandler.__init__(self, server.daemon)

    # XXX should be standard interface
    def handle_loop(self):
        try:
            self.handle()
        except CloseConnection:
            self.log.info('connection closed')
        except ProtocolError as err:
            self.log.error('error: %s', err)
        except BaseException:
            self.log.exception('unexpected error in handler')
        self.unregister(self.client_id)

    def get_version(self):
        # XXX: for now, make it the same as the classic proto
        return 15

    def recv_command(self):
        try:
            # "close connection" (clean up data associated with this client)
            # after a long stretch of inactivity
            item = self.command_queue.get(timeout=3600.)
        except queue.Empty:
            raise CloseConnection
        return self.serializer.deserialize_cmd(item[4], from_utf8(item[2]))

    def send_ok_reply(self, payload):
        self.reply_sender.send_multipart(
            [self.client_id, b'', b'ok', b'',
             self.serializer.serialize_ok_reply(payload)])

    def send_error_reply(self, reason):
        self.reply_sender.send_multipart(
            [self.client_id, b'', b'error', b'', to_utf8(reason)])

    # events are sent directly by the Server
