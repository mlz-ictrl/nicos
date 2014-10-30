#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

"""NICOS cache server."""

import os
import threading
from os import path
from time import time as currenttime, sleep, localtime, mktime
from collections import deque

from nicos import config
from nicos.core import Device, Param, ConfigurationError, intrange
from nicos.utils import ensureDirectory, allDays, createThread
from nicos.protocols.cache import OP_TELL, OP_TELLOLD, OP_LOCK, \
    OP_LOCK_LOCK, OP_LOCK_UNLOCK, FLAG_NO_STORE
from nicos.pycompat import iteritems, listitems

try:  # Windows compatibility: it does not provide os.link
    os_link = os.link
except AttributeError:
    os_link = lambda a, b: None


class Entry(object):
    __slots__ = ('time', 'ttl', 'value', 'expired')

    def __init__(self, time, ttl, value):
        self.time = time
        self.ttl = ttl
        self.value = value
        self.expired = False

    def __repr__(self):
        if self.expired:
            return '(%s+%s@%s)' % (self.time, self.ttl, self.value)
        return '%s+%s@%s' % (self.time, self.ttl, self.value)


class CacheDatabase(Device):

    def doInit(self, mode):
        if self.__class__ is CacheDatabase:
            raise ConfigurationError(
                'CacheDatabase is an abstract class, use '
                'either MemoryCacheDatabase or FlatfileCacheDatabase')
        self._lock_lock = threading.Lock()
        self._locks = {}
        self._rewrite_lock = threading.Lock()
        # map incoming prefix -> set of new prefixes
        self._rewrites = {}
        # map new prefix -> incoming prefix
        self._inv_rewrites = {}

    def initDatabase(self):
        """Initialize the database from persistent store, if present."""
        pass

    def rewrite(self, key, value):
        """Rewrite handling."""
        if value:
            value = value.lower()
        current = self._inv_rewrites.get(key)
        with self._rewrite_lock:
            if current is not None:
                self._rewrites[current].discard(key)
                if not self._rewrites[current]:
                    del self._rewrites[current]
                del self._inv_rewrites[key]
            if value:
                self._rewrites.setdefault(value, set()).add(key)
                self._inv_rewrites[key] = value

    def lock(self, key, value, time, ttl):
        """Lock handling code, common to both subclasses."""
        with self._lock_lock:
            entry = self._locks.get(key)
            # want to lock?
            req, client_id = value[0], value[1:]
            if req == OP_LOCK_LOCK:
                if entry and entry.value != client_id and \
                   (not entry.ttl or entry.time + entry.ttl >= currenttime()):
                    # still locked by different client, deny (tell the client
                    # the current client_id though)
                    self.log.debug('lock request %s=%s, but still locked by %s'
                                   % (key, client_id, entry.value))
                    return key + OP_LOCK + entry.value + '\n'
                else:
                    # not locked, expired or locked by same client, overwrite
                    ttl = ttl or 1800  # set a maximum time to live
                    self.log.debug('lock request %s=%s ttl %s, accepted' %
                                   (key, client_id, ttl))
                    self._locks[key] = Entry(time, ttl, client_id)
                    return key + OP_LOCK + '\n'
            # want to unlock?
            elif req == OP_LOCK_UNLOCK:
                if entry and entry.value != client_id:
                    # locked by different client, deny
                    self.log.debug('unlock request %s=%s, but locked by %s' %
                                   (key, client_id, entry.value))
                    return key + OP_LOCK + entry.value + '\n'
                else:
                    # unlocked or locked by same client, allow
                    self.log.debug('unlock request %s=%s, accepted' %
                                   (key, client_id))
                    self._locks.pop(key, None)
                    return key + OP_LOCK + '\n'


