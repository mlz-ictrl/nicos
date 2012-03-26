#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""Module for data analyzing user commands."""

__version__ = "$Revision$"

from math import sqrt

import numpy as np

from nicos import session
from nicos.core import NicosError, UsageError
from nicos.utils.fitting import Fit
from nicos.commands import usercommand
from nicos.commands.scan import cscan
from nicos.commands.device import maw
from nicos.commands.output import printinfo, printwarning


def _getData(columns):
    if not session.experiment._last_datasets:
        raise NicosError('no latest dataset has been stored')
    dataset = session.experiment._last_datasets[-1]

    # xcol/ycol are 1-indexed here
    if not columns:
        xcol = 1
        ycol = -1
    elif len(columns) == 1:
        xcol, ycol = 1, columns[0]
    elif len(columns) == 2:
        xcol, ycol = columns[0], columns[1]
    else:
        raise UsageError('you can give none, one or two columns names or numbers')

    if isinstance(xcol, str):
        try:
            xcol = dataset.xnames.index(xcol) + 1
        except ValueError:
            raise NicosError('no such X column name: %r' % xcol)

    if isinstance(ycol, str):
        try:
            ycol = dataset.ynames.index(ycol) + 1
        except ValueError:
            raise NicosError('no such Y column name: %r' % ycol)
    elif ycol < 0:
        try:
            ycol = [i for i in range(len(dataset.ynames))
                    if dataset.yvalueinfo[i].type == 'counter'][0] + 1
        except IndexError:
            raise NicosError('no Y column of type "counter"')

    # now make them 0-indexed
    xcol -= 1
    ycol -= 1

    try:
        xs = np.array([p[xcol] for p in dataset.xresults])
    except IndexError:
        raise NicosError('no such X column: %r' % xcol)
    try:
        ys = np.array([p[ycol] for p in dataset.yresults])
    except IndexError:
        raise NicosError('no such Y column: %r' % ycol)

    if dataset.yvalueinfo[ycol].errors == 'sqrt':
        dys = np.sqrt(ys)
    elif dataset.yvalueinfo[ycol].errors == 'next':
        try:
            dys = np.array([p[ycol+1] for p in dataset.yresults])
        except IndexError:
            dys = np.array([1] * len(ys))
    else:
        dys = np.array([1] * len(ys))

    return xs, ys, dys


COLHELP = """
    The data columns to use can be given by the arguments: either only the Y
    column, or both X and Y columns.  If they are not given, then the default X
    column is the first, and the default Y column is the first column of type
    "counter".  Examples::

        func()     # use first X column and first counter Y column
        func(2)    # use first X column and second Y column
        func(2, 3) # use second X column and third Y column

    It is also possible to give columns by name, for example::

        func('om', 'ctr1')
"""

@usercommand
def center_of_mass(*columns):
    """Calculate the center of mass x-coordinate of the last scan."""
    xs, ys, _ = _getData(columns)
    cm = (xs*ys).sum() / float(ys.sum())
    return float(cm)

center_of_mass.__doc__ += COLHELP.replace('func(', 'center_of_mass(')


@usercommand
def fwhm(*columns):
    """Calculate an estimate of full width at half maximum.

    The search starts a the 'left' end of the data.

    Returns a tuple ``(fwhm, xpeak, ymax, ymin)``:

    * fwhm - full width half maximum
    * xpeak - x value at y = ymax
    * ymax - maximum y-value
    * ymin - minimum y-value
    """
    xs, ys, _ = _getData(columns)

    ymin = ys.min()
    ymax = ys.max()

    # Locate left and right point where the
    # y-value is larger than the half maximum value
    # (offset by ymin)
    y_halfmax = ymin + .5 * (ymax - ymin)

    numpoints = len(xs)
    i1 = 0
    for index, yval in np.ndenumerate(ys):
        if yval >= y_halfmax:
            i1 = index[0]
            break

    i2 = numpoints - 1
    for index, yval in np.ndenumerate(ys[i1+1:]):
        if yval <= y_halfmax:
            i2 = index[0]+i1+1
            break

    # if not an exact match, use average
    if ys[i1] == y_halfmax:
        x_hpeak_l = xs[i1]
    else:
        x_hpeak_l = (y_halfmax - ys[i1 - 1]) / (ys[i1] - ys[i1 - 1]) * \
            (xs[i1] - xs[i1 - 1]) + xs[i1 - 1]
    if ys[i2] == y_halfmax:
        x_hpeak_r = xs[i2]
    else:
        x_hpeak_r = (y_halfmax - ys[i2 - 1]) / (ys[i2] - ys[i2 - 1]) * \
            (xs[i2] - xs[i2 - 1]) + xs[i2 - 1]
    x_hpeak = [x_hpeak_l, x_hpeak_r]

    fwhm = abs(x_hpeak[1] - x_hpeak[0])

    # locate maximum location
    jmax = ys.argmax()
    xpeak = xs[jmax]
    return (fwhm, xpeak, ymax, ymin)

