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

"""NICOS cache server.

Cache protocol documentation
============================

* The Cache server listens by default on TCP and UDP port 14869 (it will also
  receive UDP broadcasts).

* The protocol is line-based.  The basic syntax for a line (requests and
  responses) is ::

    [time1] [+|-] [time2] [@] key op [value] crlf

  The ``op`` is one character and decides the basic meaning of the request or
  response.

* Keys are hierarchic, with levels separated by an arbitrary number of slashes.

* All values are strings.  The cache server does not interpret them in any way,
  but the NICOS clients do.

Setting a key (op '=')
----------------------

- ``time1`` is the UNIX timestamp of the value.
- ``time2`` is the TTL (time to live) in seconds, after which the key expires.
- Both are optional: time1 defaults to current time, ttl to no expiration.
- Without any value, the key is deleted.

Examples::

  1327504784.71+5@nicos/temp/value=5.003     # explicit time and ttl given
  nicos/temp/setpoint=5                      # no time and ttl given
  +5@nicos/temp/value=1.102                  # only ttl given
  nicos/temp/value=                          # key deletion

Response: none.

Querying a single key (op '?')
------------------------------

- When an ``@`` is present, the timestamp is returned with the reply.
- With both ``time1-time2@``, a history query is made and several values can be
  returned.
- The value, if present, is ignored.

Examples::

  nicos/temp/value?                         # request only the value
  @nicos/temp/value?                        # request value with timestamp
  1327504780-1327504790@nicos/temp/value?   # request all values in time range

Response: except for history queries, a single line in the form ``key=value``
or ``time@key=value``, see below.  If the key is nonexistent or expired, the
form is ``[time@]key!`` or ``[time@]key!value``.  For history queries, a number
of lines of the same form.

Querying with wildcard (op '*')
-------------------------------

- Matching is done by a simple substring search: all keys for which the
  requested key is a substring are returned.
- History queries are not allowed.
- Like for op '?', timestamps are returned if ``@`` is present.
- The value, if present, is ignored.

Examples::

  nicos/temp/*                              # request only values
  @nicos/temp/*                             # request values with timestamps

Response: each value whose key contains the key given is returned as a single
line as for single query.

Subscribing to updates (op ':')
-------------------------------

- Matching is done by a simple substring search: the subscription is for all
  keys for which the requested key is a substring.
- When a @ is present, the updates contain the timestamp.

Response: none immediately, but every update matching the given key is sent to
the client, either as ``[time@]key=value`` or ``[time@]key!value`` (if the key
has expired).

Locking (op '$')
----------------

The lock mechanism allows only one client at the same time to obtain a lock on a
given identifier.  This can be used to synchronize access of multiple NICOS
clients to a shared resource (but is slow!).

- ``time1`` is the time when the lock is requested (default current time).
- ``time2`` is the ttl for the lock.  It defaults to 1800 seconds.
- ``key`` is the identifier for the lock.
- ``value`` must be either ``+clientid`` (lock) or ``-clientid`` (unlock);
  clientid is a string uniquely identifying the client.

Response:

- on lock: one of ::

    key$otherclientid      # already locked by other client, request denied
    key$                   # locked successfully

- on unlock: one of ::

    key$otherclientid      # not locked by this client, request denied
    key$                   # unlocked successfully
"""

from __future__ import with_statement

__version__ = "$Revision$"

import os
import Queue
import select
import socket
import threading
from os import path
from time import time as currenttime, sleep, localtime, mktime

from nicos import session
from nicos.core import Device, Param, ConfigurationError
from nicos.utils import loggers, closeSocket, ensureDirectory
from nicos.cache.utils import msg_pattern, line_pattern, DEFAULT_CACHE_PORT, \
     OP_TELL, OP_ASK, OP_WILDCARD, OP_SUBSCRIBE, OP_TELLOLD, OP_LOCK, Entry, \
     all_days


