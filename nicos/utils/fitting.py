#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Utilities for function fitting."""

from numpy import array, power, linspace, isscalar, asarray, inf, diagonal, \
    pi, sqrt, exp, log, piecewise

try:
    from scipy.optimize.minpack import leastsq
except ImportError:
    leastsq = None

from nicos.core import ProgrammingError


def _general_function(params, xdata, ydata, function):
    return function(xdata, *params) - ydata


def _weighted_general_function(params, xdata, ydata, function, weights):
    return weights * (function(xdata, *params) - ydata)


def curve_fit(f, xdata, ydata, p0=None, sigma=None, **kw):
    """This is scipy.optimize.curve_fit, which is only available in very recent
    scipy.  It is overwritten below by the version from scipy if it exists
    there.
    """
    if p0 is None or isscalar(p0):
        # determine number of parameters by inspecting the function
        import inspect
        args, _varargs, _varkw, _defaults = inspect.getargspec(f)
        if len(args) < 2:
            msg = "Unable to determine number of fit parameters."
            raise ValueError(msg)
        if p0 is None:
            p0 = 1.0
        p0 = [p0]*(len(args)-1)

    args = (xdata, ydata, f)
    if sigma is None:
        func = _general_function
    else:
        func = _weighted_general_function
        args += (1.0/asarray(sigma),)

    # Remove full_output from kw, otherwise we're passing it in twice.
    return_full = kw.pop('full_output', False)
    res = leastsq(func, p0, args=args, full_output=1, **kw)
    (popt, pcov, infodict, errmsg, ier) = res  # pylint: disable=unbalanced-tuple-unpacking

    if ier not in [1, 2, 3, 4]:
        msg = "Optimal parameters not found: " + errmsg
        raise RuntimeError(msg)

    if (len(ydata) > len(p0)) and pcov is not None:
        s_sq = (func(popt, *args)**2).sum()/(len(ydata)-len(p0))
        pcov = pcov * s_sq
    else:
        pcov = inf

    if return_full:
        return popt, pcov, infodict, errmsg, ier
    else:
        return popt, pcov

try:
    from scipy.optimize.minpack import curve_fit
except ImportError:
    pass


