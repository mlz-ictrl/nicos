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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""New Cache reader/writer devices."""

from nicos.devices.generic.cache import CacheReader as NicosCacheReader, \
    CacheWriter as NicosCacheWriter
from nicos.core import CommunicationError, CacheError
from time import time as currenttime


class CacheReader( NicosCacheReader ):
    def doRead(self, maxage=0):
        if self._cache:
            try:
                time, ttl, val = self._cache.get_explicit(self, 'value')
            except CacheError:
                val = time = ttl = None
            if time and ttl:
                if time + ttl > currenttime():
                    return val
                self.log.warning('Cache Value timed out, this should be considered as error!')
                return val
            else:
                return val    # always valid
        raise CommunicationError(self, 'CacheReader value not in cache or no cache found')

class CacheWriter( NicosCacheWriter ):
    def doRead(self, maxage=0):
        if self._cache:
            try:
                time, ttl, val = self._cache.get_explicit(self, 'value')
            except CacheError:
                val = time = ttl = None
            if time and ttl:
                if time + ttl > currenttime():
                    return val
                self.log.warning('Cache Value timed out, this should be considered as error!')
                return val
            else:
                return val    # always valid
        raise CommunicationError(self, 'CacheReader value not in cache or no cache found')