class CacheUDPConnection(object):
    """
    An UDP connection to use instead of a TCP connection in the CacheWorker.
    """

    def __init__(self, udpsocket, remoteaddr, log, maxsize=1496):
        self.remoteaddr = remoteaddr
        self.udpsocket = udpsocket
        self.maxsize = maxsize
        self.log = log

    def fileno(self):
        # provide a pseudo-fileno; the actual value doesn't matter as long as
        # this is negative
        return -self.udpsocket.fileno()

    def close(self):
        self.log('UDP: close')

    def shutdown(self, how):
        self.log('UDP: shutdown')

    def recv(self, maxbytes):
        # reading more is not supported
        self.log('UDP: recv')
        return ''

    def settimeout(self, timeout):
        self.udpsocket.settimeout(timeout)

    def sendall(self, data):
        datalen = len(data)
        # split data into chunks which are less than self.maxsize
        while data:
            # find rightmost \n within first self.maxsize bytes
            p = data[:self.maxsize].rfind('\n')
            # if not found, retry with \r
            if p == -1:
                p = data[:self.maxsize].rfind('\r')
            if p == -1:
                # line too long. cross your fingers and split SOMEWHERE
                p = self.maxsize - 1
            self.udpsocket.sendto(data[:p+1], self.remoteaddr)
            self.log('UDP: sent %d bytes' % (p+1))
            data = data[p+1:] # look at remaining data
        return datalen


class CacheUDPQueue(object):
    """Pseudo-queue for synchronous writes to UDP connections."""
    def __init__(self, conn):
        self.conn = conn

    def get(self):
        return None

    def put(self, msg):
        self.conn.sendall(msg)


