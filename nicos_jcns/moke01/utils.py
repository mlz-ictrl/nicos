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

import numpy
from scipy.odr import Model, Data, ODR
from scipy.optimize import curve_fit
# pylint: disable=import-error
from uncertainties.core import AffineScalarFunc, Variable, ufloat

from nicos.utils.curves import curves_from_series, incr_decr_curves, mean_curves


def minmax_curve(curve):
    """Returns min and max function values of a curve."""

    c = [i for _, i in curve]
    return min(c), max(c)


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

    if isinstance(y[0], (AffineScalarFunc, Variable)):
        if isinstance(x[0], (AffineScalarFunc, Variable)):
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
    else:
        return _lsm_dx_dy(x, y, dx, dy)


def fit_curve(curve, fittype):
    """MOKE-specific fitting function. Fitting result is a line.
    Returns (k, b), assuming the fit is y(x) = k * x + b"""

    fittypes = ['min', 'max']
    if fittype not in fittypes:
        return
    err = 0.025
    low, high = minmax_curve(curve)
    y = numpy.array([i for _, i in curve])
    y1 = [i for i in y if low * (1 - err) < i < low * (1 + err)]
    y2 = [i for i in y if high * (1 - err) < i < high * (1 + err)]
    y = numpy.array(y1) if fittype == 'min' else numpy.array(y2)
    x = numpy.array([i for i, j in curve if j in y])
    if x.any() and y.any():
        return lsm(x, y)
    else:
        return 0, 0


def calc_ellipticity(imin, imax, ext, angle):
    """Calculates ellipticity values from intensity values."""

    if imin == imax:
        raise ValueError('calc_ellipticity(i, imin, imax) cannot be finished '
                         'when imin == imax. Check input data.')
    return (imax - imin) / ((imin + imax) / 2 - ext) * angle / 4


def scale_intensity(i, imin, imax, kerr):
    """Scales intensity value.
    """

    if imin == imax:
        raise ValueError('calc_ellipticity(i, imin, imax) cannot be finished '
                         'when imin == imax. Check input data.')
    return (i - (imin + imax) / 2) / (imax - imin) * 2 * kerr


def calculate(measurement, angle, ext):
    """MOKE-specific measurement analysis."""

    # separate increasing and decreasing curves, mean them, and fit the means
    IntvB_raw = measurement['IntvB']
    all_curves = curves_from_series(IntvB_raw)
    fit_min, fit_max = None, None
    IntvB = []
    for directed_curves in incr_decr_curves(all_curves):
        curve = mean_curves(directed_curves)
        IntvB += curve
    fit_min = fit_curve(IntvB, 'min')
    fit_max = fit_curve(IntvB, 'max')

    # calculate kerr angle/ellipticity
    kerr = calc_ellipticity(fit_min[1], fit_max[1], ext, angle)

    # rescale intensity into ellipticity curves
    EvB = []
    for b, i in IntvB:
        EvB.append((b, scale_intensity(i, fit_min[1], fit_max[1], kerr)))

    return fit_min, fit_max, IntvB, EvB, kerr


def generate_output(measurement, angle=None, ext=None):
    """Generates 2 type of output:
    1. measurement settings with full measurement curve of intensity vs.
    magnetic field;
    2. measurement and analysis settings, mean (by number of cycles) intensity
    vs. magnetic field curve, calculated ellipticity vs. magnetic field curve
    and output parameter kerr."""

    keys = ['name', 'time', 'IntvB', 'exp_type', 'mode', 'ramp', 'Bmin', 'Bmax',
            'cycles']
    if not measurement or not all(key in measurement.keys() for key in keys):
        return None

    # Measurement settings
    output = f'Sample name: {measurement["name"]}\n'
    output += f'Measurement time: {measurement["time"]}\n'
    output += f'Measurement type: {measurement["exp_type"]}\n'
    output += f'Measurement mode: {measurement["mode"]}\n'
    output += f'Power supply ramp: {measurement["ramp"]} [A/min]\n'
    output += f'Lower value of the field range Bmin: {measurement["Bmin"]} [T]\n'
    output += f'Upper value of the field range Bmax: {measurement["Bmax"]} [T]\n'
    output += f'Step size: {measurement["step"] if measurement["mode"] == "stepwise" else "n/a"} [T]\n'
    output += f'Step time: {measurement["steptime"] if measurement["mode"] == "stepwise" else "n/a"} [s]\n'
    output += f'Number of cycles: {measurement["cycles"]}\n\n'

    # raw measurement output
    if not angle and not ext:
        output += 'Measured curves of intensity vs magnetic field:\n'
        if 'BvI' in measurement.keys() and measurement['BvI']:
            output += 'I, A\tdI, A\tB, T\tdB, T\tInt, V\tdInt, V\n'
            for (I, _), (B, Int) in zip(measurement['BvI'], measurement['IntvB']):
                I, dI = (I.n, I.s) if isinstance(I, (AffineScalarFunc, Variable)) else (I, 0)
                output += f'{I}\t{dI}\t{B.n}\t{B.s}\t{Int.n}\t{Int.s}\n'
        else:
            output += 'B, T\tdB, T\tInt, V\tdInt, V\n'
            for B, I in measurement['IntvB']:
                output += f'{B.n}\t{B.s}\t{I.n}\t{I.s}\n'

    # analysis output
    if angle and ext:
        fit_min, fit_max, IntvB, EvB, kerr = calculate(measurement, angle, ext)
        output += f'Minimum intensity: {fit_min[1]} [V]\n'
        output += f'Maxmimum intensity: {fit_max[1]} [V]\n'
        output += f'Canting angle: {angle} [µrad]\n'
        output += f'Extinction: {ext} [V]\n'
        output += f'Kerr angle: {kerr} [µrad]\n\n'
        output += 'Mean intensity and ellipticity curves:\n'
        if 'BvI' in measurement.keys() and measurement['BvI']:
            output += 'I, A\tdI, A\tB, mT\tdB, mT\tI, V\tdI, V\tE, a.u.\tdE, a.u.\n'
            for (I, _), (B, Int), (_, E) in zip(measurement['BvI'][:len[IntvB]], IntvB, EvB):
                I, dI = (I.n, I.s) if isinstance(I, (AffineScalarFunc, Variable)) else (I, 0)
                output += f'{I}\t{dI}\t{B.n}\t{B.s}\t{Int.n}\t{Int.s}\t{E.n}\t{E.s}\n'
        else:
            output += 'B, mT\tdB, mT\tI, V\tdI, V\tE, a.u.\tdE, a.u.\n'
            for (B, Int), (_, E) in zip(IntvB, EvB):
                output += f'{B.n}\t{B.s}\t{Int.n}\t{Int.s}\t{E.n}\t{E.s}\n'
    return output
