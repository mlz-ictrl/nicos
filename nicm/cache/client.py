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

import time
import Queue
import select
import socket
import threading

from nicm.device import Device
from nicm.cache.utils import msg_pattern, line_pattern, cache_convert, \
     DEFAULT_CACHE_PORT, OP_TELL, OP_WILDCARD, OP_SUBSCRIBE


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

        self._stoprequest = False
        self._queue = Queue.Queue()
        self._worker = threading.Thread(target=self._worker_thread)
        self._worker.setDaemon(True)
        self._worker.start()

        self._db = {}

    def doShutdown(self):
        self._stoprequest = True
        self._worker.join()

    def _connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect(self._address)
            # send request for all keys and updates....
            q = '@%s\r\n@%s\r\n' % (OP_WILDCARD, OP_SUBSCRIBE)
            while q:
                sent = self._socket.send(q)
                q = q[sent:]
        except Exception, err:
            self._disconnect('unable to connect to %s:%s: %s' %
                             (self._address + (err,)))
        else:
            self.printinfo('now connected to %s:%s' % self._address)

    def _disconnect(self, why=''):
        if why:
            self.printwarning(why)
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        except Exception:
            pass
        self._socket = None

    def _worker_thread(self):
        data = ''
        while not self._stoprequest:
            if not self._socket:
                self._connect()
                if not self._socket:
                    time.sleep(5)
                    continue

            # process data so far
            match = line_pattern.match(data)
            while match:
                line = match.group(1)
                data = data[match.end():]
                msgmatch = msg_pattern.match(line)
                if not msgmatch or msgmatch.group('op') != OP_TELL:
                    # ignore invalid lines
                    continue
                self._handle_msg(**msgmatch.groupdict())
                # continue loop
                match = line_pattern.match(data)

            # wait for a whole line of data to arrive
            while ('\r' not in data) and ('\n' not in data) and \
                      not self._stoprequest:
                try:
                    tosend = self._queue.get(False)
                    writelist = [self._socket]
                except:
                    tosend = None
                    writelist = []
                # try to read or write some data, use a timeout of 1 sec
                res = select.select([self._socket], writelist, [self._socket], 1)
                if res[2]:
                    # handle error case: close socket and reopen
                    self._disconnect('disconnect: socket in error state')
                    break
                elif res[1]:
                    # write data
                    try:
                        while tosend:
                            sent = self._socket.send(tosend)
                            tosend = tosend[sent:]
                    except:
                        self._disconnect('disconnect: send failed')
                        break
                elif res[0]:
                    # got some data
                    try:
                        newdata = self._socket.recv(8192)
                    except:
                        newdata = ''
                    if not newdata:
                        # no new data from blocking read -> abort
                        self._disconnect('disconnect: recv failed')
                        break
                    data += newdata

        # end of while loop
        self._disconnect()

    def _handle_msg(self, time, ttl, tsop, key, op, value):
        if not key.startswith(self._prefix):
            return
        self.printdebug('got %s=%s' % (key, value))
        self._db[key[len(self._prefix)+1:]] = cache_convert(value)

    def put(self, dev, key, value, timestamp=None, ttl=None):
        if timestamp is None:
            timestamp = time.time()
        ttl = ttl and '+%s' % ttl or ''
        msg = '%s%s@%s/%s/%s%s%s\n' % (timestamp, ttl, self._prefix, dev.name,
                                       key, OP_TELL, value)
        self.printdebug('putting %s/%s=%s' % (dev.name, key, value))
        self._queue.put(msg)

    def get(self, dev, key):
        value = self._db.get('%s/%s' % (dev.name, key))
        if value is None:
            self.printdebug('%s/%s not in cache' % (dev.name, key))
            return None
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