class CacheWorker(object):
    """
    Worker thread class for the cache server.
    """

    def __init__(self, db, connection, name='', initstring='', initdata='',
                 loglevel=None):
        self.db = db
        self.connection = connection
        self.name = name
        # timeout for send (recv is covered by select timeout)
        self.connection.settimeout(5)
        # list of subscriptions
        self.updates_on = set()
        # list of subscriptions with timestamp requested
        self.ts_updates_on = set()
        self.stoprequest = False

        self.log = session.getLogger(name)
        self.log.setLevel(loggers.loglevels[loglevel])

        self.start_sender(name)

        if initstring:
            if not self.writeto(initstring):
                self.stoprequest = True
                return
        self.receiver = threading.Thread(None, self._worker_thread,
                                         'receiver %s' % name, args=(initdata,))
        self.receiver.setDaemon(True)
        self.receiver.start()

    def start_sender(self, name):
        self.send_queue = Queue.Queue()
        self.sender = threading.Thread(None, self._sender_thread,
                                       'sender %s' % name, args=())
        self.sender.setDaemon(True)
        self.sender.start()

    def __str__(self):
        return 'worker(%s)' % self.name

    def join(self):
        self.send_queue.put('end')   # to wake from blocking get()
        self.sender.join()
        self.receiver.join()

    def _sender_thread(self):
        while not self.stoprequest:
            self.writeto(self.send_queue.get())

    def _worker_thread(self, initdata):
        data = initdata
        while not self.stoprequest:
            # split data buffer into message lines and handle these
            match = line_pattern.match(data)
            while match:
                line = match.group(1)
                data = data[match.end():]
                if not line:
                    self.log.info('got empty line, closing connection')
                    self.closedown()
                    return
                try:
                    ret = self._handle_line(line)
                except Exception, err:
                    self.log.warning('error handling line %r' % line, exc=err)
                else:
                    #self.log.debug('return is %r' % ret)
                    if ret:
                        self.send_queue.put(''.join(ret))
                # continue loop with next match
                match = line_pattern.match(data)
            # fileno is < 0 for UDP connections, where select isn't needed
            if self.connection and self.connection.fileno() > 0:
                # wait for data with 1-second timeout
                res = select.select([self.connection], [], [self.connection], 1)
                if self.connection in res[2]:
                    # connection is in error state
                    break
                if self.connection not in res[0]:
                    # no data arrived, wait some more
                    continue
            try:
                newdata = self.connection.recv(8192)
            except Exception:
                newdata = ''
            if not newdata:
                # no data received from blocking read, break connection
                break
            data += newdata
        self.closedown()

    def _handle_line(self, line):
        self.log.debug('handling line: %s' % line)
        match = msg_pattern.match(line)
        if not match:
            # disconnect on trash lines (for now)
            if line:
                self.log.warning('garbled line: %r' % line)
            self.closedown()
            return
        # extract and clean up individual values
        time, ttl, tsop, key, op, value = match.groups()
        key = key.lower()
        value = value or None  # no value -> value gets deleted
        try:
            time = float(time)
        except (TypeError, ValueError):
            time = currenttime()
        try:
            ttl = float(ttl)
        except (TypeError, ValueError):
            ttl = None
        if tsop == '-' and ttl:
            ttl = ttl - time

        # dispatch operations
        if op == OP_TELL:
            self.db.tell(key, value, time, ttl, self)
        elif op == OP_ASK:
            if ttl:
                return self.db.ask_hist(key, time, time+ttl)
            else:
                # although passed, time and ttl are ignored here
                return self.db.ask(key, tsop, time, ttl)
        elif op == OP_WILDCARD:
            # time and ttl are currently ignored for wildcard requests
            return self.db.ask_wc(key, tsop, time, ttl)
        elif op == OP_SUBSCRIBE:
            # both time and ttl are ignored for subscription requests,
            # but the return format changes when the @ is included
            if tsop:
                self.ts_updates_on.add(key)
            else:
                self.updates_on.add(key)
        elif op == OP_TELLOLD:
            # the server shouldn't get TELLOLD
            pass
        elif op == OP_LOCK:
            return self.db.lock(key, value, time, ttl)

    def is_active(self):
        return not self.stoprequest and self.receiver.isAlive()

    def closedown(self):
        if not self.connection:
            return
        self.stoprequest = True
        closeSocket(self.connection)
        self.connection = None

    def writeto(self, data):
        if not self.connection:
            return False
        try:
            self.connection.sendall(data)
        except socket.timeout:
            self.log.warning(self, 'send timed out, shutting down')
            self.closedown()
        except Exception:
            # if we can't write (or it would be blocking), there is some serious
            # problem: forget writing and close down
            self.log.warning(self, 'other end closed, shutting down')
            self.closedown()
            return False
        return True

    def update(self, key, op, value, time, ttl):
        """Check if we need to send the update given."""
        if not self.connection:
            return False
        # make sure line has at least a default timestamp
        for mykey in self.ts_updates_on:
            # do a substring match on key
            if mykey in key:
                if not time:
                    time = currenttime()
                self.log.debug('sending update of %s to %s' % (key, value))
                if ttl is not None:
                    msg = '%s+%s@%s%s%s\r\n' % (time, ttl, key, op, value)
                else:
                    msg = '%s@%s%s%s\r\n' % (time, key, op, value)
                self.send_queue.put(msg)
        # same for requested updates without timestamp
        for mykey in self.updates_on:
            if mykey in key:
                self.log.debug('sending update of %s to %s' % (key, value))
                self.send_queue.put('%s%s%s\r\n' % (key, op, value))
        # no update neccessary, signal success
        return True


class CacheUDPWorker(CacheWorker):
    def start_sender(self, name):
        self.send_queue = CacheUDPQueue(self.connection)

    def join(self):
        self.receiver.join()


class CacheDatabase(Device):

    def doInit(self):
        if self.__class__ is CacheDatabase:
            raise ConfigurationError(
                'CacheDatabase is an abstract class, use '
                'either MemoryCacheDatabase or FlatfileCacheDatabase')
        self._lock_lock = threading.Lock()
        self._locks = {}

    def initDatabase(self):
        """Initialize the database from persistent store, if present."""
        pass

    def lock(self, key, value, time, ttl):
        """Lock handling code, common to both subclasses."""
        with self._lock_lock:
            entry = self._locks.get(key)
            # want to lock?
            req, client_id = value[0], value[1:]
            if req == '+':
                if entry and entry.value != client_id and \
                     (not entry.ttl or entry.time + entry.ttl >= currenttime()):
                    # still locked by different client, deny (tell the client
                    # the current client_id though)
                    self.log.debug('lock request %s=%s, but still locked by %s'
                                    % (key, client_id, entry.value))
                    return '%s%s%s\r\n' % (key, OP_LOCK, entry.value)
                else:
                    # not locked, expired or locked by same client, overwrite
                    ttl = ttl or 1800  # set a maximum time to live
                    self.log.debug('lock request %s=%s ttl %s, accepted' %
                                    (key, client_id, ttl))
                    self._locks[key] = Entry(time, ttl, client_id)
                    return '%s%s\r\n' % (key, OP_LOCK)
            # want to unlock?
            elif req == '-':
                if entry and entry.value != client_id:
                    # locked by different client, deny
                    self.log.debug('unlock request %s=%s, but locked by %s'
                                    % (key, client_id, entry.value))
                    return '%s%s%s\r\n' % (key, OP_LOCK, entry.value)
                else:
                    # unlocked or locked by same client, allow
                    self.log.debug('unlock request %s=%s, accepted'
                                    % (key, client_id))
                    self._locks.pop(key, None)
                    return '%s%s\r\n' % (key, OP_LOCK)


