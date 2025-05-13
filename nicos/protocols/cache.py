# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""
Cache protocol documentation
============================

* The Cache server listens by default on TCP and UDP port 14869 (it will also
  receive UDP broadcasts).

* The protocol is line-based.  The basic syntax for a line (requests and
  responses) is ::

    [time1] [+|-] [time2] [@] key [flags] op [value] newline

  The ``op`` is one character and decides the basic meaning of the request or
  response.  Symbolic constants for the ``op`` are defined in the module
  :mod:`nicos.protocols.cache`.

  The ``newline`` can be LF or CRLF.

* Keys are hierarchic, with levels separated by an arbitrary number of slashes.

* All values are strings.  The cache server does not interpret them in any way,
  but the NICOS clients do.

Setting a key
-------------

Operation: ``OP_TELL`` or ``'='``

- ``time1`` is the UNIX timestamp of the value.
- ``time2`` is the TTL (time to live) in seconds, after which the key expires.
- Both are optional: time1 defaults to current time, ttl to no expiration.
- Instead of ``time+ttl@``, ``time-expirationtime@`` is also supported.
  TTL is then ``expirationtime - time``.
- Without any value, the key is deleted.

Examples::

  1327504784.71+5@nicos/temp/value=5.003     # explicit time and ttl given
  nicos/temp/setpoint=5                      # no time and ttl given
  +5@nicos/temp/value=1.102                  # only ttl given
  nicos/temp/value=                          # key deletion

Response: none.

Querying a single key
---------------------

Operation: ``OP_ASK`` or ``'?'``

- When an ``@`` is present, the timestamp is returned with the reply.
- With ``time1-time2@`` or ``time1+timeinterval@``, a history query is made and
  several values can be returned.
- The value, if present, is ignored.

Examples::

  nicos/temp/value?                         # request only the value
  @nicos/temp/value?                        # request value with timestamp
  1327504780-1327504790@nicos/temp/value?   # request all values in time range

Response: except for history queries, a single line in the form ``key=value``
or ``time@key=value``, see below.  If the key is nonexistent or expired, the
form is ``[time@]key!`` or ``[time@]key!value``.  For history queries, a number
of lines of the same form.

Querying with wildcard
----------------------

Operation: ``OP_WILDCARD`` or ``'*'``

- Matching is done by a simple substring search: all keys for which the
  requested key is a substring are returned.
- History queries are not allowed.
- Like for op '?', timestamps are returned if ``@`` is present.
- The value, if present, is ignored.

