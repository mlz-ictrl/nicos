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
#
# *****************************************************************************

"""NICOS parameter utilities tests."""

import pytest
from numpy import array

from nicos.core.errors import ConfigurationError, ProgrammingError
from nicos.core.params import ArrayDesc, Attach, Param, Value, absolute_path, \
    anytype, boolean, dictof, dictwith, floatrange, host, intrange, ipv4, \
    limits, listof, mailaddress, nicosdev, none_or, nonemptylistof, \
    nonemptystring, nonzero, oneof, oneofdict, oneofdict_or, pvname, \
    relative_path, secret, setof, string, subdir, tangodev, tupleof, vec3
from nicos.utils import Secret

# pylint: disable=compare-to-empty-string


def test_param_class():
    assert str(Param('my parameter')) == '<Param info>'
    text = Param('my parameter', prefercache=True).formatDoc()
    assert text == 'Parameter: my parameter\n\n    * Type: float\n    * ' \
                   'Default value: ``0.0``\n    * Not settable at runtime\n' \
                   '    * Prefer value from cache: True'


def test_attach_class():
    class MyClass:
        pass
    # test __init__()
    pytest.raises(ProgrammingError, Attach, 'desc.', MyClass, optional=3)
    pytest.raises(ProgrammingError, Attach, 'desc.', MyClass, multiple=None)
    pytest.raises(ProgrammingError, Attach, 'desc.', MyClass, multiple=[])
    pytest.raises(ProgrammingError, Attach, 'desc.', MyClass, multiple=[None])
    pytest.raises(ProgrammingError, Attach, 'desc.', MyClass, multiple=[3.14])
    pytest.raises(ProgrammingError, Attach, 'desc.', MyClass, multiple=-1)
    # test repr
    a = Attach('description', MyClass, optional=True, multiple=[3, 4])
    assert repr(a) == "Attach('description', " \
                      "test.test_basic.test_params.MyClass, " \
                      "multiple=[3, 4], optional=True)"

    # test check()
    a = Attach('description', MyClass)
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', None)
    assert a.check('devname', 'aname', 1) == [1]
    assert a.check('devname', 'aname', [1]) == [1]
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname',
                         [1, 2])

    a = Attach('description', MyClass, optional=True)
    assert a.check('devname', 'aname', None) == [None]
    assert a.check('devname', 'aname', 1) == [1]
    assert a.check('devname', 'aname', [1]) == [1]
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname',
                         [1, 2])

    a = Attach('description', MyClass, multiple=True)
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', None)
    assert a.check('devname', 'aname', 1) == [1]
    assert a.check('devname', 'aname', [1]) == [1]
    assert a.check('devname', 'aname', [1, 2]) == [1, 2]

    a = Attach('description', MyClass, multiple=True, optional=True)
    assert a.check('devname', 'aname', None) == []
    assert a.check('devname', 'aname', 1) == [1]
    assert a.check('devname', 'aname', [1]) == [1]
    assert a.check('devname', 'aname', [1, 2]) == [1, 2]
    assert a.check('devname', 'aname', [1, 2, 3]) == [1, 2, 3]

    a = Attach('description', MyClass, multiple=2)
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', None)
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', 1)
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', [1])
    assert a.check('devname', 'aname', [1, 2]) == [1, 2]
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', [1, 2, 3])

    # with optional and multiple a fixed number, we have either both, or None
    a = Attach('description', MyClass, multiple=2, optional=True)
    assert a.check('devname', 'aname', None) == [None, None]
    assert a.check('devname', 'aname', 1) == [1, None]
    assert a.check('devname', 'aname', [1]) == [1, None]
    assert a.check('devname', 'aname', [1, 2]) == [1, 2]
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', [1, 2, 3])

    # check that multiple=2 and multiple=[2] are the same
    assert repr(Attach('devname', MyClass, multiple=2)) == \
        repr(Attach('devname', MyClass, multiple=[2]))

    a = Attach('description', MyClass, multiple=[2, 3])
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', None)
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', 1)
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', [1])
    assert a.check('devname', 'aname', [1, 2]) == [1, 2]
    assert a.check('devname', 'aname', [1, 2, 3]) == [1, 2, 3]
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', [1, 2, 3, 4])

    a = Attach('description', MyClass, multiple=[2, 3], optional=True)
    assert a.check('devname', 'aname', None) == [None, None, None]
    assert a.check('devname', 'aname', 1) == [1, None, None]
    assert a.check('devname', 'aname', [1]) == [1, None, None]
    assert a.check('devname', 'aname', [1, 2]) == [1, 2, None]
    assert a.check('devname', 'aname', [1, 2, 3]) == [1, 2, 3]
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', [1, 2, 3, 4])

    a = Attach('description', MyClass, multiple=[0, 2, 3])
    assert a.check('devname', 'aname', None) == []
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', 1)
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', [1])
    assert a.check('devname', 'aname', [1, 2]) == [1, 2]
    assert a.check('devname', 'aname', [1, 2, 3]) == [1, 2, 3]
    pytest.raises(ConfigurationError, a.check, 'devname', 'aname', [1, 2, 3, 4])


