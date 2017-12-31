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
from time import time as currenttime

from nicos.core import Device, ConfigurationError
from nicos.protocols.cache import OP_LOCK, OP_LOCK_LOCK, OP_LOCK_UNLOCK
from nicos.services.cache.database.entry import CacheEntry


class CacheDatabase(Device):
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

    def initDatabase(self):
        """Initialize the database from persistent store, if present."""
        pass

    def clearDatabase(self):
        """Clear the database also from persistent store, if present."""
        self.log.info('clearing database')

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
