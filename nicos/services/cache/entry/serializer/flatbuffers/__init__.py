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
from streaming_data_types.nicos_cache_ns10 import deserialise_ns10, \
    serialise_ns10
from nicos.services.cache.entry import CacheEntry
from nicos.services.cache.entry.serializer import CacheEntrySerializer


class FlatbuffersCacheEntrySerializer(CacheEntrySerializer):
    """Serializes entries using flatbuffers

    Serialization is done using flatbuffers generated helper class within an
    auto-generated schema-specific submodule. The serialized output is a byte
    array which is converted to bytes for storing the data. The `encode` method
    returns the serialized bytes and the `decode` method can read the buffer
    and return the entry instance.
    """

    def encode(self, key, entry, schema='ns10', **params):
        try:
            ttl = entry.ttl if entry.ttl else 0
            return serialise_ns10(key, entry.value, entry.time, ttl,
                                  entry.expired)
        except Exception as error:
            self.log.error('Cannot encode ns10 cache entry: %s', error)

    def decode(self, buf):
        try:
            ns_entry = deserialise_ns10(buf)
            key = ns_entry.key if ns_entry.key.strip() else None
            ttl = ns_entry.ttl if ns_entry.ttl != 0 else None
            value = ns_entry.value if ns_entry.value else None

            entry = CacheEntry(ns_entry.time_stamp, ttl, value)
            entry.expired = ns_entry.expired
            return key, entry
        except Exception as error:
            self.log.error('Could not decode ns10 cache entry: %s', error)
            return None, None
