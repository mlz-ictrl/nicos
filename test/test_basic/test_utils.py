#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
import time
import socket

from nicos.utils import lazy_property, Repeater, formatDuration, chunks, \
    bitDescription, parseConnectionString, formatExtendedFrame, \
    formatExtendedTraceback, formatExtendedStack, readonlylist, readonlydict, \
    comparestrings, timedRetryOnExcept, tcpSocket, closeSocket
from nicos.utils.timer import Timer
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
    assert isinstance(unpickled, readonlydict)
    assert len(unpickled) == 2
    # pickle Protocoll 2
    unpickled = pickle.loads(pickle.dumps(d, 2))
    assert isinstance(unpickled, readonlydict)
    assert len(unpickled) == 2

    l = readonlylist([1, 2, 3])
    assert raises(TypeError, l.append, 4)

    # pickle Protocoll 0
    unpickled = pickle.loads(pickle.dumps(l))
    assert isinstance(unpickled, readonlylist)
    assert len(unpickled) == 3
    # pickle Protocoll 2
    unpickled = pickle.loads(pickle.dumps(l, 2))
    assert isinstance(unpickled, readonlylist)
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
    assert formatDuration(1) == '1 second'
    assert formatDuration(4) == '4 seconds'
    assert formatDuration(154, precise=False) == '3 min'
    assert formatDuration(154, precise=True) == '2 min, 34 sec'
    assert formatDuration(3700) == '1 h, 2 min'
    assert formatDuration(24*3600 + 7240, precise=False) == '1 day, 2 h'

    assert bitDescription(0x5,
                          (0, 'a'),
                          (1, 'b', 'c'),
                          (2, 'd', 'e')) == 'a, c, d'

    assert parseConnectionString('user:pass@host:1301', 1302) == \
        {'user': 'user', 'password': 'pass', 'host': 'host', 'port': 1301}
    assert parseConnectionString('user:@host:1301', 1302) == \
        {'user': 'user', 'password': '', 'host': 'host', 'port': 1301}
    assert parseConnectionString('user@host:1301', 1302) == \
        {'user': 'user', 'password': None, 'host': 'host', 'port': 1301}

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


def test_timer():
    t = time.time()

    def cb(tmr, x):
        if x == 3:
            tmr.cb_called = True
    # a) test a (short) timed timer
    tmr = Timer(0.1, cb, 3)
    assert tmr.is_running()
    while (time.time() - t < 1.5) and tmr.is_running():
        time.sleep(0.05)
    assert not tmr.is_running()
    assert tmr.cb_called
    assert tmr.elapsed_time() == 0.1
    assert tmr.remaining_time() == 0
    tmr.restart()
    # timer timed out, can not restart
    assert not tmr.is_running()

    # b) test an unlimited timer (for a short while)
    tmr.start()
    time.sleep(0.02)  # due to windows time.time() resolution
    assert tmr.is_running()
    assert tmr.elapsed_time() > 0
    assert tmr.remaining_time() is None
    time.sleep(0.1)
    assert 0.1 < tmr.elapsed_time() < 0.2
    tmr.stop()
    # check elapsed time for stopped timer
    assert 0.1 < tmr.elapsed_time() < 0.2
    assert not(tmr.is_running())
    assert not(tmr.wait())

    # c) stopping before timeout and then restart
    tmr.restart()
    tmr.restart()

    tmr.start(run_for=0.5)
    time.sleep(0.1)
    tmr.stop()
    tmr.restart()
    tmr.wait(interval=0.1)
