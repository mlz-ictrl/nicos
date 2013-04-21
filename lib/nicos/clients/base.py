#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""The base class for communication with the NICOS server."""

from __future__ import with_statement

__version__ = "$Revision$"

import os
import ast
import time
import socket
import hashlib
import threading

import numpy as np

from nicos.protocols.daemon import serialize, unserialize, ACK, STX, NAK, \
     LENGTH, RS, PROTO_VERSION, DAEMON_EVENTS

BUFSIZE = 8192
TIMEOUT = 30.0


class ProtocolError(Exception):
    pass

class ErrorResponse(Exception):
    pass


class NicosClient(object):
    def __init__(self):
        self.host = ''
        self.port = 0

        self.socket = None
        self.event_socket = None
        self.lock = threading.Lock()
        self.connected = False
        self.disconnecting = False
        self.version = None
        self.gzip = False
        self.client_id = hashlib.md5('%s%s' % (time.time(),
                                               os.getpid())).digest()

    def signal(self, name, *args):
        # must be overwritten
        raise NotImplementedError

    def connect(self, conndata, password=None, eventmask=None):
        if self.connected:
            raise RuntimeError('client already connected')
        self.disconnecting = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)
        try:
            self.socket.connect((conndata['host'], conndata['port']))
        except socket.error, err:
            msg = err.args[1]
            self.signal('failed', 'Server connection failed: %s.' % msg, err)
            return
        except Exception, err:
            self.signal('failed', 'Server connection failed: %s.' % err, err)
            return

        # write client identification: we are a new client
        self.socket.sendall(self.client_id)

        # read banner
        try:
            ret, data = self._read()
            if ret != STX:
                raise ProtocolError('invalid response format')
            banner = unserialize(data)
            if 'daemon_version' not in banner:
                raise ProtocolError('daemon version missing from response')
            daemon_proto = banner.get('protocol_version', 0)
            if daemon_proto != PROTO_VERSION:
                raise ProtocolError('daemon uses protocol %d, but we expect %d'
                                    % (daemon_proto, PROTO_VERSION))
        except Exception, err:
            self.signal('failed', 'Server (%s:%d) handshake failed: %s.'
                         % (conndata['host'], conndata['port'], err))
            return

        # log-in sequence
        if password is None:
            password = conndata['passwd']
        pw_hashing = banner.get('pw_hashing', 'sha1')
        if pw_hashing == 'sha1':
            password = hashlib.sha1(password).hexdigest()
        elif pw_hashing == 'md5':
            password = hashlib.md5(password).hexdigest()
        if not self.tell(conndata['login'], password, conndata['display']):
            return

        if eventmask:
            self.tell('eventmask', serialize(eventmask))

        # connect to event port
        self.event_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.event_socket.connect((conndata['host'], conndata['port']))
        except socket.error, err:
            msg = err.args[1]
            self.signal('failed', 'Event connection failed: %s.' % msg, err)
            return

        # write client id to ensure we get registered as event connection
        self.event_socket.sendall(self.client_id)

        # start event handler
        self.event_thread = threading.Thread(target=self.event_handler,
                                             name='event handler thread')
        self.event_thread.setDaemon(True)
        self.event_thread.start()

        self.connected = True
        self.host, self.port = conndata['host'], conndata['port']
        self.login = conndata['login']

        self.version = 'NICOS daemon version %s' % banner['daemon_version']
        self.signal('connected')

    def event_handler(self):
        recv = self.event_socket.recv
        recvinto = self.event_socket.recv_into
        while 1:
            try:
                # receive length
                start = recv(5)
                if len(start) != 5 or start[0] != STX:
                    if not self.disconnecting:
                        self.signal('broken', 'Server connection broken.')
                        self._close()
                    return
                length, = LENGTH.unpack(start[1:])
                got = 0
                # buf = ''
                # while got < length:
                #     read = recv(length - got)
                #     if not read:
                #         print 'Error in event handler: connection broken'
                #         return
                #     buf += read
                #     got += len(read)
                # try:
                #     event, data = buf.split(RS, 1)
                #     if DAEMON_EVENTS[event]:
                #         data = unserialize(data)

                # read into a pre-allocated buffer to avoid copying lots of data
                # around several times
                buf = np.zeros(length, 'c')
                while got < length:
                    read = recvinto(buf[got:], length - got)
                    if not read:
                        if not self.disconnecting:
                            self.signal('broken', 'Server connection broken.')
                            self._close()
                        return
                    got += read
                try:
                    start = buf[:15].tostring()
                    sep = start.find(RS)
                    if sep == -1:
                        raise ValueError
                    event = start[:sep]
                    # serialized or raw event data?
                    if DAEMON_EVENTS[event]:
                        data = unserialize(buf[sep+1:].tostring())
                    else:
                        data = buffer(buf, sep+1)
                except Exception, err:
                    print 'Garbled event (%s): %r' % \
                          (err, str(buffer(buf))[:100])
                else:
                    self.signal(event, data)
            except Exception, err:
                print 'Error in event handler:', err
                return

    def disconnect(self):
        self.disconnecting = True
        self.tell('quit')
        self._close()

    def _close(self):
        try:
            self.socket._sock.close()
            self.socket.close()
        except Exception:
            pass
        self.socket = None
        self.version = None
        self.gzip = False
        if self.connected:
            self.connected = False
            self.signal('disconnected')

    def handle_error(self, err):
        if isinstance(err, ErrorResponse):
            self.signal('error', 'Error from daemon: ' + err.args[0] + '.')
        else:
            if isinstance(err, ProtocolError):
                msg = 'Communication error: %s.' % err.args[0]
            elif isinstance(err, socket.timeout):
                msg = 'Connection to server timed out.'
            elif isinstance(err, socket.error):
                msg = 'Server connection broken: %s.' % err.args[1]
            # we cannot handle this without breaking connection, since
            # it generally means that the response is not yet received;
            # and to carry on means that we receive the pending response
            # "in reply" to one of the next commands
            elif isinstance(err, KeyboardInterrupt):
                msg = 'Server communication interrupted by user.'
            else:
                msg = 'Exception occurred: %s.' % err
            self.signal('broken', msg, err)
            self._close()

    def _write(self, strings):
        """Write a command to the server."""
        string = RS.join(strings)
        self.socket.sendall(STX + LENGTH.pack(len(string)) + string)

    def _read(self):
        """Receive a response from the server."""
        # receive first byte + (possibly) length
        start = self.socket.recv(5)
        if start == ACK:
            return start, ''
        if len(start) != 5:
            raise ProtocolError('connection broken')
        if start[0] not in (NAK, STX):
            raise ProtocolError('invalid response %r' % start)
        # it has a length...
        length, = LENGTH.unpack(start[1:])
        buf = ''
        while len(buf) < length:
            read = self.socket.recv(BUFSIZE)
            if not read:
                raise ProtocolError('connection broken')
            buf += read
        return start[0], buf

    def tell(self, *command):
        if not self.socket:
            self.signal('error', 'You are not connected to a server.')
            return
        try:
            with self.lock:
                self._write(command)
                ret, data = self._read()
                if ret != ACK:
                    raise ErrorResponse(data)
                return True
        except (Exception, KeyboardInterrupt), err:
            return self.handle_error(err)

    def ask(self, *command, **kwds):
        if not self.socket:
            if not kwds.get('quiet', False):
                self.signal('error', 'You are not connected to a server.')
            return
        try:
            with self.lock:
                self._write(command)
                ret, data = self._read()
                if ret != STX:
                    raise ErrorResponse(data)
                return unserialize(data)
        except (Exception, KeyboardInterrupt), err:
            return self.handle_error(err)

    def eval(self, expr, default=None):
        result = self.ask('eval', expr, quiet=True)
        if result is None:
            return default
        if result.startswith('<cannot be evaluated:'):
            if default is not None:
                return default
            return result
        try:
            return ast.literal_eval(result)
        except (Exception, KeyboardInterrupt), err:
            print '!!! error evaluating eval() result %r:' % result, err
            return default

    def read(self):
        if not self.socket:
            self.signal('error', 'You are not connected to a server.')
            return
        try:
            with self.lock:
                ret, data = self._read()
                if ret != STX:
                    raise ErrorResponse(data)
                return unserialize(data)
        except (Exception, KeyboardInterrupt), err:
            return self.handle_error(err)
