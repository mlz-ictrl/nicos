#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

"""Implementation of the "classic" daemon protocol: pickling, plain sockets."""

import queue
import socket
import socketserver
import threading
import time
import weakref

from nicos.protocols.daemon import CloseConnection, ProtocolError, \
    Server as BaseServer, ServerTransport as BaseServerTransport
from nicos.protocols.daemon.classic import ACK, ENQ, LENGTH, NAK, \
    PROTO_VERSION, READ_BUFSIZE, STX, code2command, event2code
from nicos.services.daemon.handler import ConnectionHandler
from nicos.utils import closeSocket, createThread


class Server(BaseServer, socketserver.TCPServer):
    request_queue_size = 20
    allow_reuse_address = True

    def __init__(self, daemon, address, serializer):
        BaseServer.__init__(self, daemon, address, serializer)
        self.handler_ident_lock = threading.Lock()
        self.handlers = weakref.WeakValueDictionary()
        self.handler_ident = 0
        self.pending_clients = {}
        socketserver.TCPServer.__init__(self, address, ServerTransport)

    # BaseServer methods

    def start(self, interval):
        self.serve_forever(interval)

    def stop(self):
        self.shutdown()

    def close(self):
        self.server_close()

    def emit(self, event, data, blobs, handler=None):
        data = self.serializer.serialize_event(event, data)
        for hdlr in (handler,) if handler else self.handlers.values():
            try:
                hdlr.event_queue.put((event, data, blobs), True, 0.1)
            except queue.Full:
                # close event socket to let the connection get
                # closed by the handler
                self.daemon.log.warning('handler %s: queue full, '
                                        'closing socket', hdlr.ident)
                closeSocket(hdlr.event_sock)
                closeSocket(hdlr.sock)

    # TCPServer methods

    def _handle_request_noblock(self):
        # overwritten to support passing client_id to process_request
        try:
            request, client_address = self.get_request()
        except OSError:
            return
        client_id = self.verify_request(request, client_address)
        if client_id is not None:
            try:
                self.process_request(request, client_address, client_id)
            except Exception:
                self.handle_error(request, client_address)
                self.close_request(request)

    def process_request(self, request, client_address, client_id):
        """Process a "request", that is, a client connection."""
        # mostly copied from ThreadingMixIn but without the import,
        # which causes threading issues because of the import lock
        createThread('request handler', self.process_request_thread,
                     args=(request, client_address, client_id))

    def process_request_thread(self, request, client_address, client_id):
        """Thread to process the client connection, calls the Handler."""
        try:
            # this call instantiates the RequestHandler class
            self.finish_request(request, client_address, client_id)
            self.close_request(request)
        except Exception:
            self.handle_error(request, client_address)
            self.close_request(request)

    def finish_request(self, request, client_address, client_id):
        self.RequestHandlerClass(request, client_address, client_id, self)

    def verify_request(self, request, client_address):
        """Called on a new connection.  If we have a connection from that
        host that lacks an event connection, use this.
        """
        host = client_address[0]
        clid = request.recv(16)
        if (host, clid) not in self.pending_clients:
            self.pending_clients[host, clid] = None
            return clid
        # this should be an event connection: start event sender thread on the
        # handler, but wait until the handler is registered
        while self.pending_clients[host, clid] is None:
            time.sleep(0.2)
        handler = self.pending_clients[host, clid]
        self.daemon.log.debug('event connection from %s for handler #%d',
                              host, handler.ident)
        handler.event_sock = request
        # close connection after socket send queue is full for 60 seconds
        handler.event_sock.settimeout(60.0)
        createThread('event_sender %d' % handler.ident, handler.event_sender)
        self.pending_clients.pop((host, clid), None)
        # don't call the usual handler
        return None

    def server_close(self):
        """Close the server socket and all client sockets."""
        for handler in list(self.handlers.values()):
            closeSocket(handler.sock)
            closeSocket(handler.event_sock)
        closeSocket(self.socket)

    def handle_error(self, request, client_address):
        """Last chance exception handling."""
        self.daemon.log.exception('exception while handling request')

    # Own methods

    def register_handler(self, handler, host, client_id):
        """Give each handler a unique ID."""
        with self.handler_ident_lock:
            self.pending_clients[host, client_id] = handler
            self.handler_ident += 1
            handler.setIdent(self.handler_ident)
            self.handlers[threading.get_ident()] = handler

    def unregister_handler(self, ident):
        """Remove a handler from the handlers dictionary."""
        with self.handler_ident_lock:
            del self.handlers[threading.get_ident()]


