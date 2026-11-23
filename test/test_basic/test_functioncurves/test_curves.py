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
Tests for the functioncurve Curves class
"""

import math
import pickle
import random
from random import randint

import pytest

from nicos.utils.functioncurves import Curve2D, CurvePoint2D, Curves, ufloat
from nicos.utils.functioncurves.calcs import mean


def test_basic():
    curves1, curves2 = Curves(), Curves()
    n = randint(1, 10)
    for _ in range(n):
        curves1.append(Curve2D())
        curves2.append(Curve2D())
    curves1.append(curves2)
    assert len(curves1) == 2 * n


def test_pickle():
    curve0 = Curves([Curve2D([CurvePoint2D(ufloat(i, 0.1 * i), ufloat(i, 0.1 * i))
                              for i in range(1, 10)])])
    temp = pickle.dumps(curve0)
    curve1 = pickle.loads(temp)
    assert curve1[0].x == curve0[0].x and curve1[0].y == curve0[0].y


def test_increasing_decreasing():
    vmin, vmax, n = randint(-100, -10), randint(10, 100), randint(1, 10)
    ranges = [(vmin, vmax, 1), (vmax, vmin, -1)] * n
    series = [(i, i) for r in ranges for i in range(*r)]
    curves = Curve2D.series_to_curves(series)
    assert len(curves.increasing()) == n
    assert len(curves.decreasing()) == n


def test_mean():
    # test fucntioncurves.calcs.mean
    x = [1, 2, 3]
    dx1 = [0.1, 0.1, 0.1]
    dx2 = [0.1, 0.2, 0.3]
    assert mean(x).n == mean(x, dx1).n == pytest.approx(2.0)
    assert mean(x).s / mean(x, dx1).s == pytest.approx(10.0)
    assert mean(x, dx2).n == pytest.approx(1.35, rel=0.01)
    assert mean(x, dx2).s == pytest.approx(0.09, rel=0.1)
    # test Curve.mean() return values
    x = list(range(1, 10))
    v = randint(1, 100)
    y1 = [v + (randint(1, 200) - 100) / 100 for _ in x]
    y2 = [v + (randint(1, 200) - 100) / 100 for _ in x]
    curves = Curves([list(zip(x, y1)), list(zip(x, y2))])
    assert curves.mean() is not None
    assert curves.mean().y[1].n is not None
    assert curves.mean().y[1].s is not None


def test_copy():
    curves1 = Curves([[(1, 1)]])
    curves2 = Curves(curves1)
    curves2.append(Curve2D([(2, 2)]))
    assert len(curves1) == 1 and len(curves2) == 2


def test_append_curve_as_list():
    curves = Curves()
    curves.append([(1, 1), (2, 2)])
    curves.append([[(1, 1)], Curve2D([(2, 2)])])
    curves.append([])
    assert [len(curve) for curve in curves] == [2, 1, 1]


def test_increasing_decreasing_skip_short_curves():
    curves = Curves([[], [(1, 1)], [(1, 1), (2, 2)], [(2, 2), (1, 1)]])
    assert len(curves.increasing()) == len(curves.decreasing()) == 1


def test_series_to_curves_many_short_sweeps():
    series = []
    for _ in range(10):
        series += [(i, i) for i in range(-10, 10)]
        series += [(i, i) for i in range(10, -10, -1)]
    curves = Curves.from_series(series)
    assert len(curves) == 20
    # turning points are shared by adjacent curves
    assert [len(curve) for curve in curves] == [21] * 19 + [20]
    assert len(curves.mean()) == 21


def test_series_to_curves_plateau():
    series = [(x, i) for i, x in enumerate([0, 1, 2, 3, 3, 3, 2, 1, 0])]
    curves = Curves.from_series(series)
    assert [curve.x for curve in curves] == [[0, 1, 2, 3], [3, 2, 1, 0]]
    assert [curve.y for curve in curves] == [[0, 1, 2, 3], [5, 6, 7, 8]]
    # plateau in the middle of a sweep doesn't split the curve
    series = [(x, 0) for x in [0, 1, 1, 2, 3, 2, 1, 0]]
    assert len(Curves.from_series(series)) == 2


def test_series_to_curves_noise():
    rnd = random.Random(1)
    series = []
    for _ in range(5):
        sweep = [-1 + i / 100 for i in range(200)]
        series += [(x + rnd.gauss(0, 0.01), x) for x in sweep + sweep[::-1]]
    curves = Curves.from_series(series)
    assert len(curves.increasing()) == len(curves.decreasing()) == 5


def test_series_to_curves_meta():
    series = [(i, i) for i in range(10)]
    curves = Curves.from_series(series, meta=[5, 5])
    assert [len(curve) for curve in curves] == [5, 5]
    # interrupted series
    curves = Curves.from_series(series, meta=[5, 8, 5])
    assert [len(curve) for curve in curves] == [5, 5]
    with pytest.raises(ValueError):
        Curves.from_series(series, meta=[3, 3])


def test_mean_edge_cases():
    assert math.isnan(mean([]).n)
    assert mean([5]).n == 5 and math.isnan(mean([5]).s)
    assert mean([ufloat(5, 0.2)]).s == pytest.approx(0.2)
    # zero errors are not usable as weights
    m = mean([ufloat(1, 0), ufloat(2, 0.1)])
    assert m.n == pytest.approx(1.5) and math.isfinite(m.s)
    assert mean([ufloat(1, 0.1), 2.0]).n == pytest.approx(1.5)
    curve = Curve2D([(1, 1), (2, 2)])
    mean_curve = Curves([curve]).mean()
    assert mean_curve is not curve and mean_curve.y == curve.y
    assert len(Curves().mean()) == 0
