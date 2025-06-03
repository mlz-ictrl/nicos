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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Module to test custom specific modules."""

import numpy as np
import pytest
from scipy import ndimage

pytest.importorskip('cv2')

from nicos.utils.gammafilter import gam_rem_adp_log, scharr_filter


@pytest.fixture(scope='function', autouse=True)
def img():
    """Return a test image read from file."""
    with np.load('test/test_basic/data/ascent.npz') as data:
        img = np.copy(data['arr_0'].astype(np.uint16))
        yield img


def test_sharpness(img):
    sharpvals = []
    sigmas = [-30, -11, -5, -3, 0, 3, 5, 11, 30]
    exp_sharpness = [15.34, 34.98, 63.92, 99.24, 271.84, 99.24, 63.92, 34.98,
                     15.34]

    # calculate sharpness for a series of blurred pictures
    for sigma, expected in zip(sigmas, exp_sharpness):
        blurred_img = ndimage.gaussian_filter(img, sigma=abs(sigma))
        sharp = scharr_filter(gam_rem_adp_log(blurred_img, 25, 100, 400, 0.8))
        assert sharp == pytest.approx(expected, abs=0.01)
        sharpvals.append(sharp)


def test_calculations(img):
    white = 0xffff * np.ones([500, 500], dtype=np.uint16)
    assert scharr_filter(gam_rem_adp_log(white, 25, 100, 400, 0.8)) == 0

    black = np.zeros([500, 500], dtype=np.uint16)
    assert scharr_filter(gam_rem_adp_log(black, 25, 100, 400, 0.8)) == 0

    assert scharr_filter(gam_rem_adp_log(img, 25, 100, 400, 0.8)) > \
        scharr_filter(gam_rem_adp_log(
            ndimage.gaussian_filter(img, sigma=10), 25, 100, 400, 0.8))
