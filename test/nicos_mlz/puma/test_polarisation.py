
# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Goetz Eckold <geckold@gwdg.de>
#
# *****************************************************************************

"""Module to test polarisation routines."""

from nicos_mlz.puma.lib.pa.deflector import ddefl, rdefl
from nicos_mlz.puma.lib.pa.gauss import gaussian

from test.utils import approx


def test_gauss():
    assert gaussian(1., 0., 0.787816968304882, 0) == 1.
    assert gaussian(1., 0., 0.787816968304882, 1.32) == approx(4.16480296E-04,
                                                               abs=2E-8)


def test_ddfel():
    assert ddefl(0.75, 0.5, 4., 0.055, 1) == 0.
    assert ddefl(0.75, 0.5, 4., 0.055, 2) == 0.

    assert ddefl(-0.82, 0.5, 4., 0.055, 1) == 0.
    assert ddefl(-0.82, 0.5, 4., 0.055, 2) == approx(1.01196454E-10, abs=2E-13)


def test_rdefl():
    assert rdefl(1.32, 1) == 0.
    assert rdefl(1.32, 2) == approx(1.22423962E-05, abs=1E-8)