fwhm.__doc__ += COLHELP.replace('func(', 'fwhm(')


@usercommand
def root_mean_square(col=None):
    """Calculate the root-mean-square of the last scan.

    The data column to use can be given by an argument (by name or number); the
    default is the first Y column of type "counter".
    """
    _, ys, _ = _getData(col and (0, col) or ())
    return sqrt((ys**2).sum() / len(ys))


@usercommand
def poly(n, *columns):
    """Fit a polynomial of degree *n* through the last scan.

    The return value is a pair of tuples::

        (coefficients, coeff_errors)

    where both *coefficients* and *coeff_errors* are tuples of *n+1* elements.
    """
    xs, ys, dys = _getData(columns)
    def model(x, *v):
        return sum(v[i]*x**i for i in range(n+1))
    fit = Fit(model, ['a%d' % i for i in range(n+1)], [1] * (n+1))
    res = fit.run('poly', xs, ys, dys)
    if res._failed:
        return None, None
    return tuple(res._pars[1]), tuple(res._pars[2])

poly.__doc__ += COLHELP.replace('func(', 'poly(2, ')


@usercommand
def gauss(*columns):
    """Fit a Gaussian through the data of the last scan.

    The return value is a pair of tuples::

        ((x0, ampl, sigma, background), (d_x0, d_ampl, d_sigma, d_back))

    where the elements of the second tuple are the estimated standard errors of
    the fit parameters.  The fit parameters are:

    * x0 - center of the Gaussian
    * ampl - amplitude
    * sigma - FWHM
    * background
    """
    xs, ys, dys = _getData(columns)
    c = 2 * np.sqrt(2 * np.log(2))
    def model(x, x0, A, sigma, back):
        return A * np.exp(-0.5 * (x - x0)**2 / (sigma / c)**2) + back
    fit = Fit(model, ['x0', 'A', 'sigma', 'B'],
              [0.5*(xs[0]+xs[-1]), ys.max(), (xs[1]-xs[0])*5, 0])
    res = fit.run('gauss', xs, ys, dys)
    if res._failed:
        return None, None
    return tuple(res._pars[1]), tuple(res._pars[2])

gauss.__doc__ += COLHELP.replace('func(', 'gauss(')


@usercommand
def center(dev, center, step, numsteps, *args, **kwargs):
    """Move the given device to the maximum of a Gaussian fit through a scan
    around center with the given parameters.

    This supports all arguments and keyword arguments that `cscan()` supports,
    and additionally a keyword "ycol" that gives the Y column of the dataset to
    use for the Gaussian fit (see the help for `gauss()` for the meaning of this
    parameter).
    """
    ycol = kwargs.pop('ycol', -1)
    cscan(dev, center, step, numsteps, 'centering', *args, **kwargs)
    params, _ = gauss(ycol)
    # do not allow moving outside of the scanned region
    minvalue = center - step*numsteps
    maxvalue = center + step*numsteps
    if params is None:
        printwarning('Gaussian fit failed, no centering done')
    elif not minvalue <= params[0] <= maxvalue:
        printwarning('Gaussian fit resulted in center outside scanning area, '
                     'no centering done')
    else:
        printinfo('centered peak for %s' % dev)
        maw(dev, params[0])


@usercommand
def checkoffset(dev, center, step, numsteps, *args, **kwargs):
    """Readjust offset of the given device, so that the center of the given
    scan coincides with the center of a Gaussian fit.

    This supports all arguments and keyword arguments that `cscan()` supports,
    and additionally a keyword "ycol" that gives the Y column of the dataset to
    use for the Gaussian fit (see the help for `gauss()` for the meaning of this
    parameter).
    """
    ycol = kwargs.pop('ycol', -1)
    cscan(dev, center, step, numsteps, 'offset check', *args, **kwargs)
    params, _ = gauss(ycol)
    # do not allow moving outside of the scanned region
    minvalue = center - step*numsteps
    maxvalue = center + step*numsteps
    if params is None:
        printwarning('Gaussian fit failed, offset unchanged')
    elif not minvalue <= params[0] <= maxvalue:
        printwarning('Gaussian fit resulted in center outside scanning area, '
                     'offset unchanged')
    else:
        diff = params[0] - center
        printinfo('center of Gaussian fit at %s %s' %
                  (dev.format(params[0]), dev.unit))
        printinfo('adjusting offset of %s by %s %s' %
                  (dev, dev.format(diff), dev.unit))
        dev.offset += diff
