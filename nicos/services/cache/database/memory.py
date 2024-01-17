# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

import threading
from collections import deque

from nicos.core import Param, intrange
from nicos.services.cache.database.base import CacheDatabase
from nicos.services.cache.entry import CacheEntry


class MemoryCacheDatabase(CacheDatabase):
    """Cache database that keeps the current value for each key in memory."""

    def doInit(self, mode):
        self._db = {}
        self._db_lock = threading.Lock()
        CacheDatabase.doInit(self, mode)

    def getEntry(self, dbkey):
        with self._db_lock:
            if dbkey not in self._db:
                return None
            return self._db[dbkey][-1]

    def iterEntries(self):
        with self._db_lock:
            for dbkey, entries in self._db.items():
                yield dbkey, entries[-1]

    def updateEntries(self, categories, subkey, no_store, entry):
        real_update = True
        with self._db_lock:
            for cat in categories:
                entries = self._db.setdefault((cat, subkey), [])
                if entries:
                    lastent = entries[-1]
                    if lastent.value == entry.value and not lastent.ttl:
                        # not a real update
                        real_update = False
                # never cache more than a single entry
                entries[:] = [entry]
        return real_update

    def queryHistory(self, dbkey, fromtime, totime, interval):
        return []


class MemoryCacheDatabaseWithHistory(MemoryCacheDatabase):
    """Cache database that keeps everything in memory.

    A certain amount of old values is also kept, determined by the
    *maxentries* parameter.
    """

    parameters = {
        'maxentries': Param('Maximum history length',
                            type=intrange(0, 100), default=10, settable=False),
    }

    def updateEntries(self, categories, subkey, no_store, entry):
        real_update = True
        with self._db_lock:
            for cat in categories:
                queue = deque([CacheEntry(None, None, None)], self.maxentries)
                entries = self._db.setdefault((cat, subkey), queue)
                lastent = entries[-1]
                if lastent.value == entry.value and not lastent.ttl:
                    # not a real update
                    real_update = False
                entries.append(entry)
        return real_update

    def queryHistory(self, dbkey, fromtime, totime, interval):
        _ = interval
        inrange = False
        # return the first value before the range too
        last_before = None
        try:
            entries = self._db[dbkey]
            for entry in entries:
                if fromtime <= entry.time <= totime:
                    if not inrange and last_before:
                        yield last_before
                    yield entry
                    inrange = True
                elif not inrange and entry.value and entry.time < fromtime:
                    last_before = entry
            # return at least the last value before empty range
            if not inrange and last_before is not None:
                yield last_before
        except Exception:
            self.log.exception('error reading store for history query')
