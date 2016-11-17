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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Tests for the setupSpec tests used to selectively show GUI elements
in dependence of loaded_setups.
"""

from __future__ import print_function

from nicos.guisupport.utils import checkSetupSpec, DoubleValidator, \
    extractKeyAndIndex

# Importing this AFTER nicos.guisupport to have the correct SIP API set.
from PyQt4.QtGui import QValidator


# setupspec : loaded_setups : result
CASES = [
    (None,         None,            True),
    (None,         ['a', 'b', 'c'], True),
    ('a',          ['a', 'b', 'c'], True),
    ('a and d',    ['a', 'b', 'c'], False),
    ('a and b',    ['a', 'b', 'c'], True),
    ('a or d',     ['a', 'b', 'c'], True),
    ('a or b',     ['a', ], True),
    ('a or b',     ['b', ], True),
    ('a or b',     [], False),
    ('a or b',     ['c', ], False),
    ('a*',         ['alpha', 'b'],  True),
    ('c*',         ['alpha', 'b'],  False),
    ('(b and not (c or h)', ['b'], True),
    ('(b and not (c or h))', ['b', 'c'], False),
    ('(b and not (c or h))', ['b', 'h'], False),
    ('(b and not (c or h))', ['b', 'c', 'h'], False),
    ('(b and not (c or h))', [], False),
    ('(b and not (c or h))', ['h'], False),
    ('(b and not (c or h))', ['h', 'c'], False),
    ('a and',      ['b'],           True),  # warns
    # compatibility cases
    (['a'],        ['a', 'b', 'c'], True),
    ('!a',         ['a', 'b', 'c'], False),
    (['!a'],       ['a', 'b', 'c'], False),
    (['a', 'd'],   ['a', 'b', 'c'], True),
    (['d'],        ['a', 'b', 'c'], False),
    (['!d'],       ['a', 'b', 'c'], True),
    (['a', '!d'],  ['a', 'b', 'c'], True),
    (['!a', 'd'],  ['a', 'b', 'c'], False),
    (['!a', '!d'], ['a', 'b', 'c'], True),
]


def test_checkSetupSpec():
    for spec, setups, result in CASES:
        # print is here to aid in finding the offending input parameters
        # as the stacktrace doesn't output locals
        res = checkSetupSpec(spec, setups)
        print('testing checkSetupSpec(%r, %r) == %r: %r' %
              (spec, setups, result, res))
        assert res == result


def test_double_validator():
    inf = float('inf')
    # valid cases
    validator = DoubleValidator()
    for args in [
            ('0', -inf, inf),
            ('0.0', -inf, inf),
            ('0.0e0', -inf, inf),
            ('-0.0', -inf, inf),
            ('1.23456789123456789e130', -inf, inf),
            ('0', -1, 1),
            ('0', 0, inf),
            ('0', -inf, 0),
    ]:
        validator.setBottom(args[1])
        validator.setTop(args[2])
        assert validator.validate(args[0], 0)[0] == QValidator.Acceptable
    # intermediate cases
    for args in [
            ('4', 10, 50),
            ('-4', -50, -10),
            ('1.0e', -inf, inf),
            ('0', 10, 20),
    ]:
        validator.setBottom(args[1])
        validator.setTop(args[2])
        assert validator.validate(args[0], 0)[0] == QValidator.Intermediate
    # invalid cases
    for args in [
            ('-15', 10, 20),
            ('-1', 10, 20),
            ('+15', -20, -10),
            ('+1', -20, -10),
            ('1,5', 0, 10),
    ]:
        validator.setBottom(args[1])
        validator.setTop(args[2])
        assert validator.validate(args[0], 0)[0] == QValidator.Invalid


def test_extract_key_and_index():
    assert extractKeyAndIndex('dev') == ('dev/value', (), 1, 0)
    assert extractKeyAndIndex('dev.key') == ('dev/key', (), 1, 0)
    assert extractKeyAndIndex('dev.key[0]') == ('dev/key', (0,), 1, 0)
    assert extractKeyAndIndex('dev.key[0][1]') == ('dev/key', (0, 1), 1, 0)
    assert extractKeyAndIndex('dev[0][1]') == ('dev/value', (0, 1), 1, 0)
    assert extractKeyAndIndex('dev[0,1]') == ('dev[0,1]', (), 1, 0)
    assert extractKeyAndIndex('dev.key[0][ 1]') == ('dev/key', (0, 1), 1, 0)
    assert extractKeyAndIndex('dev.key[ 0][ 1]') == ('dev/key', (0, 1), 1, 0)
    assert extractKeyAndIndex('dev.key[ 0 ][ 1]') == ('dev/key', (0, 1), 1, 0)
    assert extractKeyAndIndex('dev.key[ 0 ][ 1 ]') == ('dev/key', (0, 1), 1, 0)
    assert extractKeyAndIndex('dev.key[10 ][ 1]') == ('dev/key', (10, 1), 1, 0)
    assert extractKeyAndIndex('dev.key[0') == ('dev/key[0', (), 1, 0)
    assert extractKeyAndIndex('dev.key0]') == ('dev/key0]', (), 1, 0)
    assert extractKeyAndIndex('dev.key*10') == ('dev/key', (), 10, 0)
    assert extractKeyAndIndex('dev.key +5') == ('dev/key', (), 1, 5)
    assert extractKeyAndIndex('dev.key- 5') == ('dev/key', (), 1, -5)
    assert extractKeyAndIndex('dev.key*10 +5') == ('dev/key', (), 10, 5)
    assert extractKeyAndIndex('dev.key[0] * 10+5') == ('dev/key', (0,), 10, 5)
    assert extractKeyAndIndex('dev*1.2e1 +5e-2') == ('dev/value', (), 12, 0.05)
    assert extractKeyAndIndex('dev*1e+1+5e1') == ('dev/value', (), 10, 50)
