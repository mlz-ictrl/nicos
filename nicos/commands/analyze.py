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

"""Module for data analyzing user commands."""

from math import sqrt

import numpy as np

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.device import maw
from nicos.commands.scan import cscan
from nicos.core import NicosError, UsageError
from nicos.utils import FitterRegistry, printTable
from nicos.utils.analyze import estimateFWHM
from nicos.utils.fitting import Fit, GaussFit, PolyFit, SigmoidFit

__all__ = [
    'center_of_mass', 'fwhm', 'root_mean_square', 'poly', 'gauss', 'sigmoid',
    'center', 'checkoffset', 'findpeaks', 'ListFitters',
]


def _getData(columns=None, dataset=None):
    dslist = session.experiment.data.getLastScans()
    if dataset is None:
        if not dslist:
            raise NicosError('no latest dataset has been stored')
        dataset = dslist[-1]

    # append data from previous scans if this is a continuation
    i = -1
    xresults = dataset.devvaluelists
    if not dataset.devices:
        # Can happen with manualscan
        xresults = dataset.envvaluelists
    yresults = dataset.detvaluelists
    while dataset.chain:
        i -= 1
        dataset = dslist[i]
        if dataset.devices:
            xresults = dataset.devvaluelists + xresults
        else:
            xresults = dataset.envvaluelists + xresults
        yresults = dataset.detvaluelists + yresults

    # xcol/ycol are 1-indexed here
    if not columns:
        xcol = dataset.xindex + 1
        ycol = -1
    elif len(columns) == 1:
        xcol, ycol = dataset.xindex + 1, columns[0]
    elif len(columns) == 2:
        xcol, ycol = columns[0], columns[1]
    else:
        raise UsageError('you can give none, one or two columns names or '
                         'numbers')

    if isinstance(xcol, str):
        try:
            xcol = [v.name for v in dataset.devvalueinfo].index(xcol) + 1
        except ValueError:
            raise NicosError('no such X column name: %r' % xcol) from None

    if isinstance(ycol, str):
        try:
            ycol = [v.name for v in dataset.detvalueinfo].index(ycol) + 1
        except ValueError:
            raise NicosError('no such Y column name: %r' % ycol) from None
    elif ycol < 0:
        try:
            ycol = [j for (j, info) in enumerate(dataset.detvalueinfo)
                    if info.type == 'counter'][0] + 1
        except IndexError:
            raise NicosError('no Y column of type "counter"') from None

    # now make them 0-indexed
    xcol -= 1
    ycol -= 1

    # Another fix to account for manualscan
    if dataset.devvalueinfo:
        names = [dataset.devvalueinfo[xcol].name,
                 dataset.detvalueinfo[ycol].name]
    else:
        names = [dataset.envvalueinfo[xcol].name,
                 dataset.detvalueinfo[ycol].name]

    try:
        xs = np.array([p[xcol] for p in xresults])
    except IndexError:
        raise NicosError('no such X column: %r' % xcol) from None
    try:
        ys = np.array([p[ycol] for p in yresults])
    except IndexError:
        raise NicosError('no such Y column: %r' % ycol) from None

    if dataset.detvalueinfo[ycol].errors == 'sqrt':
        dys = np.sqrt(ys)
    elif dataset.detvalueinfo[ycol].errors == 'next':
        try:
            dys = np.array([p[ycol+1] for p in yresults])
        except IndexError:
            dys = np.array([1] * len(ys))
    else:
        dys = np.array([1] * len(ys))

    return xs, ys, dys, names, dataset


COLHELP = """
    The data columns to use can be given by the arguments: either only the Y
    column, or both X and Y columns.  If they are not given, then the default X
    column is the first, and the default Y column is the first column of type
    "counter".  Examples:

    >>> func()     # use first X column and first counter Y column
    >>> func(2)    # use first X column and second Y column
    >>> func(2, 3) # use second X column and third Y column

    It is also possible to give columns by name, for example:

    >>> func('om', 'ctr1')
"""


@usercommand
@helparglist('[[xcol, ]ycol]')
def center_of_mass(*columns):
    """Calculate the center of mass x-coordinate of the last scan."""
    xs, ys = _getData(columns)[:2]
    cm = (xs * ys).sum() / ys.sum()
    return float(cm)


center_of_mass.__doc__ += COLHELP.replace('func(', 'center_of_mass(')


@usercommand
@helparglist('[[xcol, ]ycol]')
def fwhm(*columns):
    """Calculate an estimate of full width at half maximum.

    The search starts a the 'left' end of the data.

    Returns a tuple ``(fwhm, xpeak, ymax, ymin)``:

    * fwhm - full width half maximum
    * xpeak - x value at y = ymax
    * ymax - maximum y-value
    * ymin - minimum y-value
    """
    xs, ys = _getData(columns)[:2]
    return estimateFWHM(xs, ys)


