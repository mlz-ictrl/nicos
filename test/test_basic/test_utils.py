#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

import sys
import cPickle as pickle

from nicos.utils import lazy_property, Repeater, formatDuration, chunks, \
     bitDescription, parseConnectionString, formatExtendedFrame, \
     formatExtendedTraceback, formatExtendedStack, readonlylist, readonlydict, \
     comparestrings

from test.utils import raises


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
    unpickled = pickle.loads(pickle.dumps(d))
    assert type(unpickled) is dict
    assert len(unpickled) == 2
    l = readonlylist([1, 2, 3])
    assert raises(TypeError, l.append, 4)
    unpickled = pickle.loads(pickle.dumps(l))
    assert type(unpickled) is list
    assert len(unpickled) == 3

def test_repeater():
    r = Repeater(1)
    it = iter(r)
    assert it.next() == 1
    assert it.next() == 1
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

    assert map(tuple, chunks(range(10), 3)) == [(0, 1, 2),
                                                (3, 4, 5),
                                                (6, 7, 8),
                                                (9,)]

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
