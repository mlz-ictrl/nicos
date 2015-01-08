#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

from math import sqrt, log

try:
    from scipy.odr.odrpack import Model, RealData, ODR
    from scipy import exp, array, arange, piecewise
except ImportError:
    has_odr = False
else:
    has_odr = True

from nicos.pycompat import exec_


class FitError(Exception):
    pass


def fit_peak_common(xdata, ydata, yerr, xyb, xy0, xyw, modelfunc, beta0):
    xb, x0 = xyb[0], xy0[0]
    totalwidth = abs(x0 - xb)
    xmin = x0 - totalwidth
    xmax = x0 + totalwidth
    if not len(xdata):
        raise FitError('No data in plot')
    indices = (xmin <= xdata) & (xdata <= xmax)
    xfit = xdata[indices]
    if len(xfit) == 0:
        raise FitError('No data in selected range')
    yfit = ydata[indices]
    model = Model(modelfunc)
    if yerr is not None and yerr.shape == 1:
        dyfit = yerr[indices]
        data = RealData(xfit, yfit, sy=dyfit)
    else:
        data = RealData(xfit, yfit)
    odr = ODR(data, model, beta0, ifixx=array([0]*len(xfit)))
    out = odr.run()
    if out.info & 0xFFFFFFFF >= 15:
        raise FitError(', '.join(out.stopreason))
    xfine = arange(xmin, xmax, (xmax-xmin)/500.)
    return out.beta, xfine, modelfunc(out.beta, xfine)


fwhm_to_sigma = 2*sqrt(2*log(2))

def gauss(beta, x):
    # beta: [background, height, center, sigma]
    return abs(beta[0]) + beta[1]*exp(-(x-beta[2])**2 / (2*beta[3]**2))

def fit_gauss(xdata, ydata, yerr, xyb, xy0, xyw):
    (xb, yb) = xyb
    (x0, y0) = xy0
    (xw, yw) = xyw
    beta0 = [yb, abs(y0-yb), x0, abs(x0-xw)/fwhm_to_sigma]
    return fit_peak_common(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw),
                           gauss, beta0)

def pseudo_voigt(beta, x):
    # beta: [background, height, center, width, eta]
    eta = beta[4] % 1.0
    return abs(beta[0]) + beta[1] * (
        # Lorentzian
        eta / (1 + ((x-beta[2]) / beta[3])**2) +
        # Gaussian
        (1 - eta) * exp(-log(2) * ((x-beta[2]) / beta[3])**2))

def fit_pseudo_voigt(xdata, ydata, yerr, xyb, xy0, xyw):
    (xb, yb) = xyb
    (x0, y0) = xy0
    (xw, yw) = xyw
    beta0 = [yb, abs(y0-yb), x0, abs(x0-xw), 0.5]
    return fit_peak_common(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw),
                           pseudo_voigt, beta0)

def pearson_vii(beta, x):
    # beta: [background, height, center, width, m]
    #eta = beta[4] % 1.0
    return abs(beta[0]) + beta[1] / \
           (1 + (2**(1/beta[4]) - 1)*((x-beta[2]) / beta[3])**2) ** beta[4]

def fit_pearson_vii(xdata, ydata, yerr, xyb, xy0, xyw):
    (xb, yb) = xyb
    (x0, y0) = xy0
    (xw, yw) = xyw
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

def fit_tc(xdata, ydata, yerr, TIb, TIc):
    Ib, Tc = TIb[1], TIc[0]
    if not len(xdata):
        raise FitError('No data in plot')
    Tmin, Tmax = xdata.min(), xdata.max()
    model = Model(tc_curve)
    if yerr is not None and yerr.shape == 1:
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
    if out.info & 0xFFFFFFFF >= 15:
        raise FitError(', '.join(out.stopreason))
    return out.beta, Tfine, tc_curve(out.beta, Tfine)


def fit_linear(xdata, ydata, yerr, xy1, xy2):
    (x1, y1) = xy1
    (x2, y2) = xy2
    if not len(xdata):
        raise FitError('No data in plot')
    indices = (x1 <= xdata) & (xdata <= x2)
    xfit = xdata[indices]
    if len(xfit) == 0:
        raise FitError('No data in selected range')
    yfit = ydata[indices]
    m0 = (y2-y1)/(x2-x1)
    beta0 = [m0, y1-m0*x1]
    model = Model(lambda beta, x: beta[0]*x + beta[1])
    if yerr is not None and yerr.shape == 1:
        dyfit = yerr[indices]
        data = RealData(xfit, yfit, sy=dyfit)
    else:
        data = RealData(xfit, yfit)
    odr = ODR(data, model, beta0, ifixx=array([0]*len(xfit)))
    out = odr.run()
    #if out.info & 0xFFFFFFFF >= 15:
    #    raise FitError(', '.join(out.stopreason))
    m, t = out.beta
    return out.beta, [x1, x2], [m*x1+t, m*x2+t]


def fit_arby(xdata, ydata, yerr, fcnstr, params, guesses, xlimits):
    xmin, xmax = xlimits
    if xmin is None:
        xmin = xdata.min()
    if xmax is None:
        xmax = xdata.max()
    indices = (xmin <= xdata) & (xdata <= xmax)
    xfit = xdata[indices]
    if not len(xfit):
        raise FitError('No data in plot')
    yfit = ydata[indices]
    ns = {}
    exec_('from numpy import *', ns)
    try:
        fcn = eval('lambda (%s), x: %s' % (', '.join(params), fcnstr), ns)
    except SyntaxError as e:
        raise FitError('Syntax error in function: %s' % e)
    if yerr is not None and yerr.shape == 1:
        dyfit = yerr[indices]
        data = RealData(xfit, yfit, sy=dyfit)
    else:
        data = RealData(xfit, yfit)
    model = Model(fcn)
    odr = ODR(data, model, guesses, ifixx=[0]*len(xfit))
    out = odr.run()
    xfine = arange(xmin, xmax, (xmax-xmin)/200)
    if out.info & 0xFFFFFFFF >= 15:
        raise FitError(', '.join(out.stopreason))
    return out.beta, xfine, fcn(out.beta, xfine)
