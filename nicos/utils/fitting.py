# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************
"""Utilities for function fitting."""

from numpy import array, cos, diagonal, exp, full_like, isinf, linspace, log, \
    mean, pi, piecewise, power, sqrt
from scipy.optimize import curve_fit
from scipy.signal import argrelmax

from nicos.core import ProgrammingError
from nicos.utils import FitterRegistry
from nicos.utils.analyze import estimateFWHM


class FitResult:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __str__(self):
        if self._failed:
            return 'Fit failed'
        return 'Fit success, chi2: %8.3g, params: %s' % (
            self.chi2,
            ', '.join('%s = %8.3g' % v[:2] for v in zip(*self._pars)))

    def __bool__(self):
        return not self._failed


class FitError(Exception):
    pass


class FitterMeta(type):
    """Fitter metaclass.

    Metaclass that adds all `Fit` classes to the Fitter registry.
    """

    def __new__(mcs, clsname, bases, attrs):
        new_class = type.__new__(mcs, clsname, bases, attrs)
        # Add the notification class to the registry.
        FitterRegistry.registerFitter(new_class)

        return new_class


class Fit(metaclass=FitterMeta):
    """Fit base class

    Derived classes may set the following class properties:

    `names`
       A list of names used to resolve the class by user supplied name, e.g.
       used in the center/checkoffset usercommands. Use an empty list if the
       function needs parameters.

    `center_index`
       The index of the returned param, that is suitable for centering.
       Set to None if no param is suitable.
    """

    names = []
    center_index = None

    def __init__(self, title, model, parnames=None, parstart=None,
                 xmin=None, xmax=None):
        self.title = title
        self.model = model
        self.parnames = parnames if parnames is not None else []
        self.parstart = parstart if parstart is not None else []
        self.xmin = xmin
        self.xmax = xmax
        if (parstart is not None and len(self.parnames) != len(self.parstart)):
            raise ProgrammingError(
                'number of param names (%d) must match '
                'number of starting values (%d)' %
                (len(self.parnames), len(self.parstart))
            )

    def par(self, name, start):
        self.parnames.append(name)
        self.parstart.append(start)

    def guesspar(self, x, y):
        """Guess starting parameters

        This should get implemented in derived classes if possible
        It gets the x- and y-values data.

        If successful, it returns a list with values suitable as startparams.

        """
        raise NotImplementedError

    def _prepare(self, x, y, dy):
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
        return array(xn), array(yn), array(dyn)

    def run(self, x, y, dy):
        if len(x) < 2:
            return self.result(x, y, dy, None, None,
                               msg='need at least two data points to fit')

        xn, yn, dyn = self._prepare(x, y, dy)
        if len(xn) < len(self.parnames):
            return self.result(xn, yn, dyn, None, None,
                               msg='need at least as many valid data points '
                               'as there are parameters')

        if not len(self.parstart):  # pylint: disable=len-as-condition
            try:
                self.parstart = self.guesspar(xn, yn)
            except Exception as e:
                return self.result(xn, yn, dyn, None, None,
                                   msg='while guessing parameters: %s' % e)

        try:
            popt, pcov = curve_fit(self.model, xn, yn, self.parstart, dyn,
                                   # default of 1000 can be too restrictive,
                                   # especially with automatic initial guess
                                   maxfev=5000)
            if isinf(pcov).all():
                parerrors = full_like(popt, 0)
            else:
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


class LinearFit(PredefinedFit):
    """Fits with a straight line."""

    names = ['linear', 'line']
    fit_title = 'linear fit'
    fit_params = ['m', 't']
    fit_p_descr = ['slope', 'offset']

    def __init__(self, parstart=None, xmin=None, xmax=None, timeseries=False):
        PredefinedFit.__init__(self, parstart, xmin, xmax)
        self._timeseries = timeseries

    def fit_model(self, x, m, t):
        return m * x + t

    def guesspar(self, x, y):
        m = (y[-1] - y[0]) / (x[-1] - x[0])
        t = y[0] - m * x[0]
        return [m, t]

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


class ExponentialFit(PredefinedFit):
    """Fits with a simple exponential."""

    names = ['exp', 'exponential']
    fit_title = 'exp. fit'
    fit_params = ['b', 'x0']
    fit_p_descr = fit_params

    def __init__(self, parstart=None, xmin=None, xmax=None, timeseries=False):
        PredefinedFit.__init__(self, parstart, xmin, xmax)
        self._timeseries = timeseries

    def fit_model(self, x, b, x0):
        return exp(b * (x - x0))

    def guesspar(self, x, y):
        if len(x) > 5:
            imin = 1
            imax = -2
        else:
            imin = 0
            imax = -1
        l1 = log(y[imin])
        l2 = log(y[imax])
        x1 = x[imin]
        x2 = x[imax]
        b = (l2 - l1) / (x2 - x1)
        x0 = l1 - b * x1

        return [b, x0]

    def process_result(self, res):
        x2 = max(res.curve_x)
        res.label_x = x2
        res.label_y = exp(res.b * (x2 - res.x0))
        if self._timeseries:
            if res.b < 0:
                tc = -log(2) / res.b
                label = 'Half life'
            else:
                tc = log(2) / res.b
                label = 'Doubling time'
            res.label_contents = [(label, '%.3f s' % tc, ''),
                                  ('', '%.3f min' % (tc / 60), ''),
                                  ('', '%.3f h' % (tc / 3600), '')]
        else:
            res.label_contents = [('b', '%.3g' % res.b, ''),
                                  ('x0', '%.3g' % res.x0, '')]


