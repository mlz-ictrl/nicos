#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI fitting utilities."""

__version__ = "$Revision$"

from math import sqrt, log

try:
    from scipy.odr import Model, RealData, ODR
    from scipy import exp, array, arange, piecewise
except ImportError:
    has_odr = False
else:
    has_odr = True


class FitError(Exception):
    pass


def fit_peak_common(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw),
                    modelfunc, beta0):
    totalwidth = abs(x0 - xb)
    xmin = x0 - totalwidth
    xmax = x0 + totalwidth
    if not len(xdata):
        raise FitError('No data in plot')
    i, maxi = 0, len(xdata) - 1
    while xdata[i] < xmin and i < maxi:
        i += 1
    mini = i
    while xdata[i] < xmax and i < maxi:
        i += 1
    maxi = i
    if mini >= maxi:
        raise FitError('No data in selected region')
    fitx = xdata[mini-1:maxi+1]
    fity = ydata[mini-1:maxi+1]
    model = Model(modelfunc)
    if yerr is not None and yerr.shape == 1:
        fiterr = yerr[mini-1:maxi+1]
        data = RealData(fitx, fity, sy=fiterr)
    else:
        data = RealData(fitx, fity)
    odr = ODR(data, model, beta0, ifixx=array([0]*len(fitx)))
    out = odr.run()
    if out.info & 0xFFFFFFFF >= 5:
        raise FitError(', '.join(out.stopreason))
    xfine = arange(xmin, xmax, (xmax-xmin)/200)
    return out.beta, xfine, modelfunc(out.beta, xfine)


fwhm_to_sigma = 2*sqrt(2*log(2))

def gauss(beta, x):
    # beta: [background, height, center, sigma]
    return beta[0] + beta[1]*exp(-(x-beta[2])**2 / (2*beta[3]**2))

def fit_gauss(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw)):
    beta0 = [yb, abs(y0-yb), x0, abs(x0-xw)/fwhm_to_sigma]
    return fit_peak_common(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw),
                           gauss, beta0)

def pseudo_voigt(beta, x):
    # beta: [background, height, center, width, eta]
    eta = beta[4] % 1.0
    return beta[0] + beta[1] * (
        # Lorentzian
        eta / (1 + ((x-beta[2]) / beta[3])**2) +
        # Gaussian
        (1 - eta) * exp(-log(2) * ((x-beta[2]) / beta[3])**2))

def fit_pseudo_voigt(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw)):
    beta0 = [yb, abs(y0-yb), x0, abs(x0-xw), 0.5]
    return fit_peak_common(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw),
                           pseudo_voigt, beta0)

def pearson_vii(beta, x):
    # beta: [background, height, center, width, m]
    #eta = beta[4] % 1.0
    return beta[0] + beta[1] / \
           (1 + (2**(1/beta[4]) - 1)*((x-beta[2]) / beta[3])**2) ** beta[4]

def fit_pearson_vii(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw)):
    beta0 = [yb, abs(y0-yb), x0, abs(x0-xw), 5.0]
    return fit_peak_common(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw),
                           pearson_vii, beta0)


def tc_curve(beta, T):
    # Model:
    #   I(T) = B + A * (1 - T/Tc)**alpha   for T < Tc
    #   I(T) = B                           for T > Tc
    B, A, Tc, alpha = beta
    def tc_curve_1(T):
        return A*(1 - T/Tc)**(alpha % 1.0) + abs(B)
    def tc_curve_2(T):
        return abs(B)
    return piecewise(T, [T < Tc], [tc_curve_1, tc_curve_2])

def fit_tc(xdata, ydata, yerr, (Tb, Ib), (Tc, Ic)):
    if not len(xdata):
        raise FitError('No data in plot')
    Tmin, Tmax = xdata.min(), xdata.max()
    model = Model(tc_curve)
    if yerr and yerr.shape == 1:
        data = RealData(xdata, ydata, sy=yerr)
    else:
        data = RealData(xdata, ydata)
    alpha0 = 0.5
    # guess A from maximum data point
    A0 = ydata.max() / ((Tc-Tmin)/Tc)**alpha0
    beta0 = [Ib, A0, Tc, alpha0]
    odr = ODR(data, model, beta0, ifixx=array([0]*len(xdata)))
    out = odr.run()
    Tfine = arange(Tmin, Tmax, (Tmax-Tmin)/100)
    if out.info >= 5:
        raise FitError(', '.join(out.stopreason))
    return out.beta, Tfine, tc_curve(out.beta, Tfine)
