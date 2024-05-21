#  -*- coding: utf-8 -*-
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

"""Utilities to handle curves in form of list of tuples.
For example, curve Y(X) is represented as [(X1, Y1), (X2, Y2), ...].
Essential features of a curve would be that it is sorted against argument (X) in
ascending order, one argument corresponds to only a single function value, and
there are no duplicates of arguments.
If one needs to consider uncertainties in their curves, consider using
uncertainties python module.
"""

import numpy
try:
    # pylint: disable=import-error
    from uncertainties.core import AffineScalarFunc, Variable, ufloat
    WITH_UNCERTAINTIES = True
except Exception:
    WITH_UNCERTAINTIES = False


def interp_points(x, p1, p2):
    """Interpolates y(x) of a point on a line through p1 and p2, when p1 and p2
    are (X, Y(X)) tuples.
    """
    if not p1[0] > p2[0] and not p1[0] < p2[0]:
        return (p1[1] + p2[1]) / 2
    k = (p2[1] - p1[1]) / (p2[0] - p1[0])
    b = p2[1] - k * p2[0]
    return k * x + b


def get_yvx(arg, curve):
    """Interpolates y(arg) on a curve given as an array of (X, Y(X)) tuples.
    """
    if len(curve) == 1:
        return curve[0][1]
    if curve[-1][0] - curve[0][0] < 0:
        curve = curve[::-1]
    if arg > curve[-1][0]:
        return interp_points(arg, curve[-2], curve[-1])
    for i, (x, _) in enumerate(curve):
        if not arg > x and not arg < x:
            return curve[i][1]
        if arg < x:
            return interp_points(arg, curve[i], curve[i - 1]) if i != 0 \
                else interp_points(arg, curve[0], curve[1])


def get_xvy(f, curve):
    """Interpolates arg of a given f(arg) from a curve given as an array of
    (X, Y(X)) tuples. Returns first occurrence.
    """
    output = []
    for i, (x, y) in enumerate(curve):
        if not f > y and not f < y:
            output.append(x)
        if i:
            if curve[i - 1][1] < f < curve[i][1] or curve[i - 1][1] > f > curve[i][1]:
                output.append(interp_points(f, curve[i - 1][::-1], curve[i][::-1]))
    return output[0]


def mean(x, dx=None):
    """Uncertainties-friendly mean calculation algorithm.
    """
    if WITH_UNCERTAINTIES:
        if isinstance(x[0], (AffineScalarFunc, Variable)):
            dx = [i.s for i in x]
            x = [i.n for i in x]
    x = numpy.array(x)
    dx = numpy.array(dx)
    n = len(x)
    mn = numpy.mean(x)
    std = numpy.std(x) if not dx.any() else \
        (numpy.sum((x - mn) ** 2 + dx ** 2) / (n - 1)) ** 0.5
    return ufloat(mn, std) if WITH_UNCERTAINTIES else (mn, std)


def curve_from_two_temporal(xvt, yvt, interp_by='x'):
    """Interpolates curve Y(X) from two temporal curves X(t) and Y(t). By
    default selects X(t) values for interpolation, for Y(t) use interp_by='y'.
    """
    yvx = []
    if interp_by == 'x':
        for tx, x in xvt:
            yvx.append((x, get_yvx(tx, yvt)))
    elif interp_by == 'y':
        for ty, y in yvt:
            yvx.append((get_yvx(ty, xvt), y))
    return yvx


def curves_from_series(data, meta=None):
    """Separates function curves from series dataset.
    Separation condition is taken from measurement metadata array having
    number of elements for each curve.
    If metadata is not available, separation condition is when argument values
    change from increase to decrease or vice versa
    """
    with_ufloat = False
    if WITH_UNCERTAINTIES:
        if isinstance(data[0][0], (AffineScalarFunc, Variable)):
            with_ufloat = True
    curves = []
    if meta:
        a = 0
        for b in meta:
            curves.append(data[a:a + b])
            a += b
    else:
        sep = 0
        grad0, grad1 = None, None
        for i, (x, _) in enumerate(data):
            if i > 0:
                if with_ufloat:
                    grad1 = abs(x.n - data[i - 1][0].n) / (x.n - data[i - 1][0].n) \
                        if x.n != data[i - 1][0].n else None
                else:
                    grad1 = abs(x - data[i - 1][0]) / (x - data[i - 1][0]) \
                        if x != data[i - 1][0] else None
                if grad1 != grad0:
                    curves.append(data[sep:i])
                    sep = i - 1
                grad0 = grad1
        curves.append(data[sep:])
        # clean-up algorithm artifacts
        mn = mean([len(curve) for curve in curves])
        if isinstance(mn, (AffineScalarFunc, Variable)):
            to_delete = [i for i, curve in enumerate(curves) if len(curve) < mn.s]
        else:
            to_delete = [i for i, curve in enumerate(curves) if len(curve) < mn[1]]
        for i in to_delete[::-1]:
            del curves[i]
    return curves


def incr_decr_curves(curves):
    """Separates curves by increasing and decreasing argument.
    """
    increasing, decreasing = [], []
    for curve in curves:
        if curve[-1][0] - curve[0][0] > 0:
            increasing.append(curve)
        else:
            decreasing.append(curve)
    return increasing, decreasing


def mean_curves(curves):
    """Calculates mean curve from a list of curves. Each curve should be an
    array of (X, Y(X)) tuples.
    """
    if len(curves) == 1:
        return curves[0]
    res = []
    for x, y in curves[0]:
        ys = [y]
        for curve in curves[1:]:
            ys.append(get_yvx(x, curve))
        res.append((x, mean(ys)))
    return res


def curve_range(curve):
    """Return a min and max argument values of a curve
    """
    c = [x for x, _ in curve]
    return min(c), max(c)


def subtract_curve(curve1, curve2):
    """Subtracts curve2 from curve1. If X ranges of curves are different, the
    resulting curve range will be an overlap of X ranges of curve1 and curve2.
    """
    if not curve1 or not curve2:
        return curve1 or []
    start1, end1 = curve_range(curve1)
    start2, end2 = curve_range(curve2)
    start = max(start1, start2)
    end = min(end1, end2)
    if start > end1:
        return None
    res = []
    for x, y in curve1:
        if x < start or x > end:
            continue
        res.append((x, y - get_yvx(x, curve2)))
    return res