def test_listof():
    assert listof(int)([0., 1, '2']) == [0, 1, 2]
    assert listof(int)() == []  # pylint: disable=use-implicit-booleaness-not-comparison
    # should also accept tuples
    assert listof(int)((1, 2, 3)) == [1, 2, 3]
    pytest.raises(ValueError, listof(int), 10)
    # assert that the list is read-only
    pytest.raises(TypeError, listof(int)([0, 1, 2]).__setitem__, 0, 1)


def test_nonemptylistof():
    assert nonemptylistof(int)(['1']) == [1]
    assert nonemptylistof(int)() == [0]
    # should also accept tuples
    assert nonemptylistof(int)((1, 2)) == [1, 2]
    pytest.raises(ValueError, nonemptylistof(int), [])
    pytest.raises(ValueError, nonemptylistof(int), 10)
    # assert that the list is read-only
    pytest.raises(TypeError, nonemptylistof(int)([0, 1, 2]).__setitem__, 0, 1)


def test_tupleof():
    assert tupleof(int, str, float)((1.0, 1.0, 1.0)) == (1, '1.0', 1.0)
    assert tupleof(int, str, float)() == (0, '', 0.0)
    assert tupleof(float, float)() == (0.0, 0.0)
    assert tupleof(int, int, int, int)(array((1, 2, 3, 4))) == (1, 2, 3, 4)
    pytest.raises(ValueError, tupleof(int, str), ('a', 'b'))
    pytest.raises(ValueError, tupleof(int, str), ('a',))
    pytest.raises(ValueError, tupleof(int, str), 'x')
    pytest.raises(ValueError, tupleof(float, float), (1,))
    pytest.raises(ValueError, tupleof(float, float), (1, 2, 3))
    pytest.raises(ProgrammingError, tupleof,)


def test_string():
    assert string(b'blah') == 'blah'
    assert string() == ''
    assert string('blah') == 'blah'


def test_boolean():
    assert boolean(True) is True
    assert boolean(False) is False
    assert boolean() is False
    assert boolean(10) is True
    assert boolean(0) is False
    pytest.raises(ValueError, boolean, 'True')
    pytest.raises(ValueError, boolean, 'False')


def test_dictof():
    assert dictof(int, str)({1: 0, 2: 1}) == {1: '0', 2: '1'}
    assert dictof(int, str)() == {}  # pylint: disable=use-implicit-booleaness-not-comparison
    pytest.raises(ValueError, dictof(int, str), ('a', 'b'))
    pytest.raises(ValueError, dictof(int, str), {'x': 'y'})
    # test that the dict is read-only
    pytest.raises(TypeError, dictof(int, str)({1: 'x'}).pop, 1)


def test_dictwith():
    assert dictwith()() == {}
    assert dictwith()({}) == {}
    assert dictwith(key=int)({'key': '10'}) == {'key': 10}
    pytest.raises(ValueError, dictwith(key=int), {})
    pytest.raises(ValueError, dictwith(key=int), {'key': 'a'})
    pytest.raises(ValueError, dictwith(key=int), {'x': '10'})
    pytest.raises(ValueError, dictwith(key=int),
                         {'key': '10', 'x': 'a'})
    pytest.raises(ValueError, dictwith(key=int), [])
    # test that the dict is read-only
    pytest.raises(TypeError, dictwith(key=int)({'key': '1'}).pop, 1)