class FitResult(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __str__(self):
        if self._failed:
            return 'Fit failed'
        return 'Fit success, chi2: %8.3g, params: %s' % (
            self.chi2,
            ', '.join('%s = %8.3g' % v[:2] for v in zip(*self._pars)))

    def __nonzero__(self):
        return not self._failed

    __bool__ = __nonzero__


class FitError(Exception):
    pass


class Fit(object):
    def __init__(self, title, model, parnames=None, parstart=None,
                 xmin=None, xmax=None):
        self.title = title
        self.model = model
        self.parnames = parnames or []
        self.parstart = parstart or []
        self.xmin = xmin
        self.xmax = xmax
        if len(self.parnames) != len(self.parstart):
            raise ProgrammingError('number of param names (%d) must match '
                                   'number of starting values (%d)' % (
                                       len(self.parnames), len(self.parstart)))

    def par(self, name, start):
        self.parnames.append(name)
        self.parstart.append(start)

    def run(self, x, y, dy):
        if leastsq is None:
            return self.result(x, y, dy, None, None,
                               msg='scipy leastsq function not available')
        if len(x) < 2:
            return self.result(x, y, dy, None, None,
                               msg='need at least two data points to fit')
        xn, yn, dyn = [], [], []
        for i, v in enumerate(x):
            if self.xmin is not None and v < self.xmin:
                continue
            if self.xmax is not None and v > self.xmax:
                continue
            dyval = dy[i] if dy is not None else 1
            if dyval > 0:
                xn.append(v)
                yn.append(y[i])
                dyn.append(dyval)
        if len(xn) < len(self.parnames):
            return self.result(x, y, dy, None, None,
                               msg='need at least as many valid data points '
                               'as there are parameters')
        xn, yn, dyn = array(xn), array(yn), array(dyn)
        try:
            # pylint: disable=unbalanced-tuple-unpacking
            popt, pcov = curve_fit(self.model, xn, yn, self.parstart, dyn)
            parerrors = sqrt(abs(diagonal(pcov)))
        except (RuntimeError, ValueError, TypeError) as e:
            return self.result(xn, yn, dyn, None, None, msg=str(e))
        return self.result(xn, yn, dyn, popt, parerrors)

    def run_or_raise(self, x, y, dy):
        res = self.run(x, y, dy)
        if res._failed:
            raise FitError(res._message)
        return res

    def result(self, x, y, dy, parvalues, parerrors, msg=None):
        if msg is not None:
            dct = {'_failed': True, '_message': msg, '_title': self.title}
        else:
            dct = {'_failed': False, '_message': msg, '_title': self.title,
                   '_pars': (self.parnames, parvalues, parerrors)}
            for name, val, err in zip(self.parnames, parvalues, parerrors):
                dct[name] = val
                dct['d' + name] = err
            if self.xmin is None:
                xmin = x[0]
            else:
                xmin = self.xmin
            if self.xmax is None:
                xmax = x[-1]
            else:
                xmax = self.xmax
            dct['curve_x'] = linspace(xmin, xmax, 1000)
            dct['curve_y'] = self.model(dct['curve_x'], *parvalues)
            ndf = len(x) - len(parvalues)
            residuals = self.model(x, *parvalues) - y
            dct['chi2'] = sum(power(residuals, 2) / power(dy, 2)) / ndf
            dct['label_x'] = 0
            dct['label_y'] = 0
            dct['label_contents'] = []
        return FitResult(**dct)


class PredefinedFit(Fit):
    """Represents a fit with a predefined model."""

    def __init__(self, parstart=None, xmin=None, xmax=None):
        Fit.__init__(self, self.fit_title, self.fit_model,
                     self.fit_params, parstart, xmin, xmax)

    def result(self, x, y, dy, parvalues, parerrors, msg=None):
        res = Fit.result(self, x, y, dy, parvalues, parerrors, msg)
        if not res._failed:
            self.process_result(res)
        return res

    fit_title = ''
    fit_params = []

    def process_result(self, res):
        """Can set res.label_{x,y} as well as a res.label_contents list."""
        pass


class LinearFit(PredefinedFit):
    """Fits with a straight line."""

    fit_title = 'linear fit'
    fit_params = ['m', 't']

    def __init__(self, parstart=None, xmin=None, xmax=None, timeseries=False):
        PredefinedFit.__init__(self, parstart, xmin, xmax)
        self._timeseries = timeseries

    def fit_model(self, x, m, t):
        return m*x + t

    def process_result(self, res):
        x2 = max(res.curve_x)
        res.label_x = x2
        res.label_y = res.m * x2 + res.t
        if self._timeseries:
            res.label_contents = [('Slope', '%.3f /s' % res.m, ''),
                                  ('', '%.3f /min' % (res.m * 60), ''),
                                  ('', '%.3f /h' % (res.m * 3600), '')]
        else:
            res.label_contents = [('Slope', '%.3f' % res.m, '')]


class PolyFit(PredefinedFit):
    """Fits with a polynomial of given degree."""

    fit_title = 'poly'

    def __init__(self, n, parstart=None, xmin=None, xmax=None):
        self._n = n
        PredefinedFit.__init__(self, parstart, xmin, xmax)

    @property
    def fit_params(self):
        return ['a%d' % i for i in range(self._n + 1)]

    def fit_model(self, x, *v):
        return sum(v[i] * x**i for i in range(self._n + 1))


FWHM_TO_SIGMA = 2 * sqrt(2 * log(2))


class GaussFit(PredefinedFit):
    """Fits with a Gaussian model."""

    fit_title = 'gauss'
    fit_params = ['x0', 'A', 'fwhm', 'B']

    def fit_model(self, x, x0, A, fwhm, B):
        return abs(B) + A*exp(-(x - x0)**2 / (2 * (fwhm / FWHM_TO_SIGMA)**2))

    def process_result(self, res):
        res.label_x = res.x0 + res.fwhm / 2
        res.label_y = res.B + res.A
        res.label_contents = [
            ('Center', res.x0, res.dx0),
            ('FWHM', res.fwhm, res.dfwhm),
            ('Ampl', res.A, res.dA),
            ('Integr', res.A * res.fwhm / FWHM_TO_SIGMA * sqrt(2 * pi), '')
        ]


class PseudoVoigtFit(PredefinedFit):

    fit_title = 'pseudo-voigt'
    fit_params = ['B', 'A', 'x0', 'hwhm', 'eta']

    def fit_model(self, x, B, A, x0, hwhm, eta):
        eta = eta % 1.0
        return abs(B) + A * (
            # Lorentzian
            eta / (1 + ((x-x0) / hwhm)**2) +
            # Gaussian
            (1 - eta) * exp(-log(2) * ((x-x0) / hwhm)**2))

    def process_result(self, res):
        res.label_x = res.x0 + res.hwhm / 2
        res.label_y = res.B + res.A
        eta = res.eta % 1.0
        integr = res.A * res.hwhm * (eta * pi + (1 - eta) * sqrt(pi / log(2)))
        res.label_contents = [
            ('Center', res.x0, res.dx0),
            ('FWHM', res.hwhm * 2, res.dhwhm * 2),
            ('Eta', eta, res.deta),
            ('Integr', integr, '')
        ]


class PearsonVIIFit(PredefinedFit):

    fit_title = 'pearson-vii'
    fit_params = ['B', 'A', 'x0', 'hwhm', 'm']

    def fit_model(self, x, B, A, x0, hwhm, m):
        return abs(B) + A / (1 + (2**(1/m) - 1)*((x-x0) / hwhm)**2) ** m

    def process_result(self, res):
        res.label_x = res.x0 + res.hwhm / 2
        res.label_y = res.B + res.A
        res.label_contents = [
            ('Center', res.x0, res.dx0),
            ('FWHM', res.hwhm * 2, res.dhwhm * 2),
            ('m', res.m, res.dm)
        ]


class TcFit(PredefinedFit):
    """Fits a power law critcal temperature."""

    fit_title = 'Tc fit'
    fit_params = ['B', 'A', 'Tc', 'alpha']

    def fit_model(self, T, B, A, Tc, alpha):
        # Model:
        #   I(T) = B + A * (1 - T/Tc)**alpha   for T < Tc
        #   I(T) = B                           for T > Tc

        def tc_curve_1(T):
            return A*(1 - T/Tc)**(alpha % 1.0) + abs(B)

        def tc_curve_2(T):
            return abs(B)

        return piecewise(T, [T < Tc], [tc_curve_1, tc_curve_2])

    def process_result(self, res):
        res.label_x = res.Tc
        res.label_y = res.B + res.A  # at I_max
        res.label_contents = [
            ('Tc', res.Tc, res.dTc),
            ('alpha', res.alpha, res.dalpha)
        ]
