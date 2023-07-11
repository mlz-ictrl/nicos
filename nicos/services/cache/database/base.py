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
from time import time as currenttime

from nicos.core import ConfigurationError, Device
from nicos.protocols.cache import FLAG_NO_STORE, OP_LOCK, OP_LOCK_LOCK, \
    OP_LOCK_UNLOCK, OP_TELL, OP_TELLOLD
from nicos.services.cache.entry import CacheEntry


class CacheDatabase(Device):
    """Represents a backend for the NICOS cache.

    For new subclasses, implement the methods indicated below.
    """

    def doInit(self, mode):
        if self.__class__ is CacheDatabase:
            raise ConfigurationError(
                'CacheDatabase is abstract, use a derived device class')
        self._lock_lock = threading.Lock()
        self._locks = {}
        self._rewrite_lock = threading.Lock()
        # map incoming prefix -> set of new prefixes
        self._rewrites = {}
        # map new prefix -> incoming prefix
        self._inv_rewrites = {}

    # to override in concrete implementations, if needed:

    def initDatabase(self):
        """Initialize the database from persistent store, if present."""

    def clearDatabase(self):
        """Clear the database also from persistent store, if present."""
        self.log.info('clearing database')

    # to implement in concrete implementations:

    def getEntry(self, dbkey):
        """Return the current Entry for the given (category, subkey)."""
        raise NotImplementedError

    def iterEntries(self):
        """Yield all current ((category, subkey), Entry) pairs."""
        raise NotImplementedError

    def updateEntries(self, categories, subkey, no_store, entry):
        """Update an entry which is in the given categories (can be multiple
        due to rewrites).

        If *no_store* is true, the no-store flag has been sent by the client.

        Should return True if it is a "real" update, i.e. other clients should
        be notified.
        """
        raise NotImplementedError

    def queryHistory(self, dbkey, fromtime, totime, interval):
        """Yield CacheEntry objects from history for the given timespan.

        Should also include the last entry *before* the fromtime, so that the
        history during the span is not incomplete (i.e. for keys that change
        rarely).
        """
        raise NotImplementedError

    # not needed to override:

    def ask(self, key, ts):
        """Query the current value for a single key.

        If *ts* is true, include a timestamp in the reply.
        """
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key
        entry = self.getEntry((category, subkey))

        # check for nonexisting or deleted keys
        if entry is None or entry.value is None:
            if ts:
                return [f'{entry.time if entry else ""}@{key}{OP_TELLOLD}\n']
            return [f'{key}{OP_TELLOLD}\n']

        # handle expired keys with different operator
        op = entry.expired and OP_TELLOLD or OP_TELL

        if entry.ttl:
            if ts:
                return [f'{entry.time}+{entry.ttl}@{key}{op}{entry.value}\n']
            else:
                return [f'{key}{op}{entry.value}\n']
        if ts:
            return [f'{entry.time}@{key}{op}{entry.value}\n']
        else:
            return [f'{key}{op}{entry.value}\n']

    def ask_wc(self, substring, ts):
        """Query the current values for all keys matching the wildcard.

        If *ts* is true, include a timestamp in the reply.
        """
        ret = set()
        for (dbkey, entry) in self.iterEntries():
            key = dbkey[1] if dbkey[0] == 'nocat' else f'{dbkey[0]}/{dbkey[1]}'
            if substring not in key:
                continue
            # check for removed keys
            if entry.value is None:
                continue
            # check for expired keys
            op = entry.expired and OP_TELLOLD or OP_TELL
            if entry.ttl:
                if ts:
                    ret.add(f'{entry.time}+{entry.ttl}@{key}'
                            f'{op}{entry.value}\n')
                else:
                    ret.add(f'{key}{op}{entry.value}\n')
            elif ts:
                ret.add(f'{entry.time}@{key}{op}{entry.value}\n')
            else:
                ret.add(f'{key}{op}{entry.value}\n')
        return [''.join(ret)]

    def ask_hist(self, key, fromtime, totime, interval):
        """Query the historical values for a single key between two
        timestamps. If interval is set, this will be a minimum time between
        two adjacent values.

        Returns a generator of cache message bunches.
        """
        if fromtime > totime:
            return
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key

        # bunch up 100 entries at a time
        bunch = []
        if interval in [None, '', 'None', '0', '0.0']:
            interval = None
        else:
            try:
                interval = int(float(interval))
            except ValueError:
                interval = None
        for entry in self.queryHistory((category, subkey), fromtime, totime,
                                       interval):
            bunch.append(f'{entry.time}@{key}={entry.value}\n')
            if len(bunch) > 100:
                yield ''.join(bunch)
                bunch = []
        yield ''.join(bunch)

    def tell(self, key, value, time, ttl, from_client):
        """Update the backend with a new value for a key.

        Needs to take rewrites into account.

        Needs to notify other clients about the update.  *from_client* is the
        client the update comes from, which should therefore not be notified.
        """
        try:
            category, subkey = key.rsplit('/', 1)
        except ValueError:
            category = 'nocat'
            subkey = key

        # deletes cannot have a TTL
        if value is None:
            ttl = None

        # add timestamp if not given by client
        if time is None:
            time = currenttime()

        # handle the no-store flag
        no_store = subkey.endswith(FLAG_NO_STORE)
        if no_store:
            subkey = subkey[:-len(FLAG_NO_STORE)]

        # apply rewrite mechanism: a single update might be mapped to updates
        # of multiple keys with different categories
        newcats = [category]
        if category in self._rewrites:
            newcats.extend(self._rewrites[category])

        # during updates, if we find out the new value is already the current
        # value (without TTL), we don't need to update other clients
        real_update = self.updateEntries(newcats, subkey, no_store,
                                         CacheEntry(time, ttl, value))

        # if no_store flag is set, always send an update
        if real_update or no_store:
            for client in self._server._connected.values():
                if client is not from_client:
                    for cat in newcats:
                        client.update(f'{cat}/{subkey}', OP_TELL,
                                      value or '', time, ttl)

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
                    self.log.debug(
                        'lock request %s=%s, but still locked by %s',
                        key, client_id, entry.value)
                    return [key + OP_LOCK + entry.value + '\n']
                else:
                    # not locked, expired or locked by same client, overwrite
                    ttl = ttl or 600  # set a maximum time to live
                    self.log.debug('lock request %s=%s ttl %s, accepted',
                                   key, client_id, ttl)
                    self._locks[key] = CacheEntry(time, ttl, client_id)
                    return [key + OP_LOCK + '\n']
            # want to unlock?
            elif req == OP_LOCK_UNLOCK:
                if entry and entry.value != client_id:
                    # locked by different client, deny
                    self.log.debug('unlock request %s=%s, but locked by %s',
                                   key, client_id, entry.value)
                    return [key + OP_LOCK + entry.value + '\n']
                else:
                    # unlocked or locked by same client, allow
                    self.log.debug('unlock request %s=%s, accepted',
                                   key, client_id)
                    self._locks.pop(key, None)
                    return [key + OP_LOCK + '\n']
