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

"""TOFTOF chopper calculation tests."""

import pytest

from nicos_mlz.refsans.lib.calculations import angles_SC2, chopper_config, \
    chopper_resolution, period

from test.utils import approx


class TestBasicCalculations:

    @pytest.mark.parametrize('wlmin,wlmax,D,ch2,gap,suppress_parasitic,expected', [
        (0.00, 21.00, 21.45, 6, 0.1, True,
            (537, (0.00, 301.38, 30.97, 0.00, 141.97, 0.00), 1, 0.00, 21.00)),
        (0.00, 21.00, 14.38, 6, 0.1, True,
            (852, (0.00, 324.22, 49.13, 0.00, 225.17, 0.00), 1, 0.00, 19.13)),
        (0.49, 21.00, 14.38, 6, 0.1, True,
            (876, (0.00, 324.09, 50.53, 0.00, 231.61, 6.91), 1, 0.49, 19.07)),
        (0.00, 21.00, 21.45, 5, 0.1, True,
            (510, (0.00, 0.00, 33.03, 0.00, 151.42, 0.00), 5, 0.00, 21.00)),
        (1.17, 21.00, 14.38, 5, 0.1, True,
            (836, (0.00, 0.00, 41.69, 1.74, 248.39, 15.75), 5, 1.17, 21.00)),
        (0.00, 21.00, 14.38, 5, 0.1, True,
            (785, (0.00, 0.00, 39.89, 0.00, 233.19, 0.00), 5, 0.00, 21.00)),
        (0.00, 21.00, 21.45, 4, 0.1, True,
            (494, (0.00, 0.00, 34.23, 0.00, 156.91, 0.00), 4, 0.00, 21.00)),
        (0.00, 21.00, 14.38, 4, 0.1, True,
            (748, (0.00, 0.00, 51.85, 0.00, 237.64, 0.00), 4, 0.00, 21.00)),
        (1.60, 21.00, 14.38, 4, 0.1, True,
            (813, (0.00, 0.00, 56.34, 3.52, 258.23, 20.93), 4, 1.60, 21.00)),
        (3.00, 10.00, 21.45, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3.00, 10.00, 21.45, 6, 0.1, False,
            (1699, (0.00, 0.00, 46.67, 0.00, 213.91, 82.08), 6, 3.00, 10.00)),
        (3.00, 10.00, 14.38, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3.00, 10.00, 14.38, 6, 0.1, False,
            (2784, (0.00, 0.00, 76.48, 0.00, 350.52, 134.50), 6, 3.00, 10.00)),
        (3.00, 10.00, 14.38, 5, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3.00, 10.00, 14.38, 5, 0.1, False,
            (2458, (0.00, 0.00, 75.88, 13.08, 347.80, 118.75), 5, 3.00, 10.00)),
        (3.00, 10.00, 21.45, 5, 0.1, True,
            (1572, (0.00, 0.00, 48.24, 8.37, 222.4, 75.94), 5, 3.00, 10.00)),
        (3.00, 10.00, 14.38, 4, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3.00, 10.00, 14.38, 4, 0.1, False,
            (2289, (0.00, 0.00, 75.57, 18.59, 346.38, 110.56), 4, 3.00, 10.00)),
        (3.00, 10.00, 21.45, 4, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3.00, 10.00, 21.45, 4, 0.1, False,
            (1501, (0.00, 0.00, 49.55, 12.19, 227.14, 72.5), 4, 3.00, 10.00)),
        (9.00, 21.00, 21.45, 6, 0.1, True,
            (1034, (0.00, 296.75, 59.62, 0.00, 273.26, 149.79), 1, 9.00, 20.33)),
        (9.00, 21.00, 14.38, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (9.00, 21.00, 14.38, 6, 0.1, False,
            (1741, (0.00, 0.00, 100.44, 0.00, 460.34, 252.35), 6, 9.00, 21.00)),
        (3.00, 7.00, 21.45, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3.00, 7.00, 21.45, 6, 0.1, False,
            (3101, (0.00, 0.00, 59.62, 0.00, 273.26, 149.79), 6, 3.00, 7.00)),
        (3.00, 6.00, 21.45, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3.00, 6.00, 21.45, 6, 0.1, False,
            (4277, (0.00, 0.00, 70.48, 0.00, 323.04, 206.6), 6, 3.00, 6.00)),
        (5.00, 10.00, 21.45, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (5.00, 10.00, 21.45, 6, 0.1, False,
            (2566, (0.00, 0.00, 70.48, 0.00, 323.04, 206.6), 6, 5.00, 10.00)),

        (0., 21., 21.46, 6, 0.1, True,
            (537, (0, 301.04, 30.96, 0, 141.90, 0))),
        (0., 21., 14.38, 6, 0.1, True,
            (852, (0, 324.22, 49.13, 0, 225.17, 0))),
        (0.49, 21., 14.38, 6, 0.1, True,
            (876, (0, 324.09, 50.53, 0, 231.61, 6.92))),
        (0., 21., 21.46, 5, 0.1, True,
            (509, (0, 0, 33.02, 0, 151.34, 0))),
        (0., 21., 21.46, 4, 0.1, True,
            (493, (0, 0, 34.22, 0, 156.83, 0))),
        (0, 21., 14.38, 4, 0.1, True,
            (748, (0, 0, 51.84, 0, 237.64, 0))),
        (1.6, 21., 14.38, 4, 0.1, True,
            (813, (0, 0, 56.34, 3.53, 258.23, 20.94))),
        (3., 10., 21.46, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3., 10., 14.38, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3., 10., 14.38, 5, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3., 10., 21.46, 5, 0.1, True,
            (1571, (0, 0, 48.50, 8.36, 222.29, 75.90))),
        (3., 10., 14.38, 4, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3., 10., 21.46, 4, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (9., 21., 21.46, 6, 0.1, True,
            (1033, (0, 296.78, 59.59, 0, 273.10, 149.71))),
        (9., 21., 14.38, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3., 7., 21.46, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (3., 6., 21.46, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
        (5., 10., 21.46, 6, 0.1, True,
            (None, (None, None, None, None, None, None))),
    ])
    def test_chopper_config(self, wlmin, wlmax, D, ch2, gap,
                            suppress_parasitic, expected):

        def check_results(res, expected):
            assert res[0] == expected[0]
            for v, e in zip(res[1], expected[1]):
                assert v == approx(e, abs=0.01)

        check_results(
            chopper_config(
                wlmin, wlmax, D=D, disk2_pos=ch2,
                gap=gap, suppress_parasitic=suppress_parasitic), expected)

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

    def test_angles_SC2(self):
        assert angles_SC2() == (approx(152.7922), 0.0)

    def test_period(self):
        assert period() == approx(0.094237562)
