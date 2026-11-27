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
import warnings

import numpy
from scipy.optimize import curve_fit

from .imports import AffineScalarFunc, ufloat


def _nominals_and_errors(values, errors=None):
    """Convert measurements and standard errors to two floating-point arrays.

    Explicit errors take precedence. Otherwise, use the errors attached to
    the measurements and represent unknown errors as NaN.
    """
    nominals = [v.n if isinstance(v, AffineScalarFunc) else v for v in values]
    if errors is None:
        errors = [v.s if isinstance(v, AffineScalarFunc) else math.nan
                  for v in values]
    return numpy.array(nominals, dtype=float), numpy.array(errors, dtype=float)


def _usable_as_weights(errors):
    return bool(numpy.all(numpy.isfinite(errors)) and numpy.all(errors > 0))


def mean(x, dx=None):
    """Return the mean and standard error of a sequence of measurements.

    Supply standard errors in `dx` or attach them to the values in `x`.
    For multiple measurements with finite, positive errors, weight by
    inverse variance. Otherwise, use the arithmetic mean and estimate its
    standard error from the sample scatter.

    A single measurement retains its standard error, which may be NaN.
    An empty sequence yields NaN for both the mean and its error.
    """
    x, dx = _nominals_and_errors(x, dx)
    n = len(x)
    if not n:
        return ufloat(math.nan, math.nan)
    if n == 1:
        return ufloat(x[0], dx[0])
    if _usable_as_weights(dx):
        weights = 1 / dx ** 2
        return ufloat(numpy.sum(weights * x) / numpy.sum(weights),
                      numpy.sum(weights) ** -0.5)
    return ufloat(numpy.mean(x), numpy.std(x, ddof=1) / n ** 0.5)


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
    # slope scale of the data keeps the tolerance meaningful for k close to 0
    tolerance = 1e-12 * max(numpy.abs(k), numpy.ptp(y) / numpy.ptp(x))
    for _ in range(200):
        w = wx * wy / (k ** 2 * wy + wx)
        x_bar = numpy.sum(w * x) / numpy.sum(w)
        y_bar = numpy.sum(w * y) / numpy.sum(w)
        ui = x - x_bar
        vi = y - y_bar
        beta = w * (ui / wy + k * vi / wx)
        k_new = numpy.sum(w * beta * vi) / numpy.sum(w * beta * ui)
        converged = numpy.abs(k_new - k) <= tolerance
        k = k_new
        if converged:
            break
    else:
        warnings.warn('Weighted total least-squares did not converge',
                      RuntimeWarning)
    b = y_bar - k * x_bar
    x_adj_bar = numpy.sum(w * (x_bar + beta)) / numpy.sum(w)
    u = (x_bar + beta) - x_adj_bar
    se_k = numpy.sqrt(1.0 / numpy.sum(w * u ** 2))
    se_b = numpy.sqrt(1.0 / numpy.sum(w) + x_adj_bar ** 2 * se_k ** 2)
    return ufloat(k, se_k), ufloat(b, se_b)


def lsm(x, y, dx=None, dy=None):
    """Fit Y = slope * X + intercept and return (slope, intercept).

    Supply paired coordinates with attached standard errors, or pass
    explicit errors in `dx` and `dy`. With three or more points, use a York
    fit when both error arrays are finite and positive, Y-weighted least
    squares when only the Y errors qualify, and ordinary least squares
    otherwise. The ordinary fit estimates errors from residual scatter.

    Two distinct X values define a line directly, with errors propagated
    from the endpoints when uncertainties is available. If fewer than two
    distinct X values are supplied, return two values with NaN nominals and
    standard errors.
    """
    x, dx = _nominals_and_errors(x, dx)
    y, dy = _nominals_and_errors(y, dy)

    if len(x) < 2 or numpy.all(x == x[0]):
        # a single point or points with equal X don't define a line y(x)
        return ufloat(math.nan, math.nan), ufloat(math.nan, math.nan)
    if len(x) == 2:
        x0, x1 = ufloat(x[0], dx[0]), ufloat(x[1], dx[1])
        y0, y1 = ufloat(y[0], dy[0]), ufloat(y[1], dy[1])
        k = (y1 - y0) / (x1 - x0)
        return k, y1 - k * x1
    if _usable_as_weights(dy):
        if _usable_as_weights(dx):
            return _lsm_dx_dy(x, y, dx, dy)
        return _lsm_dy(x, y, dy)
    return _lsm(x, y)
