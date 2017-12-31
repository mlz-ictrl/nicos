#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

import threading
from collections import deque
from time import time as currenttime

from nicos.core import Param, intrange
from nicos.protocols.cache import OP_TELL, OP_TELLOLD, FLAG_NO_STORE
from nicos.pycompat import iteritems
from nicos.services.cache.database.base import CacheDatabase
from nicos.services.cache.database.entry import CacheEntry


class MemoryCacheDatabase(CacheDatabase):
    """Cache database that keeps the current value for each key in memory."""

    def doInit(self, mode):
        self._db = {}
        self._db_lock = threading.Lock()
        CacheDatabase.doInit(self, mode)

    def ask(self, key, ts, time, ttl):
        dbkey = key if '/' in key else 'nocat/' + key
        with self._db_lock:
            if dbkey not in self._db:
                return [key + OP_TELLOLD + '\n']
            lastent = self._db[dbkey][-1]
        # check for already removed keys
        if lastent.value is None:
            return [key + OP_TELLOLD + '\n']
        # check for expired keys
        if lastent.ttl:
            remaining = lastent.time + lastent.ttl - currenttime()
            op = remaining > 0 and OP_TELL or OP_TELLOLD
            if ts:
                return ['%r+%s@%s%s%s\n' % (lastent.time, lastent.ttl,
                                            key, op, lastent.value)]
            else:
                return [key + op + lastent.value + '\n']
        if ts:
            return [
                '%r@%s%s%s\n' % (lastent.time, key, OP_TELL, lastent.value)]
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
                if dbkey.startswith('nocat/'):
                    dbkey = dbkey[6:]
                # check for expired keys
                if lastent.ttl:
                    remaining = lastent.time + lastent.ttl - currenttime()
                    op = remaining > 0 and OP_TELL or OP_TELLOLD
                    if ts:
                        ret.add('%r+%s@%s%s%s\n' % (lastent.time, lastent.ttl,
                                                    dbkey, op, lastent.value))
                    else:
                        ret.add(dbkey + op + lastent.value + '\n')
                elif ts:
                    ret.add('%r@%s%s%s\n' % (lastent.time, dbkey,
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
        always_send_update = False
        # remove no-store flag
        if key.endswith(FLAG_NO_STORE):
            key = key[:-len(FLAG_NO_STORE)]
            always_send_update = True
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
                entries[:] = [CacheEntry(time, ttl, value)]
            if send_update or always_send_update:
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
                    ret.append('%r@%s=%s\n' % (entry.time, key, entry.value))
                    inrange = True
                elif not inrange and entry.value:
                    ret = ['%r@%s=%s\n' % (entry.time, key, entry.value)]
        except Exception:
            self.log.exception('error reading store for history query')
        if not inrange:
            return []
        return [''.join(ret)]

    def tell(self, key, value, time, ttl, from_client):
        if value is None:
            # deletes cannot have a TTL
            ttl = None
        send_update = True
        always_send_update = False
        # remove no-store flag
        if key.endswith(FLAG_NO_STORE):
            key = key[:-len(FLAG_NO_STORE)]
            always_send_update = True
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
                queue = deque([CacheEntry(None, None, None)], self.maxentries)
                entries = self._db.setdefault(key, queue)
                lastent = entries[-1]
                if lastent.value == value and not lastent.ttl:
                    # not a real update
                    send_update = False
                entries.append(CacheEntry(time, ttl, value))
            if send_update or always_send_update:
                for client in self._server._connected.values():
                    if client is not from_client and client.is_active():
                        client.update(key, OP_TELL, value or '', time, ttl)
