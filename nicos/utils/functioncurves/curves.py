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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************


from .calcs import lsm, mean
from .imports import AffineScalarFunc
from .points import CurvePoint2D

_compatible_types = (int, float, AffineScalarFunc)


class Curve2D:
    """Class to handle an Y(X) function curve as an array of CurvePoint2D.
    For example, curve Y(X) is represented as [(X1, Y1), (X2, Y2), ...].
    Essential features of a curve would be that it is sorted against argument
    (X) in ascending or descending order, one argument corresponds to only a
    single function value, and there are no duplicates of arguments.
    Supports uncertainties python module.
    """

    def __init__(self, array=None):
        """Creates Curve2D out of list of (X, Y(X)) tuples.
        array: can be python list of tuples or CurvePoint2D objects.
        """
        if not array:
            self._xy = []
        elif isinstance(array, Curve2D):
            self._xy = array._xy.copy()
        else:
            self._xy = [CurvePoint2D(*xy) for xy in array]

    def append(self, value):
        if isinstance(value, Curve2D):
            self.extend(value._xy)
        elif isinstance(value, list):
            self.extend(value)
        elif isinstance(value, tuple):
            self._xy.append(CurvePoint2D(*value))
        elif isinstance(value, CurvePoint2D):
            self._xy.append(value)
        else:
            raise TypeError(
                f'Cannot append unsupported type {type(value).__name__}')

    def extend(self, __iterable):
        for i in __iterable:
            self.append(i)

    @classmethod
    def from_x_y(cls, x, y):
        """Creates Curve2D out lists of X and Y.
        x: python list of X values
        y: python list of Y values
        """
        return Curve2D(list(zip(x, y)))

    @classmethod
    def from_two_temporal(cls, xvt, yvt, pick_yvt_points=False):
        """Interpolates curve Y(X) from two temporal curves X(t) and Y(t).
        Experiments are performed to study dependency between variables.
        Usually variables are described as independent, the one experimenter
        manipulates, and dependent, the one measured. Sometimes experiments
        are more complex: experimenter manipulates a variable, which manipulates
        another variable, which manipulates the variable of the study. In this
        scenario a set of two dependent variables must be measured. This set
        of variables can have different nature, e.g. field and intensity, and
        thus is measured by different instruments. Two such values, e.g. X and
        Y, cannot be measured at the same time, however they can be measured at
        times very close to each other and then interpolated. Or not necessarily
        very close but interpolation error is considered.
        Currently, this function interpolates curves linearly.
        xvt: Curve2D of X(t)
        yvt: Curve2D of Y(t)
        pick_yvt_points: should be False if final curve interpolated by X(t)
                         should be True if final curve interpolated by Y(t)
        """
        if not isinstance(xvt, Curve2D):
            xvt = Curve2D(xvt)
        if not isinstance(yvt, Curve2D):
            yvt = Curve2D(yvt)
        return Curve2D([CurvePoint2D(p.y, yvt.yvx(p.x).y) for p in xvt]) \
            if not pick_yvt_points else \
            Curve2D([CurvePoint2D(xvt.yvx(p.x).y, p.y) for p in yvt])

    def series_to_curves(self, meta=None):
        """If current Curve2D is series, Curves.from_series can be called here.
        """
        return Curves.from_series(self, meta)

    @property
    def x(self):
        """Returns list of all X values.
        """
        return [p.x for p in self] if self else None

    @property
    def xmin(self):
        """Returns min X value
        """
        return min(self.x) if self else None

    @property
    def xmax(self):
        """Returns max X value
        """
        return max(self.x) if self else None

    def xvy(self, y):
        """Linearly interpolates X(Y) on the curve.
        Interpolation outside of range is only useful when Y is slightly outside
        the curve's Y range.
        y: Y component of expected CurvePoint2D
        """
        if len(self):
            if y < self.ymin and len(self) > 1:
                return CurvePoint2D.interpolate(self[0], self[1], y=y)
            if y > self.ymax and len(self) > 1:
                return CurvePoint2D.interpolate(self[-1], self[-2], y=y)
            for i, p in enumerate(self):
                if p.eq_y(y):
                    return p
                if i:
                    if self[i - 1].y < y < self[i].y or self[i - 1].y > y > self[i].y:
                        return CurvePoint2D.interpolate(self[i - 1], self[i], y=y)

    @property
    def y(self):
        """Returns list of all Y values.
        """
        return [p.y for p in self] if self else None

    @property
    def ymin(self):
        """Returns min Y value
        """
        return min(self.y) if self else None

    @property
    def ymax(self):
        """Returns max Y value
        """
        return max(self.y) if self else None

    def yvx(self, x):
        """Linearly interpolates Y(X) on the curve.
        Interpolation outside of range is only useful when X is slightly outside
        the curve's X range.
        x: X component of expected CurvePoint2D
        """
        if len(self) > 1:
            if self[0].x < self[-1].x:
                if x < self[0].x:
                    return CurvePoint2D.interpolate(self[0], self[1], x=x)
                if x > self[-1].x:
                    return CurvePoint2D.interpolate(self[-2], self[-1], x=x)
            if self[0].x > self[-1].x:
                if x > self[0].x:
                    return CurvePoint2D.interpolate(self[0], self[1], x=x)
                if x < self[-1].x:
                    return CurvePoint2D.interpolate(self[-2], self[-1], x=x)
            for i, p in enumerate(self):
                if p.eq_x(x):
                    return CurvePoint2D(*self[i])
                if i:
                    if self[i - 1].x < x < self[i].x or self[i - 1].x > x > self[i].x:
                        return CurvePoint2D.interpolate(self[i], self[i - 1], x=x)
        else:
            return CurvePoint2D(x, self[0].y) if self else None

    def lsm(self):
        return lsm(self.x, self.y) if self else None

    def __getitem__(self, index):
        result = self._xy[index]
        if isinstance(index, slice):
            return Curve2D(result)
        return result

    def __repr__(self):
        return repr(self._xy)

    def __len__(self):
        return len(self._xy)

    def __eq__(self, value):
        """There should not be user case for this feature."""
        return NotImplemented

    def __ne__(self, value):
        """There should not be user case for this feature."""
        return NotImplemented

    def __add__(self, value):
        if not value:
            return self
        elif isinstance(value, Curve2D):
            start = max(self.xmin, value.xmin)
            end = min(self.xmax, value.xmax)
            if start > end:
                return None
            res = Curve2D()
            for p in self:
                if p.x < start or p.x > end:
                    continue
                res.append(p + value.yvx(p.x))
            return res
        elif isinstance(value, _compatible_types):
            return Curve2D([p + value for p in self])
        raise TypeError(
            f'Cannot perform operation with {type(value).__name__}')

    def __radd__(self, value):
        if not value:
            return self
        elif isinstance(value, Curve2D):
            start = max(self.xmin, value.xmin)
            end = min(self.xmax, value.xmax)
            if start > end:
                return None
            res = Curve2D()
            for p in value:
                if p.x < start or p.x > end:
                    continue
                res.append(p + self.yvx(p.x))
            return res
        elif isinstance(value, _compatible_types):
            return Curve2D([p + value for p in self])
        raise TypeError(
            f'Cannot perform operation with {type(value).__name__}')

    # def __iadd__(self, value):

    def __sub__(self, value):
        if not value:
            return self
        elif isinstance(value, Curve2D):
            start = max(self.xmin, value.xmin)
            end = min(self.xmax, value.xmax)
            if start > end:
                return None
            res = Curve2D()
            for p in self:
                if p.x < start or p.x > end:
                    continue
                res.append(p - value.yvx(p.x))
            return res
        elif isinstance(value, _compatible_types):
            return Curve2D([p - value for p in self])
        raise TypeError(
            f'Cannot perform operation with {type(value).__name__}')

    def __rsub__(self, value):
        return self.__neg__().__radd__(value)

    # def __isub__(self, value):
    # def __mul__(self, value):
    # def __rmul__(self, value):
    # def __imul__(self, value):
    # def __truediv__(self, value):
    # def __rtruediv__(self, value):

    def __neg__(self):
        return Curve2D([-p for p in self])

    def __pos__(self):
        return Curve2D(self._xy)


