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

"""Utilities for function fitting."""

__version__ = "$Revision$"

from numpy import array, power, linspace

try:
    from scipy.odr import RealData, Model, ODR
    from scipy.optimize import leastsq
except ImportError:
    ODR = None

from nicos.errors import ProgrammingError


class FitResult(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __str__(self):
        if self._failed:
            return 'Fit %-20s failed' % self._name
        elif self._method == 'ODR':
            return 'Fit %-20s success (  ODR  ), chi2: %8.3g, params: %s' % (
                self._name or '', self.chi2,
                ', '.join('%s = %8.3g +/- %8.3g' % v for v in zip(*self._pars)))
        else:
            return 'Fit %-20s success (leastsq), chi2: %8.3g, params: %s' % (
                self._name or '', self.chi2,
                ', '.join('%s = %8.3g' % v[:2] for v in zip(*self._pars)))

    def __nonzero__(self):
        return not self._failed


class Fit(object):
    def __init__(self, model, parnames=None, parstart=None,
                 xmin=None, xmax=None, allow_leastsq=True, ifixb=None):
        self.model = model
        self.parnames = parnames or []
        self.parstart = parstart or []
        self.ifixb = ifixb
        self.xmin = xmin
        self.xmax = xmax
        self.allow_leastsq = allow_leastsq
        if len(self.parnames) != len(self.parstart):
            raise ProgrammingError('number of param names must match number '
                                   'of starting values')

    def par(self, name, start):
        self.parnames.append(name)
        self.parstart.append(start)

    def run(self, name, x, y, dy):
        if ODR is None:
            # fitting not available
            return self.result(name, None, x, y, dy, None, None)
        if len(x) < 2:
            # need at least two points to fit
            return self.result(name, None, x, y, dy, None, None)
        xn, yn, dyn = [], [], []
        for i, v in enumerate(x):
            if self.xmin is not None and v < self.xmin:
                continue
            if self.xmax is not None and v > self.xmax:
                continue
            xn.append(v)
            yn.append(y[i])
            dyn.append(dy[i])
        xn, yn, dyn = array(xn), array(yn), array(dyn)
        # try fitting with ODR
        data = RealData(xn, yn, sy=dyn)
        # fit with fixed x values
        odr = ODR(data, Model(self.model), beta0=self.parstart,
                  ifixx=array([0]*len(xn)), ifixb=self.ifixb)
        out = odr.run()
        if 1 <= out.info <= 3:
            return self.result(name, 'ODR', xn, yn, dyn, out.beta, out.sd_beta)
        else:
            # if it doesn't converge, try leastsq (doesn't consider errors)
            try:
                if not self.allow_leastsq:
                    raise TypeError
                out = leastsq(lambda v: self.model(v, xn) - yn, self.parstart)
            except TypeError:
                return self.result(name, None, xn, yn, dyn, None, None)
            if out[1] <= 4:
                if isinstance(out[0], float):
                    parerrors = [0]
                    parvalues = [out[0]]
                else:
                    parerrors = [0]*len(out[0])
                    parvalues = out[0]
                return self.result(name, 'leastsq', xn, yn, dyn, parvalues,
                                   parerrors=parerrors)
            else:
                return self.result(name, None, xn, yn, dyn, None, None)

    def result(self, name, method, x, y, dy, parvalues, parerrors):
        if method is None:
            dct = {'_name': name, '_failed': True}
        else:
            dct = {'_name': name, '_method': method, '_failed': False,
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
            dct['curve_y'] = self.model(parvalues, dct['curve_x'])
            ndf = len(x) - len(parvalues)
            residuals = self.model(parvalues, x) - y
            dct['chi2'] = sum(power(residuals, 2) / power(dy, 2)) / ndf
        return FitResult(**dct)
