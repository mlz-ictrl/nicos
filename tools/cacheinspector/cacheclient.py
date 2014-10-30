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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

import threading
from time import time as currenttime
from collections import namedtuple

from PyQt4.QtCore import QObject, pyqtSignal

from nicos.core import Override
from nicos.devices.cacheclient import BaseCacheClient
from nicos.protocols.cache import OP_TELL, OP_TELLOLD, END_MARKER


class CacheSignals(QObject):
    """This must be a separate object since the metaclasses of BaseCacheClient
    and CacheSignals are not compatible.
    """

    connected = pyqtSignal()
    disconnected = pyqtSignal()
    keyUpdated = pyqtSignal(str, object)


Entry = namedtuple('Entry', 'key value time ttl expired')


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

    def connect(self, host, port):
        self._address = (host, port)
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

    # def get_raw(self, key):
    #     """Get a value directly from cache with updated timestamp info."""
    #     tosend = '@%s%s%s\n' % (self._prefix, key, OP_ASK)
    #     for msgmatch in self._single_request(tosend):
    #         time, ttl, value = msgmatch.group('time'), msgmatch.group('ttl'), \
    #             msgmatch.group('value')
    #         # self.log.debug('get_explicit: %.2f %.2f %r', time, ttl, value)
    #         return (time and float(time), ttl and float(ttl), value or '')
    #     return (None, None, '')  # shouldn't happen

    def put_raw(self, key, value, time=None, ttl=None):
        if time is None:
            time = currenttime()
        ttlstr = ttl and '+%s' % ttl or ''
        msg = '%s%s@%s%s%s\n' % (time, ttlstr, key, OP_TELL, value)
        # self.log.debug('putting %s=%s' % (key, value))
        self._queue.put(msg)
