#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
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

"""The base class for communication with the NICOS server."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import socket
import struct
import hashlib
import threading

import numpy as np

from nicos.daemon import NicosDaemon
from nicos.daemon.utils import unserialize

# re-exported for the rest of nicos.gui
from nicos.daemon.pyctl import STATUS_IDLEEXC, STATUS_IDLE, STATUS_RUNNING, \
     STATUS_INBREAK, STATUS_STOPPING


DEFAULT_PORT    = 1301

# Script status constants

# General constants
BUFSIZE = 8192
TIMEOUT = 30.0

# one-byte responses without length
ACK = '\x06'   # executed ok, no further information follows

# responses with length, encoded as a 32-bit integer
STX = '\x03'   # executed ok, reply follows
NAK = '\x15'   # error occurred, message follows
LENGTH = struct.Struct('>I')   # used to encode length

# argument separator in client commands
RS = '\x1e'


class ProtocolError(Exception):
    pass

class ErrorResponse(Exception):
    pass


class TrString(str):
    def arg(self, argument):
        return self.replace('%1', argument)


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

    def signal(self, type, *args):
        # must be overwritten
        raise NotImplementedError

    def tr(self, msgstr):
        return TrString(msgstr)

    def connect(self, conndata, password=None):
        if self.connected:
            raise RuntimeError('client already connected')
        self.disconnecting = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)
        try:
            self.socket.connect((conndata['host'], conndata['port']))
        except socket.error, err:
            errno, msg = err.args
            self.signal('failed',
                self.tr('Server control connection failed: %1.').arg(msg), err)
            return
        except Exception, err:
            self.signal('failed',
                self.tr('Server control connection failed: %1.').arg(str(err)), err)
            return

        # log-in sequence
        if password is None:
            password = conndata['passwd']
        pwhash = hashlib.sha1(password).hexdigest()
        if not self.tell(conndata['login'], pwhash, conndata['display']):
            return

        # connect to event port
        self.event_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.event_socket.connect((conndata['host'], conndata['port']))
        except socket.error, err:
            errno, msg = err.args
            self.signal('failed',
                self.tr('Server connection failed: %1.').arg(msg), err)
            return

        # start event handler
        self.event_thread = threading.Thread(target=self.event_handler,
                                             name='event handler thread')
        self.event_thread.start()

        self.connected = True
        self.host, self.port = conndata['host'], conndata['port']

        self.version = self.ask('getversion')
        self.signal('connected')

    def event_handler(self):
        recv = self.event_socket.recv
        recvinto = self.event_socket.recv_into
        while 1:
            try:
                # receive length
                length = recv(4)
                if len(length) != 4:
                    if not self.disconnecting:
                        self.signal('broken',
                                    self.tr('Server connection broken.'))
                        self._close()
                    return
                length, = LENGTH.unpack(length)
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
                #     if NicosDaemon.daemon_events[event]:
                #         data = unserialize(data)

                # read into a pre-allocated buffer to avoid copying lots of data
                # around several times
                buf = np.zeros(length, 'c')
                while got < length:
                    read = recvinto(buf[got:], length - got)
                    if not read:
                        if not self.disconnecting:
                            self.signal('broken',
                                        self.tr('Server connection broken.'))
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
                    if NicosDaemon.daemon_events[event]:
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
                msg = self.tr('Communication error: %1.').arg(err.args[0])
            elif isinstance(err, socket.timeout):
                msg = self.tr('Connection to server timed out.')
            elif isinstance(err, socket.error):
                msg = self.tr('Server connection broken: %1.').arg(err.args[1])
            else:
                msg = self.tr('Exception occurred: %1.').arg(str(err))
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
            raise ProtocolError(self.tr('connection broken'))
        if start[0] not in (NAK, STX):
            raise ProtocolError(self.tr('invalid response %1').arg(repr(start)))
        # it has a length...
        length, = LENGTH.unpack(start[1:])
        buf = ''
        while len(buf) < length:
            read = self.socket.recv(BUFSIZE)
            if not read:
                raise ProtocolError(self.tr('connection broken'))
            buf += read
        return start[0], buf

    def tell(self, *command):
        if not self.socket:
            self.signal('error', self.tr('You are not connected to a server.'))
            return
        try:
            with self.lock:
                self._write(command)
                ret, data = self._read()
                if ret != ACK:
                    raise ErrorResponse(data)
                return True
        except Exception, err:
            return self.handle_error(err)

    def ask(self, *command):
        if not self.socket:
            self.signal('error', self.tr('You are not connected to a server.'))
            return
        try:
            with self.lock:
                self._write(command)
                ret, data = self._read()
                if ret != STX:
                    raise ErrorResponse(data)
                return unserialize(data)
        except Exception, err:
            return self.handle_error(err)
