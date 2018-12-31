#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import

from nicos.services.cache.entry.serializer import CacheEntrySerializer
from nicos.services.cache.entry.serializer.flatbuffers.ns10 import \
    decode as ns10decode
from nicos.services.cache.entry.serializer.flatbuffers.ns10 import \
    encode as ns10encode


class FlatbuffersCacheEntrySerializer(CacheEntrySerializer):
    """Serializes entries using flatbuffers

    Serialization is done using flatbuffers generated helper class
    `fbentry.CacheEntry` (automatically generated using schema). The
    serialized output is a byte array which is converted to bytes
    for storing the data. The `encode` method returns the serialized
    bytes and the `decode` method can read the buffer and return the
    entry instance.
    """

    def encode(self, key, entry, schema='ns10', **params):
        if schema == 'ns10':
            return ns10encode(key, entry)
        else:
            self.log.error('Cannot encode with schema %s', schema)

    def decode(self, buf):
        identifier = buf[4:8].decode('utf-8')
        if identifier == 'ns10':
            return ns10decode(buf)
        else:
            self.log.error('Incorrect file identifier found: %s', identifier)
            return None, None
