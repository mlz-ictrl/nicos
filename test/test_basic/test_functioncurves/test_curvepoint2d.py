# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

"""
Tests for the functioncurve CurvePoint2D class
"""

import math
import pickle

import numpy
import pytest

from nicos.utils.functioncurves import CurvePoint2D, ufloat
from nicos.utils.functioncurves.types import FloatWithStdError


def test_init():
    x, dx, y, dy = 1, 0.1, 1, 0.1
    p1 = CurvePoint2D(x, y)
    p2 = CurvePoint2D(ufloat(x, dx), ufloat(y, dy))
    assert p1.x.n == x
    assert math.isnan(p1.x.s)
    assert p1.y.n == y
    assert math.isnan(p1.y.s)
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


def test_interpolate_segments_parallel_to_axes():
    # vertical segment interpolated by y
    p = CurvePoint2D.interpolate((1, 0), (1, 2), y=1)
    assert p.eq_x(1) and p.eq_y(1)
    # horizontal segment interpolated by x
    p = CurvePoint2D.interpolate((0, 1), (2, 1), x=1)
    assert p.eq_x(1) and p.eq_y(1)
    with pytest.raises(ValueError):
        CurvePoint2D.interpolate((1, 0), (1, 2), x=2)
    with pytest.raises(ValueError):
        CurvePoint2D.interpolate((0, 1), (2, 1), y=2)


def test_interpolate_arguments():
    p = CurvePoint2D.interpolate((0, 0), (2, 2), x=0)
    assert p.eq_x(0) and p.eq_y(0)
    with pytest.raises(ValueError):
        CurvePoint2D.interpolate((0, 0), (2, 2), x=0, y=5)
    with pytest.raises(ValueError):
        CurvePoint2D.interpolate((0, 0), (2, 2))


def test_interpolate_uncertainties():
    p1 = CurvePoint2D(ufloat(0, 0), ufloat(0, 0.1))
    p2 = CurvePoint2D(ufloat(2, 0), ufloat(2, 0.1))
    p = CurvePoint2D.interpolate(p1, p2, x=1)
    assert p.y.n == pytest.approx(1)
    if ufloat is FloatWithStdError:
        assert math.isnan(p.y.s)
    else:
        assert p.y.s == pytest.approx(0.1 / 2 ** 0.5)


def test_comparison_with_other_types():
    p = CurvePoint2D(1, 2)
    assert p != None  # pylint: disable=singleton-comparison
    assert p not in [None, 'text']
    assert p == (1, 2) and p == [1, 2] and p != (2, 2)
    with pytest.raises(TypeError):
        assert p < None

def test_arithmetic_with_ufloat():
    p = CurvePoint2D(1, ufloat(2, 0.1))
    assert (p + ufloat(1, 0.1)).y.n == (ufloat(1, 0.1) + p).y.n == 3
    product = p * ufloat(2, 0)
    assert product.y.n == 4
    if ufloat is FloatWithStdError:
        assert math.isnan(product.y.s)
    else:
        assert product.y.s == pytest.approx(0.2)


def test_numpy_scalars():
    p = CurvePoint2D(1, 2)
    for v in (numpy.float64(3), numpy.int64(3)):
        for result in (p + v, v + p, p * v, v * p, v - p, v / p):
            assert isinstance(result, CurvePoint2D)
            assert result.eq_x(1)
    assert (numpy.int64(3) - p).eq_y(1)


def test_fallback_arithmetic():
    v = FloatWithStdError(2, 0.1)
    for result in (v + 1, 1 + v, v - 1, 1 - v, v * 2, 2 * v, v / 2, 2 / v,
                   -v, abs(v), v ** 2):
        assert isinstance(result, FloatWithStdError)
        assert math.isnan(result.s)
    assert (v + v).n == 4
    assert pickle.loads(pickle.dumps(v)).s == 0.1
