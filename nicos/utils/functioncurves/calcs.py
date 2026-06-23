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

import numpy
from scipy.optimize import curve_fit

from .imports import AffineScalarFunc, ufloat


def mean(x, dx=None):
    """Uncertainties-friendly weighted mean calculation algorithm.
    x: python list of measurement points (nominal values or values with uncertainties)
    dx: optional python list of error values related to nominal values of
    measurement points in x
    """
    if isinstance(x[0], AffineScalarFunc):
        dx = [i.s for i in x]
        x = [i.n for i in x]
    x = numpy.array(x)
    dx = numpy.array(dx)
    mn = er = 0
    n = len(x)
    if n:
        mn = x[0]
        er = dx[0] if dx.any() else 0
    if n > 1:
        if dx.any() and not numpy.any(numpy.isnan(dx)):
            mn = numpy.sum(x / dx ** 2) / numpy.sum(1 / dx ** 2)
            er = (1 / numpy.sum(1 / dx ** 2)) ** 0.5
        else:
            mn = numpy.mean(x)
            er = numpy.std(x, ddof=1) / n ** 0.5
    return ufloat(mn, er)


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
    """Weighted total least-squares via York et al., Am. J. Phys. 72 (2004) 367.
    """
    if numpy.any(dx <= 0) or numpy.any(dy <= 0):
        raise ValueError("All uncertainties must be positive")
    wx = 1.0 / dx ** 2
    wy = 1.0 / dy ** 2
    k = numpy.polyfit(x, y, 1)[0]
    w = numpy.zeros_like(x)
    beta = numpy.zeros_like(x)
    x_bar = y_bar = 0.0
    for _ in range(200):
        w = wx * wy / (k ** 2 * wy + wx)
        x_bar = numpy.sum(w * x) / numpy.sum(w)
        y_bar = numpy.sum(w * y) / numpy.sum(w)
        ui = x - x_bar
        vi = y - y_bar
        beta = w * (ui / wy + k * vi / wx)
        k_new = numpy.sum(w * beta * vi) / numpy.sum(w * beta * ui)
        if numpy.abs(k_new - k) < 1e-15 * numpy.abs(k_new):
            k = k_new
            break
        k = k_new
    b = y_bar - k * x_bar
    x_adj_bar = numpy.sum(w * (x_bar + beta)) / numpy.sum(w)
    u = (x_bar + beta) - x_adj_bar
    se_k = numpy.sqrt(1.0 / numpy.sum(w * u ** 2))
    se_b = numpy.sqrt(1.0 / numpy.sum(w) + x_adj_bar ** 2 * se_k ** 2)
    return ufloat(k, se_k), ufloat(b, se_b)


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
        return ufloat(0, 0), ufloat(y, dy if dy.any() else math.nan)
    if len(x) == 2:
        dx0, dx1 = (dx[0], dx[1]) if dx.any() else (math.nan, math.nan)
        dy0, dy1 = (dy[0], dy[1]) if dy.any() else (math.nan, math.nan)
        x0, x1, y0, y1 = x[0], x[1], y[0], y[1]
        k = (ufloat(y1, dy1) - ufloat(y0, dy0)) / (ufloat(x1, dx1) - ufloat(x0, dx0))
        return k, y1 - k * x1
    if all([math.isnan(dx[0]), math.isnan(dy[0])]):
        return _lsm(x, y)
    elif math.isnan(dx[0]):
        return _lsm_dy(x, y, dy)
    return _lsm_dx_dy(x, y, dx, dy)
