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

"""NICOS cache server."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import bsddb
import Queue
import select
import socket
import threading
from os import path
from itertools import chain
from time import time as currenttime, sleep, localtime, mktime

from nicos import session, loggers
from nicos.utils import existingdir, intrange, closeSocket, ensureDirectory
from nicos.device import Device, Param
from nicos.errors import ConfigurationError
from nicos.cache.utils import msg_pattern, line_pattern, DEFAULT_CACHE_PORT, \
     OP_TELL, OP_ASK, OP_WILDCARD, OP_SUBSCRIBE, OP_TELLOLD, OP_LOCK, Entry, \
     dump_entries, load_entries, load_last_entry


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

        self.send_queue = Queue.Queue()

        if initstring:
            if not self.writeto(initstring):
                self.stoprequest = True
                return
        self.receiver = threading.Thread(None, self._worker_thread,
                                         'receiver %s' % name, args=(initdata,))
        self.receiver.setDaemon(True)
        self.receiver.start()
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
                    raise
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
        value = value or None
        try:
            time = float(time)
        except:
            time = currenttime()
        try:
            ttl = float(ttl)
        except:
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
                return self.db.ask(key, tsop, time, ttl)
        elif op == OP_WILDCARD:
            # both time and ttl are ignored for subscription requests,
            # but the return format changes when the @ is included
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


class CacheDatabase(Device):

    def doInit(self):
        raise ConfigurationError(
            'CacheDatabase is an abstract class, use '
            'either MemoryCacheDatabase or DbCacheDatabase')

    def initDatabase(self):
        """Initialize the database from persistent store, if present."""
        pass


class MemoryCacheDatabase(CacheDatabase):
    """
    Central database of cache values, keeps everything in memory.
    """

    def doInit(self):
        self._db = {}
        self._db_lock = threading.Lock()
        self._locks = {}
        self._lock_lock = threading.Lock()

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

    def lock(self, key, value, time, ttl):
        with self._lock_lock:
            entry = self._locks.get(key)
            # want to lock?
            req, client_id = value[0], value[1:]
            if req == '+':
                if entry and entry.value != client_id and \
                     (not entry.ttl or entry.time + entry.ttl >= currenttime()):
                    # still locked by different client, deny (tell the client
                    # the current client_id though)
                    self.printdebug('lock request %s=%s, but still locked by %s'
                                    % (key, client_id, entry.value))
                    return '%s%s%s\r\n' % (key, OP_LOCK, entry.value)
                else:
                    # not locked, expired or locked by same client, overwrite
                    ttl = ttl or 1800  # set a maximum time to live
                    self.printdebug('lock request %s=%s ttl %s, accepted' %
                                    (key, client_id, ttl))
                    self._locks[key] = Entry(time, ttl, client_id)
                    return '%s%s\r\n' % (key, OP_LOCK)
            # want to unlock?
            elif req == '-':
                if entry and entry.value != client_id:
                    # locked by different client, deny
                    self.printdebug('unlock request %s=%s, but locked by %s'
                                    % (key, client_id, entry.value))
                    return '%s%s%s\r\n' % (key, OP_LOCK, entry.value)
                else:
                    # unlocked or locked by same client, allow
                    self.printdebug('unlock request %s=%s, accepted'
                                    % (key, client_id))
                    self._locks.pop(key, None)
                    return '%s%s\r\n' % (key, OP_LOCK)


class DbCacheDatabase(MemoryCacheDatabase):
    """Cache database that keeps history in bsddb stores."""

    parameters = {
        'storepath': Param('Directory where history stores should be saved',
                           type=existingdir, mandatory=True),
        'maxcached': Param('Maximum number of entries cached in memory',
                           type=int, default=1000),
    }

    def doInit(self):
        MemoryCacheDatabase.doInit(self)
        # stores timestamp of the last archived entry for all keys
        self._arctime = {}
        # maps (y, m, d) tuples to bsddb stores
        self._stores = {}
        self._max = self.maxcached
        self._storefmt = '%04d-%02d-%02d'
        # keep open two stores: this day's, and the previous day's
        time = currenttime()
        self._currday = localtime(time)[:3]
        self._prevday = localtime(time - 86400)[:3]
        self._midnight = mktime(self._currday + (0,) * 6)
        self._nextmidnight = self._midnight + 86400
        self._store_lock = threading.Lock()
        with self._store_lock:
            self._currstore = self._open_store(self._currday)
            self._prevstore = self._open_store(self._prevday)

    def initDatabase(self):
        # read the last entry for each key from disk
        nkeys = 0
        with self._db_lock:
            with self._store_lock:
                for key in self._currstore:
                    entry = load_last_entry(self._currstore[key])
                    if entry:
                        self._db[key] = [entry]
                        self._arctime[key] = entry.time
                        nkeys += 1
        self.printinfo('loaded %d keys from store' % nkeys)

    def doShutdown(self):
        # write remaining unarchived entries to disk
        nentries = 0
        with self._db_lock:
            with self._store_lock:
                for key, entries in self._db.iteritems():
                    self._archive(key, entries, sync=False)
                    nentries += len(entries)
        self.printinfo('archived %d entries on shutdown' % nentries)
        with self._store_lock:
            self._prevstore.sync()
            self._close_store(self._prevday)
            self._currstore.sync()
            self._close_store(self._currday)

    def _open_store(self, ymd):
        if ymd in self._stores:
            self._stores[ymd][1] += 1
            self.printdebug('incremented use count for store %s' % (ymd,))
            return self._stores[ymd][0]
        path = os.path.join(session.config.control_path,
                            self.storepath, self._storefmt % ymd)
        try:
            db = bsddb.hashopen(path, 'c')
        except bsddb.db.DBError, err:
            raise ConfigurationError(self, 'Error opening database store %r: %s'
                                     % (path, err.args[1]))
        self.printdebug('opened new store for %s' % (ymd,))
        self._stores[ymd] = [db, 1]
        return db

    def _close_store(self, ymd):
        info = self._stores[ymd]
        info[1] -= 1
        self.printdebug('decremented use count for store %s' % (ymd,))
        if info[1] == 0:
            db = self._stores.pop(ymd)[0]
            db.sync()
            db.close()
            self.printdebug('closed store for %s' % (ymd,))

    def _archive(self, key, entries, sync=True):
        """Archive entries to the store(s).  Must be called with the store
        lock held.
        """
        # midnight is past: change stores
        if currenttime() > self._nextmidnight:
            newday = localtime()[:3]
            # close previous day's store
            self._close_store(self._prevday)
            # this day's store is now previous day's
            self._prevstore = self._currstore
            self._currstore = self._open_store(newday)
            # set the days and midnight time correctly
            self._prevday = self._currday
            self._currday = newday
            self._midnight = mktime(self._currday + (0,) * 6)
            self._nextmidnight = self._midnight + 86400
        # divide the entries in two lists: those belonging to the previous
        # day, and those for the current day
        prev, curr = [], []
        midnight = self._midnight
        arctime = self._arctime.get(key, 0)
        for entry in entries:
            if entry.time <= arctime:
                continue
            elif entry.time < midnight:
                prev.append(entry)
            else:
                curr.append(entry)
        # dump them into their respective stores
        if prev:
            self._prevstore[key] = \
                self._prevstore.get(key, '') + dump_entries(prev)
            if sync:
                self._prevstore.sync()
        self._currstore[key] = \
            self._currstore.get(key, '') + dump_entries(curr)
        if sync:
            self._currstore.sync()
        self._arctime[key] = entries[-1].time
        self.printdebug('archived %d+%d entries for key %s' %
                        (len(prev), len(curr), key))

    # ask and ask_wc inherited from MemoryCacheDatabase

    def ask_hist(self, key, t1, t2):
        ret = []
        with self._db_lock:
            if key not in self._db:
                return []
            entries = self._db[key]
        # need to check in database files?
        store_entries = []
        if t1 < entries[0].time:
            # XXX currently this does not open additional stores to fulfill the
            # whole given time range
            with self._store_lock:
                store_entries = load_entries(self._prevstore.get(key, '')) + \
                                load_entries(self._currstore.get(key, ''))
                self.printdebug('history query loaded %d entries from store' %
                                len(store_entries))
        for entry in chain(store_entries, entries):
            if t1 <= entry.time < t2:
                if entry.ttl:
                    ret.append('%s+%s@%s%s%s\r\n' %
                               (entry.time, entry.ttl, key,
                                OP_TELLOLD, entry.value))
                else:
                    ret.append('%s@%s%s%s\r\n' % (entry.time, key,
                                                  OP_TELLOLD, entry.value))
        return ret

    def tell(self, key, value, time, ttl, from_client):
        if value is None:
            # deletes cannot have a TTL
            ttl = None
        send_update = True
        with self._db_lock:
            entries = self._db.setdefault(key, [])
            if entries:
                lastent = entries[-1]
                if lastent.value == value:
                    # special handling of constant values to avoid amassing
                    # lots of duplicate entries
                    if not lastent.ttl:
                        if not ttl:
                            # not a real update
                            send_update = False
                        else:
                            # had no ttl, but has one now -> new entry
                            entries.append(Entry(time, ttl, value))
                    else:
                        if not ttl:
                            # had ttl, but has none now -> new entry
                            entries.append(Entry(time, ttl, value))
                        elif lastent.time + lastent.ttl > currenttime() and \
                                 lastent.ttl < 120:
                            # update of nonexpired value, just update the ttl
                            # (but only for maximum 2 minutes)
                            lastent.ttl = (time - lastent.time) + ttl
                        else:
                            # old value already expired -> new entry
                            entries.append(Entry(time, ttl, value))
                else:
                    entries.append(Entry(time, ttl, value))
            else:
                entries.append(Entry(time, ttl, value))
            #self.printdebug('entries are now ' + str(entries))
            if len(entries) > self._max or ttl is None:
                # if ttl is None, the value should be stored immediately
                with self._store_lock:
                    if ttl is None:
                        self._archive(key, entries)
                    else:
                        # if last value has TTL, it can be updated still,
                        # so don't write it to the archive yet
                        self._archive(key, entries[:-1])
                    del entries[:-1]
                #self.printdebug('after archiving: ' + str(entries))
        if send_update:
            for client in self._server._connected.values():
                if client is not from_client and client.is_active():
                    client.update(key, OP_TELL, value, time, ttl)


################################################################################

class NewDatabase(CacheDatabase):

    parameters = {
        'storepath': Param('Directory where history stores should be saved',
                           type=existingdir, mandatory=True),
        'maxcached': Param('Maximum number of entries cached in memory',
                           type=int, default=1000),
    }

    def doInit(self):
        self._nt = 3
        self._ntm = {3:86400, 4:3600, 5:60}
        self._cat = {}
        self._cat_lock = threading.Lock()
        self._locks = {}
        self._lock_lock = threading.Lock()
        self._max = self.maxcached

        self._basepath = path.join(session.config.control_path, self.storepath)
        ltime = localtime()
        self._year = str(ltime[0])
        self._currday = '-'.join(['%02d']*(self._nt-1)) % ltime[1:self._nt]
        self._midnight = mktime(ltime[:self._nt] + (0,) * (8-self._nt) + (ltime[8],))
        self._nextmidnight = self._midnight + self._ntm[self._nt]

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
                    db[subkey] = [Entry(float(time), None, value)]
                lock = threading.Lock()
                self._cat[cat] = (fd, lock, db)
                nkeys += len(db)
        self.printinfo('loaded %d keys from files' % nkeys)

    def lock(self, key, value, time, ttl):
        with self._lock_lock:
            entry = self._locks.get(key)
            # want to lock?
            req, client_id = value[0], value[1:]
            if req == '+':
                if entry and entry.value != client_id and \
                     (not entry.ttl or entry.time + entry.ttl >= currenttime()):
                    # still locked by different client, deny (tell the client
                    # the current client_id though)
                    self.printdebug('lock request %s=%s, but still locked by %s'
                                    % (key, client_id, entry.value))
                    return '%s%s%s\r\n' % (key, OP_LOCK, entry.value)
                else:
                    # not locked, expired or locked by same client, overwrite
                    ttl = ttl or 1800  # set a maximum time to live
                    self.printdebug('lock request %s=%s ttl %s, accepted' %
                                    (key, client_id, ttl))
                    self._locks[key] = Entry(time, ttl, client_id)
                    return '%s%s\r\n' % (key, OP_LOCK)
            # want to unlock?
            elif req == '-':
                if entry and entry.value != client_id:
                    # locked by different client, deny
                    self.printdebug('unlock request %s=%s, but locked by %s'
                                    % (key, client_id, entry.value))
                    return '%s%s%s\r\n' % (key, OP_LOCK, entry.value)
                else:
                    # unlocked or locked by same client, allow
                    self.printdebug('unlock request %s=%s, accepted'
                                    % (key, client_id))
                    self._locks.pop(key, None)
                    return '%s%s\r\n' % (key, OP_LOCK)

    def _rollover(self):
        self.printdebug('ROLLOVER started')
        ltime = localtime()
        # set the days and midnight time correctly
        #prevday = self._currday
        self._currday = '-'.join(['%02d']*(self._nt-1)) % ltime[1:self._nt]
        self._midnight = mktime(ltime[:self._nt] + (0,) * (8-self._nt) + (ltime[8],))
        self._nextmidnight = self._midnight + self._ntm[self._nt]
        # roll over all file descriptors
        for category, (fd, lock, db) in self._cat.iteritems():
            fd.close()
            fd = self._cat[category][0] = self._create_fd(category)
            for subkey, entries in db.iteritems():
                if entries and entries[-1].value:
                    fd.write('%s\t%s\t%s\n' %
                             (subkey, self._midnight, entries[-1].value))
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
        fd = open(filename, 'a+U')
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
            fd, lock, db = self._cat[category]
        with lock:
            if subkey not in db:
                return [key + OP_TELLOLD + '\r\n']
            lastent = db[subkey][-1]
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
                return [key + op + lastent.value + '\r\n']
        if ts:
            return ['%s@%s%s%s\r\n' % (lastent.time, key,
                                       OP_TELL, lastent.value)]
        else:
            return [key + OP_TELL + lastent.value + '\r\n']

    def ask_wc(self, key, ts, time, ttl):
        ret = set()
        # look for matching keys
        for cat, (fd, lock, db) in self._cat.items():
            prefix = cat + '/'
            with lock:
                for subkey, entries in db.iteritems():
                    if key not in prefix+subkey:
                        continue
                    if not entries:
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
                            ret.add('%s+%s@%s%s%s\r\n' %
                                    (lastent.time, lastent.ttl, prefix+subkey,
                                     op, lastent.value))
                        else:
                            ret.add(prefix+subkey + op + lastent.value + '\r\n')
                    elif ts:
                        ret.add('%s@%s%s%s\r\n' % (lastent.time, prefix+subkey,
                                                   OP_TELL, lastent.value))
                    else:
                        ret.add(prefix+subkey + OP_TELL + lastent.value + '\r\n')
        return ret

    def _clean(self):
        while not self._stoprequest:
            sleep(0.5)
            with self._cat_lock:
                for cat, (fd, lock, db) in self._cat.iteritems():
                    with lock:
                        for subkey, entries in db.iteritems():
                            if not entries:
                                continue
                            lastent = entries[-1]
                            time = currenttime()
                            if lastent.value and lastent.ttl and \
                                   lastent.time + lastent.ttl < time:
                                entries.append(Entry(None, currenttime(), None))
                                for client in self._server._connected.values():
                                    client.update(cat + '/' + subkey,
                                                  OP_TELLOLD, '', time, None)
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
                                       threading.Lock(),
                                       {}]
            fd, lock, db = self._cat[category]
        update = True
        with lock:
            entries = db.setdefault(subkey, [])
            if entries:
                lastent = entries[-1]
                if lastent.value == value:
                    # existing entry with the same value: update the TTL
                    # but don't write an update to the history file
                    lastent.time = time
                    lastent.ttl = ttl
                    update = False
            if update:
                entries.append(Entry(time, ttl, value))
                fd.write('%s\t%s\t%s\n' % (subkey, time, value or '-'))
                fd.flush()
            if len(entries) > self._max:
                del entries[:-self._max/2]
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
        'db': CacheDatabase,
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
        self.printinfo('server starting')

        def bind_to(address, type='tcp'):
            if ':' not in address:
                host = address
                port = DEFAULT_CACHE_PORT
            else:
                host, port = address.split(':')
                port = int(port)
            serversocket = socket.socket(socket.AF_INET,
                type == 'tcp' and socket.SOCK_STREAM or socket.SOCK_DGRAM)
            serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if type == 'udp':
                # we want to be able to receive UDP broadcasts
                serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            try:
                serversocket.bind((socket.gethostbyname(host), port))
                if type == 'tcp':
                    serversocket.listen(50) # max waiting connections....
                return serversocket
            except Exception:
                serversocket.close()
                return None             # failed, return None as indicator

        # now try to bind to one, include 'MUST WORK' standalone names
        for server in [self.server, socket.getfqdn(), socket.gethostname()]:
            self.printdebug('trying to bind to ' + server)
            self._serversocket = bind_to(server)
            if self._serversocket:
                self._boundto = server
                break             # we had success: exit this loop

        # bind UDP broadcast socket
        self._serversocket_udp = bind_to('', 'udp')
        if self._serversocket_udp:
            self.printinfo('udp-bound to broadcast')

        if not self._serversocket and not self._serversocket_udp:
            self._stoprequest = True
            self.printerror("couldn't bind to any location, giving up!")
            return

        if not self._boundto:
            self.printwarning('starting main-loop only bound to UDP broadcast')
        else:
            self.printinfo('starting main-loop bound to %s' % self._boundto)
        # now enter main serving loop
        while not self._stoprequest:
            # loop through connections, first to remove dead ones,
            # secondly to try to reconnect
            for addr, client in self._connected.items():
                if client:
                    if not client.is_active(): # dead or stopped
                        self.printinfo('client connection %s closed' % addr)
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
                self.printinfo('new connection from %s' % addr)
                self._connected[addr] = CacheWorker(
                    self._adevs['db'], conn, name=addr, loglevel=self.loglevel)
            elif self._serversocket_udp in res[0] and not self._stoprequest:
                # UDP data came in
                data, addr = self._serversocket_udp.recvfrom(3072)
                nice_addr = 'udp://%s:%d' % addr
                self.printinfo('new connection from %s' % nice_addr)
                conn = CacheUDPConnection(self._serversocket_udp, addr,
                                          log=self.printdebug)
                self._connected[nice_addr] = CacheWorker(
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
        self.printinfo('quitting...')
        self._stoprequest = True
        for client in self._connected.values():
            self.printinfo('closing client %s' % client)
            if client.is_active():
                client.closedown()
        for client in self._connected.values():
            self.printinfo('waiting for %s' % client)
            client.join()
        self.printinfo('waiting for server')
        self._worker.join()
        self.printinfo('server finished')
