#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""NICOS tests for some utility modules."""

from __future__ import print_function

import sys
import socket

from nicos.utils import lazy_property, Repeater, formatDuration, chunks, \
    bitDescription, parseConnectionString, formatExtendedFrame, \
    formatExtendedTraceback, formatExtendedStack, readonlylist, readonlydict, \
    comparestrings, timedRetryOnExcept, tcpSocket, closeSocket
from nicos.pycompat import cPickle as pickle
from nicos.core.errors import NicosError

from test.utils import raises, SkipTest


def test_lazy_property():
    asked = []

    class P(object):
        @lazy_property
        def prop(self):
            asked.append('x')
            return 'ok'
    p = P()
    assert p.prop == 'ok'
    assert p.prop == 'ok'   # ask twice!
    assert len(asked) == 1  # but getter only called once


def test_readonly_objects():
    d = readonlydict({'a': 1, 'b': 2})
    assert raises(TypeError, d.update, {})

    # pickle Protocoll 0
    unpickled = pickle.loads(pickle.dumps(d))
    assert type(unpickled) is readonlydict
    assert len(unpickled) == 2
    # pickle Protocoll 2
    unpickled = pickle.loads(pickle.dumps(d, 2))
    assert type(unpickled) is readonlydict
    assert len(unpickled) == 2

    l = readonlylist([1, 2, 3])
    assert raises(TypeError, l.append, 4)

    # pickle Protocoll 0
    unpickled = pickle.loads(pickle.dumps(l))
    assert type(unpickled) is readonlylist
    assert len(unpickled) == 3
    # pickle Protocoll 2
    unpickled = pickle.loads(pickle.dumps(l, 2))
    assert type(unpickled) is readonlylist
    assert len(unpickled) == 3


def test_readonlylist_hashable():
    l = readonlylist([1, 2, 3])
    assert l == [1, 2, 3]
    dt = {l: 'testval'}
    print(dt.keys())
    assert dt[readonlylist([1, 2, 3])] == 'testval'


def test_repeater():
    r = Repeater(1)
    it = iter(r)
    assert next(it) == 1
    assert next(it) == 1
    assert r[23] == 1


def test_functions():
    assert formatDuration(154) == '3 minutes'
    assert formatDuration(24*3600 + 7240) == '1 day, 2 hours'

    assert bitDescription(0x5,
                          (0, 'a'),
                          (1, 'b', 'c'),
                          (2, 'd', 'e')) == 'a, c, d'

    assert parseConnectionString('user:pass@host:1301', 1302) == \
        ('user', 'pass', 'host', 1301)

    assert list(map(tuple, chunks(range(10), 3))) == \
        [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]


def test_traceback():
    a = 1  # pylint: disable=W0612
    f = sys._getframe()
    fmt = formatExtendedFrame(f)
    assert any('a                    = 1' in line for line in fmt)

    try:
        1/0
    except ZeroDivisionError:
        ei = sys.exc_info()
        tb = formatExtendedTraceback(*ei)
        assert 'ZeroDivisionError' in tb
        assert ', in test_traceback' in tb

    st = formatExtendedStack()
    assert ', in test_traceback' in st


def test_comparestrings():
    comparestrings.test()


def test_retryOnExcept():
    def raising_func(x):
        x += 1
        if x < 2:
            raise NicosError
        return x

    @timedRetryOnExcept(timeout=0.2)
    def wr(x):
        x = raising_func(x)
        return x

    @timedRetryOnExcept(max_retries=3, timeout=0.2)
    def wr2(x):
        x = raising_func(x)
        return x

    def raising_func2(x):
        if x < 2:
            raise Exception('test exception')
        return x

    @timedRetryOnExcept(ex=NicosError, timeout=0.2)
    def wr3(x):
        x = raising_func2(x)
        return x

    # Make sure we get the inner error in case of too many retries
    x = 0
    assert raises(NicosError, wr, x)

    # Make sure we get success if inner succeeds
    x = 2
    ret = wr2(x)
    assert ret == 3

    # assert we get
    x = 0
    assert raises(Exception, wr3, x)
    assert x == 0


def test_tcpsocket():
    # create a server socket
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serv.bind(('localhost', 65432))
        serv.listen(10)
    except Exception:
        raise SkipTest

    # now connect to it using several ways
    try:
        sock = tcpSocket('localhost:65432', 1)
        closeSocket(sock)
        sock = tcpSocket('localhost', 65432)
        closeSocket(sock)
        sock = tcpSocket(('localhost', 65432), 1, timeout=5)
        closeSocket(sock)
    finally:
        closeSocket(serv)