class ServerTransport(ConnectionHandler, BaseServerTransport,
                      socketserver.BaseRequestHandler):
    """This class is the SocketServer "request handler" implementation for the
    socket server.  One instance of this class is created for every control
    connection (not event connections) from a client.  When the event
    connection is opened, the `event_sender` method of the existing instance is
    spawned as a new thread.

    Note that the SocketServer interface is such that the request handling is
    done while the constructor runs, i.e. the `__init__` method calls `handle`.
    """

    def __init__(self, request, client_address, client_id, server):
        self.serializer = server.serializer
        self.event_sock = None  # set later by server
        self.sock = request
        ip = client_address[0]
        # register self as a new handler
        ConnectionHandler.__init__(self, server.daemon)
        server.register_handler(self, ip, client_id)
        try:
            host, aliases, addrlist = socket.gethostbyaddr(ip)
        except socket.herror:
            self.clientnames = [ip]
        else:
            self.clientnames = [host] + aliases + addrlist
        self.log.info('handle start')
        try:
            # this calls self.handle()
            socketserver.BaseRequestHandler.__init__(
                self, request, client_address, server)
        except BaseException as err:
            # in case the client hasn't opened the event connection, stop
            # waiting for it
            server.pending_clients.pop((client_address[0], client_id), None)
            if isinstance(err, ProtocolError):
                self.log.warning('protocol error: %s', err)
            elif not isinstance(err, CloseConnection):
                self.log.exception('unexpected handler error')
        self.close()
        server.unregister_handler(self.ident)
        self.log.info('handler unregistered')

    def close(self):
        self.log.info('closing connection')
        ConnectionHandler.close(self)
        closeSocket(self.sock)
        closeSocket(self.event_sock)

    def get_version(self):
        return PROTO_VERSION

    def recv_command(self):
        # receive: ENQ (1 byte) + commandcode (2) + length (4)
        try:
            start = b''
            while len(start) < 7:
                data = self.sock.recv(7 - len(start))
                if not data:
                    raise ProtocolError('recv_command: connection broken')
                start += data
            if start[0:1] != ENQ:
                raise ProtocolError('recv_command: invalid command header')
            # it has a length...
            length, = LENGTH.unpack(start[3:])
            buf = b''
            while len(buf) < length:
                read = self.sock.recv(min(READ_BUFSIZE, length-len(buf)))
                if not read:
                    raise ProtocolError('recv_command: connection broken')
                buf += read
            try:
                return self.serializer.deserialize_cmd(
                    buf, code2command[start[1:3]])
            except Exception as err:
                self.send_error_reply('invalid command or garbled data')
                raise ProtocolError('recv_command: invalid command or '
                                    'garbled data') from err
        except OSError as err:
            raise ProtocolError('recv_command: connection broken (%s)' %
                                err) from err

    def send_ok_reply(self, payload):
        try:
            if payload is None:
                self.sock.sendall(ACK)
            else:
                try:
                    data = self.serializer.serialize_ok_reply(payload)
                except Exception:
                    raise ProtocolError(
                        'send_ok_reply: could not serialize') from None
                self.sock.sendall(STX + LENGTH.pack(len(data)) + data)
        except OSError as err:
            raise ProtocolError('send_ok_reply: connection broken (%s)' %
                                err) from err

    def send_error_reply(self, reason):
        try:
            data = self.serializer.serialize_error_reply(reason)
        except Exception:
            raise ProtocolError(
                'send_error_reply: could not serialize') from None
        try:
            self.sock.sendall(NAK + LENGTH.pack(len(data)) + data)
        except OSError as err:
            raise ProtocolError('send_error_reply: connection broken (%s)' %
                                err) from err

    def send_event(self, evtname, payload, blobs):
        self.event_sock.sendall(STX +
                                event2code[evtname] +
                                (b'%c' % len(blobs)) +
                                LENGTH.pack(len(payload)))
        # send data separately to avoid copying lots of data
        self.event_sock.sendall(payload)
        for blob in blobs:
            self.event_sock.sendall(LENGTH.pack(len(blob)))
            self.event_sock.sendall(blob)