def test_tangodev():
    valid_names = [
        'tango://host:123/test/custom/device',
        'tango://test/custom/dev',
        'tango://host:123/test/custom/device#dbase=no',
        'tango://host:123/test/custom/device#dbase=yes',
    ]
    invalid_names = {
        'Missing port': 'tango://host/test/custom/dev',
        'Invalid dbase setting': 'tango://host:123/test/custom/dev#dbase=y',
        'Typo in dbase setting': 'tango://host:123/test/custom/dev#dbas=no',
        'Wrong separator to dbase setting': 'tango://host:123/test/custom/dev~dbase=no',
        'Missing dbase flag': 'tango://host:123/test/custom/dev#dbase',
        'Tango attribute': 'tango://host:123/test/custom/dev/attr',
        'Device property': 'tango://host:123/test/custom/dev->prop',
        'Attribute property': 'tango://host:123/test/custom/dev/attr->prop',
        'Missing tango scheme': 'test/custom/device',
    }
    assert tangodev() == ''
    for validname in valid_names:
        assert tangodev(validname) == validname

    for _key, invalidname in invalid_names.items():
        pytest.raises(ValueError, tangodev, invalidname)  # , reason=key)


def test_pvname():
    valid_names = [
        'a', 'a:b', 'a:b.r',
        'g.3:g<u>',
        'a-b:G.f', 'a_g;t',
    ]

    invalid_names = {
        'a,b': 'Comma is not allowed in PV-names.',
        'g{}': 'Curly braces are not allowed in PV-names.'
    }

    assert pvname() == ''

    for valid in valid_names:
        assert pvname(valid) == valid

    for invalid, _reason in invalid_names.items():
        pytest.raises(ValueError, pvname, invalid)  # , reason=reason)


def test_anytype():
    assert anytype('foo') == 'foo'


def test_vec3():
    assert vec3([1, 0, 0]) == [1., 0., 0.]
    assert vec3() == [0., 0., 0.]
    pytest.raises(ValueError, vec3, [1, 0])
    pytest.raises(ValueError, vec3, ['x', 'y', 'z'])
    # assert that the list is read-only
    pytest.raises(TypeError, vec3([0, 1, 2]).__setitem__, 0, 1)


def test_intrange():
    assert intrange(0, 10)(10) == 10
    assert intrange(1, 3)() == 1
    pytest.raises(ValueError, intrange(0, 10), 15)
    pytest.raises(ValueError, intrange(0, 10), 'x')
    pytest.raises(ValueError, intrange, 2, 1)
    pytest.raises(ValueError, intrange, True, False)
    pytest.raises(ValueError, intrange(0, 1), True)
    pytest.raises(ValueError, intrange(0, 1), False)


def test_floatrange():
    assert floatrange(0, 10)(5) == 5.0
    assert floatrange(1, 3)() == 1.0
    pytest.raises(ValueError, floatrange(0, 10), 15.)
    pytest.raises(ValueError, floatrange(0, 10), 'x')
    pytest.raises(ValueError, floatrange, 2, 1)

    assert floatrange(0)(5) == 5.0
    pytest.raises(ValueError, floatrange(0), -5)


def test_oneof():
    assert oneof(0, 1)(1) == 1
    assert oneof(2, 3)() == 2
    assert oneof(None)() is None
    assert oneof(None)(None) is None
    assert oneof()() is None
    assert oneof()(None) is None
    pytest.raises(ValueError, oneof(0, 1), '0')
    pytest.raises(ValueError, oneof(0, 1), 2)
    pytest.raises(ValueError, oneof(0, 1), 'x')


def test_setof():
    SETTYPES = (1, 2, 3, 4)
    assert setof(*SETTYPES)() == frozenset()
    assert setof(*SETTYPES)([1]) == frozenset([1])
    pytest.raises(ValueError, setof(*SETTYPES), [5])


def test_oneofdict():
    assert oneofdict({'A': 1, 'B': 2})('A') == 1
    assert oneofdict({'A': 1, 'B': 2})(1) == 1
    assert oneofdict({})() is None
    pytest.raises(ValueError, oneofdict({'A': 1}), 2)

    assert none_or(int)(None) is None
    assert none_or(int)(5.0) == 5
    pytest.raises(ValueError, none_or(int), 'x')


