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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""The NICOS electronic logbook."""
import sys
from time import time as currenttime

from nicos.core import Param, Override, oneof, CacheLockError
from nicos.core.sessions.utils import sessionInfo
from nicos.services.elog.handler import Handler
from nicos.protocols.cache import OP_TELL, OP_ASK, OP_SUBSCRIBE, cache_load
from nicos.devices.cacheclient import BaseCacheClient
from nicos.utils import timedRetryOnExcept
from nicos.pycompat import to_utf8


class Logbook(BaseCacheClient):

    parameters = {
        'plotformat': Param('Format for scan plots', type=oneof('svg', 'png')),
    }

    parameter_overrides = {
        'prefix':  Override(default='logbook/', mandatory=False),
    }

    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        # this is run in the main thread
        self._handler = Handler(self.log, self.plotformat)
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
            self.log.info('another elog is already active: %s' %
                          sessionInfo(err.locked_by))
            sys.exit(-1)
        else:
            self._islocked = True

        # request current directory for the handler to start up correctly
        self._socket.sendall(
            to_utf8('logbook/directory%s\n###%s\n' % (OP_ASK, OP_ASK)))

        # read response
        data, n = b'', 0
        while not data.endswith(b'###!\n') and n < 1000:
            data += self._socket.recv(8192)
            n += 1

        # send request for all relevant updates
        self._socket.sendall(to_utf8('@logbook/%s\n' % OP_SUBSCRIBE))

        self._process_data(data)

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if op != OP_TELL or not key.startswith(self._prefix):
            return
        key = key[len(self._prefix):]
        time = time and float(time)
        # self.log.info('got %s=%r' % (key, value))
        if key in self._handler.handlers:
            try:
                value = cache_load(value)
                self._handler.handlers[key](time, value)
            except Exception:
                self.log.exception('Error in handler for: %s=%r' % (key, value))

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

    def doShutdown(self):
        self._handler.close()
        BaseCacheClient.doShutdown(self)
