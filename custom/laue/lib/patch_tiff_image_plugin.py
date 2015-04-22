#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2015 by the NICOS contributors (see AUTHORS)
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
#   pedersen
#
# *****************************************************************************

"""
Patch the save function of the pillow tiff image plugin
to save float tag values as well.
"""
from __future__ import print_function

import array
import itertools
from PIL import Image
from PIL.TiffImagePlugin import native_prefix, STRIPOFFSETS, X_RESOLUTION, \
                                Y_RESOLUTION, COLORMAP, IPTC_NAA_CHUNK, \
                                PHOTOSHOP_CHUNK, ICCPROFILE, XMP
from PIL._util import isStringType  # pylint: disable=E0611,F0401


def save(self, fp):

    o16 = self.o16
    o32 = self.o32

    fp.write(o16(len(self.tags)))

    # always write in ascending tag order
    tags = sorted(self.tags.items())

    directory = []
    append = directory.append

    offset = fp.tell() + len(self.tags) * 12 + 4

    stripoffsets = None

    # pass 1: convert tags to binary format
    for tag, value in tags:

        typ = None

        if tag in self.tagtype:
            typ = self.tagtype[tag]

        if Image.DEBUG:
            print ("Tag %s, Type: %s, Value: %s" % (tag, typ, value))

        if typ == 1:
            # byte data
            if isinstance(value, tuple):
                data = value = value[-1]
            else:
                data = value
        elif typ == 7:
            # untyped data
            data = value = b"".join(value)
        elif typ in (11, 12):
            # float value
            typ = 12
            tmap = {11: 'f', 12: 'd'}
            if not isinstance(value, tuple):
                value = (value,)
            a = array.array(tmap[typ], value)
            if self.prefix != native_prefix:
                a.byteswap()
            data = a.tostring()
        elif isStringType(value[0]):
            # string data
            if isinstance(value, tuple):
                value = value[-1]
            typ = 2
            # was b'\0'.join(str), which led to \x00a\x00b sorts
            # of strings which I don't see in in the wild tiffs
            # and doesn't match the tiff spec: 8-bit byte that
            # contains a 7-bit ASCII code; the last byte must be
            # NUL (binary zero). Also, I don't think this was well
            # excersized before.
            data = value = b"" + value.encode('ascii', 'replace') + b"\0"
        else:
            # integer data
            if tag == STRIPOFFSETS:
                stripoffsets = len(directory)
                typ = 4  # to avoid catch-22
            elif tag in (X_RESOLUTION, Y_RESOLUTION) or typ == 5:
                # identify rational data fields
                typ = 5
                if isinstance(value[0], tuple):
                    # long name for flatten
                    value = tuple(itertools.chain.from_iterable(value))
            elif not typ:
                typ = 3
                for v in value:
                    if v >= 65536:
                        typ = 4
            if typ == 3:
                data = b"".join(map(o16, value))
            else:
                data = b"".join(map(o32, value))

        if Image.DEBUG:
            from PIL import TiffTags
            tagname = TiffTags.TAGS.get(tag, "unknown")
            typname = TiffTags.TYPES.get(typ, "unknown")
            print("save: %s (%d)" % (tagname, tag), end=' ')
            print("- type: %s (%d)" % (typname, typ), end=' ')
            if tag in (COLORMAP, IPTC_NAA_CHUNK, PHOTOSHOP_CHUNK,
                       ICCPROFILE, XMP):
                size = len(data)
                print("- value: <table: %d bytes>" % size)
            else:
                print("- value:", value)

        # figure out if data fits into the directory
        if len(data) == 4:
            append((tag, typ, len(value), data, b""))
        elif len(data) < 4:
            append((tag, typ, len(value), data + (4 - len(data)) * b"\0", b""))
        else:
            count = len(value)
            if typ == 5:
                count = count // 2  # adjust for rational data field

            append((tag, typ, count, o32(offset), data))
            offset += len(data)
            if offset & 1:
                offset += 1  # word padding

    # update strip offset data to point beyond auxiliary data
    if stripoffsets is not None:
        tag, typ, count, value, data = directory[stripoffsets]
        assert not data, "multistrip support not yet implemented"
        value = o32(self.i32(value) + offset)
        directory[stripoffsets] = tag, typ, count, value, data

    # pass 2: write directory to file
    for tag, typ, count, value, data in directory:
        if Image.DEBUG > 1:
            print(tag, typ, count, repr(value), repr(data))
        fp.write(o16(tag) + o16(typ) + o32(count) + value)

    # -- overwrite here for multi-page --
    fp.write(b"\0\0\0\0")  # end of directory

    # pass 3: write auxiliary data to file
    for tag, typ, count, value, data in directory:
        fp.write(data)
        if len(data) & 1:
            fp.write(b"\0")

    return offset
