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

"""Utilities for function fitting."""

from numpy import array, power, linspace, isscalar, asarray, inf, diagonal, sqrt

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
            return 'Fit %-20s failed' % self._name
        return 'Fit %-20s success, chi2: %8.3g, params: %s' % (
            self._name or '', self.chi2,
            ', '.join('%s = %8.3g' % v[:2] for v in zip(*self._pars)))

    def __nonzero__(self):
        return not self._failed

    __bool__ = __nonzero__


class Fit(object):
    def __init__(self, model, parnames=None, parstart=None,
                 xmin=None, xmax=None):
        self.model = model
        self.parnames = parnames or []
        self.parstart = parstart or []
        self.xmin = xmin
        self.xmax = xmax
        if len(self.parnames) != len(self.parstart):
            raise ProgrammingError('number of param names must match number '
                                   'of starting values')

    def par(self, name, start):
        self.parnames.append(name)
        self.parstart.append(start)

    def run(self, name, x, y, dy):
        if leastsq is None:
            return self.result(name, None, x, y, dy, None, None,
                               msg='scipy leastsq function not available')
        if len(x) < 2:
            return self.result(name, None, x, y, dy, None, None,
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
            return self.result(name, None, x, y, dy, None, None,
                               msg='need at least as many valid data points '
                               'as there are parameters')
        xn, yn, dyn = array(xn), array(yn), array(dyn)
        try:
            popt, pcov = curve_fit(self.model, xn, yn, self.parstart, dyn)  # pylint: disable=unbalanced-tuple-unpacking
            parerrors = sqrt(abs(diagonal(pcov)))
        except (RuntimeError, ValueError, TypeError) as e:
            return self.result(name, None, xn, yn, dyn, None, None, msg=str(e))
        return self.result(name, 'lsq', xn, yn, dyn, popt, parerrors)

    def result(self, name, method, x, y, dy, parvalues, parerrors, msg=''):
        if method is None:
            dct = {'_name': name, '_failed': True, '_message': msg}
        else:
            dct = {'_name': name, '_method': method, '_failed': False,
                   '_pars': (self.parnames, parvalues, parerrors),
                   '_message': msg}
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
        return FitResult(**dct)
