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
Tests for the functioncurve Curve2D class
"""

import math
import pickle
import warnings
import pytest
from random import randint

import numpy

from .utils import compare_lists

from nicos.utils.functioncurves import Curve2D, FloatWithStdError, ufloat
from nicos.utils.functioncurves.calcs import lsm


def test_basic():
    n = randint(10, 100)
    curve1 = Curve2D([(i, i) for i in range(n)])
    curve2 = Curve2D.from_x_y(list(range(n)), list(range(n)))
    assert curve1.x == list(range(n))
    assert curve1.y == list(range(n))
    assert curve1.x == curve2.x
    assert curve1.y == curve2.y
    assert curve1.xmin.n == 0
    assert curve1.xmax.n == n - 1
    assert curve1.ymin.n == 0
    assert curve1.ymax.n == n - 1


def test_append():
    curve1 = Curve2D([(i, i) for i in range(10)])
    curve1.append((10, 10))
    curve1.append(Curve2D([(i, i) for i in range(11, 15)]))
    curve2 = Curve2D([(i, i) for i in range(15)])
    assert curve1.x == curve2.x
    assert curve1.y == curve2.y


def test_pickle():
    curve1 = Curve2D([(i, i) for i in range(10)])
    temp = pickle.dumps(curve1)
    curve2 = pickle.loads(temp)
    assert curve1.x == curve2.x
    assert curve1.y == curve2.y


def test_from_temporal():
    n = randint(10, 20)
    xoff, k = randint(-10, 10) / 10, randint(-10, 10)
    xvt = Curve2D([(i, ufloat(i, math.nan)) for i in range(n)])
    yvt = Curve2D([(i + xoff, ufloat((i + xoff) * k, math.nan)) for i in range(n)])
    curve = Curve2D.from_two_temporal(xvt, yvt)
    assert compare_lists(curve.x, xvt.y)
    assert compare_lists(curve.y, [ufloat(i * k, math.nan) for i in range(n)])
    curve = Curve2D.from_two_temporal(xvt, yvt, pick_yvt_points=True)
    assert compare_lists(curve.x, [ufloat(i + xoff, math.nan) for i in range(n)])
    assert compare_lists(curve.y, yvt.y)


def test_series_to_curves():
    vmin, vmax, n = randint(-100, -10), randint(10, 100), randint(1, 10)
    ranges = [(vmin, vmax, 1), (vmax, vmin, -1)] * n
    series = [(i, 0) for r in ranges for i in range(*r)]
    curves = Curve2D.series_to_curves(series)
    assert len(curves) == n * 2


def test_arithmetics():
    curve0 = Curve2D([(i, i) for i in range(10)])
    curve1 = curve0 + curve0
    curve2 = Curve2D([(i, i * 3) for i in range(10)])
    assert curve1.y == [i * 2 for i in range(10)]
    assert (curve2 - curve0).y == curve1.y


def test_multiplication():
    curve0 = Curve2D([(i, 6) for i in range(10)])
    curve1 = Curve2D([(i, 2) for i in range(10)])
    assert (curve1 * 3).y == curve0.y
    curve2 = Curve2D([(i, 3) for i in range(-1, 11)])
    assert (curve1 * curve2).y == curve0.y


def test_interpolation():
    curve = Curve2D([(1, 2), (9, 18)])
    assert curve.xvy(11).x.n == 5.5
    assert curve.yvx(4.25).y.n == 8.5


def test_lsm():
    k, b = randint(1, 100) / 1000, randint(1, 100)
    x = numpy.array(range(1, 10))
    y = k * x + b
    dx = randint(1, 100) / 1000 * x
    dy = randint(1, 100) / 1000 * y
    curve = Curve2D.from_x_y(x, y)
    curvedy = Curve2D([(ix, ufloat(iy, idy)) for ix, iy, idy in zip(x, y, dy)])
    curvedxdy = Curve2D([(ufloat(ix, idx), ufloat(iy, idy))
                         for ix, idx, iy, idy in zip(x, dx, y, dy)])
    assert pytest.approx(curve.lsm()[0].n) == \
           pytest.approx(curvedy.lsm()[0].n) == \
           pytest.approx(curvedxdy.lsm()[0].n) == pytest.approx(k)
    assert pytest.approx(curve.lsm()[1].n) == \
           pytest.approx(curvedy.lsm()[1].n) == \
           pytest.approx(curvedxdy.lsm()[1].n) == pytest.approx(b)


def test_empty_and_numpy_input():
    assert not Curve2D().x
    assert not Curve2D([]).y
    curve = Curve2D(numpy.array([[1, 2], [3, 4]]))
    assert curve.x == [1, 3] and curve.y == [2, 4]


def test_append_point_as_list():
    curve = Curve2D()
    curve.append([1, 2])
    curve.append([(2, 3), (3, 4)])
    curve.append(((4, 5), (5, 6)))
    assert curve.x == [1, 2, 3, 4, 5]
    with pytest.raises(TypeError):
        curve.append(None)


def test_reflected_arithmetics():
    curve = Curve2D([(1, 2), (2, 4)])
    assert (10 - curve).y == [8, 6]
    assert (0 - curve).y == [-2, -4]
    assert (curve * 0).y == [0, 0]
    assert (0 * curve).y == [0, 0]
    assert (curve + 0) is not curve
    curve = Curve2D([(1, ufloat(2, 0))])
    result = (curve + ufloat(0, 0.1)).y[0]
    assert result.n == 2
    if ufloat is FloatWithStdError:
        assert math.isnan(result.s)
    else:
        assert result.s == pytest.approx(0.1)


def test_numpy_scalar_arithmetics():
    curve = Curve2D([(1, 2), (2, 4)])
    for result in (numpy.float64(2) * curve, numpy.int64(2) * curve,
                   curve * numpy.float64(2)):
        assert isinstance(result, Curve2D)
        assert result.y == [4, 8]


def test_arithmetics_of_disjoint_curves():
    curve1 = Curve2D([(1, 2), (2, 3)])
    curve2 = Curve2D([(5, 2), (6, 3)])
    assert len(curve1 + curve2) == 0
    assert len(curve1 + Curve2D()) == 0


def test_interpolation_decreasing():
    curve = Curve2D([(1, 10), (2, 5), (3, 4)])
    # extrapolation must use the end segment closest to the value
    assert curve.xvy(0).x.n == pytest.approx(7)
    assert curve.xvy(15).x.n == pytest.approx(0)
    curve = Curve2D([(10, 100), (5, 60), (0, 0), (-5, -60), (-10, -100)])
    assert curve.xvy(-110).x.n == pytest.approx(-11.25)
    assert curve.xvy(110).x.n == pytest.approx(11.25)
    assert curve.yvx(-11.25).y.n == pytest.approx(-110)
    assert curve.yvx(11.25).y.n == pytest.approx(110)


def test_interpolation_edge_cases():
    # vertical segment
    assert Curve2D([(0, 0), (1, 0), (1, 2), (2, 2)]).xvy(1).x.n == 1
    # non-monotonic curve is crossed in the middle
    assert Curve2D([(0, 0), (10, 10), (5, 5)]).yvx(7).y.n == 7
    # single point curves are constant
    assert Curve2D([(1, 1)]).xvy(2).x.n == 1
    assert Curve2D([(1, 1)]).yvx(2).y.n == 1
    assert Curve2D().xvy(1) is None and Curve2D().yvx(1) is None
    assert Curve2D([(0, 0), (1, 1)]).yvx(math.nan) is None


def test_from_temporal_not_interpolated():
    xvt = Curve2D([(0, 0), (math.nan, 1), (2, 2)])
    yvt = Curve2D([(0, 0), (2, 20)])
    # points, at which the other curve cannot be interpolated, are skipped
    curve = Curve2D.from_two_temporal(xvt, yvt)
    assert curve.x == [0, 2]
    assert curve.y == [0, 20]
    assert len(Curve2D.from_two_temporal(xvt, Curve2D())) == 0
    assert len(Curve2D.from_two_temporal(Curve2D(), yvt,
                                         pick_yvt_points=True)) == 0


def test_lsm_edge_cases():
    nan = math.nan
    k, b = lsm([1, 2, 3], [1, 2, 3])
    assert (k.n, b.n) == (pytest.approx(1), pytest.approx(0))
    for x, y in (([], []), ([1], [2]), ([1, 1, 1], [1, 2, 3])):
        k, b = lsm(x, y)
        assert math.isnan(k.n) and math.isnan(b.n)
    assert math.isnan(Curve2D([(1, ufloat(2, 0.1))]).lsm()[0].n)
    # Two points define a line, with propagation when uncertainties is installed.
    x0, x1, y0, y1 = (ufloat(v, 0.1) for v in (0, 1, 0, 1))
    k, b = lsm([x0, x1], [y0, y1])
    assert (k.n, b.n) == (pytest.approx(1), pytest.approx(0))
    if ufloat is FloatWithStdError:
        assert math.isnan(b.s)
    else:
        expected = y1 - (y1 - y0) / (x1 - x0) * x1
        assert b.s == pytest.approx(expected.s)
    # zero or partially unknown uncertainties are not usable as weights
    x = [ufloat(i, 0) for i in range(4)]
    y = [ufloat(i + 0.1 * (i % 2), 0.1) for i in range(4)]
    k, b = lsm(x, y)
    assert k.n == pytest.approx(1.02) and k.s > 0
    y = [ufloat(i + 0.1 * (i % 2), 0.1 if i != 2 else nan) for i in range(4)]
    k, b = lsm([ufloat(i, nan) for i in range(4)], y)
    assert k.n == pytest.approx(1.02) and math.isfinite(k.s)
    k, b = lsm(range(4), [ufloat(i, 0) for i in range(4)])
    assert k.n == pytest.approx(1)


def test_lsm_flat_line_with_uncertainties():
    x = [ufloat(i, 0.1) for i in range(5)]
    y = [ufloat(1, 0.1) for _ in range(5)]
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        k, b = lsm(x, y)
    assert k.n == pytest.approx(0) and b.n == pytest.approx(1)
