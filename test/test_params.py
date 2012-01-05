#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

"""NICOS parameter utilities tests."""

from nicos import session
from nicos.core import UsageError, LimitError, ModeError, FixedError

from nicos.core.params import listof, nonemptylistof, tupleof, dictof, \
     tacodev, anytype, vec3, intrange, floatrange, oneof, oneofdict, none_or

from test.utils import raises


def test_param_converters():
    assert listof(int)([0., 1, '2']) == [0, 1, 2]
    assert listof(int)() == []
    assert raises(ValueError, listof(int), (1, 2, 3))

    assert nonemptylistof(int)(['1']) == [1]
    assert nonemptylistof(int)() == [0]
    assert raises(ValueError, nonemptylistof(int), [])
    assert raises(ValueError, nonemptylistof(int), (1, 2))

    assert tupleof(int, str, float)((1.0, 1.0, 1.0)) == (1, '1.0', 1.0)
    assert tupleof(int, str, float)() == (0, '', 0.0)
    assert raises(ValueError, tupleof(int, str), ('a', 'b'))
    assert raises(ValueError, tupleof(int, str), ('a',))
    assert raises(ValueError, tupleof(int, str), 'x')

    assert dictof(int, str)({1: 0, 2: 1}) == {1: '0', 2: '1'}
    assert dictof(int, str)() == {}
    assert raises(ValueError, dictof(int, str), ('a', 'b'))
    assert raises(ValueError, dictof(int, str), {'x': 'y'})

    assert tacodev('test/custom/device') == 'test/custom/device'
    assert tacodev() == ''
    assert raises(ValueError, tacodev, 'test/device')

    assert anytype('foo') == 'foo'

    assert vec3([1, 0, 0]) == [1., 0., 0.]
    assert vec3() == [0., 0., 0.]
    assert raises(ValueError, vec3, [1, 0])
    assert raises(ValueError, vec3, ['x', 'y', 'z'])

    assert intrange(0, 10)(5) == 5
    assert intrange(1, 3)() == 1
    assert raises(ValueError, intrange(0, 10), 15)
    assert raises(ValueError, intrange(0, 10), 'x')

    assert floatrange(0, 10)(5) == 5.0
    assert floatrange(1, 3)() == 1.0
    assert raises(ValueError, floatrange(0, 10), 15.)
    assert raises(ValueError, floatrange(0, 10), 'x')

    assert oneof(int, 0, 1)('0') == 0
    assert oneof(int, 2, 3)() == 2
    assert raises(ValueError, oneof(int, 0, 1), 2)
    assert raises(ValueError, oneof(int, 0, 1), 'x')

    assert oneofdict({'A': 1, 'B': 2})('A') == 1
    assert oneofdict({'A': 1, 'B': 2})(1) == 1
    assert raises(ValueError, oneofdict({}))
    assert raises(ValueError, oneofdict({'A': 1}), 2)

    assert none_or(int)(None) == None
    assert none_or(int)(5.0) == 5
    assert raises(ValueError, none_or(int), 'x')
