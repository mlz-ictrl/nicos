#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

import numpy as np


def estimateFWHM(xs, ys):
    """Calculate an estimate of FWHM.

    Returns a tuple ``(fwhm, xpeak, ymax, ymin)``:

    * fwhm - full width half maximum
    * xpeak - x value at y = ymax
    * ymax - maximum y-value
    * ymin - minimum y-value
    """
    xs = np.asarray(xs)
    ys = np.asarray(ys)

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
