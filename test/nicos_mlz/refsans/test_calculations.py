#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

from test.utils import approx

from nicos_mlz.refsans.lib.calculations import chopper_config, \
    chopper_resolution


def test_chopper_config():

    def check_results(res, expected):
        assert res[0] == expected[0]
        for v, e in zip(res[1], expected[1]):
            assert v == approx(e, abs=0.01)

    check_results(chopper_config(0., 21., D=21.455, disk2_pos=6, gap=0.1),  # 2
                  (537, (0, 300, 31.12, 0, 141.69, 0)))
    check_results(chopper_config(0., 21., D=14.38, disk2_pos=6, gap=0.1),  # 3
                  (852, (0, 300, 49.38, 0, 224.88, 0)))
    check_results(chopper_config(0.49, 21., D=14.38, disk2_pos=6, gap=0.1),  # 3a
                  (877, (0, 300, 50.80, 0, 231.32, 6.92)))
    check_results(chopper_config(0., 21., D=21.455, disk2_pos=5, gap=0.1),  # 4
                  (509, (0, 0, 33.21, 0, 151.21, 0)))
    check_results(chopper_config(1.17, 21., D=14.38, disk2_pos=5, gap=0.1),  # 5a
                  (836, (0, 0, 54.50, 1.75, 248.17, 15.75)))
    check_results(chopper_config(0, 21., D=14.38, disk2_pos=5, gap=0.1),  # 5
                  (785, (0, 0, 51.16, 0, 232.97, 0)))
    check_results(chopper_config(0., 21., D=21.455, disk2_pos=4, gap=0.1),  # 6
                  (493, (0, 0, 34.40, 0, 156.67, 0)))
    check_results(chopper_config(0, 21., D=14.38, disk2_pos=4, gap=0.1),  # 7
                  (748, (0, 0, 52.13, 0, 237.40, 0)))
    check_results(chopper_config(1.6, 21., D=14.38, disk2_pos=4, gap=0.1),  # 7a
                  (813, (0, 0, 56.65, 3.53, 257.99, 20.94)))

    check_results(chopper_config(3., 10., D=21.455, disk2_pos=6, gap=0.1),  # 9
                  (1700, (0, 300, 46.90, 0, 213.56, 82.10)))
    check_results(chopper_config(3., 10., D=14.38, disk2_pos=6, gap=0.1),  # 10
                  (2789, (0, 300, 76.92, 0, 350.29, 134.66)))
    check_results(chopper_config(3., 10., D=14.38, disk2_pos=5, gap=0.1),  # 11
                  (2460, (0, 0, 76.33, 13.19, 347.57, 118.78)))
    check_results(chopper_config(3., 10., D=21.455, disk2_pos=5, gap=0.1),  # 12
                  (1572, (0, 0, 48.78, 8.43, 222.13, 75.91)))
    check_results(chopper_config(3., 10., D=14.38, disk2_pos=4, gap=0.1),  # 13
                  (2291, (0, 0, 76.02, 18.65, 346.18, 110.64)))
    check_results(chopper_config(3., 10., D=21.455, disk2_pos=4, gap=0.1),  # 14
                  (1501, (0, 0, 49.82, 12.22, 226.85, 72.50)))

    check_results(chopper_config(9., 21., D=21.455, disk2_pos=6, gap=0.1),  # 16
                  (1034, (0, 300, 59.93, 0, 272.89, 149.86)))
    check_results(chopper_config(9., 21., D=14.38, disk2_pos=6, gap=0.1),  # 17
                  (1745, (0, 300, 101.08, 0, 460.29, 252.78)))

    check_results(chopper_config(3., 7., D=21.455, disk2_pos=6, gap=0.1),  # 19
                  (3104, (0, 300, 59.93, 0, 272.89, 149.86)))

    check_results(chopper_config(3., 6., D=21.455, disk2_pos=6, gap=0.1),  # 20
                  (4282, (0, 300, 70.86, 0, 322.69, 206.75)))

    check_results(chopper_config(5., 10., D=21.455, disk2_pos=6, gap=0.1),  # 22
                  (2569, (0, 300, 70.86, 0, 322.69, 206.75)))


def test_chopper_resolution():
    assert chopper_resolution(6, 21.455) == 11.48
    assert chopper_resolution(5, 21.455) == 6.23
    assert chopper_resolution(4, 21.455) == 3.08

    assert chopper_resolution(6, 14.38) == 17.63
    assert chopper_resolution(5, 14.38) == 9.44
    assert chopper_resolution(4, 14.38) == 4.63
