#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

import select
import socket
import threading
from time import sleep, time as currenttime

from nicos import session
from nicos.core import Device, Param, CacheLockError, CacheError, host
from nicos.utils import tcpSocket, closeSocket, createThread, getSysInfo
from nicos.protocols.cache import msg_pattern, line_pattern, \
    cache_load, cache_dump, DEFAULT_CACHE_PORT, OP_TELL, OP_TELLOLD, OP_ASK, \
    OP_WILDCARD, OP_SUBSCRIBE, OP_UNSUBSCRIBE, OP_LOCK, OP_LOCK_LOCK, \
    OP_LOCK_UNLOCK, OP_REWRITE, END_MARKER, SYNC_MARKER, CYCLETIME, BUFSIZE
from nicos.pycompat import queue, iteritems, to_utf8, from_utf8, string_types


class BaseCacheClient(Device):
    """
    An extensible read/write client for the NICOS cache.
    """

    parameters = {
        'cache':  Param('"host[:port]" of the cache instance to connect to',
                        type=host, mandatory=True),
        'prefix': Param('Cache key prefix', type=str, mandatory=True),
    }

    remote_callbacks = True

    def doInit(self, mode):
        # Should the worker connect or disconnect?
        self._should_connect = True
        # this event is set as soon as:
        # * the connection is established and the connect_action is done, or
        # * the initial connection failed
        # this prevents devices from polling parameter values before all values
        # from the cache have been received
        self._startup_done = threading.Event()
        self._connected = False
        self._socket = None
        self._secsocket = None
        self._sec_lock = threading.RLock()
        self._prefix = self.prefix.strip('/')
        if self._prefix:
            self._prefix += '/'
        self._selecttimeout = CYCLETIME  # seconds
        self._do_callbacks = self.remote_callbacks
        self._disconnect_warnings = 0
        # maps newprefix -> oldprefix without self._prefix prepended
        self._inv_rewrites = {}
        # maps oldprefix -> set of new prefixes without self._prefix prepended
        self._rewrites = {}
        self._prefixcallbacks = {}

        self._stoprequest = False
        self._queue = queue.Queue()
        self._synced = True

        # create worker thread, but do not start yet, leave that to subclasses
        self._worker = createThread('CacheClient worker', self._worker_thread,
                                    start=False)

    def _getCache(self):
        return None

    def doShutdown(self):
        self._stoprequest = True
        self._worker.join()

    def _connect(self, socket=socket):
        self._do_callbacks = False
        self._startup_done.clear()
        self.log.debug('connecting to %s', self.cache)
        try:
            self._socket = tcpSocket(self.cache, DEFAULT_CACHE_PORT,
                                     timeout=5)
        except Exception as err:
            self._disconnect('unable to connect to %s: %s' %
                             (self.cache, err))
        else:
            self.log.info('now connected to %s', self.cache)
            self._connected = True
            self._disconnect_warnings = 0
            try:
                self._connect_action()
            except Exception as err:
                self._disconnect('unable to init connection to %s: %s' %
                                 (self.cache, err))
        self._startup_done.set()
        self._do_callbacks = self.remote_callbacks

    def _disconnect(self, why=''):
        self._connected = False
        self._startup_done.clear()
        if why:
            if self._disconnect_warnings % 10 == 0:
                self.log.warning(why)
            self._disconnect_warnings += 1
        if self._socket:
            closeSocket(self._socket)
            self._socket = None
        # close secondary socket
        with self._sec_lock:
            if self._secsocket:
                closeSocket(self._secsocket)
                self._secsocket = None
        self._disconnect_action()

    def _wait_retry(self):
        sleep(self._long_loop_delay)

    def _wait_data(self):
        pass

    def _connect_action(self):
        # send request for all keys and updates....
        # (send a single request for a nonexisting key afterwards to
        # determine the end of data)
        msg = '@%s%s\n%s%s\n' % (self._prefix, OP_WILDCARD, END_MARKER, OP_ASK)
        self._socket.sendall(to_utf8(msg))

        # read response
        data, n = b'', 0
        sentinel = to_utf8(END_MARKER + OP_TELLOLD + '\n')
        while not data.endswith(sentinel) and n < 1000:
            data += self._socket.recv(BUFSIZE)
            n += 1

        # send request for all updates
        msg = '@%s%s\n' % (self._prefix, OP_SUBSCRIBE)
        self._socket.sendall(to_utf8(msg))
        for prefix in self._prefixcallbacks:
            msg = '@%s%s\n' % (prefix, OP_SUBSCRIBE)
            self._socket.sendall(to_utf8(msg))

        self._process_data(data)

    def _disconnect_action(self):
        pass

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        raise NotImplementedError('implement _handle_msg in subclasses')

    def _process_data(self, data, sync_str=to_utf8(SYNC_MARKER + OP_TELLOLD),
                      lmatch=line_pattern.match, mmatch=msg_pattern.match):
        # n = 0
        i = 0  # avoid making a string copy for every line
        match = lmatch(data, i)
        while match:
            line = match.group(1)
            i = match.end()
            if sync_str in line:
                self.log.debug('process data: received sync: %r', line)
                self._synced = True
            else:
                msgmatch = mmatch(from_utf8(line))
                # ignore invalid lines
                if msgmatch:
                    # n += 1
                    try:
                        self._handle_msg(**msgmatch.groupdict())
                    except Exception:
                        self.log.exception('error handling message %r',
                                           msgmatch.group())
            # continue loop
            match = lmatch(data, i)
        # self.log.debug('processed %d items', n)
        return data[i:]

    def _worker_thread(self):
        while True:
            try:
                self._worker_inner()
            except Exception:
                self.log.exception('exception in cache worker thread; '
                                   'restarting (please report a bug)')
                if self._stoprequest:
                    break  # ensure we do not restart during shutdown
            else:
                # normal termination
                break

    def _worker_inner(self):
        data = b''
        range10 = range(10)
        process = self._process_data

        while not self._stoprequest:
            if self._should_connect:
                if not self._socket:
                    self._connect()
                    if not self._socket:
                        self._wait_retry()
                        continue
            else:
                if self._socket:
                    self._disconnect()
                self._wait_retry()
                continue

            # process data so far
            data = process(data)

            # wait for a whole line of data to arrive
            while b'\n' not in data and self._socket and self._should_connect \
                  and not self._stoprequest:

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
                    except EnvironmentError as e:
                        if e.errno == socket.EINTR:
                            continue
                        raise
                    except TypeError:
                        # socket was None, let the outer loop handle that
                        res = ([], [], [])
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
                    except queue.Empty:
                        pass
                    # write data
                    try:
                        self._socket.sendall(to_utf8(tosend))
                    except Exception:
                        self._disconnect('disconnect: send failed')
                        # report data as processed, but then re-queue it to send
                        # after reconnect
                        for _ in range(itemcount):
                            self._queue.task_done()
                        data = b''
                        self._queue.put(tosend)
                        break
                    for _ in range(itemcount):
                        self._queue.task_done()
                if res[0]:
                    # got some data
                    try:
                        newdata = self._socket.recv(BUFSIZE)
                    except Exception:
                        newdata = b''
                    if not newdata:
                        # no new data from blocking read -> abort
                        self._disconnect('disconnect: recv failed')
                        data = b''
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
            except queue.Empty:
                pass
            try:
                self._socket.sendall(to_utf8(tosend))
            except Exception:
                self.log.debug('exception while sending last batch of updates',
                               exc=1)
                # no reraise, we'll disconnect below anyways
            for _ in range(itemcount):
                self._queue.task_done()

        # end of while loop
        self._disconnect()

    def _single_request(self, tosend, sentinel=b'\n', retry=2, sync=False):
        """Communicate over the secondary socket."""
        if not self._socket:
            self._disconnect('single request: no socket')
            if not self._socket:
                raise CacheError('cache not connected')
        if sync:
            # sync has to be false for lock requests, as these occur during startup
            self._queue.join()
        with self._sec_lock:
            if not self._secsocket:
                try:
                    self._secsocket = tcpSocket(self.cache, DEFAULT_CACHE_PORT)
                except Exception as err:
                    self.log.warning('unable to connect secondary socket '
                                     'to %s: %s', self.cache, err)
                    self._secsocket = None
                    self._disconnect('secondary socket: could not connect')
                    raise CacheError('secondary socket could not be created')

            try:
                # write request
                # self.log.debug("get_explicit: sending %r", tosend)
                self._secsocket.sendall(to_utf8(tosend))

                # give 10 seconds time to get the whole reply
                timeout = currenttime() + 10
                # read response
                data = b''
                while not data.endswith(sentinel):
                    newdata = self._secsocket.recv(BUFSIZE)  # blocking read
                    if not newdata:
                        raise socket.error('cache closed connection')
                    if currenttime() > timeout:
                        # do not just break, we need to reopen the socket
                        raise socket.error('getting response took too long')
                    data += newdata
            except socket.error:
                self.log.warning('error during cache query', exc=1)
                closeSocket(self._secsocket)
                self._secsocket = None
                if retry:
                    for m in self._single_request(tosend, sentinel, retry - 1):
                        yield m
                    return
                raise

        lmatch = line_pattern.match
        mmatch = msg_pattern.match
        i = 0
        # self.log.debug("get_explicit: data =%r", data)
        match = lmatch(data, i)
        while match:
            line = match.group(1)
            i = match.end()
            msgmatch = mmatch(from_utf8(line))
            if not msgmatch:
                # ignore invalid lines
                continue
            # self.log.debug('line processed: %r', line)
            yield msgmatch
            match = lmatch(data, i)

    def waitForStartup(self, timeout):
        self._startup_done.wait(timeout)

    def flush(self):
        """wait for empty output queue"""
        self._synced = False
        self._queue.put('%s%s\n' % (SYNC_MARKER, OP_ASK))
        self._queue.join()
        for _ in range(100):
            # self.log.debug('flush; waiting for sync...')
            if self._synced:
                break
            sleep(CYCLETIME)

    def addPrefixCallback(self, prefix, function):
        """Add a "prefix" callback, which is called for every key and value
        that does not match the prefix parameter of the client, but matches
        the prefix given to this function.
        """
        if prefix not in self._prefixcallbacks:
            self._queue.put('@%s%s\n' % (prefix, OP_SUBSCRIBE))
        self._prefixcallbacks[prefix] = function

    def removePrefixCallback(self, prefix):
        """Remove a "prefix" callback.

        This removes the callback previously installed by addPrefixCallback.
        If prefix is unknown, then do nothing.
        """
        if prefix in self._prefixcallbacks:
            self._queue.put('@%s%s\n' % (prefix, OP_UNSUBSCRIBE))
            del self._prefixcallbacks[prefix]

    # methods to make this client usable as the main device in a simple session

    def start(self, *args):
        self._connect()
        self._worker.start()

    def wait(self):
        while not self._stoprequest:
            sleep(self._long_loop_delay)
        self._worker.join()

    def quit(self, signum=None):
        self.log.info('quitting on signal %s...', signum)
        self._stoprequest = True

    def lock(self, key, ttl=None, unlock=False, sessionid=None):
        """Locking/unlocking: opens a separate connection."""
        tosend = '%s%s%s%s%s\n' % (
            self._prefix, key.lower(), OP_LOCK,
            unlock and OP_LOCK_UNLOCK or OP_LOCK_LOCK,
            sessionid or session.sessionid)
        if ttl is not None:
            tosend = ('+%s@' % ttl) + tosend
        for msgmatch in self._single_request(tosend, sync=False):
            if msgmatch.group('value'):
                raise CacheLockError(msgmatch.group('value'))
            return
        # no response received; let's assume standalone mode
        self.log.warning('allowing lock/unlock operation without cache '
                         'connection')

    def unlock(self, key, sessionid=None):
        return self.lock(key, ttl=None, unlock=True, sessionid=sessionid)

    def storeSysInfo(self, service):
        """Store info about the service in the cache."""
        if not self._socket:
            return
        try:
            key, res = getSysInfo(service)
            msg = '%s@%s%s%s\n' % (currenttime(), key, OP_TELL,
                                   cache_dump(res))
            self._socket.sendall(to_utf8(msg))
        except Exception:
            self.log.exception('storing sysinfo failed')


