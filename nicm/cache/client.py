#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICM cache client support
#
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
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

"""NICM cache clients."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import re
import time
import select
import socket
import threading

from nicm.device import Device
from nicm.cache.utils import msg_pattern, DEFAULT_CACHE_PORT


class CacheClient(Device):
    """
    A read/write client for the NICM cache.
    """

    parameters = {
        'server': (str, '', True,
                   '"host:port" of the cache instance to connect to.'),
        'prefix': (str, '', True, 'Cache key prefix.'),
    }

    def doInit(self):
        try:
            host, port = self.server.split(':')
            port = int(port)
        except ValueError:
            host, port = self.server, DEFAULT_CACHE_PORT
        self._address = (host, port)
        self._socket = None
        self._lock = threading.Lock()
        self._prefix = self.prefix.strip('/')

    def _connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect(self._address)
        except Exception, err:
            self._socket = None
            self.printwarning('unable to connect: %s' % err)

    def _disconnect(self):
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        except Exception:
            pass
        self._socket = None

    def put(self, dev, key, value, timestamp=None, ttl=None):
        if timestamp is None:
            timestamp = time.time()
        ttl = ttl and '+%s' % ttl or ''
        msg = '%s%s@%s/%s/%s=%s\n' % (timestamp, ttl, self._prefix, dev.name,
                                      key, value)
        tries = 5
        while tries > 0:
            with self._lock:
                if not self._socket:
                    self._connect()
                    if not self._socket:
                        return None
                try:
                    self._socket.send(msg)
                except socket.error:
                    self._disconnect()
                    tries -= 1
                    continue
            break

    def get(self, dev, key):
        msg = '@%s/%s/%s?\n' % (self._prefix, dev.name, key)
        tries = 5
        answer = None
        while tries > 0:
            with self._lock:
                if not self._socket:
                    self._connect()
                    if not self._socket:
                        return None
                try:
                    self._socket.send(msg)
                except socket.error:
                    self._disconnect()
                    tries -= 1
                    continue
                sel = select.select([self._socket], [], [self._socket], 1)
                if self._socket in sel[0]:
                    answer = self._socket.recv(8192)
                    if not answer:
                        # no answer from blocking read, retry
                        tries -= 1
                        continue
                elif self._socket in sel[2]:
                    # socket in error state, reconnect and try again
                    self._disconnect()
                    tries -= 1
                    continue
                else:
                    # no answer
                    tries -= 1
                    continue
                break
        if answer is None:
            return None
        match = msg_pattern.match(answer)
        if not match:
            # garbled answer
            return None
        value = match.group('value')
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return value

    def history(self, dev, key):
        pass


class WriteonlyCacheClient(CacheClient):
    """
    A write-only client for the NICM cache.  Used in the poller application,
    so that each read() actually queries the device.
    """

    def get(self, *args):
        return None