fwhm.__doc__ += COLHELP.replace('func(', 'fwhm(')


@usercommand
@helparglist('[ycol]')
def root_mean_square(col=None):
    """Calculate the root-mean-square of the last scan.

    The data column to use can be given by an argument (by name or number); the
    default is the first Y column of type "counter".
    """
    ys = _getData(col and (0, col) or ())[1]
    return sqrt((ys**2).sum() / len(ys))


class CommandLineFitResult(tuple):
    __display__ = False


def fit(fitclass, *columns, **kwargs):
    xs, ys, dys, _, ds = _getData(columns, dataset=kwargs.pop('dataset', None))
    fit = fitclass(**kwargs)
    res = fit.run(xs, ys, dys)
    if res._failed:
        session.log.info('Fit failed.')
        return CommandLineFitResult((None, None))
    session.notifyFitCurve(ds, fit.fit_title, res.curve_x, res.curve_y)
    descrs = fit.fit_p_descr
    vals = []
    for par, err, descr in zip(res._pars[1], res._pars[2], descrs):
        vals.append((descr, '%.5g' % par, '+/- %.5g' % err,
                     '+/- {:.1%}'.format(err / par) if par else '-'))
    printTable(('parameter', 'value', 'error', 'rel. error'),
               vals, session.log.info)
    return CommandLineFitResult((tuple(res._pars[1]), tuple(res._pars[2])))


@usercommand
@helparglist('n, [[xcol, ]ycol]')
def poly(n, *columns):
    """Fit a polynomial of degree *n* through the last scan.

    The return value is a pair of tuples::

        (coefficients, coeff_errors)

    where both *coefficients* and *coeff_errors* are tuples of *n+1* elements.
    """
    return fit(PolyFit, *columns, n=n)


poly.__doc__ += COLHELP.replace('func(', 'poly(2, ')


@usercommand
@helparglist('[[xcol, ]ycol]')
def gauss(*columns):
    """Fit a Gaussian through the data of the last scan.

    The return value is a pair of tuples::

        ((x0, ampl, sigma, background), (d_x0, d_ampl, d_sigma, d_back))

    where the elements of the second tuple are the estimated standard errors of
    the fit parameters.  The fit parameters are:

    * x0 - center of the Gaussian
    * ampl - amplitude
    * fwhm - FWHM
    * background

    If the fit failed, the result is ``(None, None)``.

    Example::

        qscan(...)
        values, stderr = gauss('h', 'det2')
        if values:  # if the fit was successful
            center = values[0]
            # now work with fitted peak center
    """
    return fit(GaussFit, *columns)


gauss.__doc__ += COLHELP.replace('func(', 'gauss(')


@usercommand
@helparglist('[[xcol], ]ycol]')
def sigmoid(*columns):
    """Fit a Sigmoid through the data of the last scan.

    The return value is a pair of tuples::

        ((a, b, x0, c), (d_a, d_b, d_x0, d_c))

    where the elemets of the second tuple the estimated standard errors of the
    fit parameters.  The fit parameters are:

    * a - amplitude of the Sigmoid
    * b - steepness of the curve
    * x0 - center
    * c - background

    if the fit failed, the result is ``(None, None)``.

    Example::

        cscan(...)
        values, stderr = sigmoid('h', 'adet')
    """
    xs, ys, dys, _, ds = _getData(columns)
    fit = SigmoidFit()
    res = fit.run(xs, ys, dys)
    if res._failed:
        return None, None
    session.notifyFitCurve(ds, 'sigmoid', res.curve_x, res.curve_y)
    descrs = ['amplitude', 'steepness', 'center', 'background']
    vals = []
    for par, err, descr in zip(res._pars[1], res._pars[2], descrs):
        vals.append((descr, '%.4f' % par, '%.4f' % err))
    printTable(('parameter', 'value', 'error'), vals, session.log.info)
    return CommandLineFitResult((tuple(res._pars[1]), tuple(res._pars[2])))


sigmoid.__doc__ += COLHELP.replace('func(', 'sigmoid(')


@usercommand
def ListFitters():
    """Print a table with all known fitters.

    These fitters are usable for `center()`, `checkoffset()` and related
    commands.
    """
    items = []
    for k, v in FitterRegistry.fitters.items():
        items.append((k, 'yes' if v.center_index is not None else 'no'))
    items.sort()
    printTable(('name', 'can center'), items, session.log.info)


