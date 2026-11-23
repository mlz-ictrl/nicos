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


import math

from .calcs import lsm, mean
from .imports import ufloat
from .points import CurvePoint2D, _compatible_types, _nominal, is_point

REVERSAL_TOLERANCE = 0.05


class ArrayOfPoints2D(list):
    """List of AffineScalarFunc values returned by Curve2D.x and Curve2D.y.

    Overrides equality to compare by nominal value (.n), avoiding the
    uncertainties library's NaN-sensitive equality check.
    """

    def __eq__(self, value):
        """Compare two lists by the nominal value of each coordinate."""
        if isinstance(value, list) and len(self) == len(value):
            return all(v0.n == _nominal(v1) for v0, v1 in zip(self, value))
        return False

    def __ne__(self, value):
        """Return whether the lists differ in nominal values."""
        return not self.__eq__(value)


class Curve2D:
    """Store an ordered sequence of points representing a function Y(X).

    Coordinates carry a nominal value and a standard error. Use unique,
    monotonic X coordinates when the points represent a single sweep. Sample
    series may contain repeated X coordinates and changes in direction.
    Curve instances compare by identity.

    Addition, subtraction, and multiplication by a scalar affect Y only.
    Operations between curves use the left curve's X values within the
    shared X range and interpolate the right curve at those values.
    """

    __array_ufunc__ = None

    def __init__(self, array=None):
        """Build a curve from an iterable of pairs or copy an existing curve.

        The order is preserved. Copying a curve creates a separate point list
        and shares its immutable points.
        """
        if array is None:
            self._xy = []
        elif isinstance(array, Curve2D):
            self._xy = array._xy.copy()
        else:
            self._xy = [CurvePoint2D(*xy) for xy in array]

    def append(self, value):
        """Append a point or extend the curve with a sequence of points.

        Pass a point as an (X, Y) tuple or list, or as a CurvePoint2D.
        Pass multiple points as a curve, list, or tuple.
        """
        if isinstance(value, Curve2D):
            self.extend(value._xy)
        elif is_point(value):
            self._xy.append(value if isinstance(value, CurvePoint2D)
                            else CurvePoint2D(*value))
        elif isinstance(value, (list, tuple)):
            self.extend(value)
        else:
            raise TypeError(
                f'Cannot append unsupported type {type(value).__name__}')

    def extend(self, __iterable):
        for i in __iterable:
            self.append(i)

    @classmethod
    def from_x_y(cls, x, y):
        """Pair successive X and Y values until either iterable is exhausted."""
        return Curve2D(list(zip(x, y)))

    @classmethod
    def from_two_temporal(cls, xvt, yvt, pick_yvt_points=False):
        """Align two time series to produce Y(X).

        Supply X(t) and Y(t) as curves or iterables of (time, value) pairs in
        time order. By default, use the times sampled in X(t). Set
        `pick_yvt_points` to use the times sampled in Y(t) instead.

        Evaluate the other series by linear interpolation or short-range
        extrapolation. Omit a sample if the other series gives no estimate.
        """
        if not isinstance(xvt, Curve2D):
            xvt = Curve2D(xvt)
        if not isinstance(yvt, Curve2D):
            yvt = Curve2D(yvt)
        res = Curve2D()
        picked, other = (yvt, xvt) if pick_yvt_points else (xvt, yvt)
        for p in picked:
            if (q := other.yvx(p.x)) is not None:
                res.append((q.y, p.y) if pick_yvt_points else (p.y, q.y))
        return res

    def series_to_curves(self, meta=None):
        """Split a measurement series into sweeps using Curves.from_series."""
        return Curves.from_series(self, meta)

    @property
    def x(self):
        """Returns list of all X values.
        """
        return ArrayOfPoints2D(p.x for p in self)

    @property
    def xmin(self):
        """Returns min X value
        """
        return min(self.x, key=lambda x: x.n) if self else ufloat(math.nan, math.nan)

    @property
    def xmax(self):
        """Returns max X value
        """
        return max(self.x, key=lambda x: x.n) if self else ufloat(math.nan, math.nan)

    def xvy(self, y):
        """Find the first point at the given nominal Y in traversal order.

        Interpolate linearly between adjacent points. Outside the sampled
        Y range, extrapolate from the end segment with the nearer endpoint.
        A single sample supplies a constant X. An empty curve returns None.
        """
        return self._interpolate(y, 1)

    @property
    def y(self):
        """Returns list of all Y values.
        """
        return ArrayOfPoints2D(p.y for p in self)

    @property
    def ymin(self):
        """Returns min Y value
        """
        return min(self.y, key=lambda y: y.n) if self else ufloat(math.nan, math.nan)

    @property
    def ymax(self):
        """Returns max Y value
        """
        return max(self.y, key=lambda y: y.n) if self else ufloat(math.nan, math.nan)

    def yvx(self, x):
        """Find the first point at the given nominal X in traversal order.

        Interpolate linearly between adjacent points. Outside the sampled
        X range, extrapolate from the end segment with the nearer endpoint.
        A single sample supplies a constant Y. An empty curve returns None.
        """
        return self._interpolate(x, 0)

    def _interpolate(self, value, axis):
        """Look up a coordinate on axis 0 (X) or axis 1 (Y).

        Return the first exact match or segment crossing in traversal order.
        For an out-of-range coordinate, choose the nearer endpoint by
        nominal distance, favoring the first endpoint on a tie.
        """
        if not self:
            return None
        if len(self) == 1:
            p = self[0]
            return CurvePoint2D(value, p.y) if axis == 0 \
                else CurvePoint2D(p.x, value)
        kwargs = {'x': value} if axis == 0 else {'y': value}
        vn = _nominal(value)
        nominals = [p[axis].n for p in self]
        if vn < min(nominals) or vn > max(nominals):
            if abs(vn - nominals[0]) <= abs(vn - nominals[-1]):
                return CurvePoint2D.interpolate(self[0], self[1], **kwargs)
            return CurvePoint2D.interpolate(self[-2], self[-1], **kwargs)
        for i, n in enumerate(nominals):
            if n == vn:
                return self[i]
            if i and min(nominals[i - 1], n) < vn < max(nominals[i - 1], n):
                return CurvePoint2D.interpolate(self[i - 1], self[i], **kwargs)
        return None

    def lsm(self):
        """Fit Y = slope * X + intercept and return (slope, intercept).

        Return None for an empty curve. A nonempty curve with fewer than two
        distinct nominal X values yields two values with NaN nominals and
        standard errors. See calcs.lsm for the weighting rules.
        """
        return lsm(self.x, self.y) if self else None

    def __iter__(self):
        return iter(self._xy)

    def __getitem__(self, index):
        result = self._xy[index]
        if isinstance(index, slice):
            return Curve2D(result)
        return result

    def __repr__(self):
        return repr(self._xy)

    def __len__(self):
        return len(self._xy)

    def _operation(self, value, direct, func):
        """Apply an arithmetic operator to a scalar or a second curve.

        The `direct` flag indicates whether this curve is the left operand.
        With two curves, return an empty curve if the left curve has no X
        sample within their shared nominal X range.
        """
        if isinstance(value, Curve2D):
            res = Curve2D()
            if not self or not value:
                return res
            start = max(self.xmin.n, value.xmin.n)
            end = min(self.xmax.n, value.xmax.n)
            (c1, c2) = (self, value) if direct else (value, self)
            for p in c1:
                if start <= p.x.n <= end:
                    res.append(func(p, c2.yvx(p.x)))
            return res
        elif isinstance(value, _compatible_types):
            return Curve2D([func(p, value) if direct else func(value, p)
                            for p in self])
        raise TypeError(f'Cannot perform operation with {type(value).__name__}')

    def __add__(self, value):
        return self._operation(value, True, lambda a, b: a + b)

    def __radd__(self, value):
        return self._operation(value, False, lambda a, b: a + b)

    # def __iadd__(self, value):

    def __sub__(self, value):
        return self._operation(value, True, lambda a, b: a - b)

    def __rsub__(self, value):
        return self._operation(value, False, lambda a, b: a - b)

    # def __isub__(self, value):

    def __mul__(self, value):
        return self._operation(value, True, lambda a, b: a * b)

    def __rmul__(self, value):
        return self._operation(value, False, lambda a, b: a * b)

    # def __imul__(self, value):
    # def __truediv__(self, value):
    # def __rtruediv__(self, value):

    def __neg__(self):
        return Curve2D([-p for p in self])

    def __pos__(self):
        return Curve2D(self._xy)