class CosineFit(PredefinedFit):
    """Fits with a cosine including offset."""

    names = ['cos', 'cosine']
    fit_title = 'cosine fit'
    fit_params = ['A', 'f', 'x0', 'B']
    center_index = 2
    fit_p_descr = fit_params

    def fit_model(self, x, A, f, x0, B):
        return B + A * cos(2 * pi * f * (x - x0))

    def guesspar(self, x, y):
        ymin = min(y)
        ymax = max(y)
        A = (ymax - ymin) / 2
        B = ymax - A
        maxes = argrelmax(y, order=2)[0]
        if len(maxes) > 1:
            dx = x[maxes[1]] - x[maxes[0]]
            f = 1.0 / dx
        else:
            f = 1.0 / x.ptp()
        x0 = x[maxes[0]]
        return [A, f, x0, B]

    def process_result(self, res):
        res.label_x = res.x0
        res.label_y = min(res.curve_x)
        res.label_contents = [
            ('Freq', res.f, res.df),
            ('Omega', 2 * pi * res.f, 2 * pi * res.df),
            ('Center', res.x0, res.dx0),
            ('Ampl', res.A, res.dA),
            ('Offset', res.B, res.dB),
        ]


class PolyFit(PredefinedFit):
    """Fits with a polynomial of given degree."""

    def __init__(self, parstart=None, xmin=None, xmax=None, n=None):
        if n is None:
            raise ValueError('Polynomial fit requires the order (n) to be given')
        self._n = n
        PredefinedFit.__init__(self, parstart, xmin, xmax)

    @property
    def fit_params(self):
        return ['a%d' % i for i in range(self._n + 1)]

    @property
    def fit_p_descr(self):
        return self.fit_params

    @property
    def fit_title(self):
        return 'poly(%d)' % self._n

    def fit_model(self, x, *v, **args):
        if args and not v:
            for k in self.fit_params:
                par = args.get(k, None)
                if par is not None:
                    v += (par,)
        return sum(v[i] * x ** i for i in range(self._n + 1))

    def guesspar(self, x, y):
        return [1] + [0] * self._n


FWHM_TO_SIGMA = 2 * sqrt(2 * log(2))


class GaussFit(PredefinedFit):
    """Fits with a Gaussian model."""

    names = ['gauss', 'gaussian']
    fit_title = 'gauss'
    fit_params = ['x0', 'A', 'fwhm', 'B']
    fit_p_descr = ['center', 'amplitude', 'FWHM', 'background']
    center_index = 0

    def fit_model(self, x, x0, A, fwhm, B):
        return abs(B) + A * exp(-(x - x0) ** 2 / (2 * (fwhm / FWHM_TO_SIGMA) ** 2))

    def guesspar(self, x, y):
        (fwhm, x0, ymax, B) = estimateFWHM(x, y)
        A = ymax - B
        return [x0, A, fwhm, B]

    def process_result(self, res):
        res.label_x = res.x0 + res.fwhm / 2
        res.label_y = res.B + res.A
        res.label_contents = [
            ('Center', res.x0, res.dx0),
            ('FWHM', res.fwhm, res.dfwhm),
            ('Ampl', res.A, res.dA),
            ('Integr', res.A * res.fwhm / FWHM_TO_SIGMA * sqrt(2 * pi), '')
        ]


class LorentzFit(PredefinedFit):

    names = ['lorentzian', 'lorentz']
    fit_title = 'lorentz'
    fit_params = ['x0', 'A', 'fwhm', 'B']
    fit_p_descr = ['center', 'amplitude', 'FWHM', 'background']
    center_index = 0

    def fit_model(self, x, x0, A, fwhm, B):
        return abs(B) + A / (1 + 4 * ((x - x0) / fwhm) ** 2)

    def guesspar(self, x, y):
        fwhm, x0, ymax, B = estimateFWHM(x, y)
        A = ymax - B
        return [x0, A, fwhm, B]

    def process_result(self, res):
        res.label_x = res.x0 + res.fwhm / 2
        res.label_y = res.B + res.A
        res.label_contents = [
            ('Center', res.x0, res.dx0),
            ('FWHM', res.fwhm, res.dfwhm),
            ('Ampl', res.A, res.dA),
            ('Integr', res.A * res.fwhm / 2 * pi, '')
        ]


