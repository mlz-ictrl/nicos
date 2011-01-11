#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""NICOS cache utils."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import re
import struct


DEFAULT_CACHE_PORT = 14869

OP_TELL = '='
OP_ASK = '?'
OP_WILDCARD = '*'
OP_SUBSCRIBE = ':'
OP_TELLOLD = '!'
OP_LOCK = '$'

# regular expression matching a cache protocol message
msg_pattern = re.compile(r'''
    ^ (?:
      \s* (?P<time>\d+\.?\d*)?    # timestamp
      \s* [+-]?                   # ttl operator
      \s* (?P<ttl>\d+\.?\d*)?     # ttl
      \s* (?P<tsop>@)             # timestamp mark
    )?
    \s* (?P<key>[^=!?:*$]*?)      # key
    \s* (?P<op>[=!?:*$])          # operator
    \s* (?P<value>[^\r\n]*?)      # value
    \s* $
    ''', re.X)

line_pattern = re.compile(r'([^\r\n]*)(\r\n|\r|\n)')


# PyON -- "Python object notation"

def cache_dump(obj):
    res = []
    if isinstance(obj, (int, long, bool, float, str, unicode)):
        res.append(repr(obj))
    elif isinstance(obj, list):
        res.append('[')
        for item in obj:
            res.append(cache_dump(item))
            res.append(',')
        res.append(']')
    elif isinstance(obj, tuple):
        res.append('(')
        for item in obj:
            res.append(cache_dump(item))
            res.append(',')
        res.append(')')
    elif isinstance(obj, dict):
        res.append('{')
        for key, value in obj.iteritems():
            res.append(cache_dump(key))
            res.append(':')
            res.append(cache_dump(value))
            res.append(',')
        res.append('}')
    else:
        raise ValueError('unserializable object: %r' % obj)
    return ''.join(res)

cache_load = eval  # TODO: rewrite as a safer function


# cache entry support

class Entry(object):
    __slots__ = ('time', 'ttl', 'value')

    def __init__(self, time, ttl, value):
        self.time = time
        self.ttl = ttl
        self.value = value


# Struct for saving entries:
# 1 byte   marker (0x1E, "record separator")
# 8 bytes  time
# 8 bytes  ttl
# 2 bytes  length of value string
head = struct.Struct('bddH')

def dump_entries(entries):
    """Dump a list of entries as a bytestring."""
    return ''.join(head.pack(0x1E, e.time, (e.ttl or 0.), len(e.value or ''))
                   + (e.value or '') for e in entries)


def load_entries(bytes):
    """Load a list of entries from a bytestring."""
    entries = []
    headsize = head.size
    i = 0
    n = len(bytes)
    try:
        while i < n:
            rs, time, ttl, valuelen = head.unpack_from(bytes, i)
            assert rs == 0x1E
            i += valuelen + headsize
            entries.append(Entry(time, ttl or None, bytes[i-valuelen:i] or None))
        return entries
    except (AssertionError, struct.error):
        return []


def load_last_entry(bytes):
    """Load the last entry from the bytestring."""
    i = -head.size + 1
    # Since the RS can also occur in the binary format of time or ttl,
    # search backwards until a consistent entry is found.
    while 1:
        i = bytes.rfind('\x1E', 0, i)
        if i == -1:
            return None
        try:
            rs, time, ttl, valuelen = head.unpack_from(bytes, i)
        except struct.error:
            continue
        if i + headsize + valuelen != len(bytes):
            continue
        return Entry(time, ttl or None,
                     bytes[i+headsize:i+headsize+valuelen] or None)
