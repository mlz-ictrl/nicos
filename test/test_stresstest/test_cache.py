# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS cache tests."""

import os
from time import sleep, time

import numpy
import pytest

from nicos.devices.cacheclient import CacheError
from nicos.protocols.cache import FLAG_NO_STORE

from test.utils import TestCacheClient as CacheClient, alt_cache_addr, \
    killSubprocess, raises, startCache

session_setup = 'cachestress'


def all_setups():
    yield from ['cache_db', 'cache_mem', 'cache_mem_hist']

    if os.environ.get('KAFKA_URI', None):
        yield 'cache_kafka'

    if os.environ.get('INFLUXDB_URI', None):
        yield 'cache_influxdb'


@pytest.fixture(scope='module', autouse=True)
def guard_cached_connection():
    """Use CacheClient without local caching"""

    CacheClient._use_cache = False
    yield
    CacheClient._use_cache = True


@pytest.mark.parametrize('setup', all_setups())
def test_basic(session, setup):
    cache = startCache(alt_cache_addr, setup)
    try:
        sleep(1)
        cc = session.cache
        testval = 'test1'
        key = 'value'
        cc.put('testcache', key, testval, ttl=10)
        cc.put('nostore', key, testval, ttl=10, flag=FLAG_NO_STORE)
        cc.flush()
        cachedval_local = cc.get('testcache', key, None)
        cachedval = cc.get_explicit('testcache', key, None)
        cachedval2 = cc.get_explicit('testcache', key, None)
        nostore = cc.get_explicit('nostore', key, None)

        print(cachedval_local, cachedval, cachedval2)
        assert cachedval_local == testval
        assert cachedval[2] == testval
        assert cachedval2[2] == testval
        assert nostore[2] == testval
    finally:
        killSubprocess(cache)


@pytest.mark.parametrize('setup', all_setups())
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


@pytest.mark.parametrize('setup', all_setups())
def test_history(session, setup):
    unsupported = ['cache_mem']
    if setup not in unsupported:
        cache = startCache(alt_cache_addr, setup)
        cc = session.cache
        time0 = time()
        n = 50
        for i in range(n):
            # 50 is maxentries for cache_mem_hist
            cc.put('history_test', 'value', i, time0 - (n - i) * 0.01)
        sleep(1)
        history = cc.history('history_test', 'value', time0 - (n + 1) * 0.01,
                             time())
        killSubprocess(cache)
        values = []
        for i, (_, value) in enumerate(history):
            values.append(value)
        assert values == list(range(50))


@pytest.mark.parametrize('setup', all_setups())
def test_history_interval(session, setup):
    supported = ['cache_influxdb']
    if setup in supported:
        cache = startCache(alt_cache_addr, setup)
        cc = session.cache
        time0 = time()
        n = 100
        for i in range(n):
            cc.put('history_interval_test', 'value', i, time0 - (n - i) * 0.1)
        sleep(1)
        intervals = [0, 1]
        results = []
        for interval in intervals:
            history = cc.history('history_interval_test', 'value',
                                 time0 - (n + 1) * 0.1, time(), interval)
            ts0, ts1 = 0, 0
            deltas = []
            for i, (ts, _) in enumerate(history):
                if i:
                    ts0 = ts1
                ts1 = ts
                if ts0:
                    deltas.append(ts1 - ts0)
            results.append((interval, numpy.mean(deltas),
                            interval <= numpy.mean(deltas)))
        killSubprocess(cache)
        for interval, mean, result in results:
            assert result, f'interval of {interval}s resulted in {mean}s'


@pytest.mark.parametrize('setup', all_setups())
def test_init(session, setup):
    unsupported = ['cache_mem', 'cache_mem_hist']
    if setup in unsupported:
        pytest.skip('n/a')
    unimplemented = ['cache_kafka']
    if setup in unimplemented:
        pytest.skip('not implemented')
    cache = startCache(alt_cache_addr, setup)
    cc = session.cache
    while not cc.is_connected():
        sleep(0.02)
    time0 = time()
    keys = [f'test{i}' for i in range(10)]
    n = 2
    for key in keys:
        for i in range(n):
            cc.put(f'init_{key}', 'value', i, time0 - (n - i) * 0.1)
    sleep(1)
    killSubprocess(cache)
    cache = startCache(alt_cache_addr, setup)
    cc = session.cache
    while not cc.is_connected():
        sleep(0.02)
    results = []
    for key in keys:
        results.append(cc.get(f'init_{key}', 'value'))
    killSubprocess(cache)
    assert results == [n - 1] * len(keys)
