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


from .imports import AffineScalarFunc, ufloat

_compatible_types = (int, float, AffineScalarFunc)


class CurvePoint2D(tuple):
    """Class to represent a 2D point of a Y(X) function curve.
    The class acts like normal tuple, however has its own arithmetic and
    logical methods.
    """

    def __new__(cls, x, y):
        if not isinstance(x, AffineScalarFunc):
            x = ufloat(x, 0)
        if not isinstance(y, AffineScalarFunc):
            y = ufloat(y, 0)
        return super(CurvePoint2D, cls).__new__(cls, (x, y))

    def __getnewargs__(self):
        # Otherwise doesn't unpickle properly
        return self.x, self.y

    @classmethod
    def interpolate(cls, p1, p2, x=None, y=None):
        """Interpolates Y(X) of a point on a line through p1 and p2, when p1
        and p2 are CurvePoint2D or (X, Y(X)) tuples.
        """
        # TODO: currently the interpolation is only linear, add more when needed
        if x and y:
            raise ValueError('Can interpolate either by `x` or by `y`')
        p1 = CurvePoint2D(*p1)
        p2 = CurvePoint2D(*p2)
        if x is not None and p1.eq_x(p2):
            if not p1.eq_x(x):
                raise ValueError(
                    f'Interpolation error for x={x} p1={p1} and p2={p2}')
            return (p1 + p2) / 2
        if y is not None and p1.eq_y(p2):
            if not p1.eq_y(y):
                raise ValueError(
                    f'Interpolation error for y={y} p1={p1} and p2={p2}')
            return CurvePoint2D((p1.x + p2.x) / 2, y)
        k = (p2.y - p1.y) / (p2.x - p1.x)
        b = p2.y - k * p2.x
        if x is not None:
            return CurvePoint2D(x, k * x + b)
        elif y is not None:
            return CurvePoint2D((y - b) / k, y)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    def eq_x(self, value):
        """Returns if X value matches to a value or to X value of another
        CurvePoint2D.
        """
        if isinstance(value, CurvePoint2D):
            return self.x.n == value.x.n
        elif isinstance(value, AffineScalarFunc):
            return self.x.n == value.n
        elif isinstance(value, _compatible_types):
            return self.x.n == value
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

    def eq_y(self, value):
        """Returns if Y value matches to a value or to Y value of another
        CurvePoint2D.
        """
        if isinstance(value, CurvePoint2D):
            return self.y.n == value.y.n
        elif isinstance(value, AffineScalarFunc):
            return self.y.n == value.n
        elif isinstance(value, _compatible_types):
            return self.y.n == value
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

    def __lt__(self, value):
        if isinstance(value, CurvePoint2D):
            return self.eq_x(value) and self.y.n < value.y.n
        elif isinstance(value, AffineScalarFunc):
            return self.y.n < value.n
        elif isinstance(value, _compatible_types):
            return self.y.n < value
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

    def __le__(self, value):
        if isinstance(value, CurvePoint2D):
            return self.eq_x(value) and self.y.n <= value.y.n
        elif isinstance(value, AffineScalarFunc):
            return self.y.n <= value.n
        elif isinstance(value, _compatible_types):
            return self.y.n <= value
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

    def __eq__(self, value):
        if isinstance(value, CurvePoint2D):
            return self.eq_x(value) and self.eq_y(value)
        else:
            return self.eq_y(value)

    def __ge__(self, value):
        if isinstance(value, CurvePoint2D):
            return self.eq_x(value) and self.y.n >= value.y.n
        elif isinstance(value, AffineScalarFunc):
            return self.y.n >= value.n
        elif isinstance(value, _compatible_types):
            return self.y.n >= value
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

    def __gt__(self, value):
        if isinstance(value, CurvePoint2D):
            return self.eq_x(value) and self.y.n > value.y.n
        elif isinstance(value, AffineScalarFunc):
            return self.y.n > value.n
        elif isinstance(value, _compatible_types):
            return self.y.n > value
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

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
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

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
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

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
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

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
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

    def __rtruediv__(self, value):
        if isinstance(value, CurvePoint2D):
            if self.eq_x(value):
                return CurvePoint2D(self.x, value.y / self.y)
            else:
                raise ValueError('Operation is possible for the CurvePoint2D '
                                 'points having equal argument values')
        elif isinstance(value, _compatible_types):
            return CurvePoint2D(self.x, value / self.y)
        else:
            raise TypeError(
                f'Cannot perform operation with {type(value).__name__}')

    def __neg__(self):
        return CurvePoint2D(self.x, -self.y)

    def __pos__(self):
        return CurvePoint2D(self.x, self.y)
