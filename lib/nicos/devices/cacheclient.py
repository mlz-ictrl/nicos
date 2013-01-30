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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS cache clients."""

from __future__ import with_statement

__version__ = "$Revision$"

import Queue
import select
import socket
import threading
from time import sleep, time as currenttime

from nicos import session
from nicos.core import Device, Param, CacheLockError, CacheError
from nicos.utils import closeSocket
from nicos.protocols.cache import msg_pattern, line_pattern, \
     cache_load, cache_dump, DEFAULT_CACHE_PORT, OP_TELL, OP_TELLOLD, OP_ASK, \
     OP_WILDCARD, OP_SUBSCRIBE, OP_LOCK, OP_REWRITE

BUFSIZE = 81920


class BaseCacheClient(Device):
    """
    An extensible read/write client for the NICOS cache.
    """

    parameters = {
        'cache':  Param('"host:port" of the cache instance to connect to',
                        type=str, mandatory=True),
        'prefix': Param('Cache key prefix', type=str, mandatory=True),
    }

    def doInit(self, mode):
        try:
            host, port = self.cache.split(':')
            port = int(port)
        except ValueError:
            host, port = self.cache, DEFAULT_CACHE_PORT
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
        if self._prefix:
            self._prefix += '/'
        self._selecttimeout = 0.1  # seconds
        self._do_callbacks = True
        self._disconnect_warnings = 0
        # maps newprefix -> oldprefix without self._prefix prepended
        self._inv_rewrites = {}
        self._prefixcallbacks = {}

        self._stoprequest = False
        self._queue = Queue.Queue()
        self._sync = True  # must be set to False on forking, since no thread
                           # can signal task_done anymore

        # create worker thread, but do not start yet, leave that to subclasses
        self._worker = threading.Thread(target=self._worker_thread,
                                        name='CacheClient worker')
        self._worker.setDaemon(True)

    def _getCache(self):
        return None

    def doShutdown(self):
        self._stoprequest = True
        self._worker.join()

    def _connect(self):
        self._do_callbacks = False
        self._startup_done.clear()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(5)
        try:
            self.log.debug('connecting to %s:%s' % self._address)
            self._socket.connect(self._address)
            self._connect_action()
        except Exception, err:
            self._disconnect('unable to connect to %s:%s: %s' %
                             (self._address + (err,)))
        else:
            self.log.info('now connected to %s:%s' % self._address)
            self._disconnect_warnings = 0
        self._startup_done.set()
        self._do_callbacks = True

    def _disconnect(self, why=''):
        self._startup_done.clear()
        if not self._socket:
            return
        if why:
            if self._disconnect_warnings % 10 == 0:
                self.log.warning(why)
            self._disconnect_warnings += 1
        closeSocket(self._socket)
        self._socket = None
        # close secondary socket
        with self._sec_lock:
            if self._secsocket:
                closeSocket(self._secsocket)
                self._secsocket = None

    def _wait_retry(self):
        sleep(1)

    def _wait_data(self):
        pass

    def _connect_action(self):
        # send request for all keys and updates....
        # HACK: send a single request for a nonexisting key afterwards to
        # determine the end of data
        self._socket.sendall('@%s%s\n###%s\n' %
                             (self._prefix, OP_WILDCARD, OP_ASK))

        # read response
        data, n = '', 0
        while not data.endswith('###!\n') and n < 1000:
            data += self._socket.recv(BUFSIZE)
            n += 1

        # send request for all updates
        self._socket.sendall('@%s%s\n' % (self._prefix, OP_SUBSCRIBE))
        for prefix in self._prefixcallbacks:
            self._socket.sendall('@%s%s\n' % (prefix, OP_SUBSCRIBE))

        self._process_data(data)

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        raise NotImplementedError('implement _handle_msg in subclasses')

    def _process_data(self, data,
                      lmatch=line_pattern.match, mmatch=msg_pattern.match):
        #n = 0
        i = 0  # avoid making a string copy for every line
        match = lmatch(data, i)
        while match:
            line = match.group(1)
            i = match.end()
            msgmatch = mmatch(line)
            # ignore invalid lines
            if msgmatch:
                #n += 1
                self._handle_msg(**msgmatch.groupdict())
            # continue loop
            match = lmatch(data, i)
        #self.log.debug('processed %d items' % n)
        return data[i:]

    def _worker_thread(self):
        data = ''
        range10 = range(10)
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
            while '\n' not in data and not self._stoprequest:

                # optionally do some action while waiting
                self._wait_data()

                if self._queue.empty():
                    # NOTE: the queue.empty() check is not 100% reliable, but
                    # that is not important here: all we care is about not
                    # having the select always return immediately for writing
                    writelist = []
                else:
                    writelist = [self._socket]

                # read or write some data
                while 1:
                    try:
                        res = select.select([self._socket], writelist, [],
                                            self._selecttimeout)
                    except select.error, e:
                        if e[0] == 4: # EINTR
                            continue
                        raise
                    break

                if res[1]:
                    # determine if something needs to be sent
                    tosend = ''
                    itemcount = 0
                    try:
                        # bunch a few messages together, but not unlimited
                        for _ in range10:
                            tosend += self._queue.get(False)
                            itemcount += 1
                    except Queue.Empty:
                        pass
                    # write data
                    try:
                        self._socket.sendall(tosend)
                    except socket.error:
                        data = ''
                        break
                    for _ in range(itemcount):
                        self._queue.task_done()
                if res[0]:
                    # got some data
                    try:
                        newdata = self._socket.recv(BUFSIZE)
                    except Exception:
                        newdata = ''
                    if not newdata:
                        # no new data from blocking read -> abort
                        self._disconnect('disconnect: recv failed')
                        data = ''
                        break
                    data += newdata

        if self._socket:
            # send rest of data
            tosend = ''
            itemcount = 0
            try:
                while 1:
                    tosend += self._queue.get(False)
                    itemcount += 1
            except Queue.Empty:
                pass
            self._socket.sendall(tosend)
            for _ in range(itemcount):
                self._queue.task_done()

        # end of while loop
        self._disconnect()

    def _single_request(self, tosend, sentinel='\n', retry=2, sync=True):
        """Communicate over the secondary socket."""
        if not self._socket:
            self._disconnect('single request: no socket')
            if not self._socket:
                raise CacheError('cache not connected')
        if sync and self._sync:
            # sync has to be false for lock requests, as these occur during startup
            self._queue.join()
        with self._sec_lock:
            if not self._secsocket:
                try:
                    self._secsocket = socket.socket(socket.AF_INET,
                                                    socket.SOCK_STREAM)
                    self._secsocket.connect(self._address)
                except Exception, err:
                    self.log.warning('unable to connect secondary socket to %s:%s: %s' %
                                      (self._address + (err,)))
                    self._secsocket = None
                    self._disconnect('secondary socket: could not connect')
                    raise CacheError('secondary socket could not be created')

        try:
            with self._sec_lock:
                # write request
                self._secsocket.sendall(tosend)

                # read response
                data, n = '', 0
                while not data.endswith(sentinel) and n < 1000:
                    data += self._secsocket.recv(BUFSIZE)
                    n += 1
        except socket.error:
            # retry?
            if retry:
                self._secsocket = None
                for m in self._single_request(tosend, sentinel, retry - 1):
                    yield m
                return
            raise


        lmatch = line_pattern.match
        mmatch = msg_pattern.match
        i = 0
        match = lmatch(data, i)
        while match:
            line = match.group(1)
            i = match.end()
            msgmatch = mmatch(line)
            if not msgmatch:
                # ignore invalid lines
                continue
            yield msgmatch
            match = lmatch(data, i)

    # methods to make this client usable as the main device in a simple session

    def start(self, *args):
        self._connect()
        self._worker.start()

    def wait(self):
        while not self._stoprequest:
            sleep(1)
        self._worker.join()

    def quit(self):
        self._stoprequest = True


class CacheClient(BaseCacheClient):

    temporary = True

    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        self._db = {}
        self._callbacks = {}

        # the execution master lock needs to be refreshed every now and then
        self._ismaster = False
        self._master_expires = 0.
        self._mastertimeout = 5.

        self._worker.start()

    def doShutdown(self):
        BaseCacheClient.doShutdown(self)
        # make sure the interface is still usable but has no values to return
        self._db.clear()
        self._startup_done.set()

    def _connect_action(self):
        # clear the local database of possibly outdated values
        self._db.clear()
        # get all current values from the cache
        BaseCacheClient._connect_action(self)
        # tell the server all our rewrites
        for newprefix, oldprefix in self._inv_rewrites.iteritems():
            self._queue.put(newprefix + OP_REWRITE + oldprefix + '\n')

    def _wait_data(self):
        if self._ismaster:
            time = currenttime()
            if time > self._master_expires:
                self._master_expires = time + self._mastertimeout - 1
                self.lock('master', self._mastertimeout)
                self.put('session', 'master', session.sessionid,
                         ttl=self._mastertimeout)

    def _unlock_master(self):
        self.unlock('master')
        self.put('session', 'master', '')

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if op not in (OP_TELL, OP_TELLOLD):
            return
        if not key.startswith(self._prefix):
            for cb in self._prefixcallbacks:
                if key.startswith(cb):
                    value = cache_load(value) if value is not None else value
                    time = time and float(time)
                    try:
                        self._prefixcallbacks[cb](key, value, time)
                    except Exception:
                        self.log.warning('error in cache callback', exc=1)
            return
        key = key[len(self._prefix):]
        time = time and float(time)
        self._propagate((time, key, op, value))
        #self.log.debug('got %s=%s' % (key, value))
        if value is None or op == OP_TELLOLD:
            self._db.pop(key, None)
            value = None
        else:
            value = cache_load(value)
            self._db[key] = (value, time)
        if key in self._callbacks and self._do_callbacks:
            try:
                self._callbacks[key](key, value, time)
            except Exception:
                self.log.warning('error in cache callback', exc=1)

    def _propagate(self, args):
        pass

    def addCallback(self, dev, key, function):
        """Add a callback to be called when the given device/subkey value is
        updated.  There can be only one callback per subkey.

        The callback is also called if the value is expired or deleted.
        """
        self._callbacks[('%s/%s' % (dev, key)).lower()] = function

    def removeCallback(self, dev, key):
        """Remove a callback for the given device/subkey, if present."""
        self._callbacks.pop(('%s/%s' % (dev, key)).lower(), None)

    def addPrefixCallback(self, prefix, function):
        """Add a "prefix" callback, which is called for every key and value
        that does not match the prefix parameter of the client, but matches
        the prefix given to this function.
        """
        if prefix not in self._prefixcallbacks:
            self._queue.put('@%s%s\n' % (prefix, OP_SUBSCRIBE))
        self._prefixcallbacks[prefix] = function

    def get(self, dev, key, default=None, mintime=None):
        """Get a value from the local cache for the given device and subkey.

        Since ``None`` can be a valid value for some cache entries, you can give
        another value that is returned if the value is missing or expired.  A
        singleton such as ``Ellipsis`` works well in these cases.
        """
        self._startup_done.wait()
        dbkey = ('%s/%s' % (dev, key)).lower()
        entry = self._db.get(dbkey)
        if entry is None:
            if str(dev).lower() in self._inv_rewrites:
                self.log.debug('%s not in cache, trying rewritten' % dbkey)
                return self.get(self._inv_rewrites[str(dev).lower()],
                                key, default, mintime)
            self.log.debug('%s not in cache' % dbkey)
            return default
        value, time = entry
        if mintime and time < mintime:
            try:
                time, _ttl, value = self.get_explicit(dev, key, default)
            except CacheError:
                return default
            if value is not default and time < mintime:
                return default
        return value

    def get_explicit(self, dev, key, default=None):
        """Get a value from the cache server, bypassing the local cache.  This
        is needed if the current update time and ttl is required.
        """
        if dev:
            key = ('%s/%s' % (dev, key)).lower()
        tosend = '@%s%s%s\n' % (self._prefix, key, OP_ASK)
        for msgmatch in self._single_request(tosend):
            time, ttl, value = msgmatch.group('time'), msgmatch.group('ttl'), \
                               msgmatch.group('value')
            if value:
                return (time and float(time), ttl and float(ttl),
                        cache_load(value))
            return (time and float(time), ttl and float(ttl),
                    default)
        return (None, None, default)  # shouldn't happen

    def put(self, dev, key, value, time=None, ttl=None):
        """Put a value for a given device and subkey.

        The value is serialized by this method using `cache_dump()`.
        """
        if ttl == 0:
            # no need to process immediately-expired values
            return
        if time is None:
            time = currenttime()
        ttlstr = ttl and '+%s' % ttl or ''
        dbkey = ('%s/%s' % (dev, key)).lower()
        self._db[dbkey] = (value, time)
        value = cache_dump(value)
        msg = '%s%s@%s%s%s%s\n' % (time, ttlstr, self._prefix, dbkey,
                                   OP_TELL, value)
        #self.log.debug('putting %s=%s' % (dbkey, value))
        self._queue.put(msg)
        self._propagate((time, dbkey, OP_TELL, value))

    def put_raw(self, key, value, time=None, ttl=None):
        """Put a key given by full name.

        The instance's key prefix is *not* prepended to the key.  This enables
        e.g. the session logger writing to ``logbook/message`` although the
        prefix is ``nicos/``.
        """
        if ttl == 0:
            # no need to process immediately-expired values
            return
        if time is None:
            time = currenttime()
        ttlstr = ttl and '+%s' % ttl or ''
        value = cache_dump(value)
        msg = '%s%s@%s%s%s\n' % (time, ttlstr, key, OP_TELL, value)
        #self.log.debug('putting %s=%s' % (key, value))
        self._queue.put(msg)

    def setRewrite(self, newprefix, oldprefix):
        oldprefix = oldprefix.lower()
        newprefix = newprefix.lower()
        self._queue.put(self._prefix + newprefix + OP_REWRITE + \
                        self._prefix + oldprefix + '\n')
        self._inv_rewrites[newprefix] = oldprefix

    def unsetRewrite(self, newprefix):
        newprefix = newprefix.lower()
        if newprefix in self._inv_rewrites:
            del self._inv_rewrites[newprefix]
            self._queue.put(self._prefix + newprefix + OP_REWRITE + '\n')

    def clear(self, dev):
        """Clear all cache subkeys belonging to the given device."""
        time = currenttime()
        devprefix = str(dev).lower() + '/'
        for dbkey in self._db.keys():
            if dbkey.startswith(devprefix):
                msg = '%s@%s%s%s\n' % (time, self._prefix, dbkey, OP_TELL)
                self._db.pop(dbkey, None)
                self._queue.put(msg)
                self._propagate((time, dbkey, OP_TELL, ''))

    def clear_all(self):
        """Clear all cache keys."""
        time = currenttime()
        for dbkey in self._db.keys():
            msg = '%s@%s%s%s\n' % (time, self._prefix, dbkey, OP_TELL)
            self._db.pop(dbkey, None)
            self._queue.put(msg)
            self._propagate((time, dbkey, OP_TELL, ''))

    def invalidate(self, dev, key):
        """Locally invalidate device/subkey.  This does not touch the remote
        cache, but will trigger re-initializing short-lived things like device
        values and status from the hardware.
        """
        dbkey = ('%s/%s' % (dev, key)).lower()
        self.log.debug('invalidating %s' % dbkey)
        self._db.pop(dbkey, None)

    def history(self, dev, key, fromtime, totime):
        """History query: opens a separate connection since it is otherwise not
        possible to determine which response lines belong to it.
        """
        if dev:
            key = ('%s/%s' % (dev, key)).lower()
        tosend = '%s-%s@%s%s%s\n###?\n' % (fromtime, totime,
                                           self._prefix, key, OP_ASK)
        ret = []
        for msgmatch in self._single_request(tosend, '###!\n'):
            # process data
            time, value = msgmatch.group('time'), msgmatch.group('value')
            if time is None:
                break  # it's the '###' value
            if value:
                ret.append((float(time), cache_load(value)))
        return ret

    def lock(self, key, ttl=None, unlock=False, sessionid=None):
        """Locking/unlocking: opens a separate connection."""
        tosend = '%s%s%s%s%s\n' % (
            self._prefix, key.lower(), OP_LOCK,
            unlock and '-' or '+', sessionid or session.sessionid)
        if ttl is not None:
            tosend = ('+%s@' % ttl) + tosend
        for msgmatch in self._single_request(tosend, sync=False):
            if msgmatch.group('value'):
                raise CacheLockError(msgmatch.group('value'))
            return
        else:
            # no response received; let's assume standalone mode
            self.log.warning('allowing lock/unlock operation without cache '
                              'connection')

    def unlock(self, key, sessionid=None):
        return self.lock(key, ttl=None, unlock=True, sessionid=sessionid)


class DaemonCacheClient(CacheClient):
    def _propagate(self, args):
        session.emitfunc('cache', args)


class SyncCacheClient(BaseCacheClient):

    temporary = True

    def doInit(self, mode):
        self._db = {}
        BaseCacheClient.doInit(self, mode)

    def get_values(self):
        # connect, get data, disconnect
        self._worker.start()
        self._worker.join()
        return self._db

    def _connect_action(self):
        # like for BaseCacheClient, but without request for updates
        self._socket.sendall('@%s%s\n###%s\n' %
                             (self._prefix, OP_WILDCARD, OP_ASK))

        # read response
        data, n = '', 0
        while not data.endswith('###!\n') and n < 1000:
            data += self._socket.recv(BUFSIZE)
            n += 1

        self._process_data(data)

        # stop immediately after reading data
        self._stoprequest = True

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if op not in (OP_TELL, OP_TELLOLD) or not key.startswith(self._prefix):
            return
        key = key[len(self._prefix):]
        if value is None:
            self._db.pop(key, None)
        else:
            # even with TELLOLD; an old value is better than no value
            self._db[key] = cache_load(value)
