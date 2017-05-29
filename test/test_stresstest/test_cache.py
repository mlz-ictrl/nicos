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

"""NICOS cache tests."""

from __future__ import print_function

from time import sleep

import pytest

from nicos.devices.cacheclient import CacheError

from test.utils import startCache, killSubprocess, alt_cache_addr, raises, \
    TestCacheClient as CacheClient

session_setup = 'cachestress'

all_setups = ['cache_db', 'cache_mem', 'cache_mem_hist']


@pytest.yield_fixture(scope='module', autouse=True)
def guard_cached_connection():
    """Use CacheClient without local caching"""

    CacheClient._use_cache = False
    yield
    CacheClient._use_cache = True


@pytest.mark.parametrize('setup', all_setups)
def test_basic(session, setup):
    cache = startCache(alt_cache_addr, setup)
    try:
        sleep(1)
        cc = session.cache
        testval = 'test1'
        key = 'value'
        cc.put('testcache', key, testval, ttl=10)
        cc.flush()
        cachedval_local = cc.get('testcache', key, None)
        cachedval = cc.get_explicit('testcache', key, None)
        cachedval2 = cc.get_explicit('testcache', key, None)

        print(cachedval_local, cachedval, cachedval2)
        assert cachedval_local == testval
        assert cachedval[2] == testval
        assert cachedval2[2] == testval
    finally:
        killSubprocess(cache)


@pytest.mark.parametrize('setup', all_setups)
def test_restart(session, setup):
    cc = session.cache
    testval = 'test2'
    key = 'value'

    cc.put('testcache', key, testval)
    cachedval_local = cc.get('testcache', key, None)
    assert raises(CacheError, cc.get_explicit, 'testcache', key, None)
    sleep(1)
    cache = startCache(alt_cache_addr, setup)
    try:
        sleep(1)
        cc.flush()
        cachedval2 = cc.get_explicit('testcache', key, None)

        print(cachedval2)
        assert cachedval_local == testval
        assert cachedval2[2] == testval
    finally:
        killSubprocess(cache)