class CacheClient(BaseCacheClient):

    temporary = True

    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        self._db = {}
        self._dblock = threading.Lock()
        self._callbacks = {}

        # the execution master lock needs to be refreshed every now and then
        self._ismaster = False
        self._master_expires = 0.
        self._mastertimeout = 5.

        self._worker.start()

    def doShutdown(self):
        BaseCacheClient.doShutdown(self)
        # make sure the interface is still usable but has no values to return
        with self._dblock:
            self._db.clear()
        self._startup_done.set()

    def is_connected(self):
        return self._connected

    def _connect_action(self):
        # clear the local database of possibly outdated values
        with self._dblock:
            self._db.clear()
        # get all current values from the cache
        BaseCacheClient._connect_action(self)
        # tell the server all our rewrites
        for newprefix, oldprefix in iteritems(self._inv_rewrites):
            self._queue.put(self._prefix + newprefix + OP_REWRITE +
                            self._prefix + oldprefix + '\n')

    def _wait_data(self):
        if self._ismaster:
            time = currenttime()
            if time > self._master_expires:
                self._master_expires = time + self._mastertimeout - 1
                try:
                    self.lock('master', self._mastertimeout)
                except Exception:
                    # ignore this, may be caused by the cache server being
                    # unavailable
                    pass
                else:
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
                    if value is not None:
                        value = cache_load(value)
                    time = time and float(time)
                    try:
                        self._prefixcallbacks[cb](key, value, time,
                                                  op != OP_TELL)
                    except Exception:
                        self.log.warning('error in cache callback', exc=1)
            return
        key = key[len(self._prefix):]
        time = time and float(time)
        self._propagate((time, key, op, value))
        # self.log.debug('got %s=%s', key, value)
        if not value or op == OP_TELLOLD:
            with self._dblock:
                self._db.pop(key, None)
        else:
            value = cache_load(value)
            with self._dblock:
                self._db[key] = (value, time)
            if self._do_callbacks:
                if key in self._callbacks:
                    self._call_callbacks(key, value, time)
                if key.endswith('/value') and session.data:
                    session.data.cacheCallback(key, value, time)

    def _call_callbacks(self, key, value, time):
        with self._dblock:
            # copy is intented here to avoid races with add/removeCallback
            callbacks = tuple(self._callbacks[key])
        for callback in callbacks:
            try:
                callback(key, value, time)
            except Exception:
                self.log.warning('error in cache callback', exc=1)

    def _propagate(self, args):
        pass

    def addCallback(self, dev, key, function):
        """Add a callback to be called when the given device/subkey value is
        updated. Multiple callbacks are called in the order of their registration.

        The callback is also called if the value is expired or deleted.
        """
        with self._dblock:  # {}.setdefault may not be threadsafe
            cbs = self._callbacks.setdefault(('%s/%s' % (dev, key)).lower(), [])
            cbs.append(function)  # this is supposed to be safe, but why bother?

    def removeCallback(self, dev, key, function):
        """Remove the given callback for the given device/subkey, if present."""
        with self._dblock:
            cbs = self._callbacks.get(('%s/%s' % (dev, key)).lower(), None)
            if cbs and function and function in cbs:
                cbs.remove(function)
                if not cbs:
                    # emty list: remove!
                    self._callbacks.pop(('%s/%s' % (dev, key)).lower(), None)

    def get(self, dev, key, default=None, mintime=None):
        """Get a value from the local cache for the given device and subkey.

        Since ``None`` can be a valid value for some cache entries, you can give
        another value that is returned if the value is missing or expired.  A
        singleton such as ``Ellipsis`` works well in these cases.
        """
        if not self._stoprequest and not self._startup_done.wait(15):
            self.log.warning('Cache _startup_done took more than 15s!')
            raise CacheError(self, 'Cache _startup_done took more than 15s!')
        dbkey = ('%s/%s' % (dev, key)).lower()
        with self._dblock:
            entry = self._db.get(dbkey)
        if entry is None:
            if self.is_connected():
                if str(dev).lower() in self._inv_rewrites:
                    self.log.debug('%s not in cache, trying rewritten', dbkey)
                    return self.get(self._inv_rewrites[str(dev).lower()],
                                    key, default, mintime)
                self.log.debug('%s not in cache', dbkey)
            else:
                self.log.debug('%s not in cache and no cache connection', dbkey)
            return default
        value, time = entry
        if mintime and time < mintime:
            try:
                if self.is_connected():
                    time, _ttl, value = self.get_explicit(dev, key, default)
                else:
                    return default
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
            if msgmatch.group('tsop') is None:
                raise CacheError('Cache did not send timestamp info')
            time, ttl, value = msgmatch.group('time'), msgmatch.group('ttl'), \
                msgmatch.group('value')
            # self.log.debug('get_explicit: %.2f %.2f %r', time, ttl, value)
            if value:
                return (time and float(time), ttl and float(ttl),
                        cache_load(value))
            return (time and float(time), ttl and float(ttl),
                    default)
        return (None, None, default)  # shouldn't happen

    def put(self, dev, key, value, time=None, ttl=None, flag=''):
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
        with self._dblock:
            self._db[dbkey] = (value, time)
        dvalue = cache_dump(value)
        msg = '%r%s@%s%s%s%s%s\n' % (time, ttlstr, self._prefix, dbkey,
                                     flag, OP_TELL, dvalue)
        # self.log.debug('putting %s=%s', dbkey, value)
        self._queue.put(msg)
        self._propagate((time, dbkey, OP_TELL, dvalue))
        if key == 'value' and session.data:
            session.data.cacheCallback(dbkey, value, time)
        # we have to check rewrites here, since the cache server won't send
        # us updates for a rewritten key if we sent the original key
        if str(dev).lower() in self._rewrites:
            for newprefix in self._rewrites[str(dev).lower()]:
                rdbkey = ('%s/%s' % (newprefix, key)).lower()
                with self._dblock:
                    self._db[rdbkey] = (value, time)
                self._propagate((time, rdbkey, OP_TELL, dvalue))
                if key == 'value' and session.data:
                    session.data.cacheCallback(rdbkey, value, time)

    def put_raw(self, key, value, time=None, ttl=None, flag=''):
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
        msg = '%r%s@%s%s%s%s\n' % (time, ttlstr, key, flag, OP_TELL, value)
        # self.log.debug('putting %s=%s', key, value)
        self._queue.put(msg)

    def setRewrite(self, newprefix, oldprefix):
        oldprefix = oldprefix.lower()
        newprefix = newprefix.lower()
        self._queue.put(self._prefix + newprefix + OP_REWRITE +
                        self._prefix + oldprefix + '\n')
        self._inv_rewrites[newprefix] = oldprefix
        self._rewrites.setdefault(oldprefix, set()).add(newprefix)

    def unsetRewrite(self, newprefix):
        newprefix = newprefix.lower()
        if newprefix in self._inv_rewrites:
            old = self._inv_rewrites[newprefix]
            self._rewrites[old].discard(newprefix)
            if not self._rewrites[old]:
                del self._rewrites[old]
            del self._inv_rewrites[newprefix]
            self._queue.put(self._prefix + newprefix + OP_REWRITE + '\n')

    def clear(self, dev, exclude=()):
        """Clear all cache subkeys belonging to the given device."""
        time = currenttime()
        devprefix = str(dev).lower() + '/'
        with self._dblock:
            for dbkey in list(self._db):
                if dbkey.startswith(devprefix):
                    if exclude and dbkey.rsplit('/', 1)[-1] in exclude:
                        continue
                    msg = '%r@%s%s%s\n' % (time, self._prefix, dbkey, OP_TELL)
                    self._db.pop(dbkey, None)
                    self._queue.put(msg)
                    self._propagate((time, dbkey, OP_TELL, ''))

    def clear_all(self):
        """Clear all cache keys."""
        time = currenttime()
        with self._dblock:
            for dbkey in list(self._db):
                msg = '%r@%s%s%s\n' % (time, self._prefix, dbkey, OP_TELL)
                self._db.pop(dbkey, None)
                self._queue.put(msg)
                self._propagate((time, dbkey, OP_TELL, ''))

    def invalidate(self, dev, key):
        """Locally invalidate device/subkey.  This does not touch the remote
        cache, but will trigger re-initializing short-lived things like device
        values and status from the hardware.
        """
        dbkey = ('%s/%s' % (dev, key)).lower()
        self.log.debug('invalidating %s', dbkey)
        with self._dblock:
            self._db.pop(dbkey, None)

    # pylint: disable=W0221
    def history(self, dev, key, fromtime, totime):
        """History query: opens a separate connection since it is otherwise not
        possible to determine which response lines belong to it.
        """
        if dev:
            key = ('%s/%s' % (dev, key)).lower()
        tosend = '%r-%r@%s%s%s\n###?\n' % (fromtime, totime,
                                           self._prefix, key, OP_ASK)
        ret = []
        for msgmatch in self._single_request(tosend, b'###!\n', sync=False):
            # process data
            time, value = msgmatch.group('time'), msgmatch.group('value')
            if time is None:
                break  # it's the '###' value
            if value:
                ret.append((float(time), cache_load(value)))
        return ret

    def query_db(self, query, tries=3):
        with self._dblock:
            if isinstance(query, string_types):
                return [(k, self._db[k][0]) for k in self._db if k.startswith(query)]
            else:
                query = set(query)
                return [(k, self._db[k][0]) for k in self._db if k in query]


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
        msg = '@%s%s\n###%s\n' % (self._prefix, OP_WILDCARD, OP_ASK)
        self._socket.sendall(to_utf8(msg))

        # read response
        data, n = b'', 0
        while not data.endswith(b'###!\n') and n < 1000:
            data += self._socket.recv(BUFSIZE)
            n += 1

        self._process_data(data)

        # stop immediately after reading data
        self._stoprequest = True

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if op not in (OP_TELL, OP_TELLOLD) or not key.startswith(self._prefix):
            return
        key = key[len(self._prefix):]
        if not value:
            self._db.pop(key, None)
        else:
            # even with TELLOLD; an old value is better than no value
            self._db[key] = cache_load(value)
