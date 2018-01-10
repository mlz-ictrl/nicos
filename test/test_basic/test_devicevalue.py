#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Bjoern Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
Tests for DeviceInfo
"""

from nicos.core.utils import DeviceValue, DeviceValueDict
from test.utils import raises


def test_deviceinfo():
    val = 10.0
    unit = 'mm'
    formatted = '%f %s' % (val, unit)
    a = DeviceValue(val, formatted, unit, 'meta')
    assert str(a) == formatted
    assert float(a) == val
    assert int(a) == int(val)

    b = DeviceValue('str', 'str', '', 'meta')
    assert raises(ValueError, float, b)
    assert raises(ValueError, int, b)

    c = DeviceValue(0, str(0), '', 'meta')
    assert int(c) == 0


def test_devicevaluedict():
    dvd = DeviceValueDict()

    val = '0 mm'
    dvd['a.b.c'] = val

    assert dvd['a.b.c'].raw == val
    assert dvd['a.b.c'].formatted == val

    val2 = DeviceValue(12, '12 cm', 'cm', 'meta')
    dvd['x.y'] = val2

    assert dvd['x.y'].raw == 12
    assert dvd['x.y'].formatted == '12 cm'
    assert dvd['x.y'].unit == 'cm'
