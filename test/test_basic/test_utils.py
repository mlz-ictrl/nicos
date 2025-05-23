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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""NICOS tests for some utility modules."""

import os
import pickle
import socket
import sys
from datetime import timedelta
from time import mktime, monotonic, sleep

import pytest

from nicos.core.errors import NicosError
from nicos.core.sessions.utils import SimClock
from nicos.utils import KEYEXPR_NS, TB_CAUSE_MSG, Repeater, allDays, \
    bitDescription, checkSetupSpec, chunks, closeSocket, comparestrings, \
    expandTemplate, formatDuration, formatExtendedFrame, formatExtendedStack, \
    formatExtendedTraceback, lazy_property, moveOutOfWay, num_sort, \
    parseConnectionString, parseDuration, parseKeyExpression, \
    readFileCounter, readonlydict, readonlylist, safeName, safeWriteFile, \
    squeeze, tcpSocket, timedRetryOnExcept, tupelize, updateFileCounter
from nicos.utils.timer import Timer


def test_lazy_property():
    asked = []

    class P:
        @lazy_property
        def prop(self):
            asked.append('x')
            return 'ok'
    p = P()
    assert p.prop == 'ok'
    assert p.prop == 'ok'  # ask twice!
    assert len(asked) == 1  # but getter only called once


def test_readonly_objects():
    d = readonlydict({'a': 1, 'b': 2})
    pytest.raises(TypeError, d.update, {})

    # pickle Protocoll 0
    unpickled = pickle.loads(pickle.dumps(d))
    assert isinstance(unpickled, readonlydict)
    assert len(unpickled) == 2
    # pickle Protocoll 2
    unpickled = pickle.loads(pickle.dumps(d, 2))
    assert isinstance(unpickled, readonlydict)
    assert len(unpickled) == 2

    lst = readonlylist([1, 2, 3])
    pytest.raises(TypeError, lst.append, 4)

    # pickle Protocoll 0
    unpickled = pickle.loads(pickle.dumps(lst))
    assert isinstance(unpickled, readonlylist)
    assert len(unpickled) == 3
    # pickle Protocoll 2
    unpickled = pickle.loads(pickle.dumps(lst, 2))
    assert isinstance(unpickled, readonlylist)
    assert len(unpickled) == 3


def test_readonlylist_hashable():
    lst = readonlylist([1, 2, 3])
    assert lst == [1, 2, 3]
    dt = {lst: 'testval'}
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
    assert formatDuration(7199) == '2 h, 0 min'
    assert formatDuration(3700) == '1 h, 2 min'
    assert formatDuration(24 * 3600 + 7240, precise=False) == '1 day, 2 h'
    assert formatDuration(48 * 3600 - 1) == '2 days, 0 h'

    assert bitDescription(0x5,
                          (0, 'a'),
                          (1, 'b', 'c'),
                          (2, 'd', 'e')) == 'a, c, d'

    assert parseConnectionString('u-ser@user.de:pass@host:1301', 1302) == \
        {'user': 'u-ser@user.de', 'password': 'pass', 'host': 'host',
         'port': 1301}
    assert parseConnectionString('user:@host', 1302) == \
        {'user': 'user', 'password': '', 'host': 'host', 'port': 1302}
    assert parseConnectionString('user@host:1301', 1302) == \
        {'user': 'user', 'password': None, 'host': 'host', 'port': 1301}
    assert parseConnectionString('user@ho-st:1301', 1302) == \
        {'user': 'user', 'password': None, 'host': 'ho-st', 'port': 1301}
    assert parseConnectionString('', 1302) is None
    assert parseConnectionString('host?', 1302) is None

    assert [tuple(x) for x in chunks(range(10), 3)] == \
        [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]


def test_traceback():
    a = 1  # pylint: disable=unused-variable
    f = sys._getframe()
    fmt = formatExtendedFrame(f)
    assert any('a                    = 1' in line for line in fmt)

    try:
        try:
            1 / 0
        except ZeroDivisionError as err:
            raise RuntimeError from err
    except Exception:
        ei = sys.exc_info()
        tb = formatExtendedTraceback(ei[1])
        assert 'ZeroDivisionError' in tb
        assert 'RuntimeError' in tb
        assert TB_CAUSE_MSG in tb
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
    pytest.raises(NicosError, wr, x)

    # Make sure we get success if inner succeeds
    x = 2
    ret = wr2(x)
    assert ret == 3

    # assert we get
    x = 0
    pytest.raises(Exception, wr3, x)
    assert x == 0


@pytest.fixture()
def serversocket():
    """create a server socket"""

    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serv.bind(('localhost', 65432))
        serv.listen(10)
    except Exception:
        pytest.skip('could not bind')
    yield serv
    closeSocket(serv)


def test_tcpsocket(serversocket):
    sock = None

    sockargs = [
        ('localhost:65432', 1),
        ('localhost', 65432),
        (('localhost', 65432), 1, dict(timeout=5))
    ]
    for args in sockargs:
        try:
            if len(args) == 3:
                kwds = args[2]
                args = args[:2]
                sock = tcpSocket(*args, **kwds)
            else:
                sock = tcpSocket(*args)
        finally:
            if sock:
                closeSocket(sock)


def test_timer():
    t = monotonic()

    def cb(tmr, x, y=None):
        if x == 3 and y == 'ykwd':
            tmr.cb_called = True

    def nf(tmr, info):
        if info == 'notify':
            tmr.notify_called = True

    def nf1(tmr):
        tmr.notify_called = 'yes'

    # a) test a (short) timed timer
    tmr = Timer(0.1, cb, cb_args=(3,), cb_kwds={'y': 'ykwd'})
    assert tmr.is_running()
    while (monotonic() - t < 1.5) and tmr.is_running():
        sleep(0.05)
    assert not tmr.is_running()
    assert tmr.cb_called
    assert tmr.elapsed_time() == 0.1
    assert tmr.remaining_time() == 0
    tmr.restart()
    # timer timed out, can not restart
    assert not tmr.is_running()

    # b) test an unlimited timer (for a short while)
    tmr.start()
    sleep(0.02)  # due to windows time() resolution
    assert tmr.is_running()
    assert tmr.elapsed_time() > 0
    assert tmr.remaining_time() is None
    sleep(0.1)
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
    sleep(0.1)
    tmr.stop()
    tmr.restart()
    tmr.wait(interval=0.1, notify_func=nf, notify_args=('notify',))
    assert tmr.notify_called
    tmr.start(run_for=0.5)
    tmr.wait(0.1, nf1)
    assert tmr.notify_called == 'yes'


def test_num_sort():
    # purely alpha keys
    assert sorted(['a', 'c', 'b'], key=num_sort) == ['a', 'b', 'c']
    # mixed with floats
    assert sorted(['X', '12A', '2.4B'], key=num_sort) == ['2.4B', '12A', 'X']
    # also negative ones
    assert sorted(['X', '-1', '2'], key=num_sort) == ['-1', '2', 'X']
    # handle invalid floats
    assert sorted(['X', '1A', '2.4.5A'], key=num_sort) == ['1A', '2.4.5A', 'X']
    # handle non-strings too
    assert sorted([0.4, '1A'], key=num_sort) == [0.4, '1A']


# setupspec : loaded_setups : result
CASES = [
    (None,         None,            True),
    (None,         ['a', 'b', 'c'], True),
    ('a',          ['a', 'b', 'c'], True),
    ('a and d',    ['a', 'b', 'c'], False),
    ('a and b',    ['a', 'b', 'c'], True),
    ('a or d',     ['a', 'b', 'c'], True),
    ('a or b',     ['a'], True),
    ('a or b',     ['b'], True),
    ('a or b',     [], False),
    ('a or b',     ['c'], False),
    ('a*',         ['alpha', 'b'],  True),
    ('c*',         ['alpha', 'b'],  False),
    ('c-d*',       ['c-de'], True),
    ('(b and not (c or h)', ['b'], True),
    ('(b and not (c or h))', ['b', 'c'], False),
    ('(b and not (c or h))', ['b', 'h'], False),
    ('(b and not (c or h))', ['b', 'c', 'h'], False),
    ('(b and not (c or h))', [], False),
    ('(b and not (c or h))', ['h'], False),
    ('(b and not (c or h))', ['h', 'c'], False),
    ('a and',      ['b'],           True),  # warns
    ('a?', ['a1'], True),
    ('a? or c', ['c'], True),
    ('a?', ['a12', 'a2'], True),
    ('a?', ['a12', 'a34'], False),
]

OLDSTYLE_CASES = [
    # old style cases
    (['a'],        ['a', 'b', 'c'], True),
    ('!a',         ['a', 'b', 'c'], True),
    (['!a'],       ['a', 'b', 'c'], True),
    (['a', 'd'],   ['a', 'b', 'c'], True),
    (['d'],        ['a', 'b', 'c'], True),
    (['!d'],       ['a', 'b', 'c'], True),
    (['a', '!d'],  ['a', 'b', 'c'], True),
    (['!a', 'd'],  ['a', 'b', 'c'], True),
    (['!a', '!d'], ['a', 'b', 'c'], True),
]


def test_check_setup_spec():
    for spec, setups, result in CASES + OLDSTYLE_CASES:
        # print is here to aid in finding the offending input parameters
        # as the stacktrace doesn't output locals
        res = checkSetupSpec(spec, setups)
        print('testing checkSetupSpec(%r, %r) == %r: %r' %
              (spec, setups, result, res))
        assert res == result


def test_parse_key_expression():
    assert parseKeyExpression('dev.key')[0] == 'dev/key'
    assert parseKeyExpression('dev.key', normalize=lambda s: s)[0] == \
        'dev.key/value'
    assert parseKeyExpression('dev.key', False, normalize=lambda s: s)[0] == \
        'dev.key'

    key, expr, _ = parseKeyExpression('dev + 1')
    assert key == 'dev/value'
    assert eval(expr, {}, {'x': 42}) == 43

    _, expr, _ = parseKeyExpression('100/(dev/key)/10')
    assert eval(expr, {}, {'x': 2}) == 5

    _, expr, _ = parseKeyExpression('sqrt(key)')
    assert eval(expr, KEYEXPR_NS, {'x': 25}) == 5

    _, _, descs = parseKeyExpression('a/b, c.d*2, sqrt(e)', multiple=True)
    assert descs == [
        'a/b',
        'c.d*2',
        'sqrt(e)'
    ]


def test_squeeze():
    assert isinstance(squeeze([]), list)
    assert isinstance(squeeze(tuple()), tuple)

    assert squeeze((256, 256, 1)) == (256, 256)
    assert squeeze((1, 10, 1)) == (10, )
    assert squeeze((1, 1, 1), 2) == (1, 1)
    assert squeeze((1, 10, 1), -1) == (1, 10)
    assert squeeze((1, 10, 1), 1) == (1, 10)
    assert squeeze((1, ), 2) == (1, )  # n > len(shape)


@pytest.mark.parametrize('maxbackup', [2, None, 0])
def test_moveOutOfWay(tmpdir, maxbackup):
    i = 0
    fn1 = str(tmpdir.join('test1'))
    while i < 3:
        with open(fn1, 'w', encoding='utf-8') as fp:
            fp.write('Test %r %i' % (maxbackup, i))
        moveOutOfWay(fn1, maxbackup)
        i += 1

    files = [f for f in os.listdir(str(tmpdir)) if f.startswith('test1')]
    assert 'test1' not in files
    assert len(files) == maxbackup if maxbackup is not None else 3


@pytest.mark.parametrize(('inp', 'expected'), [
    ['1d:2h:3m:14s', 93794],
    ['1d2h 3m  14s', 93794],
    ['1d :2h: 3m : 14s ', 93794],
    ['1day 2hr 2min 74sec', 93794],
    ['5days', 5*86400],
    [93794, 93794],
    ['0.5h', 1800],
    [1.0, 1.0],
    ['2.0', 2.0],
    ['1h:0.005s', 3600.005],
    [timedelta(hours=2), 7200],
    ['-20s', -20],
    ['+30m', 1800],
    ['-2500', -2500],
    [-50, -50],
    [-2.71828, -2.71828],
])
def test_parse_duration(inp, expected):
    assert parseDuration(inp, allownegative=True) == expected


@pytest.mark.parametrize('inp', [
    '1m3d',
    '1d::3m',
    '1d:3m jad',
    '42secop',
    '-2m',
    -50,
    '-3.1415',
    '+-5d',
])
def test_parse_duration_parse_errors(inp):
    pytest.raises(ValueError, parseDuration, inp)


@pytest.mark.parametrize('inp', [
    [1, 2, 3],
    {'days': 5},
])
def test_parse_duration_type_errors(inp):
    pytest.raises(TypeError, parseDuration, inp)


def test_all_days():
    # 25. Oct 2020 switch CEST -> CET
    exp_list = [('2020', '10-24'), ('2020', '10-25'), ('2020', '10-26'),
                ('2020', '10-27'), ('2020', '10-28')]
    # 28. Oct 2020, 08:00:00
    tmto = mktime((2020, 10, 28, 8, 0, 0, 0, 0, -1))
    assert list(allDays(tmto - 86400, tmto)) == exp_list[3:]
    assert list(allDays(tmto - 2 * 86400, tmto)) == exp_list[2:]
    assert list(allDays(tmto - 3 * 86400, tmto)) == exp_list[1:]
    assert list(allDays(tmto - 4 * 86400, tmto)) == exp_list

    # 28. Mar 2020 switch CET -> CEST
    exp_list = [('2020', '03-27'), ('2020', '03-28'), ('2020', '03-29'),
                ('2020', '03-30'), ('2020', '03-31')]
    # 31. Mar 2020, 08:00:00
    tmto = mktime((2020, 3, 31, 8, 0, 0, 0, 0, 1))
    assert list(allDays(tmto - 86400, tmto)) == exp_list[3:]
    assert list(allDays(tmto - 2 * 86400, tmto)) == exp_list[2:]
    assert list(allDays(tmto - 3 * 86400, tmto)) == exp_list[1:]
    assert list(allDays(tmto - 4 * 86400, tmto)) == exp_list


@pytest.mark.parametrize('name', [('COM1', '_COM1_'),
                                  ('xyz.txt', 'xyz.txt')])
def test_safeName(name):
    assert safeName(name[0]) == name[1]


@pytest.mark.parametrize('maxbackup', [2, None, 0])
@pytest.mark.parametrize('content', ['XXXXX', ['XXXX\n', 'YYYYY\n']])
def test_safeWriteFile(tmpdir, maxbackup, content):
    i = 0
    fn1 = str(tmpdir.join('test1'))
    while i < 3:
        safeWriteFile(fn1, content, maxbackups=maxbackup)
        i += 1
    files = [f for f in os.listdir(str(tmpdir)) if f.startswith('test1')]
    assert 'test1' in files
    assert len(files) == maxbackup + 1 if maxbackup is not None else 4
    with open(fn1, encoding='utf-8') as fp:
        if isinstance(content, list):
            assert len(fp.readlines()) == len(content)
        else:
            assert len(fp.read()) == len(content)


def test_tupelize():
    ilist = ['a', 1, 'b', 2, 'c', 3]
    assert list(tupelize(ilist)) == [('a', 1), ('b', 2), ('c', 3)]
    assert list(tupelize(ilist[:3])) == [('a', 1)]
    assert list(tupelize(ilist, 3)) == [('a', 1, 'b'), (2, 'c', 3)]
    assert list(tupelize(ilist[:4], 3)) == [('a', 1, 'b')]


@pytest.fixture(scope='function')
def nonexistantfile(tmpdir):
    fc1 = str(tmpdir.join('testcounter1'))
    try:
        os.unlink(fc1)
    except FileNotFoundError:
        pass
    yield fc1
    try:
        os.unlink(fc1)
    except FileNotFoundError:
        pass


@pytest.fixture(scope='function')
def filecounterfile(tmpdir):
    fc = str(tmpdir.join('testcounter2'))
    with open(fc, 'w', encoding='utf-8') as f:
        f.write('key1 1234\n')
        f.write('key2 5678\n')
    yield fc
    os.unlink(fc)


def test_readfilecounter_exist(filecounterfile):
    assert readFileCounter(filecounterfile, 'key1') == 1234
    assert readFileCounter(filecounterfile, 'key3') == 0


def test_readfilecounter_nofile(nonexistantfile):
    assert readFileCounter(nonexistantfile, 'key') == 0
    assert os.path.exists(nonexistantfile)


def test_updatefilecounter_exist(filecounterfile):
    updateFileCounter(filecounterfile, 'key1', 222)
    assert readFileCounter(filecounterfile, 'key1') == 222
    assert readFileCounter(filecounterfile, 'key2') == 5678


def test_updatefilecounter_nofile(nonexistantfile):
    updateFileCounter(nonexistantfile, 'key', 9876)
    assert os.path.exists(nonexistantfile)
    assert readFileCounter(nonexistantfile, 'key') == 9876


def test_simclock():
    clock = SimClock()

    # unconditional tick
    clock.tick(2)
    assert clock.time == 2

    # conditional waits, the maximum wins
    clock.wait(5)
    clock.wait(7)
    assert clock.time == 7

    clock.reset()
    assert clock.time == 0


@pytest.mark.parametrize(
    ('expr', 'expected', 'defaulted_keys', 'missing_keys'), [
    ('literal', 'literal', [], []),
    ('a{{b}}c', 'axc', [], []),
    ('a{{key}}b', 'ab', [], ['key']),
    ('a{{key!replace}}b', 'ab', [], ['key']),
    ('a{{key:default}}b', 'adefaultb', ['key'], []),
    ('a{{key!replace:default}}b', 'adefaultb', ['key'], []),
    ('a{{quo}}b', 'aqb', [], []),
    ('a{{quo!replace}}b', 'areplaceb', [], []),
    ('a{{quo:default}}b', 'aqb', [], []),
    ('a{{quo!replace:default}}b', 'areplaceb', [], []),
    ('a{{c!r}}c', 'arc', [], []),
    ('a{{{{c:b}}r}}c', 'arc', [], []),
    ('{{a{{{{c:b}}r}}c}}', 'True', [], []),
    ('{{q!}}', '', [], ['q']),
    ('{{b!}}', '', [], []),
    ],
)
def test_expandTemplate(expr, expected, defaulted_keys, missing_keys):
    kwds = dict(b='x', c='c!', arc=True, quo='q')
    res, defaulted, missing = expandTemplate(expr, kwds)
    assert expected == res
    assert [e['key'] for e in defaulted] == defaulted_keys
    assert [e['key'] for e in missing] == missing_keys


@pytest.mark.parametrize(
    ('expr', 'expected', 'defaulted_keys', 'missing_keys'), [
    ('{{key1}}', '{{key1}}', [], []),
    ('{{{{key1!key1}}}}', '{{key1}}', [], []),
    ],
)
def test_expandTemplateRecursion(expr, expected, defaulted_keys, missing_keys):
    kwds = dict(key1='{{key1}}')
    res, defaulted, missing = expandTemplate(expr, kwds)
    assert expected == res
    assert [e['key'] for e in defaulted] == defaulted_keys
    assert [e['key'] for e in missing] == missing_keys
