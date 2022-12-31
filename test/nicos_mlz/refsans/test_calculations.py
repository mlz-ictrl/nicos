#  -*- coding: utf-8 -*-
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF chopper calculation tests."""

import pytest

from nicos_mlz.refsans.lib.calculations import chopper_config, \
    chopper_resolution

from test.utils import approx


class TestBasicCalculations:

    @pytest.mark.parametrize('wlmin,wlmax,D,ch2,gap,expected', [
            (0., 21., 21.46, 6, 0.1, (537, (0, 301.04, 30.96, 0, 141.90, 0))),
            (0., 21., 14.38, 6, 0.1, (852, (0, 324.22, 49.13, 0, 225.17, 0))),
            (0.49, 21., 14.38, 6, 0.1, (876, (0, 324.09, 50.53, 0, 231.61,
                                              6.92))),
            (0., 21., 21.46, 5, 0.1, (509, (0, 0, 33.02, 0, 151.34, 0))),
            (1.17, 21., 14.38, 5, 0.1, (836, (0, 0, 54.19, 1.74, 248.39,
                                              15.75))),
            (0, 21., 14.38, 5, 0.1, (785, (0, 0, 50.88, 0, 233.19, 0))),
            (0., 21., 21.46, 4, 0.1, (493, (0, 0, 34.22, 0, 156.83, 0))),
            (0, 21., 14.38, 4, 0.1, (748, (0, 0, 51.84, 0, 237.64, 0))),
            (1.6, 21., 14.38, 4, 0.1, (813, (0, 0, 56.34, 3.53, 258.23,
                                             20.94))),
            (3., 10., 21.46, 6, 0.1, (1571, (0, 0, 48.50, 8.36, 222.29,
                                             75.90))),
            (3., 10., 14.38, 6, 0.1, (2458, (0, 0, 75.88, 13.08, 347.80,
                                             118.75))),
            (3., 10., 14.38, 5, 0.1, (2458, (0, 0, 75.88, 13.08, 347.80,
                                             118.75))),
            (3., 10., 21.46, 5, 0.1, (1571, (0, 0, 48.50, 8.36, 222.29,
                                             75.90))),
            (3., 10., 14.38, 4, 0.1, (2289, (0, 0, 75.57, 18.59, 346.38,
                                             110.56))),
            (3., 10., 21.46, 4, 0.1, (1500, (0, 0, 49.54, 12.19, 227.03,
                                             72.47))),
            (9., 21., 21.46, 6, 0.1, (1033, (0, 296.78, 59.59, 0, 273.10,
                                             149.71))),
            (9., 21., 14.38, 6, 0.1, (1483, (0, 0, 96.13, 23.68, 440.60,
                                             214.91))),
            (3., 7., 21.46, 6, 0.1, (2809, (0, 0, 60.69, 14.95, 278.17,
                                            135.69))),
            (3., 6., 21.46, 6, 0.1, (3809, (0, 0, 70.55, 20.27, 323.34,
                                            184.00))),
            (5., 10., 21.46, 6, 0.1, (2285, (0, 0, 70.55, 20.27, 323.34,
                                             184.00))),
        ])
    def test_chopper_config(self, wlmin, wlmax, D, ch2, gap, expected):

        def check_results(res, expected):
            assert res[0] == expected[0]
            for v, e in zip(res[1], expected[1]):
                assert v == approx(e, abs=0.01)

        check_results(chopper_config(wlmin, wlmax, D=D, disk2_pos=ch2,
                                     gap=gap), expected)

    @pytest.mark.parametrize('chopper2_pos,D,expected', [
            (6, 21.455, 5.706),
            (5, 21.455, 3.096),
            (4, 21.455, 1.51),
            (6, 14.38, 8.759),
            (5, 14.38, 4.69),
            (4, 14.38, 2.27),
        ])
    def test_chopper_resolution(self, chopper2_pos, D, expected):
        assert chopper_resolution(chopper2_pos, D) == expected
