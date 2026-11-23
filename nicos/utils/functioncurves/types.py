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

from math import nan


def _unknown_error_result(name):
    operation = getattr(float, name)

    def method(self, *args):
        result = operation(self, *args)
        if isinstance(result, float):
            return FloatWithStdError(result)
        return result

    method.__name__ = name
    return method


class FloatWithStdError(float):
    """Represent a number with a standard error when uncertainties is unavailable.

    The ``.n`` attribute gives the numeric value, and ``.s`` gives its
    standard error. If no standard error is supplied, ``.s`` is NaN.

    Operations such as addition and multiplication return a new
    FloatWithStdError. They calculate the numeric result using normal
    float arithmetic. The fallback does not calculate the resulting
    standard error, so the result's ``.s`` is NaN.

    >>> reading = FloatWithStdError(2.0, 0.1)
    >>> adjusted = reading + 1.0
    >>> adjusted.n
    3.0
    >>> adjusted.s
    nan
    """

    def __new__(cls, nominal_value, std_error=nan):
        obj = super().__new__(cls, nominal_value)  # type: ignore[arg-type]
        obj._s = std_error
        return obj

    @property
    def n(self):
        return self

    @property
    def s(self):
        return self._s

    for _name in ('__abs__', '__add__', '__mod__', '__mul__', '__neg__',
                  '__pos__', '__pow__', '__radd__', '__rmod__', '__rmul__',
                  '__rpow__', '__rsub__', '__rtruediv__', '__sub__',
                  '__truediv__'):
        locals()[_name] = _unknown_error_result(_name)

    del _name