def test_limits():
    assert limits((-10, 10)) == (-10, 10)
    assert limits((0, 0)) == (0, 0)
    assert limits() == (0, 0)
    assert limits([-10, 10]) == (-10, 10)
    pytest.raises(ValueError, limits, (1,))
    pytest.raises(ValueError, limits, 1)
    pytest.raises(ValueError, limits, (10, 10, 10))
    pytest.raises(TypeError, limits, 1, 1)
    pytest.raises(ValueError, limits, (10, -10))
    pytest.raises(ValueError, limits, ('a', 'b'))


def test_mailaddress():
    assert mailaddress() == ''
    assert mailaddress('my.address@domain.my') == 'my.address@domain.my'
    assert mailaddress('my_address@domain.my') == 'my_address@domain.my'
    assert mailaddress('myaddress@domain.my') == 'myaddress@domain.my'
    assert mailaddress('myaddress+local@my.domain.my') == 'myaddress+local@my.domain.my'
    assert mailaddress('myaddress@my.domain123.my') == 'myaddress@my.domain123.my'
    assert mailaddress('myaddress@my.dömäin.my') == 'myaddress@my.xn--dmin-moa0i.my'
    assert mailaddress('myaddress@وزارة-الأتصالات.مصر') == \
        'myaddress@xn----rmckbbajlc6dj7bxne2c.xn--wgbh1c'
    assert mailaddress('M. Address <my.address@domain.my>') == 'M. Address <my.address@domain.my>'
    assert mailaddress('M. Address <my.address@domain.my> ') == 'M. Address <my.address@domain.my> '
    assert mailaddress('W. Lohstroh, G. Simeoni '
                       '<wiebke.lohstroh+giovanna.simeoni@frm2.tum.de>') == \
        'W. Lohstroh, G. Simeoni <wiebke.lohstroh+giovanna.simeoni@frm2.tum.de>'
    pytest.raises(ValueError, mailaddress, 'M. Address my.address@domain.my>')
    pytest.raises(ValueError, mailaddress, 'M. Address <my.address@domain.my')
    pytest.raises(ValueError, mailaddress, 'my.name.domain.my')
    pytest.raises(ValueError, mailaddress, '@my.domain')
    pytest.raises(ValueError, mailaddress, 'my@domain')
    pytest.raises(ValueError, mailaddress, 'my@domain.123')
    pytest.raises(ValueError, mailaddress, 'my@domain@dummy.my')
    pytest.raises(ValueError, mailaddress, 'my@nonsens@dömain.my')
    pytest.raises(ValueError, mailaddress, 'M. Address <my.address@domain.my>,')


def test_value_class():
    pytest.raises(ProgrammingError, Value, 'my value', type='mytype')
    pytest.raises(ProgrammingError, Value, 'my value', errors='double')


def test_path():
    assert absolute_path('/tmp') == '/tmp'
    assert relative_path('tmp') == 'tmp'
    assert subdir('tmp') == 'tmp'
    pytest.raises(ValueError, absolute_path, 'tmp')
    pytest.raises(ValueError, absolute_path, '../')
    pytest.raises(ValueError, relative_path, '/tmp')
    pytest.raises(ValueError, relative_path, '../')
    pytest.raises(ValueError, subdir, 'tmp/')


def test_oneofdict_or():
    m = dict(a=1, b=2)
    v = oneofdict_or(m, floatrange(0, 10))
    assert v('a') == 1.0
    assert v('b') == 2.0
    assert v(5) == 5.0
    pytest.raises(ValueError, v, 'c')
    pytest.raises(ValueError, v, 11)


def test_nicosdev():
    assert nicosdev('nicosdev') == 'nicosdev'
    assert nicosdev('nicos.dev') == 'nicos.dev'
    pytest.raises(ValueError, nicosdev, 'a.nicos.dev')
    assert nicosdev() == ''


def test_nonemptystring():
    p = Param('nonemptystring', type=nonemptystring)
    assert p.default is None
    pytest.raises(ValueError, nonemptystring, '')
    assert nonemptystring('text') == 'text'


