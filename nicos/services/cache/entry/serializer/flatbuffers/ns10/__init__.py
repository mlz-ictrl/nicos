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

from nicos import session
from nicos.pycompat import to_utf8
from nicos.services.cache.entry import CacheEntry as NicosCacheEntry

try:
    import flatbuffers
    from nicos.services.cache.entry.serializer.flatbuffers.ns10 import \
        CacheEntry as CacheEntryFB
except ImportError:
    flatbuffers = None
    CacheEntryFB = None

file_identifier = 'ns10'


def encode(key, entry):
    # Start with a buffer which can automatically grow
    builder = flatbuffers.Builder(136)

    # Create the strings - this has to be done before starting to build
    value_fb_str = None
    if entry.value is not None:
        value_fb_str = builder.CreateString(entry.value)
    key_fb_str = builder.CreateString(key)

    # Start building the buffer.
    # Flatbuffer must be constructed in the reverse order of the schema.
    # This might be a bug in flatbuffers.
    CacheEntryFB.CacheEntryStart(builder)
    if value_fb_str:
        CacheEntryFB.CacheEntryAddValue(builder, value_fb_str)
    CacheEntryFB.CacheEntryAddExpired(builder, entry.expired)
    # Do not write ttl if it is None
    if entry.ttl is not None:
        CacheEntryFB.CacheEntryAddTtl(builder, entry.ttl)
    CacheEntryFB.CacheEntryAddTime(builder, entry.time)
    CacheEntryFB.CacheEntryAddKey(builder, key_fb_str)
    fb_entry = CacheEntryFB.CacheEntryEnd(builder)
    builder.Finish(fb_entry, file_identifier=to_utf8(file_identifier))

    # Generate the output and replace the file_identifier
    fb_array = builder.Output()

    return bytes(fb_array)


def decode(buf):
    # Check for the correct file identifier
    identifier = buf[4:8].decode('utf-8')
    if identifier != file_identifier:
        session.log.error('Incorrect file identifier found: %s', identifier)
        return None, None

    # Convert the buffer to FB class
    fb_entry = CacheEntryFB.CacheEntry.GetRootAsCacheEntry(buf, 0)

    # Capture the default values of key, ttl and set them to None
    key = fb_entry.Key() if fb_entry.Key() else None
    ttl = fb_entry.Ttl() if fb_entry.Ttl() != 0 else None

    # Try to get the value if it was written
    try:
        value = fb_entry.Value()
    except Exception:
        value = None

    entry = NicosCacheEntry(fb_entry.Time(), ttl, value)
    entry.expired = bool(fb_entry.Expired())
    return key, entry
