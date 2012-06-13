#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS cache utils."""

__version__ = "$Revision$"

import re
import ast
import cPickle as pickle
from time import time, localtime
from base64 import b64encode, b64decode


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
      \s* (?P<ttlop>[+-]?)        # ttl operator
      \s* (?P<ttl>\d+\.?\d*(?:[eE][+-]?\d+)?)?     # ttl
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
    elif obj is None:
        return 'None'
    else:
        try:
            resstr = 'cache_unpickle("' + \
                     b64encode(pickle.dumps(obj, protocol=0)) + '")'
            res.append(resstr)
        except Exception, err:
            raise ValueError('unserializable object: %r (%s)' % (obj, err))
    return ''.join(res)

def cache_load(entry):
    try:
        # parsing with 'eval' always gives an ast.Expression node
        expr = ast.parse(entry, mode='eval').body
        if isinstance(expr, ast.Call) and expr.func.id == 'cache_unpickle':
            return pickle.loads(b64decode(ast.literal_eval(expr.args[0])))
        else:
            return ast.literal_eval(expr)
    except Exception, err:
        raise ValueError('corrupt cache entry: %r (%s)' % (entry, err))


# cache entry support

class Entry(object):
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


# determine days of an interval between two timestamps

def all_days(fromtime, totime):
    tmfr = int(fromtime)
    tmto = int(min(time(), totime))
    for tmday in xrange(tmfr, tmto+1, 86400):
        lt = localtime(tmday)
        yield str(lt[0]), '%02d-%02d' % lt[1:3]
