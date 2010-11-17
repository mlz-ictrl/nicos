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

import Queue
import select
import socket
import threading
from time import sleep, time as currenttime

from nicm import nicos
from nicm.device import Device, Param
from nicm.cache.utils import msg_pattern, line_pattern, cache_load, \
     DEFAULT_CACHE_PORT, OP_TELL, OP_WILDCARD, OP_SUBSCRIBE, cache_dump

BUFSIZE = 8192


class BaseCacheClient(Device):
    """
    An extensible read/write client for the NICM cache.
    """

    parameters = {
        'server': Param('"host:port" of the cache instance to connect to',
                        type=str, mandatory=True),
        'prefix': Param('Cache key prefix', type=str, mandatory=True),
    }

    def doInit(self):
        try:
            host, port = self.server.split(':')
            port = int(port)
        except ValueError:
            host, port = self.server, DEFAULT_CACHE_PORT
        # this event is set as soon as:
        # * the connection is established and the connect_action is done, or
        # * the initial connection failed
        # this prevents devices from polling parameter values before all values
        # from the cache have been received
        self._startup_done = threading.Event()
        self._address = (host, port)
        self._socket = None
        self._prefix = self.prefix.strip('/')
        self._selecttimeout = 1.0  # seconds

        self._stoprequest = False
        self._queue = Queue.Queue()

        # create worker thread, but do not start yet, leave that to subclasses
        self._worker = threading.Thread(target=self._worker_thread)
        self._worker.setDaemon(True)

    def _getCache(self):
        return None

    def doShutdown(self):
        self._stoprequest = True
        #self._worker.join()

    def _connect(self):
        self._startup_done.clear()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect(self._address)
            self._connect_action()
        except Exception, err:
            self._disconnect('unable to connect to %s:%s: %s' %
                             (self._address + (err,)))
        else:
            self.printinfo('now connected to %s:%s' % self._address)
        self._startup_done.set()

    def _disconnect(self, why=''):
        if not self._socket:
            return
        if why:
            self.printwarning(why)
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        except Exception:
            pass
        self._socket = None

    def _wait_retry(self):
        sleep(5)

    def _wait_data(self):
        pass

    def _connect_action(self):
        # send request for all keys and updates....
        # HACK: send a single request for a nonexisting key afterwards to
        # determine the end of data
        tosend = '@%s\r\n###?\r\n@%s\r\n' % (OP_WILDCARD, OP_SUBSCRIBE)
        while tosend:
            sent = self._socket.send(tosend)
            tosend = tosend[sent:]

        # read response
        data, n = '', 0
        while not data.endswith('###!\r\n') and n < 100:
            data += self._socket.recv(BUFSIZE)
            n += 1

        # process data
        match = line_pattern.match(data)
        while match:
            line = match.group(1)
            data = data[match.end():]
            msgmatch = msg_pattern.match(line)
            if not msgmatch:
                # ignore invalid lines
                continue
            self._handle_msg(**msgmatch.groupdict())
            # continue loop
            match = line_pattern.match(data)

    def _handle_msg(self, time, ttl, tsop, key, op, value):
        raise NotImplementedError

    def _worker_thread(self):
        data = ''

        while not self._stoprequest:
            if not self._socket:
                self._connect()
                if not self._socket:
                    self._wait_retry()
                    continue

            # process data so far
            match = line_pattern.match(data)
            while match:
                line = match.group(1)
                data = data[match.end():]
                msgmatch = msg_pattern.match(line)
                if not msgmatch:
                    # ignore invalid lines
                    continue
                self._handle_msg(**msgmatch.groupdict())
                # continue loop
                match = line_pattern.match(data)

            # wait for a whole line of data to arrive
            while ('\r' not in data) and ('\n' not in data) and \
                      not self._stoprequest:

                # optionally do some action while waiting
                self._wait_data()

                # determine if something needs to be sent
                try:
                    tosend = self._queue.get(False)
                    writelist = [self._socket]
                except:
                    tosend = None
                    writelist = []
                # try to read or write some data
                res = select.select([self._socket], writelist, [self._socket],
                                    self._selecttimeout)
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
                        newdata = self._socket.recv(BUFSIZE)
                    except:
                        newdata = ''
                    if not newdata:
                        # no new data from blocking read -> abort
                        self._disconnect('disconnect: recv failed')
                        break
                    data += newdata

        # end of while loop
        self._disconnect()


class CacheClient(BaseCacheClient):
    def doInit(self):
        BaseCacheClient.doInit(self)
        self._db = {}
        self._worker.start()
        # the execution master lock
        self._ismaster = False
        self._mastermsg = '+%s@%s/master="%s"\r\n' % (
            3*self._selecttimeout, self._prefix, nicos.sessionid)
        self._master_expires = 0

    def _wait_data(self):
        if self._ismaster:
            time = currenttime()
            if time > self._master_expires:
                self._master_expires = time + self._selecttimeout
                self._queue.put(self._mastermsg)

    def getMaster(self):
        self._startup_done.wait()
        return self._db.get('master')

    def setMaster(self):
        self._queue.put(self._mastermsg)
        self._ismaster = True

    def releaseMaster(self):
        self._queue.put('%s/master=\r\n' % self._prefix)
        self._ismaster = False

    def _handle_msg(self, time, ttl, tsop, key, op, value):
        if op != OP_TELL or not key.startswith(self._prefix):
            return
        key = key[len(self._prefix)+1:]
        if key == 'master':
            self._ismaster = value == '"' + nicos.sessionid + '"'
        self.printdebug('got %s=%s' % (key, value))
        if value is None:
            self._db.pop(key, None)
        else:
            self._db[key] = (cache_load(value),
                             time and float(time), ttl and float(ttl))

    def get(self, dev, key):
        self._startup_done.wait()
        dbkey = '%s/%s' % (dev.name.lower(), key)
        entry = self._db.get(dbkey)
        if entry is None:
            self.printdebug('%s not in cache' % dbkey)
            return None
        value, time, ttl = entry
        if ttl and time + ttl < currenttime():
            self.printdebug('%s timed out' % dbkey)
            del self._db[dbkey]
            return None
        return value

    def put(self, dev, key, value, time=None, ttl=None):
        if time is None:
            time = currenttime()
        ttlstr = ttl and '+%s' % ttl or ''
        dbkey = '%s/%s' % (dev.name.lower(), key)
        msg = '%s%s@%s/%s%s%s\r\n' % (time, ttlstr, self._prefix, dbkey,
                                      OP_TELL, cache_dump(value))
        self.printdebug('putting %s=%s' % (dbkey, value))
        self._db[dbkey] = (value, time, ttl)
        self._queue.put(msg)

    def history(self, dev, key):
        pass


class WriteonlyCacheClient(CacheClient):
    """
    A write-only client for the NICM cache.  Used in the poller application,
    so that each read() actually queries the device.
    """

    def get(self, dev, key):
        return None