class Curves:
    """Class to handle a list of Curve2D objects.
    """

    def __init__(self, curves=None):
        if not curves:
            self._curves = []
        elif isinstance(curves, Curves):
            self._curves = curves._curves
        else:
            self._curves = [Curve2D(curve) for curve in curves]

    @classmethod
    def from_series(cls, series, meta=None):
        """Separates function curves from series.
        Series is a product of continuous measurement, and is considered here
        as a set of not yet separated curves.
        Separation condition is taken from measurement metadata array
        representing number of elements for each curve. If metadata is not
        available, separation condition is when argument values change from
        increase to decrease or vice versa.
        series: python list of (X, Y(X)) tuples or CurvePoint2D objects
        meta: python list of experiment metadata indicating number of points for
        each resulting curve
        """
        if not isinstance(series, Curve2D):
            series = Curve2D(series)
        curves = Curves()
        if series:
            if meta:
                a = 0
                for b in meta:
                    curves.append(series[a:a + b])
                    a += b
            else:
                sep = 0
                grad0, grad1 = None, None
                for i, p in enumerate(series):
                    if i:
                        grad1 = None if p.x.n == series[i - 1].x.n else \
                            abs(p.x.n - series[i - 1].x.n) / (p.x.n - series[i - 1].x.n)
                        if grad1 != grad0:
                            curves.append(series[sep:i])
                            sep = i - 1
                        grad0 = grad1
                curves.append(series[sep:])
                # clean-up algorithm artifacts
                mn = mean([len(curve) for curve in curves])
                to_delete = [i for i, curve in enumerate(curves) if len(curve) < mn.s]
                for i in to_delete[::-1]:
                    del curves[i]
        return curves

    def append(self, curve):
        if isinstance(curve, (Curves, list)):
            self.extend(curve)
        elif not isinstance(curve, Curve2D):
            self._curves.append(Curve2D(curve))
        else:
            self._curves.append(curve)

    def extend(self, curves):
        for curve in curves:
            self.append(curve)

    def __getitem__(self, index):
        result = self._curves[index]
        if isinstance(index, slice):
            return Curves(result)
        return result

    def __repr__(self):
        return repr(self._curves)

    def __len__(self):
        return len(self._curves)

    def __delitem__(self, index):
        del self._curves[index]

    def increasing(self, by_y=True):
        """Filters curves by increasing function or argument.
        Only makes sense to be used if function or argument gradients don't
        change their sign.
        """
        curves = []
        for curve in self:
            if by_y:
                if curve[-1].y > curve[0].y:
                    curves.append(curve)
            else:
                if curve[-1].x > curve[0].x:
                    curves.append(curve)
        return Curves(curves)

    def decreasing(self, by_y=True):
        """Filters curves by decreasing function or argument.
        Only makes sense to be used if function or argument gradients don't
        change their sign.
        """
        curves = []
        for curve in self:
            if by_y:
                if curve[-1].y < curve[0].y:
                    curves.append(curve)
            else:
                if curve[-1].x < curve[0].x:
                    curves.append(curve)
        return Curves(curves)

    def mean(self, std=True):
        """Returns mean curve from curves.
        std: flag to calculate the standard deviation. If `False`, simple
        arithmetic mean is calculated.
        """
        res = Curve2D()
        if len(self):
            if len(self) == 1:
                return self[0]
            for p in self[0]:
                ys = [p.y]
                for curve in self[1:]:
                    if curve.xmin <= p.x <= curve.xmax:
                        ys.append(curve.yvx(p.x).y)
                res.append((p.x, mean(ys) if std else sum(ys)/len(ys)))
        return res

    def amean(self):
        """Return simple arithmetic mean from curves.
        """
        return self.mean(std=False)
