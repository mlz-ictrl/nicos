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

from nicos.devices.cacheclient import CacheClient
from nicos.protocols.cache import cache_load, OP_TELL, OP_TELLOLD

class CICacheClient(CacheClient):

    def doInit(self, mode):
        CacheClient.doInit(self, mode)

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if op not in (OP_TELL, OP_TELLOLD):
            return
        if not key.startswith(self._prefix):
#           for cb in self._prefixcallbacks:
#               if key.startswith(cb):
#                   value = cache_load(value)
#                   time = time and float(time)
#                   try:
#                       self._prefixcallbacks[cb](key, value, time,
#                                                 op != OP_TELL)
#                   except Exception:
#                       self.log.warning('error in cache callback', exc=1)
            return
        key = key[len(self._prefix):]
        time = time and float(time)
        self._propagate((time, key, op, value))
        # self.log.debug('got %s=%s' % (key, value))
        value = cache_load(value)
        with self._dblock:
            self._db[key] = (value, time)
        if key in self._callbacks and self._do_callbacks:
            self._call_callbacks(key, value, time)