def test_host():
    assert host()('localhost') == 'localhost'
    assert host()('localhost:14869') == 'localhost:14869'
    assert host()('') == ''
    pytest.raises(ValueError, host(), None)
    pytest.raises(ValueError, host(), 123)
    pytest.raises(ValueError, host(), 'localhost:')
    pytest.raises(ValueError, host(), 'localhost:14869:')
    pytest.raises(ValueError, host(), 'localhost:0')
    pytest.raises(ValueError, host(), 'localhost:65536')
    pytest.raises(ValueError, host(), 'localhost:port')
    assert host(defaulthost='localhost')('') == ''
    assert host(defaulthost='localhost')(None) == 'localhost'
    assert host(defaulthost='localhost')('otherhost') == 'otherhost'

    assert host(defaultport=123)('') == ':123'
    assert host(defaultport=123)('otherhost') == 'otherhost:123'
    assert host(defaultport='456')('otherhost') == 'otherhost:456'
    assert host(defaultport=123)('otherhost:789') == 'otherhost:789'
    assert host()(('name', 1234)) == 'name:1234'

    assert host(defaulthost='localhost',
                defaultport=123)('') == ':123'
    assert host(defaulthost='localhost',
                defaultport='456')('otherhost') == 'otherhost:456'
    assert host(defaulthost='localhost',
                defaultport='456')('otherhost:789') == 'otherhost:789'

    pytest.raises(ValueError, host().__call__, ':123')

    pytest.raises(ValueError, host, **{'defaultport': 'abc'})
    pytest.raises(ValueError, host, **{'defaultport': '9999999'})


def test_ipv4():
    assert ipv4('1.2.3.4') == '1.2.3.4'
    assert ipv4('123.234.249.255') == '123.234.249.255'
    assert ipv4('123.255.249.255') == '123.255.249.255'
    assert ipv4('255.255.255.255') == '255.255.255.255'
    assert ipv4() == '0.0.0.0'
    assert ipv4('') == ''
    assert ipv4(None) == ''
    pytest.raises(ValueError, ipv4, '1')
    pytest.raises(ValueError, ipv4, '1.2')
    pytest.raises(ValueError, ipv4, '1.2.3')
    pytest.raises(ValueError, ipv4, '1.2.3.4.')
    pytest.raises(ValueError, ipv4, '1.2.3.256')
    pytest.raises(ValueError, ipv4, '1.2.256.4')
    pytest.raises(ValueError, ipv4, '1.256.3.4')
    pytest.raises(ValueError, ipv4, '256.2.3.4')
    pytest.raises(ValueError, ipv4, ' 255.255.255.255')


def test_ArrayDesc():
    ad = ArrayDesc('arr', (1, 1), '<u4')
    ad2 = ad.copy()
    assert ad != ad2
    assert ad2.name == ad.name and ad2.shape == ad.shape \
        and ad2.dtype == ad.dtype and ad2.dimnames == ad.dimnames


def test_nonzero():
    assert nonzero(int)() == 1
    assert nonzero(int, 5.0)() == 5
    assert nonzero(int)(5.0) == 5
    assert nonzero(float)(1) == 1
    assert nonzero(intrange(-1, 1))(1) == 1
    assert nonzero(intrange(-1, 1))() == -1
    assert nonzero(intrange(-1, 1), -1)() == -1
    assert nonzero(floatrange(0, 1))() == 1
    assert nonzero(floatrange(0, 1), 0.01)() == 0.01
    assert nonzero(floatrange(0, 1))(0.5) == 0.5
    assert nonzero(floatrange(-1, 1))(1) == 1
    assert nonzero(floatrange(-1, 1))() == -1
    pytest.raises(TypeError, nonzero, 'x')
    pytest.raises(ValueError, nonzero, floatrange(0, 0.1))
    pytest.raises(ValueError, nonzero, floatrange(0, 0.1), 1)
    pytest.raises(ValueError, nonzero(int), 0)
    pytest.raises(ValueError, nonzero(float), 0)
    pytest.raises(ValueError, nonzero(intrange(-1, 1)), 0)
    pytest.raises(ValueError, nonzero(floatrange(-1, 1)), 0)
    pytest.raises(ValueError, nonzero(floatrange(-1, 1)), 10)


def test_secret():
    s = secret()
    assert f'{s!r}' == "<secret ''>"
    pytest.raises(ConfigurationError, s.lookup)

    s = secret('secret')
    pytest.raises(ConfigurationError, s.lookup, 'error')
    assert s.lookup() is None

    s = secret(Secret(('secret', {})))
    pytest.raises(ConfigurationError, s.lookup, 'error')
    assert s.lookup() is None
