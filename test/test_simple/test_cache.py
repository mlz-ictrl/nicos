#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

from nicos import session

def setup_module():
    session.loadSetup('cachetests')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()


def test_float_literals():
    cc = session.cache
    for fv in [float('+inf'), float('-inf'), float('nan')]:
        cc.put('testcache', 'fval', fv)
        cc.flush()
        fvc = cc.get_explicit('testcache', 'fval')[2]
        assert repr(fvc) == repr(fv)   # cannot compare fvc == fv, since
                                       # nan is not equal to itself

def test_01write():
    cc = session.cache
    testval = 'test1'
    key = 'value'
    cc.put('testcache', key, testval)
    cc.flush()
    cachedval_local = cc.get('testcache', key, None)
    cachedval = cc.get_explicit('testcache', key, None)

    assert cachedval_local == testval
    assert cachedval[2] == testval

def test_02setRewrite():
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

def test_03unsetRewrite():
    cc = session.cache
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

def test_04writeToRewritten():
    cc = session.cache
    cc.setRewrite('testrewrite2', 'testcache')
    testval1 = 'testwrite1'
    testval2 = 'testwrite2'
    testval3 = 'testwrite3'
    key = 'value'
    cc.put('testcache', key, testval1)
    cc.flush()
    cachedval1 =  cc.get_explicit('testcache', key, Ellipsis)
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