class MemoryCacheDatabase(CacheDatabase):
    """Cache database that keeps the current value for each key in memory."""

    def doInit(self, mode):
        self._db = {}
        self._db_lock = threading.Lock()
        CacheDatabase.doInit(self, mode)

    def ask(self, key, ts, time, ttl):
        with self._db_lock:
            if key not in self._db:
                return [key + OP_TELLOLD + '\n']
            lastent = self._db[key][-1]
        # check for already removed keys
        if lastent.value is None:
            return [key + OP_TELLOLD + '\n']
        # check for expired keys
        if lastent.ttl:
            remaining = lastent.time + lastent.ttl - currenttime()
            op = remaining > 0 and OP_TELL or OP_TELLOLD
            if ts:
                return ['%s+%s@%s%s%s\n' % (lastent.time, lastent.ttl,
                                            key, op, lastent.value)]
            else:
                return [key + op + lastent.value + '\n']
        if ts:
            return ['%s@%s%s%s\n' % (lastent.time, key, OP_TELL, lastent.value)]
        else:
            return [key + OP_TELL + lastent.value + '\n']

    def ask_wc(self, key, ts, time, ttl):
        ret = set()
        with self._db_lock:
            # look for matching keys
            for dbkey, entries in iteritems(self._db):
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
                        ret.add('%s+%s@%s%s%s\n' % (lastent.time, lastent.ttl,
                                                    dbkey, op, lastent.value))
                    else:
                        ret.add(dbkey + op + lastent.value + '\n')
                elif ts:
                    ret.add('%s@%s%s%s\n' % (lastent.time, dbkey,
                                             OP_TELL, lastent.value))
                else:
                    ret.add(dbkey + OP_TELL + lastent.value + '\n')
        return ret

    def ask_hist(self, key, fromtime, totime):
        return []

    def tell(self, key, value, time, ttl, from_client):
        if value is None:
            # deletes cannot have a TTL
            ttl = None
        send_update = True
        # remove no-store flag
        if key.endswith(FLAG_NO_STORE):
            key = key[:-len(FLAG_NO_STORE)]
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key
        newcats = [category]
        if category in self._rewrites:
            newcats.extend(self._rewrites[category])
        for newcat in newcats:
            key = newcat + '/' + subkey
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
                        client.update(key, OP_TELL, value or '', time, ttl)


