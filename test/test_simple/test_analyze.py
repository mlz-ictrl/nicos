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

"""NICOS tests for nicos.commands.analyze."""

try:
    import scipy.odr as odrmod
except ImportError:
    odrmod = None

from nicos import session
from nicos.core import Value

from nicos.commands.analyze import fwhm, center_of_mass, root_mean_square, \
    poly, gauss
from nicos.core.data import dataman
from nicos.core.sessions.utils import MASTER


def setup_module():
    session.loadSetup('scanning')
    session.setMode(MASTER)


def teardown_module():
    session.unloadSetup()


def generate_dataset():
    """Generate a dataset as if a scan has been run."""
    import numpy
    data = numpy.array((1, 2, 1, 2, 2, 2, 5, 20, 30, 20, 10, 2, 3, 1, 2, 1, 1, 1))
    xpoints = numpy.arange(-9, 9)
    assert len(data) == len(xpoints)
    dataset = dataman.beginScan()
    dataset.xvalueinfo = [Value('x', 'other')]
    dataset.yvalueinfo = [Value('y1', 'counter'), Value('y2', 'counter')]
    dataset.xresults = [[x] for x in xpoints]
    dataset.yresults = [[y, y*2] for y in data]
    dataman._last_scans.append(dataset)


def test_fwhm():
    generate_dataset()
    result = fwhm(1, 1)
    assert result == (2.75, -1, 30, 1)


def test_center_of_mass():
    generate_dataset()
    result1 = center_of_mass()
    assert -0.840 < result1 < -0.839
    result2 = center_of_mass(2)  # center of mass from values*2 should be same
    assert result1 == result2


def test_root_mean_square():
    generate_dataset()
    result = root_mean_square()
    assert 10.176 < result < 10.177


def test_poly():
    if not odrmod:
        return
    generate_dataset()
    result1 = poly(1)
    assert len(result1) == 2 and len(result1[0]) == 2
    assert 5.851 < result1[0][0] < 5.852
    result2 = poly(2)
    assert -0.203 < result2[0][2] < -0.202
    result3 = poly(2, 2)
    assert -0.405 < result3[0][2] < -0.404
    result4 = poly(2, 1, 2)
    assert result4 == result3


def test_gauss():
    if not odrmod:
        return
    generate_dataset()
    result = gauss()
    assert len(result) == 2 and len(result[0]) == 4
    assert -0.927 < result[0][0] < -0.926
