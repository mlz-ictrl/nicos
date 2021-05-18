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

    @pytest.mark.parametrize('wlmin,wlmax,D,ch2,gap,manner,expected', [
        (0.,   21., 21.455, 6, 0.1, 'normal',
            (537, (0, 301.39635305072477, 30.966976901943077, 0.0, 141.93298015396692, 0.0))),               # 01
        (0.,   21., 14.38,  6, 0.1, 'normal',
            (852, (0, 324.21765825991173, 49.12818462272917, 0.0, 225.17243692007648, 0.0))),                # 02
        (0.49, 21., 14.38,  6, 0.1, 'normal',
            (876, (0, 324.09436426218247, 50.53370212734737, 0.0, 231.61443765914476, 6.912510286683571))),  # 03
        (0.,   21., 21.455, 5, 0.1, 'normal',
            (510, (0, 0, 33.02790166353888, 0.0, 151.37895204242858, 0.0))),                                 # 04
        (1.17, 21., 14.38,  5, 0.1, 'normal',
            (836, (0, 0, 41.691491393370285, 1.7387822236806074, 248.38909868207003, 15.750422489312417))),  # 05
        (0.,   21., 14.38,  5, 0.1, 'normal',
            (785, (0, 0, 39.89014894527624, 0.0, 233.18822414266023, 0.0))),                                 # 06
        (0.,   21., 21.455, 4, 0.1, 'normal',
            (494, (0, 0, 34.22639694268385, 0.0, 156.87209421152525, 0.0))),                                 # 07
        (0.,   21., 14.38,  4, 0.1, 'normal',
            (748, (0, 0, 51.848199234228375, 0.0, 237.6392586280809, 0.0))),                                 # 08
        (1.6,  21., 14.38,  4, 0.1, 'normal',
            (813, (0, 0, 56.34020937402483, 3.520121851067104, 258.22778388329056, 20.933280789105496))),    # 09
        (3.,   10., 21.455, 6, 0.1, 'normal',
            (None, (None, None, None, None, None, None))),                                                   # 10
        (3.,   10., 21.455, 6, 0.1, 'parasitic',
            (1699, (0, 0, 46.658663919102054, 0.0, 213.8537204006178, 82.05998674531685))),                  # 11
        (3.,   10., 14.38,  6, 0.1, 'normal',
            (None, (None, None, None, None, None, None))),                                                   # 12
        (3.,   10., 14.38,  6, 0.1, 'parasitic',
            (2784, (0, 0, 76.47620950917043, 0.0, 350.5184364907967, 134.50099534644744))),                  # 13
        (3.,   10., 14.38,  5, 0.1, 'normal',
            (None, (None, None, None, None, None, None))),                                                   # 14
        (3.,   10., 14.38,  5, 0.1, 'parasitic',
            (2458, (0, 0, 75.88233311281765, 13.084645315521074, 347.7964837782554, 118.7516221744647))),    # 15
        (3.,   10., 21.455, 5, 0.1, 'normal',
            (1572, (0, 0, 48.215035935436745, 8.368932202148624, 222.3440376084222, 75.91714228961133))),    # 16
        (3.,   10., 14.38,  4, 0.1, 'normal',
            (None, (None, None, None, None, None, None))),                                                   # 17
        (3.,   10., 14.38,  4, 0.1, 'parasitic',
            (2289, (0, 0, 75.57355155045532, 18.592151066782893, 346.38122495265355, 110.56285413428273))),  # 18
        (3.,   10., 21.455, 4, 0.1, 'normal',
            (None, (None, None, None, None, None, None))),                                                   # 19
        (3.,   10., 21.455, 4, 0.1, 'parasitic',
            (1501, (0, 0, 49.54605424142201, 12.189022565712504, 227.08768620271326, 72.48505668502749))),   # 20
        (9.,   21., 21.455, 6, 0.1, 'normal',
            (1033, (0, 296.7649521666166, 59.602329196699216, 0.0, 273.1792720287948, 149.7491396040226))),  # 21
        (9.,   21., 14.38,  6, 0.1, 'normal',
            (None, (None, None, None, None, None, None))),                                                   # 22
        (9.,   21., 14.38,  6, 0.1, 'parasitic',
            (1741, (0, 0, 100.43780103647481, 0.0, 460.34317351538357, 252.34708931081596))),                # 23
        (3.,    7., 21.455, 6, 0.1, 'normal',
            (None, (None, None, None, None, None, None))),                                                   # 24
        (3.,    7., 21.455, 6, 0.1, 'parasitic',
            (3100, (0, 0, 59.602329196699216, 0.0, 273.1792720287948, 149.74913960402256))),                 # 25
        (3.,    6., 21.455, 6, 0.1, 'normal',
            (None, (None, None, None, None, None, None))),                                                   # 26
        (3.,    6., 21.455, 6, 0.1, 'parasitic',
            (4276, (0, 0, 70.46172731990892, 0.0, 322.9518650457398, 206.5385762706002))),                   # 27
        (5.,   10., 21.455, 6, 0.1, 'normal',
            (None, (None, None, None, None, None, None))),                                                   # 28
        (5.,   10., 21.455, 6, 0.1, 'parasitic',
            (2565, (0, 0, 70.46172731990893, 0.0, 322.95186504573985, 206.5385762706002))),                  # 29
        ])
    def test_chopper_config(self, wlmin, wlmax, D, ch2, gap, manner, expected):

        def check_results(res, expected):
            assert res[0] == expected[0]
            for v, e in zip(res[1], expected[1]):
                assert v == approx(e, abs=0.01)

        check_results(
            chopper_config(wlmin, wlmax, D=D, disk2_pos=ch2,
                           gap=gap, suppress_parasitic=(manner=='normal')),
                      expected)

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
