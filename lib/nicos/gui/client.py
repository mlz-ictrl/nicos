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

import zlib
import socket
import struct
import hashlib
import threading
import cPickle as pickle


# nicos/licos daemon protocol
EOF = '\x04'
OK = 'NICOSD OK\n'
BYE = 'BYE...\n'
WARN = 'NICOSD WARNING: '
ERROR = 'NICOSD ERROR: '

# Script status constants
STATUS_IDLE     = -1
STATUS_RUNNING  = 0
STATUS_INBREAK  = 1
STATUS_STOPPING = 2

# General constants
BUFSIZE = 8192
TIMEOUT = 30.0

lengthheader = struct.Struct('>I')


class ProtocolError(Exception):
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
            self.signal('error',
                self.tr('Server control connection failed: %1.').arg(msg), err)
            return
        except Exception, err:
            self.signal('error',
                self.tr('Server control connection failed: %1.').arg(str(err)), err)
            return

        # log-in sequence
        if not self.answer_prompt('display', conndata['display']):
            return
        if not self.answer_prompt('login: ', conndata['login']):
            return
        if password is None:
            password = conndata['passwd']
        if not self.answer_prompt('passwd: ', hashlib.sha1(password).hexdigest()):
            return
        try:
            ret = self._read()
            if 'Invalid passwd' in ret:
                raise ProtocolError(self.tr('Wrong password'))
            elif ret != OK:
                raise ProtocolError(
                    self.tr('Server protocol mismatch: ') + str(ret))
        except Exception, err:
            return self.handle_error(err)

        # connect to event port
        self.event_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.event_socket.connect((conndata['host'], conndata['port']))
        except socket.error, err:
            errno, msg = err.args
            self.signal('error',
                self.tr('Server connection failed: %1.').arg(msg), err)
            return

        # start event handler
        self.event_thread = threading.Thread(target=self.event_handler,
                                             name='event handler thread')
        self.event_thread.start()

        self.connected = True
        self.host, self.port = conndata['host'], conndata['port']

        self.version = self.send_command('get_version')
        self.signal('connected')

    def event_handler(self):
        rfile = self.event_socket.makefile('r')
        while 1:
            line = rfile.readline()
            if not line:
                if self.connected and not self.disconnecting:
                    self.signal('error', self.tr('Connection to server lost.'))
                    self._close()
                try:
                    self.event_socket.close()
                except Exception:
                    pass
                return
            try:
                event, data = line.split(None, 1)
                data = self.unserialize(data)
            except Exception:
                print 'Garbled event: %r' % line
            else:
                self.signal(event, data)

    def disconnect(self):
        self.disconnecting = True
        ret = self.send_command('exit')
        if ret != BYE:
            self.signal('error',
                        self.tr('Error in disconnect command:') + str(ret))
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

    def serialize(self, data):
        """Serialize an object according to the selected protocol."""
        return pickle.dumps(data).replace('\n', '\xff')

    def unserialize(self, data):
        """Unserialize an object according to the selected protocol."""
        return pickle.loads(data.replace('\xff', '\n'))

    def handle_error(self, err):
        if isinstance(err, ProtocolError):
            self.signal('error', err.args[0] + '.')
        else:
            if isinstance(err, socket.timeout):
                msg = self.tr('Connection to server timed out.')
            elif isinstance(err, socket.error):
                msg = self.tr('Server connection broken: %1.').arg(err.args[1])
            else:
                msg = self.tr('Exception occurred: %1.').arg(str(err))
            self.signal('error', msg, err)
            self._close()

    def _write(self, string):
        sent = self.socket.send(string + EOF)
        if sent != len(string) + 1:
            raise socket.error(0, self.tr('Not enough bytes written'))

    def _read(self, lsize=lengthheader.size):
        buf = ''
        if self.gzip:
            while len(buf) < lsize:
                read = self.socket.recv(BUFSIZE)
                if not read:
                    raise ProtocolError(self.tr('No data to read'))
                buf += read
            length = lengthheader.unpack(buf[:lsize])[0]
            buf = buf[lsize:]
            while len(buf) < length:
                read = self.socket.recv(BUFSIZE)
                if not read:
                    raise ProtocolError(self.tr('No data to read'))
                read += buf
            if len(buf) != length:
                raise socket.error(0, self.tr('Server response jumbled'))
            return zlib.decompress(buf)
        i = 0
        while 1:
            i += 1
            read = self.socket.recv(BUFSIZE)
            if not read:
                raise ProtocolError(self.tr('No data to read'))
            elif read.endswith(EOF):
                return buf + read[:-1]
            elif EOF in read:
                raise socket.error(0, self.tr('Server response jumbled'))
            else:
                buf += read

    def answer_prompt(self, prompt, answer):
        try:
            with self.lock:
                ret = self._read()
                if ret != prompt:
                    raise ProtocolError(self.tr('Server protocol mismatch'))
                self._write(answer)
        except Exception, err:
            self.handle_error(err)
            return False
        else:
            return True

    def send_command(self, command, expect_ok=False):
        if not self.socket:
            self.signal('error', self.tr('You are not connected to a server.'))
            return
        try:
            with self.lock:
                self._write(command)
                ret = self._read()
                if expect_ok and ret != OK:
                    raise ProtocolError(ret.strip())
        except Exception, err:
            return self.handle_error(err)
        else:
            return ret

    def send_commands(self, *commands):
        if not self.socket:
            self.signal('error', self.tr('You are not connected to a server.'))
            return False
        try:
            with self.lock:
                for command in commands:
                    self._write(command)
                    ret = self._read()
                    if ret != OK:
                        raise ProtocolError(ret.strip())
        except Exception, err:
            self.handle_error(err)
            return False
        else:
            return True
