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

"""Module for data analyzing user commands."""

__version__ = "$Revision$"

from math import sqrt

import numpy as np

from nicos import session
from nicos.errors import UsageError
from nicos.commands import usercommand
from nicos.commands.scan import cscan
from nicos.commands.device import maw
from nicos.commands.output import printinfo, printwarning
from nicos.fitutils import Fit


def _getData(xcol=None, ycol=None):
    if not session.experiment._last_datasets:
        raise UsageError('no latest dataset has been stored')
    dataset = session.experiment._last_datasets[-1]
    xs = ys = None
    if xcol is not None:
        if isinstance(xcol, str):
            try:
                xcol = dataset.xnames.index(xcol)
            except ValueError:
                raise UsageError('no such x column: %r' % xcol)
        try:
            xs = np.array([p[xcol] for p in dataset.positions])
        except IndexError:
            raise UsageError('no such x column: %r' % xcol)
    if ycol is not None:
        if isinstance(ycol, str):
            try:
                ycol = dataset.ynames.index(ycol)
            except ValueError:
                raise UsageError('no such y column: %r' % ycol)
        try:
            ys = np.array([p[ycol] for p in dataset.yresults])
        except IndexError:
            raise UsageError('no such y column: %r' % ycol)
    return xs, ys


@usercommand
def center_of_mass(xcol, ycol):
    """
    Calculate the center of mass x-coordinate of the last scan.
    """
    xs, ys = _getData(xcol, ycol)
    cm = (xs*ys).sum() / float(ys.sum())
    return float(cm)


@usercommand
def root_mean_square(ycol):
    """
    Calculate the root-mean-square of the last scan.
    """
    ys = _getData(None, ycol)
    return sqrt((ys**2).sum() / len(ys))


@usercommand
def gauss(xcol, ycol):
    """
    Fit a Gaussian through the data.
    """
    xs, ys = _getData(xcol, ycol)
    c = 2 * np.sqrt(2 * np.log(2))
    def model(v, x):
        return v[1] * np.exp(-0.5 * (x - v[0])**2 / (v[2] / c)**2) + v[3]
    fit = Fit(model, ['x0', 'A', 'sigma', 'B'],
              [0.5*(xs[0]+xs[-1]), xs.max(), (xs[1]-xs[0])*5, 0],
              allow_leastsq=False)
    res = fit.run('gauss', xs, ys, np.sqrt(ys))
    if res._failed:
        return None, None
    return tuple(res._pars[1]), tuple(res._pars[2])


@usercommand
def center(dev, center, step, numsteps, *args, **kwargs):
    """
    Move the given device to the maximum of a Gaussian fit through a
    center scan with the given parameters.
    """
    cscan(dev, center, step, numsteps, *args, **kwargs)
    params, errors = gauss(0, -1)  # XXX which column!
    # do not allow moving outside of the scanned region
    minvalue = center - step*numsteps
    maxvalue = center + step*numsteps
    if params is None:
        printwarning('Gaussian fit failed, no centering done')
    elif not minvalue <= params[0] <= maxvalue:
        printwarning('Gaussian fit resulted in center outside scanning area, '
                     'no centering done')
    else:
        printinfo('Centered peak for %s' % dev)
        maw(dev, params[0])


@usercommand
def checkoffset(dev, center, step, numsteps, *args, **kwargs):
    """
    Readjust offset of the given device, so that the center of the given
    scan coincides with the center of a Gaussian fit.
    """
    cscan(dev, center, step, numsteps, *args, **kwargs)
    params, errors = gauss(0, -1)  # XXX which column!
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
        printinfo('Center of Gaussian fit at %.2f %s' % (params[0], dev.unit))
        printinfo('Adjusting offset of %s by %.2f %s' % (dev, diff, dev.unit))
        dev.offset += diff
