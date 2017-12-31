#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

from json import JSONDecoder, JSONEncoder

from nicos.core import Device
from nicos.core.errors import ProgrammingError

try:
    import flatbuffers
    from nicos.services.cache.database.fbentry import \
        CacheEntry as CacheEntryFB
except ImportError:
    flatbuffers = None
    CacheEntryFB = None


class CacheEntry(object):
    __slots__ = ('time', 'ttl', 'value', 'expired')

    def __init__(self, time, ttl, value):
        self.time = time
        self.ttl = ttl
        self.value = value
        self.expired = False

    def __repr__(self):
        if self.expired:
            return '(%s+%s@%s)' % (self.time, self.ttl, self.value)
        return '%s+%s@%s' % (self.time, self.ttl, self.value)

    def asDict(self):
        return {x: getattr(self, x) for x in self.__slots__}


class CacheEntrySerializer(Device):
    """Base class to serialize and de-serialize the entries for cache

    Following methods must be implemented in the derived classes:
    * encode(entry, key)
    where `entry` represents the instance to be serialized and the `key`
    is the NICOS key for which this entry is written. Writing `key` is
    optional but a desired feature.

    * decode(entry) : returns tuple of (key, entry)
    The decode method should return a key and entry tuple decoded from
    the message.
    """

    def encode(self, entry, key=''):
        raise ProgrammingError('Encoder not implemented')

    def decode(self, entry):
        raise ProgrammingError('Decoder not implemented')


class JsonCacheEntrySerializer(CacheEntrySerializer):
    """Encodes the entry object to JSON format

    For encoding, first converts the entry object to a python dict and then
    uses the inbuilt JSON encoder to serialize to JSON object.
    For decoding, converts the JSON object to python dict and then to the
    entry class
    """

    def doInit(self, mode):
        self._encoder = JSONEncoder()
        self._decoder = JSONDecoder()

    def encode(self, entry, key=''):
        entry_dict = entry.asDict()
        if key:
            entry_dict['key'] = key
        return self._encoder.encode(entry_dict)

    def decode(self, coded):
        edict = self._decoder.decode(coded)
        entry = CacheEntry(edict['time'], edict['ttl'], edict['value'])
        entry.expired = edict['expired']
        key = edict['key'] if 'key' in edict else None
        return key, entry


class FlatbuffersCacheEntrySerializer(CacheEntrySerializer):
    """Serializes entries using flatbuffers

    Serialization is done using flatbuffers generated helper class
    `fbentry.CacheEntry` (automatically generated using schema). The
    serialized output is a byte array which is converted to bytes
    for storing the data. The `encode` method returns the serialized
    bytes and the `decode` method can read the buffer and return the
    entry instance.
    """

    # Unique identifier for the flatbuffers schema
    # This has to be 4 characters long
    file_identifier = 'ns10'

    def encode(self, entry, key=''):
        # Start with a buffer which can automatically grow
        builder = flatbuffers.Builder(136)

        # Create the buffered strings for key and value
        # This has to be done before starting to build
        try:
            value_fb_str = builder.CreateString(entry.value)
        except TypeError:
            value_fb_str = None

        try:
            key_fb_str = builder.CreateString(key)
        except TypeError:
            key_fb_str = None

        # Start building the buffer
        CacheEntryFB.CacheEntryStart(builder)

        # Do not write the key if it is None
        if key_fb_str:
            CacheEntryFB.CacheEntryAddKey(builder, key_fb_str)

        # Do not write the value if it is None
        if value_fb_str:
            CacheEntryFB.CacheEntryAddValue(builder, value_fb_str)

        CacheEntryFB.CacheEntryAddExpired(builder, entry.expired)
        CacheEntryFB.CacheEntryAddTime(builder, entry.time)

        # Do not write ttl if it is None
        if entry.ttl is not None:
            CacheEntryFB.CacheEntryAddTtl(builder, entry.ttl)

        fb_entry = CacheEntryFB.CacheEntryEnd(builder)
        builder.Finish(fb_entry)

        # Generate the output and replace the file_identifier
        fb_array = builder.Output()
        fb_array[4:8] = bytes(self.file_identifier)

        return bytes(fb_array)

    def decode(self, buf):

        # Check for the correct file identifier
        identifier = buf[4:8].decode('utf-8')
        if identifier != self.file_identifier:
            self.log.debug('Incorrect file identifier found: %s', identifier)
            return None, None

        # Convert the buffer to FB class
        fb_entry = CacheEntryFB.CacheEntry.GetRootAsCacheEntry(buf, 0)

        # Capture the default values of key, ttl and value and set them to None
        key = fb_entry.Key() if fb_entry.Key() != 0 else None
        ttl = fb_entry.Ttl() if fb_entry.Ttl() != 0 else None
        value = fb_entry.Value() if fb_entry.Value() else None

        entry = CacheEntry(fb_entry.Time(), ttl, value)
        entry.expired = bool(fb_entry.Expired())
        return key, entry
