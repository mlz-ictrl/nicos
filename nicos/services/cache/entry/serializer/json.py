#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from json import JSONDecoder, JSONEncoder

from nicos.services.cache.entry import CacheEntry
from nicos.services.cache.entry.serializer import CacheEntrySerializer


class JsonCacheEntrySerializer(CacheEntrySerializer):
    """Encodes the entry object to JSON format.

    For encoding, first converts the entry object to a python dict and then
    uses the inbuilt JSON encoder to serialize to JSON object.  For decoding,
    converts the JSON object to python dict and then to the entry class.
    """

    def doInit(self, mode):
        self._encoder = JSONEncoder()
        self._decoder = JSONDecoder()

    def encode(self, key, entry, **params):
        entry_dict = entry.asDict()
        entry_dict['key'] = key
        return self._encoder.encode(entry_dict)

    def decode(self, coded):
        edict = self._decoder.decode(coded)
        entry = CacheEntry(edict['time'], edict['ttl'], edict['value'])
        entry.expired = edict['expired']
        key = edict['key']
        return key, entry
