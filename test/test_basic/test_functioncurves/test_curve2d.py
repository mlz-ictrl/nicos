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
Tests for the functioncurve Curve2D class
"""

import pickle
from random import randint

from utils import compare_lists

from nicos.utils.functioncurves import Curve2D, ufloat


def test_basic():
    n = randint(10, 100)
    curve1 = Curve2D([(i, i) for i in range(n)])
    curve2 = Curve2D.from_x_y(list(range(n)), list(range(n)))
    assert curve1.x == list(range(n)) and curve1.y == list(range(n))
    assert curve1.x == curve2.x and curve1.y == curve2.y
    assert curve1.xmin == 0
    assert curve1.xmax == n - 1
    assert curve1.ymin == 0
    assert curve1.ymax == n - 1


def test_append():
    curve1 = Curve2D([(i, i) for i in range(10)])
    curve1.append((10, 10))
    curve1.append(Curve2D([(i, i) for i in range(11, 15)]))
    curve2 = Curve2D([(i, i) for i in range(15)])
    assert curve1.x == curve2.x and curve1.y == curve2.y


def test_pickle():
    curve1 = Curve2D([(i, i) for i in range(10)])
    temp = pickle.dumps(curve1)
    curve2 = pickle.loads(temp)
    assert curve1.x == curve2.x and curve1.y == curve2.y


def test_from_temporal():
    n = randint(10, 20)
    xoff, k = randint(-10, 10) / 10, randint(-10, 10)
    xvt = Curve2D([(i, ufloat(i, 0)) for i in range(n)])
    yvt = Curve2D([(i + xoff, ufloat((i + xoff) * k, 0)) for i in range(n)])
    curve = Curve2D.from_two_temporal(xvt, yvt)
    assert compare_lists(curve.x, xvt.y) and \
           compare_lists(curve.y, [ufloat(i * k, 0) for i in range(n)])
    curve = Curve2D.from_two_temporal(xvt, yvt, pick_yvt_points=True)
    assert compare_lists(curve.x, [ufloat(i + xoff, 0) for i in range(n)]) and \
           compare_lists(curve.y, yvt.y)


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
    assert curve.xvy(11).x == 5.5
    assert curve.yvx(4.25).y == 8.5


def test_lsm():
    k, b = randint(0, 100), randint(0, 100)
    curve = Curve2D([(i, i * k + b) for i in range(10)])
    assert curve.lsm() == (k, b)