def _scanFC(dev, center, step, numpoints, sname, *args, **kwargs):
    """
    The scan is performed around *center* with the given parameters.

    This supports all arguments and keyword arguments that `cscan()` supports,
    and additionally:

    * a keyword "fit", that specifies the fit function to use. Defaults to
      gaussian if not specified.

      Use `ListFitters()` to see possible values.

    * a keyword "ycol" that gives the Y column of the dataset to use for the
      fit.
    """
    ycol = kwargs.pop('ycol', -1)
    fitname = kwargs.pop('fit', 'gauss')
    fitclass = FitterRegistry.getFitterCls(fitname)
    if fitclass.center_index is None:
        raise UsageError('Fit class is not suitable for centering.')
    cscan(dev, center, step, numpoints, sname, *args, **kwargs)
    params, _ = fit(fitclass, ycol)
    newcenter = params[fitclass.center_index] if params is not None else None
    minvalue = center - step * numpoints
    maxvalue = center + step * numpoints
    return minvalue, newcenter, maxvalue


@usercommand
@helparglist('dev, center, step, numpoints, ...')
def center(dev, center, step, numpoints, *args, **kwargs):
    """Move the given device to the maximum of a fit through a scan.

    Examples:

    >>> center(omega, 5, 0.1, 10)  # scan and use a Gauss fit, move to center
    >>> center(omega, 5, 0.1, 10, fit='sigmoid')  # use different fit function
    """
    minvalue, newcenter, maxvalue = _scanFC(dev, center, step, numpoints,
                                            'centering',
                                            *args, **kwargs)
    if newcenter is None:
        session.log.warning('Fit failed, no centering done')
    elif not minvalue <= newcenter <= maxvalue:
        # do not allow moving outside of the scanned region
        session.log.warning('Fit resulted in center outside scanning '
                            'area, no centering done')
    else:
        session.log.info('centered peak for %s', dev)
        maw(dev, newcenter)


center.__doc__ += _scanFC.__doc__


@usercommand
@helparglist('dev, center, step, numpoints, ...')
def checkoffset(dev, center, step, numpoints, *args, **kwargs):
    """Readjust offset of the given device to the center of a scan.

    The adjustment is done so that afterward, the given *center* coincides
    with the center of a fit through the scan performed with the given
    stepsize and number of points.

    Examples:

    >>> checkoffset(omega, 5, 0.1, 10)  # scan and use a Gauss fit
    # scan and use different fit function
     >>> checkoffset(omega, 5, 0.1, 10, fit='sigmoid')
   """
    minvalue, newcenter, maxvalue = _scanFC(dev, center, step, numpoints,
                                            'offset check',
                                            *args, **kwargs)
    if newcenter is None:
        session.log.warning('Fit failed, offset unchanged')
    elif not minvalue <= newcenter <= maxvalue:
        # do not allow moving outside of the scanned region
        session.log.warning('Fit resulted in center outside scanning '
                            'area, offset unchanged')
    else:
        diff = newcenter - center
        session.log.info('center of fit at %s',
                         dev.format(newcenter, True))
        session.log.info('adjusting offset of %s by %s',
                         dev, dev.format(abs(diff), True))
        # what was formerly newcenter is now the real center
        dev.doAdjust(newcenter, center)


checkoffset.__doc__ += _scanFC.__doc__


@usercommand
@helparglist('[[xcol, ]ycol][, npoints=n]')
def findpeaks(*columns, **kwds):
    """Find peaks the data of the last scan.

    Peaks are determined by the property that a data point is bigger than some
    neighbors (by default 2) on every side.  Then a parabola is fitted to these
    points, which gives a good approximation to the peak center position.

    The return value is a list of possible X values of peaks.

    The following keyword arguments are accepted:

    * *npoints* -- number of neighbors (default 2) per side of peak to be
      considered: if the scan is very fine, this must be increased
    """
    # parabola model
    def model(x, b, s, c):
        return b + s*(x-c)**2
    xs, ys, dys = _getData(columns)[:3]
    np = kwds.get('npoints', 2)
    peaks = []
    # peak has to be different from background
    minpeakheight = (ys.max() - ys.min()) * 0.1 + ys.min()
    for i in range(len(xs) - 2*np):
        subys = ys[i:i+2*np+1]
        subdys = dys[i:i+2*np+1]
        # need a peak of at least minpeakheight
        if subys.max() < minpeakheight:
            continue
        # peak must be bigger than sides - including errors!
        miny = subys[np] - subdys[np]
        if (subys[0] + subdys[0] > miny) or \
           (subys[2*np] + subdys[2*np] > miny):
            continue
        # values must rise to peak and fall down
        for v in range(np):
            if subys[v] > subys[v+1] or subys[v+np] < subys[v+np+1]:
                break
        else:
            # we (probably) have a peak
            subxs = xs[i:i+2*np+1]
            b = subys[np]
            s = (subys[0] - subys[np])/(subxs[0] - subxs[np])**2
            c = subxs[np]
            fit = Fit('parabola', model, ['b', 's', 'c'], [b, s, c])
            res = fit.run(subxs, subys, subdys)
            if not res._failed:
                peaks.append(res._pars[1][2])

    return peaks


findpeaks.__doc__ += COLHELP.replace('func(', 'findpeaks(')
