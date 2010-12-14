#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICM cache client support
#
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""NICM cache utils."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import re


DEFAULT_CACHE_PORT = 14869

OP_TELL = '='
OP_ASK = '?'
OP_WILDCARD = '*'
OP_SUBSCRIBE = ':'
OP_TELLOLD = '!'

# regular expression matching a cache protocol message
msg_pattern = re.compile(r'''
    ^ (?:
      \s* (?P<time>\d+\.?\d*)?    # timestamp
      \s* [+-]?                   # ttl operator
      \s* (?P<ttl>\d+\.?\d*)?     # ttl
      \s* (?P<tsop>@)             # timestamp mark
    )?
    \s* (?P<key>[^=!?:*]*?)       # key
    \s* (?P<op>[=!?:*])           # operator
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

cache_load = eval
