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

import numpy
from scipy.odr import ODR, Data, Model
from scipy.optimize import curve_fit

from .imports import AffineScalarFunc, ufloat


def mean(x, dx=None):
    """Uncertainties-friendly mean calculation algorithm.
    x: python list of values with uncertainties or nominal values
    dx: python list of standard deviations corresponding to nominal values in x
    """
    if isinstance(x[0], AffineScalarFunc):
        dx = [i.s for i in x]
        x = [i.n for i in x]
    x = numpy.array(x)
    dx = numpy.array(dx)
    mn = std = 0
    n = len(x)
    if n:
        mn = x[0]
        std = dx[0] if dx.any() else 0
    if n > 1:
        mn = numpy.mean(x)
        std = numpy.std(x) if not dx.any() else \
            (numpy.sum((x - mn) ** 2 + dx ** 2) / (n - 1)) ** 0.5
    return ufloat(mn, std)


def _lsm(x, y):
    n = len(x)
    sum_x = numpy.sum(x)
    sum_y = numpy.sum(y)
    sum_x_squared = numpy.sum(x ** 2)
    sum_xy = numpy.sum(x * y)
    k = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x ** 2)
    b = (sum_y - k * sum_x) / n

    x_mean = numpy.mean(x)
    residuals = y - (k * x + b)
    SE_k = (numpy.sum(residuals ** 2) / (n - 2) /
            numpy.sum((x - x_mean) ** 2)) ** 0.5
    SE_b = (numpy.sum(residuals ** 2) / (n - 2) *
            (1/n + (x_mean ** 2) / numpy.sum((x - x_mean) ** 2))) ** 0.5
    return ufloat(k, SE_k), ufloat(b, SE_b)


def _lsm_dy(x, y, dy):
    def linear_model(x, k, b):
        return k * x + b

    params, covariance = curve_fit(linear_model, x, y, sigma=dy,
                                   absolute_sigma=True)
    k, b = params
    SE_k = numpy.sqrt(covariance[0, 0])
    SE_b = numpy.sqrt(covariance[1, 1])
    return ufloat(k, SE_k), ufloat(b, SE_b)


def _lsm_dx_dy(x, y, dx, dy):
    def linear_model(p, x):
        k, b = p
        return k * x + b

    model = Model(linear_model)
    data = Data(x, y, wd=1.0 / dx ** 2, we=1.0 / dy ** 2)
    odr = ODR(data, model, beta0=[1.0, 0.0])
    odr_result = odr.run()
    k, b = odr_result.beta
    SE_k, SE_b = odr_result.sd_beta
    return ufloat(k, SE_k), ufloat(b, SE_b)


def lsm(x, y, dx=None, dy=None):
    """Uncertainties-friendly least squares algorithm."""

    if isinstance(y[0], AffineScalarFunc):
        if isinstance(x[0], AffineScalarFunc):
            dx = [i.s for i in x]
            x = [i.n for i in x]
        dy = [i.s for i in y]
        y = [i.n for i in y]

    x = numpy.array(x)
    y = numpy.array(y)
    dx = numpy.array(dx)
    dy = numpy.array(dy)

    if len(x) == 1:
        return ufloat(0, 0), ufloat(y, dy if dy.any() else 0)
    if not dx.any() and not dy.any():
        return _lsm(x, y)
    elif not dx.any():
        return _lsm_dy(x, y, dy)
    return _lsm_dx_dy(x, y, dx, dy)
