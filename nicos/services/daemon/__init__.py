#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""NICOS daemon package."""

import sys
import time
import socket
import weakref
import traceback
import threading

from nicos import nicos_version
from nicos.core import listof, Device, Param, ConfigurationError, host, Attach
from nicos.utils import closeSocket, createThread
from nicos.pycompat import get_thread_id, queue, socketserver, listitems
from nicos.services.daemon.auth import Authenticator
from nicos.services.daemon.script import ExecutionController
from nicos.services.daemon.handler import ConnectionHandler
from nicos.protocols.daemon import serialize, DEFAULT_PORT, DAEMON_EVENTS


class Server(socketserver.TCPServer):
    def __init__(self, daemon, address, handler):
        self.daemon = daemon
        self.handler_ident_lock = threading.Lock()
        self.handlers = weakref.WeakValueDictionary()
        self.handler_ident = 0
        self.pending_clients = {}
        socketserver.TCPServer.__init__(self, address, handler)

    def _handle_request_noblock(self):
        # overwritten to support passing client_id to process_request
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        client_id = self.verify_request(request, client_address)
        if client_id is not None:
            try:
                self.process_request(request, client_address, client_id)
            except Exception:
                self.handle_error(request, client_address)
                self.close_request(request)

    # pylint: disable=W0221
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
        self.daemon.log.debug('event connection from %s for handler #%d' %
                              (host, handler.ident))
        handler.event_sock = request
        createThread('event_sender %d' % handler.ident, handler.event_sender,
                     args=(request,))
        self.pending_clients.pop((host, clid), None)
        # don't call the usual handler
        return None

    def server_close(self):
        """Close the server socket and all client sockets."""
        for handler in list(self.handlers.values()):
            closeSocket(handler.sock)
            closeSocket(handler.event_sock)
        closeSocket(self.socket)

    def register_handler(self, handler, host, client_id):
        """Give each handler a unique ID."""
        with self.handler_ident_lock:
            self.pending_clients[host, client_id] = handler
            self.handler_ident += 1
            handler.ident = self.handler_ident
            self.handlers[get_thread_id()] = handler

    def unregister_handler(self, ident):
        """Remove a handler from the handlers dictionary."""
        with self.handler_ident_lock:
            del self.handlers[get_thread_id()]

    def handle_error(self, request, client_address):
        """Last chance exception handling."""
        self.daemon.log.exception('exception while handling request')


class NicosDaemon(Device):
    """
    This class abstracts the main daemon process.
    """

    attached_devices = {
        'authenticators': Attach('The authenticator devices to use for '
                                 'validating users and passwords',
                                 Authenticator, multiple=True),
    }

    parameters = {
        'server':         Param('Address to bind to (host or host[:port])',
                                type=host, mandatory=True),
        'maxlogins':      Param('Maximum number of logins', type=int,
                                default=10),
        'reuseaddress':   Param('Whether to set SO_REUSEADDR', type=bool,
                                default=True),
        'updateinterval': Param('Update interval for watch expressions',
                                type=float, unit='s', default=0.2),
        'trustedhosts':   Param('Trusted hosts allowed to log in',
                                type=listof(str)),
        'simmode':        Param('Whether to always start in dry run mode',
                                type=bool),
    }

    def doInit(self, mode):
        self._stoprequest = False
        # the controller represents the internal script execution machinery
        self._controller = ExecutionController(self.log, self.emit_event,
                                               'startup', self.simmode)

        # check that all configured authenticators use the same hashing method
        self._pw_hashing = 'sha1'
        auths = self._attached_authenticators
        if auths:
            self._pw_hashing = auths[0].pw_hashing()
            for auth in auths[1:]:
                if self._pw_hashing != auth.pw_hashing():
                    raise ConfigurationError(
                        self, 'incompatible hash methods for authenticators: '
                        '%s requires %r, while %s requires %r' %
                        (auths[0], self._pw_hashing, auth, auth.pw_hashing()))

        # cache log messages emitted so far
        self._messages = []

        address = self.server
        if ':' not in address:
            host = address
            port = DEFAULT_PORT
        else:
            host, port = address.split(':')
            port = int(port)

        Server.request_queue_size = self.maxlogins * 2
        Server.allow_reuse_address = self.reuseaddress
        self._server = Server(self, (host, port), ConnectionHandler)

        self._watch_worker = createThread('daemon watch monitor', self._watch_entry)

    def _watch_entry(self):
        """
        This thread checks for watch value changes periodically and sends out
        events on changes.
        """
        # pre-fetch attributes for speed
        ctlr, intv, emit, sleep = self._controller, self.updateinterval, \
            self.emit_event, time.sleep
        lastwatch = {}
        while not self._stoprequest:
            sleep(intv)
            # new watch values?
            watch = ctlr.eval_watch_expressions()
            if watch != lastwatch:
                emit('watch', watch)
                lastwatch = watch

    def emit_event(self, event, data):
        """Emit an event to all handlers."""
        if DAEMON_EVENTS[event][0]:
            data = serialize(data)
        for handler in self._server.handlers.values():
            try:
                handler.event_queue.put((event, data), True, 0.05)
            except queue.Full:
                self.log.warning('handler %s: event queue full' % handler.ident)

    def emit_event_private(self, event, data):
        """Emit an event to only the calling handler."""
        if DAEMON_EVENTS[event][0]:
            data = serialize(data)
        handler = self._controller.get_current_handler()
        if handler:
            try:
                handler.event_queue.put((event, data), True, 0.05)
            except queue.Full:
                self.log.warning('handler %s: event queue full' % handler.ident)

    def clear_handlers(self):
        """Remove all handlers."""
        self._server.handlers.clear()

    def statusinfo(self):
        self.log.info('got SIGUSR2 - current stacktraces for each thread:')
        active = threading._active
        for tid, frame in listitems(sys._current_frames()):
            if tid in active:
                name = active[tid].getName()
            else:
                name = str(tid)
            self.log.info('%s: %s' %
                          (name, ''.join(traceback.format_stack(frame))))

    def start(self):
        """Start the daemon's server."""
        self.log.info('NICOS daemon v%s started, starting server on %s' %
                      (nicos_version, self.server))
        # startup the script thread
        self._controller.start_script_thread()
        self._worker = createThread('daemon server', self._server.serve_forever,
                                    kwargs={'poll_interval': self._long_loop_delay})

    def wait(self):
        while not self._stoprequest:
            time.sleep(self._long_loop_delay)
        self._worker.join()

    def quit(self, signum=None):
        self.log.info('quitting on signal %s...' % signum)
        self._stoprequest = True
        self._server.shutdown()
        self._worker.join()
        self._server.server_close()

    def current_script(self):
        return self._controller.current_script

    def get_authenticators(self):
        return self._attached_authenticators, self._pw_hashing