class PseudoVoigtFit(PredefinedFit):

    names = ['pseudovoigt', 'pseudo-voigt']
    fit_title = 'pseudo-voigt'
    fit_params = ['B', 'A', 'x0', 'hwhm', 'eta']
    fit_p_descr = fit_params
    center_index = 2

    def fit_model(self, x, B, A, x0, hwhm, eta):
        eta = eta % 1.0
        return abs(B) + A * (
            # Lorentzian
            eta / (1 + ((x - x0) / hwhm) ** 2) +
            # Gaussian
            (1 - eta) * exp(-log(2) * ((x - x0) / hwhm) ** 2))

    def guesspar(self, x, y):
        (fwhm, x0, ymax, B) = estimateFWHM(x, y)
        A = ymax - B
        eta = 0.5
        return [B, A, x0, fwhm / 2., eta]

    def process_result(self, res):
        res.label_x = res.x0 + res.hwhm / 2
        res.label_y = res.B + res.A
        eta = res.eta = res.eta % 1.0
        integr = res.A * res.hwhm * (eta * pi + (1 - eta) * sqrt(pi / log(2)))
        res.label_contents = [
            ('Center', res.x0, res.dx0),
            ('FWHM', res.hwhm * 2, res.dhwhm * 2),
            ('Eta', eta, res.deta),
            ('Integr', integr, '')
        ]


class PearsonVIIFit(PredefinedFit):

    names = ['pearson', 'pearson-vii']
    center_index = 2
    fit_title = 'pearson-vii'
    fit_params = ['B', 'A', 'x0', 'hwhm', 'm']
    fit_p_descr = fit_params

    def fit_model(self, x, B, A, x0, hwhm, m):
        return abs(B) + A / (1 + (2 ** (1 / m) - 1) * ((x - x0) / hwhm) ** 2) ** m

    def guesspar(self, x, y):
        (fwhm, x0, ymax, B) = estimateFWHM(x, y)
        A = ymax - B
        m = 5
        return [B, A, x0, fwhm / 2., m]

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

    names = ['tc', 'tcfit']
    fit_title = 'Tc fit'
    fit_params = ['B', 'A', 'Tc', 'alpha']
    fit_p_descr = fit_params
    center_index = 2

    def fit_model(self, T, B, A, Tc, alpha):
        # Model:
        #   I(T) = B + A * (1 - T/Tc)**alpha   for T < Tc
        #   I(T) = B                           for T > Tc

        def tc_curve_1(T):
            return A * (1 - T / Tc) ** (alpha) + abs(B)

        def tc_curve_2(T):
            return abs(B)

        return piecewise(T, [T < Tc], [tc_curve_1, tc_curve_2])

    def guesspar(self, x, y):
        B = min(y)
        A = max(y) - B
        alpha = 0.5
        Tc = mean(x)
        return [B, A, Tc, alpha]

    def process_result(self, res):
        res.label_x = res.Tc
        res.label_y = res.B + res.A  # at I_max
        res.label_contents = [
            ('Tc', res.Tc, res.dTc),
            ('alpha', res.alpha, res.dalpha)
        ]


class SigmoidFit(PredefinedFit):
    """Fit a Sigmoid function."""

    names = ['sigmoid']
    fit_title = 'Sigmoid'
    fit_params = ['a', 'b', 'x0', 'c']
    fit_p_descr = fit_params
    center_index = 2

    def fit_model(self, x, a, b, x0, c):
        v = a / (1 + exp(-b * (x - x0))) + c
        v[isinf(v)] = 0.0
        return v

    def guesspar(self, x, y):
        c = min(y)
        a = max(y) - c
        b = 0.5 if y[0] > y[-1] else -0.5
        x0 = mean(x)
        return [a, b, x0, c]

    def process_result(self, res):
        res.label_x = res.x0
        res.label_y = res.c
        res.label_contents = [
            ('a', res.a, res.da),
            ('b', res.b, res.db),
            ('x0', res.x0, res.dx0),
            ('c', res.c, res.dc)
        ]


class CenterOfMass(Fit):
    """'Fit' the center of mass."""

    names = ['center_of_mass']
    fit_title = 'Center of mass'
    fit_params = ['x0']
    fit_p_descr = ['Center of mass']
    center_index = 0

    def __init__(self, xmin=None, xmax=None):
        def model(x, x0):
            return 0 * x
        Fit.__init__(self, 'Center of mass', model, xmin=xmin, xmax=xmax)

    def guesspar(self, x, y):
        # no need to guess anything here.
        return 0

    def run(self, x, y, dy):
        # apply limits
        xn, yn, dyn = self._prepare(x, y, dy)
        cm = (xn * yn).sum() / yn.sum()
        res = self.result(xn, yn, dyn, [cm], [0])
        # plot the result by showing a more or less vertical line at the
        # center-of-mass position
        res.curve_x = array([cm-0.001, cm, cm+0.001])
        res.curve_y = array([0, yn.max(), 0])
        return res
