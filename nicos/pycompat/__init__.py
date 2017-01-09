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

"""Python 2/3 compatibility."""

__all__ = [
    'builtins', 'cPickle', 'socketserver', 'input',
    'queue', 'xrange', 'configparser', 'urllib',
    'reraise', 'exec_', 'add_metaclass', 'BytesIO', 'StringIO',
    'string_types', 'integer_types', 'text_type', 'binary_type',
    'number_types',
    'iteritems', 'itervalues', 'iterkeys', 'listitems', 'listvalues',
    'get_thread_id', 'escape_html',
]

import threading

from nicos._vendor import six

# Pylint cannot handle submodules created by "six".  Import them here to
# ignore the Pylint errors only once.
from nicos._vendor.six.moves import builtins, cPickle, socketserver  # pylint: disable=F0401
from nicos._vendor.six.moves import queue, configparser, urllib      # pylint: disable=F0401
from nicos._vendor.six.moves import xrange, input, reduce            # pylint: disable=F0401,W0622
from nicos._vendor.six.moves import zip_longest    # pylint: disable=F0401,W0622

# For consistency import everything from "six" here.
from nicos._vendor.six import reraise, exec_, add_metaclass, BytesIO, StringIO
from nicos._vendor.six import string_types, integer_types, text_type, binary_type
from nicos._vendor.six import iteritems, itervalues, iterkeys

# functionality in addition to what "six" provides

try:
    get_thread_id = threading._get_ident
except AttributeError:
    get_thread_id = threading.get_ident

try:
    from html import escape as escape_html  # pylint: disable=F0401
except ImportError:
    from cgi import escape as escape_html

# missing dict helpers to get a list of items/values

if six.PY2:
    listitems = dict.items
    listvalues = dict.values
else:
    def listitems(d):
        return list(d.items())
    def listvalues(d):
        return list(d.values())

# all builtin number types (useful for isinstance checks)

number_types = integer_types + (float,)

# missing str/bytes helpers

if six.PY2:
    # use standard file and buffer for Py2
    File = file
    memory_buffer = buffer

    # encode str/unicode (Py2) or str (Py3) to bytes, using UTF-8
    def to_utf8(s):
        if isinstance(s, str):
            return s
        return s.encode('utf-8')  # will complain for any other type
    # encode str/unicode (Py2) or str (Py3) to bytes, using selected encoding
    def to_encoding(s, encoding, errors='strict'):
        if isinstance(s, str):
            return s
        return s.encode(encoding, errors)
    def from_utf8(s):
        if isinstance(s, unicode):
            return s
        return s.decode('utf-8')
    from_maybe_utf8 = from_utf8
    def from_encoding(s, encoding, errors='strict'):
        if isinstance(s, unicode):
            return s
        return s.decode(encoding, errors)
    def srepr(u):
        """repr() without 'u' prefix for Unicode strings."""
        if isinstance(u, unicode):
            return repr(u.encode('unicode-escape'))
        return repr(u)
    def to_ascii_escaped(s):
        """Encode to ASCII with any non-printables backslash-escaped."""
        if isinstance(s, str):
            s = s.decode('ascii', 'ignore')
        return s.encode('unicode-escape')
    to_ascii_string = to_ascii_escaped
    # on Py2, io.TextIOWrapper exists but only accepts Unicode objects
    class TextIOWrapper(object):
        def __init__(self, fp):
            self.fp = fp
        def write(self, s):
            if isinstance(s, unicode):
                s = s.encode('utf-8')
            self.fp.write(s)
        def detach(self):
            pass
        def __getattr__(self, att):
            return getattr(self.fp, att)
else:
    from io import FileIO, BufferedWriter
    # create file like class for py3
    class File(BufferedWriter):
        def __init__(self, filepath, openmode):
            self._raw = FileIO(filepath, openmode)
            BufferedWriter.__init__(self, self._raw)

    # on Py3, UTF-8 is the default encoding already
    to_utf8 = str.encode
    to_encoding = str.encode
    from_utf8 = bytes.decode
    from_encoding = bytes.decode
    def from_maybe_utf8(s):
        if isinstance(s, str):
            return s
        return s.decode()
    srepr = repr
    memory_buffer = memoryview
    def to_ascii_escaped(s):
        if isinstance(s, bytes):
            s = s.decode('ascii', 'ignore')
        return s.encode('unicode-escape')
    def to_ascii_string(s):
        return s.encode('unicode-escape').decode('ascii')
    from io import TextIOWrapper
