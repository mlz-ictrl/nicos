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

"""The NICOS cache collector daemon."""

from nicos.core import Override, Attach
from nicos.protocols.cache import OP_TELL, OP_TELLOLD
from nicos.devices.cacheclient import BaseCacheClient


class GlobalCache(BaseCacheClient):

    def _connect_action(self):
        # send no requests for keys or updates
        pass

    def put_change(self, time, key, value):
        if value is None:
            msg = '%s@%s%s%s\n' % (time, self._prefix, key, OP_TELLOLD)
        else:
            msg = '%s@%s%s%s%s\n' % (time, self._prefix, key, OP_TELL, value)
        self._queue.put(msg)


class Collector(BaseCacheClient):

    attached_devices = {
        'globalcache':  Attach('The cache to submit keys to', GlobalCache),
    }

    parameter_overrides = {
        'prefix':  Override(mandatory=False, default='nicos/'),
    }

    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        self._global = self._attached_globalcache
        self._global._worker.start()

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if not key.startswith(self._prefix):
            return
        key = key[len(self._prefix):]
        if op == OP_TELL:
            self._global.put_change(time, key, value or None)
        elif op == OP_TELLOLD:
            self._global.put_change(time, key, None)