Examples::

  nicos/temp/*                              # request only values
  @nicos/temp/*                             # request values with timestamps

Response: each value whose key contains the key given is returned as a single
line as for single query.

Subscribing to updates
----------------------

Operation: ``OP_SUBSCRIBE`` or ``':'``

- Matching is done by a simple substring search: the subscription is for all
  keys for which the requested key is a substring.
- When a @ is present, the updates contain the timestamp.

Response: none immediately, but every update matching the given key is sent to
the client, either as ``[time@]key=value`` or ``[time@]key!value`` (if the key
has expired).

Unsubscribing updates
---------------------

Operation: ``OP_UNSUBSCRIBE`` or ``'|'``

- Key must be the same as for the subscription.
- Unsubscribing keys which were never subscribed has no side effects.

Response: none immediately, no updates for the specified keys will be sent
anymore.

Locking
-------

Operation: ``OP_LOCK`` or ``'$'``

The lock mechanism allows only one client at the same time to obtain a lock on
a given identifier.  This can be used to synchronize access of multiple NICOS
clients to a shared resource (but is slow!).

- ``time1`` is the time when the lock is requested (default current time).
- ``time2`` is the ttl for the lock.  It defaults to 1800 seconds.
- ``key`` is the identifier for the lock.
- ``value`` must be either ``+clientid`` (lock) or ``-clientid`` (unlock);
  clientid is a string uniquely identifying the client.

Response:

- on lock: one of ::

    key$otherclientid      # already locked by other client, request denied
    key$                   # locked successfully

- on unlock: one of ::

    key$otherclientid      # not locked by this client, request denied
    key$                   # unlocked successfully

Key rewriting
-------------

Operation: ``OP_REWRITE`` or ``'~'``

The cache supports storing incoming keys under multiple prefixes (definition of
prefix: for "nicos/dev/value" the key prefix is "nicos/dev").

- ``key`` is the additional prefix.
- ``value`` is either ``prefix`` (add rewrite) or nothing (remove rewrite).

For example, after ::

    nicos/t~nicos/tcryo

all incoming keys with prefix "nicos/tcryo" will be set in the cache with
prefix "nicos/tcryo" and "nicos/t" (and also written in the store files, if the
cache is configured for that).

Response: none.

Optional Flags
--------------

Optional flags can be put between a key and the operator, i.e. they append
the key.  So far only one flag is defined:

FLAG_NO_STORE (``'#'``)
  Avoids storing the update in an on-disk-database.  The flag is removed by the
  cache server before any updates are handled, i.e. no client will ever see it.
  Its use is intented for particular noisy actions which don't need to be
  stored on disk.  Only the updates with this flag will not be stored, so a
  client can select this feature for each request.

Works only with the "set a key" operator.  This flag makes no sense otherwise.

"""

import pickle
import re
from ast import Add, BinOp, Call, Constant, Dict, List, Name, Set, Sub, \
    Tuple, UnaryOp, USub, parse
from base64 import b64decode, b64encode

from nicos.utils import number_types, readonlydict, readonlylist

DEFAULT_CACHE_PORT = 14869

OP_TELL = '='
OP_ASK = '?'
OP_WILDCARD = '*'
OP_SUBSCRIBE = ':'
OP_UNSUBSCRIBE = '|'
OP_TELLOLD = '!'
OP_LOCK = '$'
OP_REWRITE = '~'

OP_LOCK_LOCK = '+'
OP_LOCK_UNLOCK = '-'

# put flags between key and op...
FLAG_NO_STORE = '#'

# end/sync special token
END_MARKER = '###'
SYNC_MARKER = '#sync#'

# Time constant
CYCLETIME = 0.1


# Buffer size
BUFSIZE = 8192

opkeys = OP_TELL + OP_ASK + OP_WILDCARD + OP_SUBSCRIBE + OP_UNSUBSCRIBE + \
    OP_TELLOLD + OP_LOCK + OP_REWRITE

# regular expression matching a cache protocol message
msg_pattern = re.compile(r"""
    ^ (?:
      \s* (?P<time>\d+\.?\d*)?                   # timestamp
      \s* (?P<ttlop>[+-]?)                       # ttl operator
      \s* (?P<ttl>\d+\.?\d*(?:[eE][+-]?\d+)?)?   # ttl
      \s* (?P<tsop>@)                            # timestamp mark
    )?
    \s* (?P<key>[^%(opkeys)s]*?)                     # key
    \s* (?P<op>[%(opkeys)s])                        # operator
    \s* (?P<value>[^\r\n]*?)                     # value
    \s* $
    """ % dict(opkeys=opkeys), re.X)

line_pattern = re.compile(br'([^\r\n]*)\r?\n')


# PyON -- "Python object notation"

repr_types = number_types + (str, bytes)


def cache_dump(obj):
    res = []
    if isinstance(obj, repr_types):
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
        for key, value in obj.items():
            res.append(cache_dump(key))
            res.append(':')
            res.append(cache_dump(value))
            res.append(',')
        res.append('}')
    elif isinstance(obj, frozenset):
        res.append('{')
        for item in obj:
            res.append(cache_dump(item))
            res.append(',')
        res.append('}')
    elif obj is None:
        return 'None'
    else:
        try:
            resstr = 'cache_unpickle("' + \
                b64encode(pickle.dumps(obj, protocol=0)).decode() + '")'
            res.append(resstr)
        except Exception as err:
            raise ValueError(
                'unserializable object: %r (%s)' % (obj, err)) from err
    return ''.join(res)


_safe_names = {'None': None, 'True': True, 'False': False,
               'inf': float('inf'), 'nan': float('nan')}


def ast_eval(node):
    # copied from Python 2.7 ast.py, but added support for float inf/-inf/nan
    def _convert(node):
        if isinstance(node, Constant):
            return node.value
        elif isinstance(node, Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, List):
            return readonlylist(map(_convert, node.elts))
        elif isinstance(node, Dict):
            return readonlydict((_convert(k), _convert(v)) for k, v
                                in zip(node.keys, node.values))
        elif isinstance(node, Set):
            return frozenset(map(_convert, node.elts))
        elif isinstance(node, Name):
            if node.id in _safe_names:
                return _safe_names[node.id]
        elif isinstance(node, UnaryOp) and \
                isinstance(node.op, USub) and \
                isinstance(node.operand, Name) and \
                node.operand.id in _safe_names:
            return -_safe_names[node.operand.id]
        elif isinstance(node, UnaryOp) and \
                isinstance(node.op, USub) and \
                isinstance(node.operand, Constant):
            return -node.operand.value
        elif isinstance(node, BinOp) and \
                isinstance(node.op, (Add, Sub)) and \
                isinstance(node.right, Constant) and \
                isinstance(node.right.value, complex) and \
                isinstance(node.left, Constant) and \
                isinstance(node.left.value, number_types):
            left = node.left.value
            right = node.right.value
            if isinstance(node.op, Add):
                return left + right
            else:
                return left - right
        elif isinstance(node, Call) and \
                isinstance(node.func, Name) and \
                node.func.id == 'cache_unpickle':
            return pickle.loads(b64decode(ast_eval(node.args[0])))
        raise ValueError('malformed literal string with %s' % node)
    return _convert(node)


def cache_load(entry):
    try:
        # parsing with 'eval' always gives an ast.Expression node
        expr = parse(entry, mode='eval').body
        return ast_eval(expr)
    except Exception as err:
        raise ValueError(
            'corrupt cache entry: %r (%s)' % (entry, err)) from err
