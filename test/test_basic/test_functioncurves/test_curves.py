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
Tests for the functioncurve Curves class
"""

import pickle
from random import randint

import numpy

from nicos.utils.functioncurves import Curve2D, Curves


def test_basic():
    curves1, curves2 = Curves(), Curves()
    n = randint(1, 10)
    for _ in range(n):
        curves1.append(Curve2D())
        curves2.append(Curve2D())
    curves1.append(curves2)
    assert len(curves1) == 2 * n


def test_pickle():
    curve0 = Curves([Curve2D([(i, i) for i in range(10)])])
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
    y1, y2 = randint(0, 100), randint(0, 100)
    m, s = numpy.mean([y1, y2]), numpy.std([y1, y2])
    curve1 = Curve2D([(1, y1), (10, y1)])
    curve2 = Curve2D([(1, y2), (10, y2)])
    curves = Curves([curve1, curve2])
    assert curves.mean().y[0].n == m and curves.mean().y[0].s == s
    assert curves.mean().y[1].n == m and curves.mean().y[1].s == s
