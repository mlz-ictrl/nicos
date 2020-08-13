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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Python compatibility."""

from __future__ import absolute_import, division, print_function

from io import BufferedWriter, FileIO

# For consistency import everything from "six" here.
from six import iteritems, itervalues, reraise

# functionality in addition to what "six" provides

# missing dict helpers to get a list of items/values
def listitems(d):
    return list(d.items())


def listvalues(d):
    return list(d.values())


# all builtin number types (useful for isinstance checks)

number_types = (int, float)


# create file like class for py3
class File(BufferedWriter):
    def __init__(self, filepath, openmode):
        self._raw = FileIO(filepath, openmode)
        BufferedWriter.__init__(self, self._raw)


# missing str/bytes helpers
# on Py3, UTF-8 is the default encoding already
to_utf8 = str.encode
to_encoding = str.encode
from_utf8 = bytes.decode
from_encoding = bytes.decode


def from_maybe_utf8(s):
    if isinstance(s, str):
        return s
    return s.decode()


def memory_buffer(obj):
    # For numpy arrays, memoryview() keeps info about the element size and
    # shape, so that len() gives unexpected results compared to buffer().
    # Casting to a pure byte view gets rid of that.
    return memoryview(obj).cast('B')


def to_ascii_escaped(s):
    if isinstance(s, bytes):
        s = s.decode('ascii', 'ignore')
    return s.encode('unicode-escape')


def to_ascii_string(s):
    return s.encode('unicode-escape').decode('ascii')


try:
    # numpy 1.14+ compat
    import numpy
    numpy.set_printoptions(sign=' ')
except Exception:
    pass


__all__ = [
    'reraise', 'number_types',
    'iteritems', 'itervalues', 'listitems', 'listvalues',
]
