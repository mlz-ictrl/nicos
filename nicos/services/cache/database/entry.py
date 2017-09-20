#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
