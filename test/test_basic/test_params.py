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
#
# *****************************************************************************

"""NICOS parameter utilities tests."""

from nicos.core.params import listof, nonemptylistof, tupleof, dictof, \
     tacodev, tangodev, anytype, vec3, intrange, floatrange, oneof, oneofdict, \
     none_or, limits, mailaddress, Param, Value
from nicos.core.errors import ProgrammingError

from test.utils import raises

def test_param_class():
    assert str(Param('my parameter')) == '<Param info>'
    text = Param('my parameter', prefercache=True).formatDoc()
    assert text == 'Parameter: my parameter\n\n    * Type: float\n    * ' \
                   'Default value: ``0.0``\n    * Not settable at runtime\n' \
                   '    * Prefer value from cache: True'

def test_listof():
    assert listof(int)([0., 1, '2']) == [0, 1, 2]
    assert listof(int)() == []
    # should also accept tuples
    assert listof(int)((1, 2, 3)) == [1, 2, 3]
    assert raises(ValueError, listof(int), 10)
    # assert that the list is read-only
    assert raises(TypeError, listof(int)([0, 1, 2]).__setitem__, 0, 1)

def test_nonemptylistof():
    assert nonemptylistof(int)(['1']) == [1]
    assert nonemptylistof(int)() == [0]
    # should also accept tuples
    assert nonemptylistof(int)((1, 2)) == [1, 2]
    assert raises(ValueError, nonemptylistof(int), [])
    assert raises(ValueError, nonemptylistof(int), 10)
    # assert that the list is read-only
    assert raises(TypeError, nonemptylistof(int)([0, 1, 2]).__setitem__, 0, 1)

def test_tupleof():
    assert tupleof(int, str, float)((1.0, 1.0, 1.0)) == (1, '1.0', 1.0)
    assert tupleof(int, str, float)() == (0, '', 0.0)
    assert tupleof(float, float)() == (0.0, 0.0)
    assert raises(ValueError, tupleof(int, str), ('a', 'b'))
    assert raises(ValueError, tupleof(int, str), ('a',))
    assert raises(ValueError, tupleof(int, str), 'x')
    assert raises(ProgrammingError, tupleof,)

def test_dictof():
    assert dictof(int, str)({1: 0, 2: 1}) == {1: '0', 2: '1'}
    assert dictof(int, str)() == {}
    assert raises(ValueError, dictof(int, str), ('a', 'b'))
    assert raises(ValueError, dictof(int, str), {'x': 'y'})
    # test that the dict is read-only
    assert raises(TypeError, dictof(int, str)({1: 'x'}).pop, 1)

def test_tacodev():
    assert tacodev('test/custom/device') == 'test/custom/device'
    assert tacodev('test/custom/device1') == 'test/custom/device1'
    assert tacodev('test1/custom1/device1') == 'test1/custom1/device1'
    assert tacodev('1/2/3') == '1/2/3'
    assert tacodev() == ''
    assert raises(ValueError, tacodev, '/taco23/test/custom/device')
    assert raises(ValueError, tacodev, 'test/device')

def test_tangodev():
    assert tangodev('tango://host:123/test/custom/device') == \
        'tango://host:123/test/custom/device'
    assert tangodev() == ''
    assert raises(ValueError, tangodev, 'test/custom/device')

def test_anytype():
    assert anytype('foo') == 'foo'

def test_vec3():
    assert vec3([1, 0, 0]) == [1., 0., 0.]
    assert vec3() == [0., 0., 0.]
    assert raises(ValueError, vec3, [1, 0])
    assert raises(ValueError, vec3, ['x', 'y', 'z'])
    # assert that the list is read-only
    assert raises(TypeError, vec3([0, 1, 2]).__setitem__, 0, 1)

def test_intrange():
    assert intrange(0, 10)(10) == 10
    assert intrange(1, 3)() == 1
    assert raises(ValueError, intrange(0, 10), 15)
    assert raises(ValueError, intrange(0, 10), 'x')
    assert raises(ValueError, intrange, 2, 1)

def test_floatrange():
    assert floatrange(0, 10)(5) == 5.0
    assert floatrange(1, 3)() == 1.0
    assert raises(ValueError, floatrange(0, 10), 15.)
    assert raises(ValueError, floatrange(0, 10), 'x')
    assert raises(ValueError, floatrange, 2, 1)

def test_oneof():
    assert oneof(0, 1)(1) == 1
    assert oneof(2, 3)() == 2
    assert raises(ValueError, oneof(0, 1), '0')
    assert raises(ValueError, oneof(0, 1), 2)
    assert raises(ValueError, oneof(0, 1), 'x')

def test_oneofdict():
    assert oneofdict({'A': 1, 'B': 2})('A') == 1
    assert oneofdict({'A': 1, 'B': 2})(1) == 1
    assert raises(ValueError, oneofdict({}))
    assert raises(ValueError, oneofdict({'A': 1}), 2)

    assert none_or(int)(None) == None
    assert none_or(int)(5.0) == 5
    assert raises(ValueError, none_or(int), 'x')

def test_limits():
    assert limits((-10, 10)) == (-10, 10)
    assert limits((0, 0)) == (0, 0)
    assert limits() == (0, 0)
    assert limits([-10, 10]) == (-10, 10)
    assert raises(ValueError, limits, (1,))
    assert raises(ValueError, limits, 1)
    assert raises(ValueError, limits, (10, 10, 10))
    assert raises(TypeError, limits, 1, 1)
    assert raises(ValueError, limits, (10, -10))
    assert raises(ValueError, limits, ('a', 'b'))

def test_mailaddress():
    assert mailaddress() == ''
    assert mailaddress('my.address@domain.my') == 'my.address@domain.my'
    assert mailaddress('my_address@domain.my') == 'my_address@domain.my'
    assert mailaddress('myaddress@domain.my') == 'myaddress@domain.my'
    assert mailaddress('myaddress+local@my.domain.my') == 'myaddress+local@my.domain.my'
    assert mailaddress('myaddress@my.domain123.my') == 'myaddress@my.domain123.my'
    assert mailaddress(u'myaddress@my.dömäin.my') == 'myaddress@my.xn--dmin-moa0i.my'
    assert mailaddress(u'myaddress@وزارة-الأتصالات.مصر') == \
        'myaddress@xn----rmckbbajlc6dj7bxne2c.xn--wgbh1c'
    assert raises(ValueError, mailaddress, 'my.name.domain.my')
    assert raises(ValueError, mailaddress, '@my.domain')
    assert raises(ValueError, mailaddress, 'my@domain')
    assert raises(ValueError, mailaddress, 'my@domain.123')
    assert raises(ValueError, mailaddress, 'my@domain@dummy.my')
    assert raises(ValueError, mailaddress, 'my@nonsens@dömain.my')

def test_value_class():
    assert raises(ProgrammingError, Value, 'my value', type='mytype')
    assert raises(ProgrammingError, Value, 'my value', errors='double')
