#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
    'iteritems', 'itervalues', 'iterkeys', 'listitems', 'listvalues',
    'OrderedDict', 'get_thread_id', 'escape_html',
]

import six
import threading

# Pylint cannot handle submodules created by "six".  Import them here to
# ignore the Pylint errors only once.
from six.moves import builtins, cPickle, socketserver  # pylint: disable=F0401
from six.moves import queue, configparser, urllib      # pylint: disable=F0401
from six.moves import xrange, input  # pylint: disable=F0401,W0622

# For consistency import everything from "six" here.
from six import reraise, exec_, add_metaclass, BytesIO, StringIO
from six import string_types, integer_types, text_type, binary_type
from six import iteritems, itervalues, iterkeys

try:
    from collections import OrderedDict  # pylint: disable=E0611
except ImportError:
    from ordereddict import OrderedDict

try:
    get_thread_id = threading._get_ident
except AttributeError:
    get_thread_id = threading.get_ident

try:
    from html import escape as escape_html  # pylint: disable=F0401
except ImportError:
    from cgi import escape as escape_html

if six.PY2:
    listitems = dict.items
    listvalues = dict.values
else:
    def listitems(d):
        return list(d.items())
    def listvalues(d):
        return list(d.values())
