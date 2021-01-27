#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Module to test custom specific modules."""

import numpy as np
import scipy.misc
from scipy import ndimage

from nicos_mlz.antares.lib.calculations import gam_rem_adp_log, scharr_filter

from test.utils import approx


def test_calculations():
    img = scipy.misc.ascent()

    sharpvals = []
    sigmas = [-30, -11, -5, -3, 0, 3, 5, 11, 30]
    exp_sharpness = [15.34, 34.98, 63.92, 99.24, 271.79, 99.24, 63.92, 34.98,
                     15.34]

    # calculate sharpness for a series of blurred pictures
    for sigma, expected in zip(sigmas, exp_sharpness):
        blurred_img = ndimage.gaussian_filter(img, sigma=abs(sigma))
        sharp = scharr_filter(gam_rem_adp_log(blurred_img, 25, 100, 400, 0.8))
        assert sharp == approx(expected, abs=0.01)
        sharpvals.append(sharp)


def test_sharpness():
    img = scipy.misc.ascent()

    assert scharr_filter(gam_rem_adp_log(img, 25, 100, 400, 0.8)) > \
       scharr_filter(gam_rem_adp_log(
           ndimage.gaussian_filter(img, sigma=10), 25, 100, 400, 0.8))

    white = 0xff * np.ones([500, 500, 3], dtype=np.uint8)
    assert scharr_filter(gam_rem_adp_log(white, 25, 100, 400, 0.8)) == 0

    black = np.zeros([500, 500, 3], dtype=np.uint8)
    assert scharr_filter(gam_rem_adp_log(black, 25, 100, 400, 0.8)) == 0
