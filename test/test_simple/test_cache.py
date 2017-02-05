#  -*- coding: utf-8 -*-
#  pylint: disable=unidiomatic-typecheck
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""Tests for the cache."""

from __future__ import print_function

from time import sleep

from nicos.devices.cacheclient import CacheClient
from nicos.core.errors import LimitError, CommunicationError
from nicos.utils import readonlylist, readonlydict

from test.utils import raises, cache_addr

session_setup = 'cachetests'


def test_float_literals(session):
    cc = session.cache
    for fv in [float('+inf'), float('-inf'), float('nan')]:
        cc.put('testcache', 'fval', fv)
        cc.flush()
        fvc = cc.get_explicit('testcache', 'fval')[2]
        # cannot compare fvc == fv, since nan is not equal to itself
        assert repr(fvc) == repr(fv)


def test_write(session):
    cc = session.cache
    testval = 'test1'
    key = 'value'
    cc.put('testcache', key, testval)
    cc.flush()
    cachedval_local = cc.get('testcache', key, None)
    cachedval = cc.get_explicit('testcache', key, None)

    assert cachedval_local == testval
    assert cachedval[2] == testval


def test_rewrite(session):
    cc = session.cache
    cc.setRewrite('testrewrite', 'testcache')
    testval = 'test2'
    key = 'value'
    cc.put('testcache', key, testval)
    cc.flush()
    cachedval1_local = cc.get('testcache', key, None)
    cachedvalrw_local = cc.get('testrewrite', key, None)
    cachedval1 = cc.get_explicit('testcache', key, None)
    cachedval2 = cc.get_explicit('testrewrite', key, Ellipsis)
    assert cachedval1_local == testval
    assert cachedvalrw_local == testval
    assert cachedval1[2] == testval
    assert cachedval2[2] == testval

    cc.unsetRewrite('testrewrite')
    testval = 'test3'
    key = 'value'
    testvalold = cc.get_explicit('testrewrite', key, Ellipsis)
    cc.put('testcache', key, testval)
    cc.flush()
    cachedval1 = cc.get('testcache', key, None)
    cachedval_rw = cc.get('testrewrite', key, None)
    cachedval2 = cc.get_explicit('testrewrite', key, Ellipsis)
    assert cachedval1 == testval
    assert cachedval2[2] == testvalold[2]
    assert cachedval2[2] != Ellipsis
    assert cachedval_rw == 'test2'  # still from test_02setRewrite


def test_write_to_rewritten(session):
    cc = session.cache
    cc.setRewrite('testrewrite2', 'testcache')
    testval1 = 'testwrite1'
    testval2 = 'testwrite2'
    testval3 = 'testwrite3'
    key = 'value'
    cc.put('testcache', key, testval1)
    cc.flush()
    cachedval1 = cc.get_explicit('testcache', key, Ellipsis)
    cc.put('testrewrite2', key, testval2)
    cc.flush()
    cachedval2 = cc.get_explicit('testrewrite2', key, Ellipsis)
    cc.setRewrite('testcache', 'testrewrite3')
    cc.put('testrewrite3', key, testval3)
    cc.flush()
    cachedval5 = cc.get_explicit('testrewrite3', key, Ellipsis)
    cachedval6 = cc.get_explicit('testcache', key, Ellipsis)

    assert cachedval1[2] == testval1
    assert cachedval2[2] == testval2
    assert cachedval5[2] == testval3
    assert cachedval6[2] == cachedval5[2]


def test_readonly_objects(session):
    cc = session.cache
    testval1 = readonlylist(('A', 'B', 'C'))
    cc.put('testcache', 'rolist', testval1)
    cc.flush()
    rol1 = cc.get('testcache', 'rolist')
    rol = cc.get_explicit('testcache', 'rolist', None)
    assert rol[2] is not None
    print(type(rol1), type(testval1))
    assert type(rol1) == type(testval1)
    assert type(rol[2]) == type(testval1)

    testval2 = readonlydict((('A', 'B'), ('C', 'D')))
    cc.put('testcache', 'rodict', testval2)
    cc.flush()
    rod = cc.get_explicit('testcache', 'rodict', None)
    assert rod[2] is not None
    print(type(rod[2]), type(testval2))
    assert type(rod[2]) == type(testval2)

    testval3 = readonlylist((testval1, testval2, 'C'))
    cc.put('testcache', 'rolist2', testval3)
    cc.flush()
    rol = cc.get_explicit('testcache', 'rolist2', None)
    assert rol[2] is not None
    print(type(rol[2]), type(testval3))
    assert type(rol[2]) == type(testval3)
    assert type(rol[2][0]) == type(testval1)
    assert type(rol[2][1]) == type(testval2)

    testval4 = readonlydict((('A', testval1), ('B', testval2), ('C', 'D')))
    cc.put('testcache', 'rodict2', testval4)
    cc.flush()
    rod = cc.get_explicit('testcache', 'rodict2', None)
    assert rod[2] is not None
    print(type(rod[2]), type(testval4))
    assert type(rod[2]) == type(testval4)
    assert type(rod[2]['A']) == type(testval1)
    assert type(rod[2]['B']) == type(testval2)


def test_cache_reader(session, log):
    rd1 = session.getDevice('reader1')
    cc = session.cache
    cc2 = CacheClient(name='cache2', prefix='nicos', cache=cache_addr)
    try:
        testval = 'testr1'
        testval2 = 'testr2'
        key = 'value'
        sleep(0.1)
        cc.clear('reader1')
        cc.flush()
        assert raises(CommunicationError, rd1.read)
        cc2.put(rd1, key, None)
        cc2.flush()
        assert rd1.read() is None

        cc2.put(rd1, key, testval)
        cc2.flush()
        assert rd1.read() == testval
        cc2.put(rd1, key, testval2)
        cc2.flush()
        # this needn't work immediately
        sleep(0.2)
        assert rd1.read() == testval2
    finally:
        cc2.shutdown()

    cc2 = CacheClient(name='cache2', prefix='nicos', cache=cache_addr)
    try:
        testval = 'testr3'
        key = 'value'
        cc.clear('reader1')
        cc.flush()
        cc2.put(rd1, key, testval, ttl=0.1)
        cc2.flush()
        # just make sure we put the value into the cache
        assert rd1.read() == testval
        sleep(0.71)  # sleep longer than ttl (0.1) + self.maxage (0.1) + 0.5
        with log.assert_warns('value timed out in cache, this should be '
                              'considered as an error!'):
            rd1.read()
    finally:
        cc2.shutdown()


def test_cache_writer(session, log):
    cc = session.cache
    cc.loglevel = 'debug'

    cc2 = CacheClient(name='cache2', prefix='nicos', cache=cache_addr)
    try:
        testval = 'testw1'
        testval2 = 'testw2'
        key = 'value'
        cc2.put('writer1', 'value', None)
        cc2.flush()
        wrt1 = session.getDevice('writer1')
        cc.clear('writer')
        assert wrt1.read() is None

        cc2.put('writer1', key, testval)
        cc2.flush()
        assert wrt1.read() == testval
        cc2.put(wrt1, key, testval2, ttl=0.1)
        cc2.flush()
        sleep(0.71)  # ttl+ wrt1.maxage
        with log.assert_warns('value timed out in cache, this should be '
                              'considered as an error!'):
            wrt1.read()
        wrt1.move(10)
        assert cc.get('writer1', 'setpoint') == 10.0
        cc.flush()
        cce = cc.get_explicit('writer1', 'setpoint')
        assert cce[2] == 10.0
        assert raises(LimitError, wrt1.move, 500)
    finally:
        cc2.shutdown()
