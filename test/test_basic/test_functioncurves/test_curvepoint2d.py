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
#   k.kholostov@fz-juelich.de
#
# *****************************************************************************

"""
Tests for the functioncurve CurvePoint2D class
"""

import pickle

from nicos.utils.functioncurves import CurvePoint2D, ufloat


def test_init():
    x, dx, y, dy = 1, 0.1, 1, 0.1
    p1 = CurvePoint2D(x, y)
    p2 = CurvePoint2D(ufloat(x, dx), ufloat(y, dy))
    assert p1.x.n == x
    assert p1.x.s == 0
    assert p1.y.n == y
    assert p1.y.s == 0
    assert p2.x.n == x
    assert p2.x.s == dx
    assert p2.y.n == y
    assert p2.y.s == dy


def test_pickle():
    x, dx, y, dy = 1, 0.1, 1, 0.1
    p1 = CurvePoint2D(ufloat(x, dx), ufloat(y, dy))
    temp = pickle.dumps(p1)
    p2 = pickle.loads(temp)
    assert p1.eq_x(p2)
    assert p1.eq_y(p2)


# pylint: disable=unneeded-not
def test_logical_operators():
    p1 = CurvePoint2D(ufloat(1, 0.1), ufloat(1, 0.1))
    p2 = CurvePoint2D(ufloat(1, 0.1), ufloat(2, 0.1))
    p3 = CurvePoint2D(ufloat(1, 0.1), ufloat(3, 0.1))
    p4 = CurvePoint2D(ufloat(1, 0.1), ufloat(3, 0.2))
    p5 = CurvePoint2D(ufloat(3, 0.1), ufloat(3, 0.1))
    assert p1 < p2 and p3 <= p4
    assert p2 > p1 and p4 >= p3
    assert p3 == p4
    assert not p3 != p4
    assert not p3 == p5
    assert p3 != p5
    v1, v2, v3 = 1, 2, 3
    assert p1 == v1
    assert p1 < v2 and p2 <= v2
    assert v3 > p2 and v3 >= p3
    assert p3 != v1


def test_arithmetic():
    p1 = CurvePoint2D(ufloat(1, 0.1), ufloat(2, 0.1))
    assert p1 + 2 == 4
    assert 2 + p1 == 4
    p1 += 2
    assert p1 == 4

    assert p1 - 2 == 2
    assert 2 - p1 == -2
    p1 -= 2
    assert p1 == 2

    assert p1 * 4 == 8
    assert 4 * p1 == 8
    p1 *= 4
    assert p1 == 8

    assert p1 / 4 == 2
    assert 4 / p1 == 0.5
    p1 /= 4
    assert p1 == 2

    p2 = CurvePoint2D(ufloat(1, 0.1), ufloat(4, 0.1))
    assert p1 + p2 == 6
    assert p1 - p2 == -2
    assert p1 * p2 == 8
    assert p2 / p1 == 2


def test_interpolate():
    p1 = CurvePoint2D(1, 1)
    p3 = CurvePoint2D(3, 3)
    p2 = CurvePoint2D.interpolate(p1, p3, x=2)
    assert p2.eq_x(2)
    assert p2.eq_y(2)