class Curves:
    """Group an ordered collection of Curve2D objects."""

    def __init__(self, curves=None):
        """Build a collection with a separate point list for each curve.

        Accept another Curves collection or an iterable of curves or point
        sequences.
        """
        if curves is None:
            self._curves = []
        else:
            self._curves = [Curve2D(curve) for curve in curves]

    @classmethod
    def from_series(cls, series, meta=None):
        """Split an ordered measurement series into sweeps.

        Pass a Curve2D or an iterable of (X, Y) pairs. When `meta` supplies
        expected point counts, slice in that order. An interrupted series can
        end with a partial sweep. Raise ValueError if the counts leave
        samples unassigned.

        Without counts, confirm a turn when X retreats from its latest
        extreme by more than 5% of the full nominal X range. Adjacent sweeps
        share a single turning sample. If the extreme repeats, end the first
        sweep at its first occurrence and start the next at its last
        occurrence. Small reversals within each sweep are retained.
        """
        if not isinstance(series, Curve2D):
            series = Curve2D(series)
        curves = Curves()
        if not series:
            return curves
        if meta:
            if sum(meta) < len(series):
                raise ValueError(f'Metadata describes {sum(meta)} points, '
                                 f'however series has {len(series)} points')
            a = 0
            for b in meta:
                if a < len(series):
                    curves.append(series[a:a + b])
                a += b
            return curves
        x = [p.x.n for p in series]
        tolerance = REVERSAL_TOLERANCE * (max(x) - min(x))
        # start of the current curve, its direction, the first and the last
        # point of its farthest argument value (more than one on a plateau)
        start, direction, turn, turn_last = 0, 0, 0, 0
        for i in range(1, len(x)):
            if not direction:
                if abs(x[i] - x[start]) > tolerance:
                    direction = 1 if x[i] > x[start] else -1
                    turn = turn_last = i
            elif (x[i] - x[turn]) * direction > 0:
                turn = turn_last = i
            elif x[i] == x[turn]:
                turn_last = i
            elif abs(x[i] - x[turn]) > tolerance:
                # a plateau at the turning point is not a part of any curve,
                # so that curves don't have duplicate arguments
                curves.append(series[start:turn + 1])
                start, direction, turn, turn_last = turn_last, -direction, i, i
        curves.append(series[start:])
        return curves

    def append(self, curve):
        """Append a curve, or extend the collection with multiple curves.

        A Curve2D is stored by reference. A list of points is converted to
        one curve. Pass a Curves collection or a list of curves to add each
        curve individually.
        """
        if isinstance(curve, Curves):
            self.extend(curve)
        elif isinstance(curve, Curve2D):
            self._curves.append(curve)
        elif isinstance(curve, list) and \
                not (curve and all(is_point(p) for p in curve)):
            # list of curves rather than a curve as a list of points
            self.extend(curve)
        else:
            self._curves.append(Curve2D(curve))

    def extend(self, curves):
        for curve in curves:
            self.append(curve)

    def __getitem__(self, index):
        result = self._curves[index]
        if isinstance(index, slice):
            return Curves(result)
        return result

    def __iter__(self):
        return iter(self._curves)

    def __repr__(self):
        return repr(self._curves)

    def __len__(self):
        return len(self._curves)

    def __delitem__(self, index):
        del self._curves[index]

    def increasing(self, by_y=True):
        """Return copies of curves whose last nominal Y exceeds their first.

        Set `by_y=False` to compare X instead. Only curves with at least two
        points are considered.
        """
        axis = 1 if by_y else 0
        return Curves([curve for curve in self if len(curve) > 1 and
                       curve[-1][axis].n > curve[0][axis].n])

    def decreasing(self, by_y=True):
        """Return copies of curves whose last nominal Y is below their first.

        Set `by_y=False` to compare X instead. Only curves with at least two
        points are considered.
        """
        axis = 1 if by_y else 0
        return Curves([curve for curve in self if len(curve) > 1 and
                       curve[-1][axis].n < curve[0][axis].n])

    def mean(self):
        """Average Y at the X samples of the first curve.

        Each later curve contributes an interpolated Y where its nominal X
        range covers the sample. Use inverse-variance weighting when all
        contributing standard errors are finite and positive. Otherwise,
        use the arithmetic mean and its sample standard error. A sole
        contribution keeps its standard error. Return an empty curve if the
        collection or its first curve is empty.
        """
        if not self:
            return Curve2D()
        first, others = self._curves[0], self._curves[1:]
        others = [(curve, curve.xmin.n, curve.xmax.n) for curve in others]
        res = Curve2D()
        for p in first:
            ys = [p.y] + [curve.yvx(p.x).y for curve, xmin, xmax in others
                          if xmin <= p.x.n <= xmax]
            res.append((p.x, mean(ys)))
        return res
