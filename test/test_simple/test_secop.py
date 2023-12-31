# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Markus Zolliker <markus.zolliker@psi.ch>
#
# *****************************************************************************

"""SECoP client test suite."""

import pytest

session_setup = 'secop'

pytest.importorskip('frappy')

from frappy.datatypes import get_datatype

from nicos.core.params import anytype, dictwith, floatrange, intrange, \
    listof, nonemptystring, oneofdict, string, tupleof
from nicos.devices.secop.validators import get_validator
from nicos.protocols.cache import cache_dump

from test.utils import raises

simple_types = [
    (None, anytype),
    (dict(type='double'), float),
    (dict(type='int', min=-0x8000, max=0x7fff), int),
    (dict(type='bool'), bool),
    (dict(type='string'), string),
    (dict(type='string', minchars=1), nonemptystring),
]

ambiguous_types = [  # matching some nicos types from above
    (dict(type='string', minchars=10, maxchars=12), nonemptystring),
    (dict(type='blob'), string),
    (dict(type='blob', minbytes=1), nonemptystring),
]

special_types = [
    (dict(type='double', min=0.5), floatrange(0.5), float,
     [0.5, 1], [0]),
    (dict(type='double', min=-2.5, max=2.3), floatrange(-2.5, 2.3), float,
     [-2.5, 2.3], [4]),
    (dict(type='int', min=0, max=10000), intrange(0, 10000), int,
     [0, 10000], [-1, 10001]),
]

complex_types = [
    (dict(type='enum', members=dict(off=0, on=1, auto=2)),
     oneofdict(dict(off=0, on=1, auto=2)),
     0, ['on', 2], ['disabled', 3]),
]

secop_array1 = dict(type='array', members=dict(type='double'))
nicos_array1 = listof(float)
valid_array1 = [-2.5, 3]
invalid_array1 = ['x']
complex_types.append(
    (secop_array1, nicos_array1, [], [valid_array1], [invalid_array1]))

secop_struct1 = dict(type='struct',
                     members=dict(b=dict(type='bool'), f=dict(type='double')))
nicos_struct1 = dictwith(b=bool, f=float)
valid_struct1 = dict(b=True, f=2.5)
invalid_struct1 = dict(b='x')
default_struct1 = dict(b=False, f=0)
complex_types.append(
    (secop_struct1, nicos_struct1,
     default_struct1,
     [valid_struct1],
     [invalid_struct1, dict(b=True)]))

secop_array2 = dict(type='array', members=secop_struct1, minlen=2, maxlen=3)
nicos_array2 = listof(nicos_struct1)
valid_array2 = [valid_struct1] * 3
invalid_array2 = [valid_struct1] * 5  # to long
default_array2 = [default_struct1] * 2
complex_types.append(
    (secop_array2, nicos_array2,
     default_array2,
     [valid_array2],
     [invalid_array2,
      valid_array2[:1],  # to short
      [1, 2],  # invalid elements
      ]))

secop_struct2 = dict(type='struct',
                     members=dict(a=secop_struct1, b=secop_array2),
                     optional=['b'])
nicos_struct2 = dictwith(a=nicos_struct1, b=nicos_array2)
valid_struct2 = dict(a=valid_struct1, b=valid_array2)
default_struct2 = dict(a=default_struct1)
complex_types.append(
    (secop_struct2, nicos_struct2,
     default_struct2,
     [valid_struct2,
      dict(a=valid_struct1)],  # omit optional member
     [dict(b=valid_array2),  # omitted mandatory member
      dict(a=valid_struct1, b=valid_array2, c=1),  # unknown member
      dict(a=valid_struct1, b=invalid_array2),  # bad member
      ]))

secop_tuple = dict(type='tuple', members=[secop_array2, secop_struct2])
nicos_tuple = tupleof(nicos_array2, nicos_struct2)
complex_types.append(
    (secop_tuple, nicos_tuple,
     (default_array2, default_struct2),
     [(valid_array2, valid_struct2)],
     [(invalid_array2, valid_struct2),  # invalid member
      (valid_array2,),  # to short
      (valid_array2, valid_struct2, 0),  # to long
      ]))


@pytest.mark.parametrize('datainfo, validator', simple_types + ambiguous_types)
def test_simple_types(datainfo, validator):
    assert get_validator(datainfo, True) == validator


@pytest.mark.parametrize('datainfo, validator, dtype, valid, invalid', special_types)
def test_special_types(datainfo, validator, dtype, valid, invalid):
    v = get_validator(datainfo, True)
    assert isinstance(v, type(validator))
    assert get_validator(datainfo, False) is dtype
    for value in valid:
        v(value)
    for value in invalid:
        assert raises(ValueError, v, value)
    assert v.__doc__ == validator.__doc__


@pytest.mark.parametrize('datainfo, validator, default, valid, invalid', complex_types)
def test_complex_types(datainfo, validator, default, valid, invalid):
    v = get_validator(datainfo, True)
    assert isinstance(v, type(validator))
    assert v() == default
    for value in valid:
        v(value)
    for value in invalid:
        assert raises(ValueError, v, value)


def test_no_pickle_for_values():
    all_types = simple_types + special_types + complex_types
    for args in all_types:
        typ = get_validator(args[0], True)
        # check that cache_dump of default value does not need pickle
        assert 'cache_unpickle' not in cache_dump(typ())


def desc(type_, **kwds):
    kwds['type'] = type_
    return {'description': 'x', 'datainfo': kwds,
            # check that datatype will be filtered away in createDevices:
            'datatype': get_datatype(kwds)}


class TestPickleNotNeeded:
    funny_desc = desc('struct', members={
            'f': {'type': 'double', 'min': 0, 'max': 1},
            'a': {'type': 'array', 'members': {'type': 'string'}, 'maxlen': 10},
            't': {'type': 'tuple', 'members': [
                {'type': 'scaled', 'scale': 10, 'min': 0, 'max': 1},
                {'type': 'blob', 'maxbytes': 999},
            ]},
        })
    on_off = desc('enum', members={'off': 0, 'on': 1})
    modules = {
        'mod1': {
            'description': 'a test drivable',
            'parameters': {
                'value:': on_off,
                'target': on_off,
                'funny_param': funny_desc,
            },
            'commands': {
                'communicate': desc(
                    'command',
                    argument={'type': 'string'},
                    result={'type': 'string'},
                    )
            }
        }
    }
    nodename = 'dummy'

    def disconnect(self):
        pass

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session
        self.secnode = session.getDevice('secnode')
        # yield "resource"

    def test_no_pickle_needed(self):
        # we use self as SecNode connection
        # createDevices needs only the attributes: modules, nodename, disconnect
        self.secnode._secnode = self
        self.secnode.createDevices()
        assert 'cache_unpickle("' not in cache_dump(self.secnode.setup_info)

    def test_datatype_needs_pickle(self):
        # test above test: this was one of the bad contents of setup_info
        assert 'cache_unpickle("' in cache_dump(desc('double'))
