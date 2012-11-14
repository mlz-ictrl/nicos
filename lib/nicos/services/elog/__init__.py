#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

__version__ = "$Revision$"

from nicos.services.elog.handler import Handler
from nicos.protocols.cache import OP_TELL, OP_ASK, OP_SUBSCRIBE, cache_load
from nicos.devices.cacheclient import BaseCacheClient


class Logbook(BaseCacheClient):
    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        # this is run in the main thread
        self._handler = Handler(self.log)

    def _connect_action(self):
        # request current directory for the handler to start up correctly
        self._socket.sendall('logbook/directory%s\n###%s\n' %
                             (OP_ASK, OP_ASK))

        # read response
        data, n = '', 0
        while not data.endswith('###!\n') and n < 1000:
            data += self._socket.recv(8192)
            n += 1

        # send request for all relevant updates
        self._socket.sendall('@logbook/%s\n' % OP_SUBSCRIBE)

        self._process_data(data)

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if op != OP_TELL or not key.startswith(self._prefix):
            return
        key = key[len(self._prefix):]
        time = time and float(time)
        #self.log.info('got %s=%r' % (key, value))
        if key in self._handler.handlers:
            value = cache_load(value)
            try:
                self._handler.handlers[key](time, value)
            except Exception:
                self.log.exception('Error in handler for: %s=%r' % (key, value))

    def doShutdown(self):
        self._handler.close()
        BaseCacheClient.doShutdown(self)