class MemoryCacheDatabase(CacheDatabase):
    """
    Central database of cache values, keeps everything in memory.
    """

    def doInit(self):
        self._db = {}
        self._db_lock = threading.Lock()
        CacheDatabase.doInit(self)

    def ask(self, key, ts, time, ttl):
        with self._db_lock:
            if key not in self._db:
                return [key + OP_TELLOLD + '\r\n']
            lastent = self._db[key][-1]
        # check for already removed keys
        if lastent.value is None:
            return [key + OP_TELLOLD + '\r\n']
        # check for expired keys
        if lastent.ttl:
            remaining = lastent.time + lastent.ttl - currenttime()
            op = remaining > 0 and OP_TELL or OP_TELLOLD
            if ts:
                return ['%s+%s@%s%s%s\r\n' % (lastent.time, lastent.ttl,
                                              key, op, lastent.value)]
            else:
                return [key + op + lastent.value]
        if ts:
            return ['%s@%s%s%s\r\n' % (lastent.time, key,
                                       OP_TELL, lastent.value)]
        else:
            return [key + OP_TELL + lastent.value + '\r\n']

    def ask_wc(self, key, ts, time, ttl):
        ret = set()
        with self._db_lock:
            # look for matching keys
            for dbkey, entries in self._db.iteritems():
                if key not in dbkey:
                    continue
                lastent = entries[-1]
                # check for removed keys
                if lastent.value is None:
                    continue
                # check for expired keys
                if lastent.ttl:
                    remaining = lastent.time + lastent.ttl - currenttime()
                    op = remaining > 0 and OP_TELL or OP_TELLOLD
                    if ts:
                        ret.add('%s+%s@%s%s%s\r\n' % (lastent.time, lastent.ttl,
                                                      dbkey, op, lastent.value))
                    else:
                        ret.add(dbkey + op + lastent.value + '\r\n')
                elif ts:
                    ret.add('%s@%s%s%s\r\n' % (lastent.time, dbkey,
                                               OP_TELL, lastent.value))
                else:
                    ret.add(dbkey + OP_TELL + lastent.value + '\r\n')
        return ret

    def ask_hist(self, key, fromtime, totime):
        return []

    def tell(self, key, value, time, ttl, from_client):
        if value is None:
            # deletes cannot have a TTL
            ttl = None
        send_update = True
        with self._db_lock:
            entries = self._db.setdefault(key, [])
            if entries:
                lastent = entries[-1]
                if lastent.value == value and not lastent.ttl:
                    # not a real update
                    send_update = False
            # never cache more than a single entry, memory fills up too fast
            entries[:] = [Entry(time, ttl, value)]
        if send_update:
            for client in self._server._connected.values():
                if client is not from_client and client.is_active():
                    client.update(key, OP_TELL, value, time, ttl)


