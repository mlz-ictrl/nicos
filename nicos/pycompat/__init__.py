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
