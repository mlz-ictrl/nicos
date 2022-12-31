# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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

"""ARIANE visualization."""

import numpy as np
import matplotlib.pyplot as pl
from numpy import array, mgrid, clip
from scipy.interpolate import griddata as griddata_sp

from nicos.devices.tas.plotting import pylab_key_handler


def bin_mapping(xs, ys, zs, log=False, xscale=1, yscale=1,
                interpolate=100, minmax=None):
    xss = array(xs) * xscale
    yss = array(ys) * yscale
    if log:
        zss = list(np.log10(zs))
    else:
        zss = zs
    if minmax is not None:
        if log:
            minmax = list(map(np.log10, minmax))
        zss = clip(zss, minmax[0], minmax[1])
    interpolate = interpolate * 1j
    xi, yi = mgrid[min(xss):max(xss):interpolate,
                   min(yss):max(yss):interpolate]
    zi = griddata_sp(array((xss, yss)).T, zss, (xi, yi))
    return xss/xscale, yss/yscale, xi/xscale, yi/yscale, zi


data_x = []
data_y = []
data_z = []
options = {'log': True, 'mode': 0, 'yscale': 1, 'interpolate': 100,
           'xlabel': '', 'ylabel': ''}


def make_map(xlabel, ylabel, log, mode, yscale, interpolate):
    pl.ion()
    pl.figure('ARIANE scan', figsize=(8.5, 6), dpi=120, facecolor='1.0')
    pl.clf()
    pl.connect('key_press_event', pylab_key_handler)
    options['log'] = log
    options['mode'] = mode
    options['yscale'] = yscale
    options['interpolate'] = interpolate
    options['xlabel'] = xlabel
    options['ylabel'] = ylabel
    del data_x[:]
    del data_y[:]
    del data_z[:]


def update_map(x, y, z):
    data_x.append(x)
    data_y.append(y)
    data_z.append(z)

    try:
        mapdata = bin_mapping(data_x, data_y, data_z, log=options['log'],
                              yscale=options['yscale'],
                              interpolate=options['interpolate'])
    except Exception:
        return

    figure = pl.gcf()
    figure.clf()
    axes = pl.gca()
    _xss, _yss, xi, yi, zi = mapdata
    zi[~np.isfinite(zi)] = np.nanmin(zi)
    if options['mode'] == 0:
        im = axes.imshow(zi.T, origin='lower', aspect='auto',
                         interpolation='nearest', vmin=None, vmax=None,
                         extent=(xi[0][0], xi[-1][-1], yi[0][0], yi[-1][-1]))
    else:
        fcn = axes.contourf if options['mode'] == 1 else axes.contour
        kwds = {}
        im = fcn(xi, yi, zi, 20,
                 extent=(xi[0][0], xi[-1][-1], yi[0][0], yi[-1][-1]),
                 **kwds)
    figure.colorbar(im, ax=axes, fraction=0.05)
    colors = np.linspace(0, 1, len(data_x))
    axes.scatter(data_x, data_y, 15, colors, cmap='gray',
                 linewidths=1, edgecolors='w')
    axes.set_xlabel(options['xlabel'])
    axes.set_ylabel(options['ylabel'])
    figure.tight_layout()