class MemoryCacheDatabaseWithHistory(MemoryCacheDatabase):
    """Cache database that keeps everything in memory.

    A certain amount of old values is also kept, determined by the
    *maxentries* parameter.
    """

    parameters = {
        'maxentries': Param('Maximum history length',
                            type=intrange(0, 100), default=10, settable=False),
    }

    def ask_hist(self, key, fromtime, totime):
        if fromtime > totime:
            return []
        ret = []
        # return the first value before the range too
        inrange = False
        try:
            entries = self._db[key]
            for entry in entries:
                if fromtime <= entry.time <= totime:
                    ret.append('%s@%s=%s\n' % (entry.time, key, entry.value))
                    inrange = True
                elif not inrange and entry.value:
                    ret = ['%s@%s=%s\n' % (entry.time, key, entry.value)]
        except Exception:
            self.log.exception('error reading store for history query')
        if not inrange:
            return []
        return ret

    def tell(self, key, value, time, ttl, from_client):
        if value is None:
            # deletes cannot have a TTL
            ttl = None
        send_update = True
        # remove no-store flag
        if key.endswith(FLAG_NO_STORE):
            key = key[:-len(FLAG_NO_STORE)]
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key
        newcats = [category]
        if category in self._rewrites:
            newcats.extend(self._rewrites[category])
        for newcat in newcats:
            key = newcat + '/' + subkey
            with self._db_lock:
                queue = deque([Entry(None, None, None)], self.maxentries)
                entries = self._db.setdefault(key, queue)
                lastent = entries[-1]
                if lastent.value == value and not lastent.ttl:
                    # not a real update
                    send_update = False
                entries.append(Entry(time, ttl, value))
            if send_update:
                for client in self._server._connected.values():
                    if client is not from_client and client.is_active():
                        client.update(key, OP_TELL, value or '', time, ttl)


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

    The format of these files is a simple four-column tab-separated ascii
    format:

    * the first column is the last part of the cache key (which combined
      with the category gives the full key)
    * the second column is the Unix timestamp of the change
    * the third column is either ``+`` or ``-``, where ``-`` means "the key will
      expire at some point" (on re-loading old files, such values will be
      ignored)
    * the fourth column is the actual value or ``-`` meaning "expired"

    All values should be valid Python literals, but this is not enforced by the
    cache server, rather by the NICOS clients.  The value can also a single
    dash, this indicates that at the given timestamp the latest value for this
    key expired.
    """

    parameters = {
        'storepath': Param('Directory where history stores should be saved',
                           type=str, mandatory=True),
    }

    def doInit(self, mode):
        self._cat = {}
        self._cat_lock = threading.Lock()
        CacheDatabase.doInit(self, mode)

        self._basepath = path.join(config.nicos_root, self.storepath)
        ltime = localtime()
        self._year = str(ltime[0])
        self._currday = '%02d-%02d' % ltime[1:3]
        self._midnight = mktime(ltime[:3] + (0,) * (8-3) + (ltime[8],))
        self._nextmidnight = self._midnight + 86400

        self._stoprequest = False
        self._cleaner = createThread('cleaner', self._clean)

    def doShutdown(self):
        self._stoprequest = True
        self._cleaner.join()

    def _read_one_storefile(self, filename):
        fd = open(filename, 'r+U')
        # read file format identification
        firstline = fd.readline()
        if firstline.startswith('# NICOS cache store file v2'):
            return self._read_one_storefile_v2(filename, fd)
        # v1 has no comment; go back to first line for reading
        fd.seek(0, os.SEEK_SET)
        return self._convert_storefile(filename, fd)

    def _read_one_storefile_v2(self, filename, fd):
        db = {}
        for line in fd:
            try:
                subkey, time, hasttl, value = line.rstrip().split(None, 3)
                if hasttl == '+':
                    # the value is valid indefinitely, so we can use it
                    db[subkey] = Entry(float(time), None, value)
                elif value != '-':
                    # the value is not valid indefinitely, add it but mark as expired
                    db[subkey] = Entry(float(time), None, value)
                    db[subkey].expired = True
                elif subkey in db:  # implied: value == '-'
                    # the value is already present, but now explicitly invalidated
                    # => mark it as expired
                    db[subkey].expired = True
            except Exception:
                self.log.warning('could not interpret line from '
                                 'cache file %s: %r' % (filename, line), exc=1)
        return fd, db

    def _convert_storefile(self, filename, fd):
        # read whole content and write back in new format
        self.log.info('converting store file %s to new format' % filename)
        content = fd.read()
        fd.seek(0, os.SEEK_SET)
        fd.write('# NICOS cache store file v2\n')
        db = {}
        for line in content.splitlines():
            try:
                subkey, time, value = line.rstrip().split(None, 2)
                if value != '-':
                    db[subkey] = Entry(float(time), None, value)
                elif subkey in db:  # implied: value == '-'
                    db[subkey].expired = True
            except Exception:
                self.log.warning('could not interpret line from '
                                 'cache file %s: %r' % (filename, line), exc=1)
            else:
                # mark all entries as not expiring, mirroring old behavior
                if value == '-':
                    fd.write('%s\t%s\t-\t-\n' % (subkey, time))
                else:
                    fd.write('%s\t%s\t+\t%s\n' % (subkey, time, value))
        # we should have written more than was in the file before, but make sure
        fd.truncate()
        return fd, db

    def initDatabase(self):
        # read the last entry for each key from disk
        nkeys = 0
        do_rollover = False
        # read entries from today if they exist
        curdir = path.join(self._basepath, self._year, self._currday)
        # else read from last day with cache entries by default (lastday must be
        # a symlink to the last day directory)
        if not path.isdir(curdir):
            curdir = path.join(self._basepath, 'lastday')
            # in this case, we need to create new cache files for today, so we
            # perform a faux rollover immediately after reading the db
            do_rollover = True
        # and if that doesn't exist, give up
        if not path.isdir(curdir):
            # ... but at least set the symlink correctly for today
            self.log.info('no previous values found, setting "lastday" link '
                          'to %s/%s' % (self._year, self._currday))
            self._set_lastday()
            return
        with self._cat_lock:
            for fn in os.listdir(curdir):
                cat = fn.replace('-', '/')
                try:
                    fd, db = self._read_one_storefile(path.join(curdir, fn))
                    lock = threading.Lock()
                    self._cat[cat] = [fd, lock, db]
                    nkeys += len(db)
                except Exception:
                    self.log.warning('could not read cache file %s' % fn, exc=1)
            if do_rollover:
                self._rollover()
        self.log.info('loaded %d keys from files in %s' % (nkeys, curdir))

    def _rollover(self):
        """Must be called with self._cat_lock held."""
        self.log.info('midnight passed, data file rollover started')
        ltime = localtime()
        # set the days and midnight time correctly
        self._year = str(ltime[0])
        self._currday = '%02d-%02d' % ltime[1:3]
        self._midnight = mktime(ltime[:3] + (0,) * (8-3) + (ltime[8],))
        self._nextmidnight = self._midnight + 86400
        # roll over all file descriptors
        for category, (fd, _, db) in iteritems(self._cat):
            fd.close()
            fd = self._cat[category][0] = self._create_fd(category)
            for subkey, entry in iteritems(db):
                if entry.value:
                    fd.write('%s\t%s\t%s\t%s\n' % (
                        subkey, entry.time,
                        (entry.ttl or entry.expired) and '-' or '+',
                        entry.value))
            fd.flush()
        # set the 'lastday' symlink to the current day directory
        self._set_lastday()
        # old files could be compressed here, but it is probably not worth it

    def _set_lastday(self):
        if not hasattr(os, 'symlink'):
            return
        try:
            lname = path.join(self._basepath, 'lastday')
            if path.lexists(lname):
                os.unlink(lname)
            os.symlink(path.join(self._year, self._currday), lname)
        except Exception:
            self.log.warning('error setting "lastday" symlink', exc=1)

    def _create_fd(self, category):
        """Open the by-date output file for the current day for a given
        category, and create the by-category hard link if necessary.
        """
        category = category.replace('/', '-')
        bydate = path.join(self._basepath, self._year, self._currday)
        ensureDirectory(bydate)
        filename = path.join(bydate, category)
        fd = open(filename, 'a+')
        fd.seek(0, os.SEEK_END)
        # write version identification, but only for empty files
        if fd.tell() == 0:
            fd.write('# NICOS cache store file v2\n')
        bycat = path.join(self._basepath, category, self._year)
        ensureDirectory(bycat)
        linkname = path.join(bycat, self._currday)
        if not path.isfile(linkname):
            os_link(filename, linkname)
        return fd

    def ask(self, key, ts, time, ttl):
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key
        with self._cat_lock:
            if category not in self._cat:
                return [key + OP_TELLOLD + '\n']
            _, lock, db = self._cat[category]
        with lock:
            if subkey not in db:
                return [key + OP_TELLOLD + '\n']
            entry = db[subkey]
        # check for expired keys
        if entry.value is None:
            return [key + OP_TELLOLD + '\n']
        # check for expired keys
        op = entry.expired and OP_TELLOLD or OP_TELL
        if entry.ttl:
            if ts:
                return ['%s+%s@%s%s%s\n' % (entry.time, entry.ttl,
                                            key, op, entry.value)]
            else:
                return [key + op + entry.value + '\n']
        if ts:
            return ['%s@%s%s%s\n' % (entry.time, key, op, entry.value)]
        else:
            return [key + op + entry.value + '\n']

    def ask_wc(self, key, ts, time, ttl):
        ret = set()
        # look for matching keys
        for cat, (_, lock, db) in listitems(self._cat):
            prefix = cat + '/' if cat != 'nocat' else ''
            with lock:
                for subkey, entry in iteritems(db):
                    if key not in prefix+subkey:
                        continue
                    # check for removed keys
                    if entry.value is None:
                        continue
                    # check for expired keys
                    op = entry.expired and OP_TELLOLD or OP_TELL
                    if entry.ttl:
                        if ts:
                            ret.add('%s+%s@%s%s%s\n' %
                                    (entry.time, entry.ttl, prefix+subkey,
                                     op, entry.value))
                        else:
                            ret.add(prefix+subkey + op + entry.value + '\n')
                    elif ts:
                        ret.add('%s@%s%s%s\n' % (entry.time, prefix+subkey,
                                                 op, entry.value))
                    else:
                        ret.add(prefix+subkey + op + entry.value + '\n')
        return ret

    def _read_one_histfile(self, year, monthday, category, subkey):
        fn = path.join(self._basepath, year, monthday, category)
        if not path.isfile(fn):
            return
        with open(fn, 'U') as fd:
            firstline = fd.readline()
            nsplit = 2
            if firstline.startswith('# NICOS cache store file v2'):
                nsplit = 3
            else:
                fd.seek(0, os.SEEK_SET)
            for line in fd:
                fields = line.rstrip().split(None, nsplit)
                if fields[0] == subkey:
                    time = float(fields[1])
                    value = fields[-1]
                    if value == '-':
                        value = ''
                    yield (time, value)

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
            days = allDays(fromtime, totime)
        ret = []
        # return the first value before the range too
        inrange = False
        for year, monthday in days:
            try:
                for time, value in self._read_one_histfile(year, monthday,
                                                           category, subkey):
                    if fromtime <= time <= totime:
                        ret.append('%s@%s=%s\n' % (time, key, value))
                        inrange = True
                    elif not inrange and value:
                        ret = ['%s@%s=%s\n' % (time, key, value)]
            except Exception:
                self.log.exception('error reading store file for history query')
        if not inrange:
            return []
        return ret

    def _clean(self):
        def cleanonce():
            with self._cat_lock:
                for cat, (fd, lock, db) in iteritems(self._cat):
                    with lock:
                        for subkey, entry in iteritems(db):
                            if not entry.value or entry.expired:
                                continue
                            time = currenttime()
                            if entry.ttl and (entry.time + entry.ttl < time):
                                entry.expired = True
                                for client in self._server._connected.values():
                                    client.update(cat + '/' + subkey,
                                                  OP_TELLOLD, entry.value,
                                                  time, None)
                                fd.write('%s\t%s\t-\t-\n' % (subkey, time))
                                fd.flush()
        while not self._stoprequest:
            sleep(0.5)
            cleanonce()

    def tell(self, key, value, time, ttl, from_client, fdupdate=True):
        # self.log.debug('updating %s %s' % (key, value))
        if value is None:
            # deletes cannot have a TTL
            ttl = None
        if time is None:
            time = currenttime()
        store_on_disk = True
        if key.endswith(FLAG_NO_STORE):
            key = key[:-len(FLAG_NO_STORE)]
            store_on_disk = False
        with self._cat_lock:
            if currenttime() > self._nextmidnight:
                self._rollover()
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key
        newcats = [category]
        if category in self._rewrites:
            newcats.extend(self._rewrites[category])
        for newcat in newcats:
            with self._cat_lock:
                if newcat not in self._cat:
                    self._cat[newcat] = [self._create_fd(newcat),
                                         threading.Lock(), {}]
                fd, lock, db = self._cat[newcat]
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
                    elif value is None and entry.expired:
                        # do not delete old value, it is already expired
                        update = False
                if update:
                    db[subkey] = Entry(time, ttl, value)
                    if store_on_disk:
                        fd.write('%s\t%s\t%s\t%s\n' % (
                            subkey, time,
                            ttl and '-' or (value and '+' or '-'),
                            value or '-'))
                        fd.flush()
            if update:
                key = newcat + '/' + subkey
                for client in self._server._connected.values():
                    if client is not from_client:
                        client.update(key, OP_TELL, value or '', time, ttl)
