#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
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

from __future__ import with_statement

"""NICOS cache clients."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import Queue
import select
import socket
import threading
from time import sleep, time as currenttime

from nicos import session
from nicos.utils import closeSocket
from nicos.device import Device, Param
from nicos.errors import CacheLockError
from nicos.cache.utils import msg_pattern, line_pattern, cache_load, cache_dump, \
     DEFAULT_CACHE_PORT, OP_TELL, OP_ASK, OP_WILDCARD, OP_SUBSCRIBE, OP_LOCK

BUFSIZE = 8192


class BaseCacheClient(Device):
    """
    An extensible read/write client for the NICOS cache.
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
        self._secsocket = None
        self._sec_lock = threading.Lock()
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
        self._worker.join()

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
        with self._sec_lock:
            if self._socket:
                try:
                    self._secsocket = socket.socket(socket.AF_INET,
                                                    socket.SOCK_STREAM)
                    self._secsocket.connect(self._address)
                except Exception:
                    self.printexception('unable to connect secondary socket')
                    self._secsocket = None
        self._startup_done.set()

    def _disconnect(self, why=''):
        if not self._socket:
            return
        if why:
            self.printwarning(why)
        closeSocket(self._socket)
        self._socket = None
        # close secondary socket
        with self._sec_lock:
            if self._secsocket:
                closeSocket(self._secsocket)
                self._secsocket = None

    def _wait_retry(self):
        sleep(5)

    def _wait_data(self):
        pass

    def _connect_action(self):
        # send request for all keys and updates....
        # HACK: send a single request for a nonexisting key afterwards to
        # determine the end of data
        self._socket.sendall(
            '@%s\r\n###?\r\n@%s\r\n' % (OP_WILDCARD, OP_SUBSCRIBE))

        # read response
        data, n = '', 0
        while not data.endswith('###!\r\n') and n < 100:
            data += self._socket.recv(BUFSIZE)
            n += 1

        self._process_data(data)

    def _handle_msg(self, time, ttl, tsop, key, op, value):
        raise NotImplementedError

    def _process_data(self, data,
                      lmatch=line_pattern.match, mmatch=msg_pattern.match):
        #n = 0
        match = lmatch(data)
        while match:
            line = match.group(1)
            data = data[match.end():]
            msgmatch = mmatch(line)
            # ignore invalid lines
            if msgmatch:
                #n += 1
                self._handle_msg(**msgmatch.groupdict())
            # continue loop
            match = lmatch(data)
        #self.printdebug('processed %d items' % n)
        return data

    def _worker_thread(self):
        data = ''
        process = self._process_data

        while not self._stoprequest:
            if not self._socket:
                self._connect()
                if not self._socket:
                    self._wait_retry()
                    continue

            # process data so far
            data = process(data)

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
                    data = ''
                    break
                elif res[1]:
                    # write data
                    try:
                        self._socket.sendall(tosend)
                    except:
                        self._disconnect('disconnect: send failed')
                        data = ''
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
                        data = ''
                        break
                    data += newdata
        if self._socket:
            # send rest of data
            while True:
                try:
                    tosend = self._queue.get(False)
                except:
                    break
                self._socket.sendall(tosend)

        # end of while loop
        self._disconnect()

    def _single_request(self, tosend, sentinel='\r\n'):
        """Communicate over the secondary socket."""
        if not self._secsocket:
            return

        with self._sec_lock:
            # write request
            self._secsocket.sendall(tosend)

            # read response
            data, n = '', 0
            while not data.endswith(sentinel) and n < 100:
                data += self._secsocket.recv(BUFSIZE)
                n += 1

        match = line_pattern.match(data)
        while match:
            line = match.group(1)
            data = data[match.end():]
            msgmatch = msg_pattern.match(line)
            if not msgmatch:
                # ignore invalid lines
                continue
            yield msgmatch
            match = line_pattern.match(data)


class CacheClient(BaseCacheClient):

    temporary = True

    def doInit(self):
        BaseCacheClient.doInit(self)
        self._db = {}
        self._callbacks = {}
        # XXX in simulation mode?
        self._worker.start()
        # the execution master lock needs to be refreshed every now and then
        self._ismaster = False
        self._master_expires = 0
        self._mastertimeout = self._selecttimeout * 10

    def _wait_data(self):
        if self._ismaster:
            time = currenttime()
            if time > self._master_expires:
                self._master_expires = time + self._mastertimeout - 1
                self.lock('master', self._mastertimeout)

    def _handle_msg(self, time, ttl, tsop, key, op, value):
        if op != OP_TELL or not key.startswith(self._prefix):
            return
        key = key[len(self._prefix)+1:]
        #self.printdebug('got %s=%s' % (key, value))
        if value is None:
            self._db.pop(key, None)
        else:
            value = cache_load(value)
            self._db[key] = (value, time and float(time), ttl and float(ttl))
        if key in self._callbacks:
            try:
                self._callbacks[key](key, value)
            except:
                self.printwarning('error in cache callback', exc=1)

    def addCallback(self, dev, key, function):
        self._callbacks['%s/%s' % (dev.name.lower(), key)] = function

    def removeCallback(self, dev, key):
        self._callbacks.pop('%s/%s' % (dev.name.lower(), key), None)

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

    def clear(self, devname):
        for dbkey in self._db.keys():
            if dbkey.startswith(devname.lower() + '/'):
                msg = '%s@%s/%s%s\r\n' % (currenttime(), self._prefix,
                                          dbkey, OP_TELL)
                self._db.pop(dbkey, None)
                self._queue.put(msg)

    def invalidate(self, dev, key):
        dbkey = '%s/%s' % (dev.name.lower(), key)
        self.printdebug('invalidating %s' % dbkey)
        self._db.pop(dbkey, None)

    def history(self, dev, key, fromtime, totime):
        """History query: opens a separate connection since it is otherwise not
        possible to determine which response lines belong to it.
        """
        dbkey = '%s/%s' % (dev.name.lower(), key)
        tosend = '%s-%s@%s/%s%s\r\n###?\r\n' % (fromtime, totime,
                                                self._prefix, dbkey, OP_ASK)
        ret = []
        for msgmatch in self._single_request(tosend, '###!\r\n'):
            # process data
            time, ttl, value = msgmatch.group('time'), msgmatch.group('ttl'), \
                               msgmatch.group('value')
            if time is None:
                break  # it's the '###' value
            ret.append((float(time), ttl and float(ttl), cache_load(value)))
        return ret

    def lock(self, key, ttl=None, unlock=False, sessionid=None):
        """Locking/unlocking: opens a separate connection."""
        tosend = '%s/%s%s%s%s\r\n' % (
            self._prefix, key.lower(), OP_LOCK,
            unlock and '-' or '+', sessionid or session.sessionid)
        if ttl is not None:
            tosend = ('+%s@' % ttl) + tosend
        for msgmatch in self._single_request(tosend):
            if msgmatch.group('value'):
                raise CacheLockError(msgmatch.group('value'))
            return
        else:
            # no response received; let's assume standalone mode
            self.printwarning('allowing lock/unlock operation without cache '
                              'connection')

    def unlock(self, key, sessionid=None):
        return self.lock(key, ttl=None, unlock=True, sessionid=sessionid)
