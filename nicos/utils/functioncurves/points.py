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
from numbers import Real

from .imports import AffineScalarFunc, ufloat

_compatible_types = (AffineScalarFunc, Real)


def _nominal(value):
    """Return the nominal value of an uncertain number, or the input itself."""
    return value.n if isinstance(value, AffineScalarFunc) else value


def is_point(value):
    """Return whether value is a two-coordinate tuple or list."""
    return isinstance(value, (tuple, list)) and len(value) == 2 and \
        all(isinstance(v, _compatible_types) for v in value)


class CurvePoint2D(tuple):
    """Represent an (X, Y) pair with uncertainties.

    Plain numbers get an unknown (NaN) standard error. Comparisons use
    nominal values. Equality compares both coordinates for a pair and Y
    for a scalar. Point-to-point arithmetic requires matching nominal X
    coordinates. Arithmetic with a scalar changes Y only.
    """

    __array_ufunc__ = None

    def __new__(cls, x, y):
        if not isinstance(x, AffineScalarFunc):
            x = ufloat(x, math.nan)
        if not isinstance(y, AffineScalarFunc):
            y = ufloat(y, math.nan)
        return super().__new__(cls, (x, y))  # type: ignore[arg-type]

    def __getnewargs__(self):
        # Otherwise doesn't unpickle properly
        return self.x, self.y

    @classmethod
    def interpolate(cls, p1, p2, x=None, y=None):
        """Evaluate the line through two points at the given X or Y.

        Supply exactly one of `x` and `y`. Each endpoint may be an (X, Y)
        pair or a CurvePoint2D. If the endpoints share the queried
        coordinate, return their midpoint when the query matches that
        coordinate and raise ValueError otherwise.
        """
        # TODO: currently the interpolation is only linear, add more when needed
        if (x is None) == (y is None):
            raise ValueError('Can interpolate either by `x` or by `y`')
        p1 = CurvePoint2D(*p1)
        p2 = CurvePoint2D(*p2)
        if x is not None:
            if p1.eq_x(p2):
                if not p1.eq_x(x):
                    raise ValueError(
                        f'Interpolation error for x={x} p1={p1} and p2={p2}')
                return (p1 + p2) / 2
            return CurvePoint2D(
                x, p1.y + (x - p1.x) * (p2.y - p1.y) / (p2.x - p1.x))
        if p1.eq_y(p2):
            if not p1.eq_y(y):
                raise ValueError(
                    f'Interpolation error for y={y} p1={p1} and p2={p2}')
            return CurvePoint2D((p1.x + p2.x) / 2, y)
        return CurvePoint2D(
            p1.x + (y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y), y)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    def _operation_error(self, value):
        return TypeError(f'Cannot perform operation with {type(value).__name__}')

    def eq_x(self, value):
        """Compare nominal X with a scalar or another point's nominal X."""
        if isinstance(value, CurvePoint2D):
            return self.x.n == value.x.n
        elif isinstance(value, _compatible_types):
            return self.x.n == _nominal(value)
        return False

    def eq_y(self, value):
        """Compare nominal Y with a scalar or another point's nominal Y."""
        if isinstance(value, CurvePoint2D):
            return self.y.n == value.y.n
        elif isinstance(value, _compatible_types):
            return self.y.n == _nominal(value)
        return False

    def __lt__(self, value):
        if isinstance(value, CurvePoint2D):
            return self.eq_x(value) and self.y.n < value.y.n
        elif isinstance(value, _compatible_types):
            return self.y.n < _nominal(value)
        raise self._operation_error(value)

    def __le__(self, value):
        if isinstance(value, CurvePoint2D):
            return self.eq_x(value) and self.y.n <= value.y.n
        elif isinstance(value, _compatible_types):
            return self.y.n <= _nominal(value)
        raise self._operation_error(value)

    def __eq__(self, value):
        if is_point(value):
            return self.eq_x(value[0]) and self.eq_y(value[1])
        elif isinstance(value, _compatible_types):
            return self.eq_y(value)
        return False

    def __ge__(self, value):
        if isinstance(value, CurvePoint2D):
            return self.eq_x(value) and self.y.n >= value.y.n
        elif isinstance(value, _compatible_types):
            return self.y.n >= _nominal(value)
        raise self._operation_error(value)

    def __gt__(self, value):
        if isinstance(value, CurvePoint2D):
            return self.eq_x(value) and self.y.n > value.y.n
        elif isinstance(value, _compatible_types):
            return self.y.n > _nominal(value)
        raise self._operation_error(value)

    def __ne__(self, value):
        return not self.__eq__(value)

    def __add__(self, value):
        if isinstance(value, CurvePoint2D):
            if self.eq_x(value):
                return CurvePoint2D(self.x, self.y + value.y)
            else:
                raise ValueError('Operation is possible for the CurvePoint2D '
                                 'points having equal argument values')
        elif isinstance(value, _compatible_types):
            return CurvePoint2D(self.x, self.y + value)
        raise self._operation_error(value)

    def __radd__(self, value):
        return self.__add__(value)

    # def __iadd__(self, value):

    def __sub__(self, value):
        if isinstance(value, CurvePoint2D):
            if self.eq_x(value):
                return CurvePoint2D(self.x, self.y - value.y)
            else:
                raise ValueError('Operation is possible for the CurvePoint2D '
                                 'points having equal argument values')
        elif isinstance(value, _compatible_types):
            return CurvePoint2D(self.x, self.y - value)
        raise self._operation_error(value)

    def __rsub__(self, value):
        return self.__neg__().__add__(value)

    # def __isub__(self, value):

    def __mul__(self, value):
        if isinstance(value, CurvePoint2D):
            if self.eq_x(value):
                return CurvePoint2D(self.x, self.y * value.y)
            else:
                raise ValueError('Operation is possible for the CurvePoint2D '
                                 'points having equal argument values')
        elif isinstance(value, _compatible_types):
            return CurvePoint2D(self.x, self.y * value)
        raise self._operation_error(value)

    def __rmul__(self, value):
        return self.__mul__(value)

    # def __imul__(self, value):

    def __truediv__(self, value):
        if isinstance(value, CurvePoint2D):
            if self.eq_x(value):
                return CurvePoint2D(self.x, self.y / value.y)
            else:
                raise ValueError('Operation is possible for the CurvePoint2D '
                                 'points having equal argument values')
        elif isinstance(value, _compatible_types):
            return CurvePoint2D(self.x, self.y / value)
        raise self._operation_error(value)

    def __rtruediv__(self, value):
        if isinstance(value, _compatible_types):
            return CurvePoint2D(self.x, value / self.y)
        raise self._operation_error(value)

    def __neg__(self):
        return CurvePoint2D(self.x, -self.y)

    def __pos__(self):
        return CurvePoint2D(self.x, self.y)
