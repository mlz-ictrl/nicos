#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

import time
import threading
from time import time as currenttime
from collections import namedtuple

from PyQt4.QtCore import QObject, pyqtSignal

from nicos.core import Override
from nicos.devices.cacheclient import BaseCacheClient
from nicos.protocols.cache import OP_TELL, OP_TELLOLD, OP_ASK, END_MARKER


class CacheSignals(QObject):
    """This must be a separate object since the metaclasses of BaseCacheClient
    and CacheSignals are not compatible.
    """

    connected = pyqtSignal()
    disconnected = pyqtSignal()
    keyUpdated = pyqtSignal(str, object)


class Entry(namedtuple('Entry', 'key value time ttl expired')):

    def convertTime(self, ts=None):
        """Converts the unix time stamp to a readable time stamp."""
        ttup = time.localtime(ts if ts else self.time)
        if ttup[:3] == time.localtime()[:3]:
            return time.strftime('%H:%M:%S', ttup)
        else:
            return time.strftime('%Y-%m-%d %H:%M:%S', ttup)

    @staticmethod
    def parseTime(string):
        if not string:
            return time.time()
        try:
            tval = time.mktime(time.strptime(string, '%H:%M:%S'))
        except ValueError:
            tval = time.mktime(time.strptime(string, '%Y-%m-%d %H:%M:%S'))
        return tval


class CICacheClient(BaseCacheClient):

    parameter_overrides = {
        'cache':  Override(mandatory=False, default=''),
        'prefix': Override(mandatory=False, default=''),
    }

    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        self.__dict__['signals'] = CacheSignals()
        self._db = {}
        self._dblock = threading.Lock()
        # since the base cache client automatically reconnects, we use
        # this flag to override
        self._should_connect = False
        self._worker.start()

    def connect(self, cache):
        # override otherwise read-only server location parameter
        self._setROParam('cache', cache)
        self._should_connect = True
        self._connect()

    def disconnect(self):
        self._should_connect = False

    def _disconnect_action(self):
        with self._dblock:
            self._db.clear()
        self.signals.disconnected.emit()

    def is_connected(self):
        return self._connected

    def _connect_action(self):
        # clear the local database before filling it up
        with self._dblock:
            self._db.clear()
        BaseCacheClient._connect_action(self)
        self.signals.connected.emit()

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if op not in (OP_TELL, OP_TELLOLD):
            return
        if not key.startswith(self._prefix):
            return
        key = key[len(self._prefix):]
        time = time and float(time)
        ttl = ttl and float(ttl) or None
        # self.log.debug('got %s=%s' % (key, value))
        if key == END_MARKER:
            return
        entry = Entry(key, value, time, ttl, op == OP_TELLOLD)
        with self._dblock:
            self._db[key] = entry
        self.signals.keyUpdated.emit(key, entry)

    def keys(self):
        with self._dblock:
            return list(self._db)

    def get(self, key):
        if not self._startup_done.wait(15):
            self.log.warning('Cache _startup_done took more than 15s!')
            return None
        with self._dblock:
            return self._db.get(key)

    def update(self, key):
        """Refresh a value from cache with updated timestamp info."""
        tosend = '@%s%s%s\n' % (self._prefix, key, OP_ASK)
        for msgmatch in self._single_request(tosend):
            self._handle_msg(**msgmatch.groupdict())

    def put(self, key, entry):
        time = entry.time or currenttime()
        ttlstr = entry.ttl and '+%s' % entry.ttl or ''
        msg = '%s%s@%s%s%s\n' % (time, ttlstr, key, OP_TELL, entry.value)
        # self.log.debug('putting %s=%s' % (key, value))
        self._queue.put(msg)
        # the cache doesn't send this update back to us
        with self._dblock:
            self._db[key] = entry
        self.signals.keyUpdated.emit(key, entry)

    def delete(self, key):
        self._queue.put('%s%s\n' % (key, OP_TELL))
        entry = Entry(key, '', time.time(), '', True)
        with self._dblock:
            self._db[key] = entry
        self.signals.keyUpdated.emit(key, entry)
