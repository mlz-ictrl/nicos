# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""The NICOS electronic logbook."""

import sys
from os import unlink
from time import time as currenttime

from nicos.core import Attach, CacheLockError, Override
from nicos.core.sessions.utils import sessionInfo
from nicos.devices.cacheclient import BaseCacheClient
from nicos.protocols.cache import BUFSIZE, END_MARKER, OP_ASK, OP_SUBSCRIBE, \
    OP_TELL, OP_TELLOLD, cache_load
from nicos.services.elog.handler import Handler
from nicos.utils import timedRetryOnExcept


class Logbook(BaseCacheClient):

    attached_devices = {
        'handlers': Attach('The handlers for incoming data', Handler,
                           multiple=True),
    }

    parameter_overrides = {
        'prefix': Override(default='logbook/', mandatory=False),
    }

    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        # the execution master lock needs to be refreshed every now and then
        self._islocked = False
        self._lock_expires = 0.
        self._locktimeout = 5.

    def _connect_action(self):

        @timedRetryOnExcept(max_retries=1, timeout=self._locktimeout,
                            ex=CacheLockError)
        def trylock():
            return self.lock('elog')

        try:
            trylock()
        except CacheLockError as err:
            self.log.info('another elog is already active: %s',
                          sessionInfo(err.locked_by))
            sys.exit(-1)
        else:
            self._islocked = True

        # request persistent data for the handler to start up correctly
        msg = (f'@{self._prefix}hidden{OP_ASK}\n'
               f'@{self._prefix}directory{OP_ASK}\n'
               f'@{self._prefix}newexperiment{OP_ASK}\n'
               f'{END_MARKER}{OP_ASK}\n')
        self._socket.sendall(msg.encode())

        # read response
        data, n = b'', 0
        sentinel = (END_MARKER + OP_TELLOLD + '\n').encode()
        while not data.endswith(sentinel) and n < 1000:
            data += self._socket.recv(BUFSIZE)
            n += 1

        self.storeSysInfo('elog')

        # send request for all relevant updates
        msg = f'@{self._prefix}{OP_SUBSCRIBE}\n'
        self._socket.sendall(msg.encode())

        self._process_data(data)

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        self.log.debug('got %s, op: %s', key, op)
        if op != OP_TELL or not key.startswith(self._prefix):
            return
        key = key[len(self._prefix):]
        time = time and float(time)
        self.log.debug('got %s=%r', key, value)
        value = cache_load(value)
        for handler in self._attached_handlers:
            try:
                handler.handle(key, time, value)
            except Exception:
                self.log.exception('Error in %s for: %s=%r',
                                   handler.__class__.__name__, key, value)
        if key in ('attachment', 'image'):
            for fn in value[1]:
                unlink(fn)

    def _wait_data(self):
        if self._islocked:
            time = currenttime()
            if time > self._lock_expires:
                self._lock_expires = time + self._locktimeout - 1
                self.lock('elog', self._locktimeout)

    def _disconnect(self, why=None):
        if self._islocked and self._stoprequest and self._connected:
            self._islocked = False
            self.unlock('elog')
        BaseCacheClient._disconnect(self, why)