class FlatfileCacheDatabase(CacheDatabase):
    """Cache database which writes historical values to disk in a flatfile
    (ASCII) format.

    The store format is the following:

    * Each cache key is separated at the last slash.  The part before the slash
      is called "category" (usually prefix + a device name).
    * For each category, there is a subdirectory (with slashes in the category
      name replaced by dashes) in the store path.  This contains subdirectories
      for every year, and these subdirectories contain one file per day, in the
      format "MM-DD".
    * These files are also hardlinked at another hierarchy, starting with year
      and day subdirectories, where the files are named by category.

    For example, the cache entries for category "nicos/slit" at 2012-01-05 are
    available in the files ``nicos-slit/2012/01-05`` and
    ``2012/01-05/nicos-slit``.

    The format of these files is a simple three-column tab-separated ascii
    format: the first column is the last part of the cache key (which combined
    with the category gives the full key); the second column is the Unix
    timestamp of the change, and the third column is the actual value.

    All values should be valid Python literals, but this is not enforced by the
    cache server, rather by the NICOS clients.  The value can also a single
    dash, this indicates that at the given timestamp the latest value for this
    key expired.
    """

    parameters = {
        'storepath': Param('Directory where history stores should be saved',
                           type=str, mandatory=True),
    }

    def doInit(self):
        self._cat = {}
        self._cat_lock = threading.Lock()
        CacheDatabase.doInit(self)

        self._basepath = path.join(session.config.control_path, self.storepath)
        ltime = localtime()
        self._year = str(ltime[0])
        self._currday = '%02d-%02d' % ltime[1:3]
        self._midnight = mktime(ltime[:3] + (0,) * (8-3) + (ltime[8],))
        self._nextmidnight = self._midnight + 86400

        self._stoprequest = False
        self._cleaner = threading.Thread(target=self._clean)
        self._cleaner.setDaemon(True)
        self._cleaner.start()

    def doShutdown(self):
        self._stoprequest = True

    def initDatabase(self):
        # read the last entry for each key from disk
        nkeys = 0
        with self._cat_lock:
            curdir = path.join(self._basepath, self._year, self._currday)
            if not path.isdir(curdir):
                return
            for fn in os.listdir(curdir):
                cat = fn.replace('-', '/')
                fd = open(path.join(curdir, fn), 'r+U')
                db = {}
                for line in fd:
                    subkey, time, value = line.rstrip().split(None, 2)
                    if value != '-':
                        db[subkey] = Entry(float(time), None, value)
                    elif subkey in db:
                        db[subkey].expired = True
                lock = threading.Lock()
                self._cat[cat] = [fd, lock, db]
                nkeys += len(db)
        self.log.info('loaded %d keys from files' % nkeys)

    def _rollover(self):
        self.log.debug('ROLLOVER started')
        ltime = localtime()
        # set the days and midnight time correctly
        #prevday = self._currday
        self._currday = '%02d-%02d' % ltime[1:3]
        self._midnight = mktime(ltime[:3] + (0,) * (8-3) + (ltime[8],))
        self._nextmidnight = self._midnight + 86400
        # roll over all file descriptors
        for category, (fd, _, db) in self._cat.iteritems():
            fd.close()
            fd = self._cat[category][0] = self._create_fd(category)
            for subkey, entry in db.iteritems():
                if entry.value:
                    fd.write('%s\t%s\t%s\n' %
                             (subkey, self._midnight, entry.value))
            fd.flush()
        # XXX start compress action of old files here

    def _create_fd(self, category):
        """Open the by-date output file for the current day for a given
        category, and create the by-category hard link if necessary.
        """
        category = category.replace('/', '-')
        bydate = path.join(self._basepath, self._year, self._currday)
        ensureDirectory(bydate)
        filename = path.join(bydate, category)
        fd = open(filename, 'a+')
        bycat = path.join(self._basepath, category, self._year)
        ensureDirectory(bycat)
        linkname = path.join(bycat, self._currday)
        if not path.isfile(linkname):
            os.link(filename, linkname)
        return fd

    def ask(self, key, ts, time, ttl):
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key
        with self._cat_lock:
            if category not in self._cat:
                return [key + OP_TELLOLD + '\r\n']
            _, lock, db = self._cat[category]
        with lock:
            if subkey not in db:
                return [key + OP_TELLOLD + '\r\n']
            entry = db[subkey]
        # check for expired keys
        if entry.value is None:
            return [key + OP_TELLOLD + '\r\n']
        # check for expired keys
        if entry.ttl:
            op = entry.expired and OP_TELLOLD or OP_TELL
            if ts:
                return ['%s+%s@%s%s%s\r\n' % (entry.time, entry.ttl,
                                              key, op, entry.value)]
            else:
                return [key + op + entry.value + '\r\n']
        if ts:
            return ['%s@%s%s%s\r\n' % (entry.time, key,
                                       OP_TELL, entry.value)]
        else:
            return [key + OP_TELL + entry.value + '\r\n']

    def ask_wc(self, key, ts, time, ttl):
        ret = set()
        # look for matching keys
        for cat, (_, lock, db) in self._cat.items():
            prefix = cat + '/' if cat != 'nocat' else ''
            with lock:
                for subkey, entry in db.iteritems():
                    if key not in prefix+subkey:
                        continue
                    # check for removed keys
                    if entry.value is None:
                        continue
                    # check for expired keys
                    if entry.ttl:
                        op = entry.expired and OP_TELLOLD or OP_TELL
                        if ts:
                            ret.add('%s+%s@%s%s%s\r\n' %
                                    (entry.time, entry.ttl, prefix+subkey,
                                     op, entry.value))
                        else:
                            ret.add(prefix+subkey + op + entry.value + '\r\n')
                    elif ts:
                        ret.add('%s@%s%s%s\r\n' % (entry.time, prefix+subkey,
                                                   OP_TELL, entry.value))
                    else:
                        ret.add(prefix+subkey + OP_TELL + entry.value + '\r\n')
        return ret

    def ask_hist(self, key, fromtime, totime):
        try:
            category, subkey = key.rsplit('/', 1)
            category = category.replace('/', '-')
        except ValueError:
            category = 'nocat'
            subkey = key
        if fromtime > totime:
            return []
        elif fromtime >= self._midnight:
            days = [(self._year, self._currday)]
        else:
            days = all_days(fromtime, totime)
        ret = []
        try:
            for year, monthday in days:
                fn = path.join(self._basepath, year, monthday, category)
                if not path.isfile(fn):
                    continue
                with open(fn, 'U') as fd:
                    for line in fd:
                        fsubkey, time, value = line.rstrip().split(None, 2)
                        if fsubkey == subkey:
                            time = float(time)
                            if value == '-':
                                value = ''
                            if fromtime <= time <= totime:
                                ret.append('%s@%s=%s\r\n' % (time, key, value))
        except Exception:
            self.log.exception('error reading store files for history query')
        return ret

    def _clean(self):
        while not self._stoprequest:
            sleep(0.5)
            with self._cat_lock:
                for cat, (fd, lock, db) in self._cat.iteritems():
                    with lock:
                        for subkey, entry in db.iteritems():
                            if not entry.value or entry.expired:
                                continue
                            time = currenttime()
                            if entry.ttl and entry.time + entry.ttl < time:
                                entry.expired = True
                                for client in self._server._connected.values():
                                    client.update(cat + '/' + subkey,
                                                  OP_TELLOLD, entry.value,
                                                  time, None)
                                fd.write('%s\t%s\t-\n' % (subkey, time))
                                fd.flush()

    def tell(self, key, value, time, ttl, from_client, fdupdate=True):
        if value is None:
            # deletes cannot have a TTL
            ttl = None
        if time is None:
            time = currenttime()
        with self._cat_lock:
            if currenttime() > self._nextmidnight:
                self._rollover()
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key
        with self._cat_lock:
            if category not in self._cat:
                self._cat[category] = [self._create_fd(category),
                                       threading.Lock(), {}]
            fd, lock, db = self._cat[category]
        update = True
        with lock:
            if subkey in db:
                entry = db[subkey]
                if entry.value == value and not entry.expired:
                    # existing entry with the same value: update the TTL
                    # but don't write an update to the history file
                    entry.time = time
                    entry.ttl = ttl
                    update = False
            if update:
                db[subkey] = Entry(time, ttl, value)
                fd.write('%s\t%s\t%s\n' % (subkey, time, value or '-'))
                fd.flush()
        if update:
            for client in self._server._connected.values():
                if client is not from_client:
                    client.update(key, OP_TELL, value, time, None)


class CacheServer(Device):
    """
    The server class.
    """

    parameters = {
        'server':   Param('Address to bind to (host or host:port)', type=str,
                          mandatory=True),
    }

    attached_devices = {
        'db': (CacheDatabase, 'The cache database instance'),
    }

    def doInit(self):
        self._stoprequest = False
        self._boundto = None
        self._serversocket = None
        self._serversocket_udp = None
        self._connected = {}  # worker connections
        self._adevs['db']._server = self

    def start(self):
        self._adevs['db'].initDatabase()
        self._worker = threading.Thread(target=self._worker_thread)
        self._worker.start()

    def _worker_thread(self):
        self.log.info('server starting')

        def bind_to(address, proto='tcp'):
            if ':' not in address:
                host = address
                port = DEFAULT_CACHE_PORT
            else:
                host, port = address.split(':')
                port = int(port)
            serversocket = socket.socket(socket.AF_INET,
                proto == 'tcp' and socket.SOCK_STREAM or socket.SOCK_DGRAM)
            serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if proto == 'udp':
                # we want to be able to receive UDP broadcasts
                serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            try:
                serversocket.bind((socket.gethostbyname(host), port))
                if proto == 'tcp':
                    serversocket.listen(50) # max waiting connections....
                return serversocket
            except Exception:
                serversocket.close()
                return None             # failed, return None as indicator

        # now try to bind to one, include 'MUST WORK' standalone names
        for server in [self.server, socket.getfqdn(), socket.gethostname()]:
            self.log.debug('trying to bind to ' + server)
            self._serversocket = bind_to(server)
            if self._serversocket:
                self._boundto = server
                break             # we had success: exit this loop

        # bind UDP broadcast socket
        self._serversocket_udp = bind_to('', 'udp')
        if self._serversocket_udp:
            self.log.info('udp-bound to broadcast')

        if not self._serversocket and not self._serversocket_udp:
            self._stoprequest = True
            self.log.error("couldn't bind to any location, giving up!")
            return

        if not self._boundto:
            self.log.warning('starting main-loop only bound to UDP broadcast')
        else:
            self.log.info('starting main-loop bound to %s' % self._boundto)
        # now enter main serving loop
        while not self._stoprequest:
            # loop through connections, first to remove dead ones,
            # secondly to try to reconnect
            for addr, client in self._connected.items():
                if client:
                    if not client.is_active(): # dead or stopped
                        self.log.info('client connection %s closed' % addr)
                        client.closedown()
                        client.join()  # wait for threads to end
                        del self._connected[addr]

            # now check for additional incoming connections
            # build list of things to check
            selectlist = []
            if self._serversocket:
                selectlist.append(self._serversocket)
            if self._serversocket_udp:
                selectlist.append(self._serversocket_udp)

            res = select.select(selectlist, [], [], 1)  # timeout 1 second
            if not res[0]:
                continue  # nothing to read -> continue loop
            # TODO: check address for tcp and udp, currently all are allowed....
            if self._serversocket in res[0] and not self._stoprequest:
                # TCP connection came in
                conn, addr = self._serversocket.accept()
                addr = 'tcp://%s:%d' % addr
                self.log.info('new connection from %s' % addr)
                self._connected[addr] = CacheWorker(
                    self._adevs['db'], conn, name=addr, loglevel=self.loglevel)
            elif self._serversocket_udp in res[0] and not self._stoprequest:
                # UDP data came in
                data, addr = self._serversocket_udp.recvfrom(3072)
                nice_addr = 'udp://%s:%d' % addr
                self.log.info('new connection from %s' % nice_addr)
                conn = CacheUDPConnection(self._serversocket_udp, addr,
                                          log=self.log.debug)
                self._connected[nice_addr] = CacheUDPWorker(
                    self._adevs['db'], conn, name=nice_addr, initdata=data,
                    loglevel=self.loglevel)
        if self._serversocket:
            closeSocket(self._serversocket)
        self._serversocket = None

    def wait(self):
        while not self._stoprequest:
            sleep(1)
        self._worker.join()

    def quit(self):
        self.log.info('quitting...')
        self._stoprequest = True
        for client in self._connected.values():
            self.log.info('closing client %s' % client)
            if client.is_active():
                client.closedown()
        for client in self._connected.values():
            self.log.info('waiting for %s' % client)
            client.join()
        self.log.info('waiting for server')
        self._worker.join()
        self.log.info('server finished')
