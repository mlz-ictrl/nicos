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

from nicos_mlz.toftof.lib.calculations import Eres1, ResolutionAnalysis, \
    alpha, calculateChopperDelay, calculateCounterDelay, calculateFrameTime, \
    phi, phi1, speedRatio, t1, t2


class TestBasicCalculations:

    @pytest.fixture(autouse=True)
    def prepare(self):
        assert alpha == pytest.approx(252.7784, abs=1e-4)

    def test_speedRatio(self):
        for x, expected in [
            (1., 1.),
            (2., 0.5),
            (4., 0.75),
            (5., 0.8),
            (8., 0.875),
            (10., 0.7),
        ]:
            assert speedRatio(x) == expected

    def test_phi1_calculations(self):
        for x, speed, wl, expected in [
            (1, 14000, 6, 0.),
            (2, 14000, 6, 12.74),
            (3, 14000, 6, 432.78),
            (4, 14000, 6, 1013.21),
            (5, 14000, 6, 1022.77),
            (6, 14000, 6, 1264.45),
            (7, 14000, 6, 1274.00),
            (5, 7000, 6, 511.38)
        ]:
            assert phi1(x, speed, wl) == pytest.approx(expected, abs=1e-2)

    def test_phi_calculations(self):
        res2 = ['0.00', '-12.74', '-72.78', '66.79', '-57.23', '176.25',
                '166.70']
        for x in range(1, 8):
            assert '%.2f' % phi(x, 14000, 6) == res2[x - 1]

        assert '%.2f' % phi(5, 14000, 6, ch5_90deg_offset=1) == '32.77'

        res3 = ['0.00', '-12.74', '-162.78', '-23.21', '32.77', '176.25',
                '166.70']
        for x in range(1, 8):
            assert '%.2f' % phi(x, 14000, 6, slittype=1) == res3[x - 1]

        res3_1 = ['0.00', '12.74', '-162.78', '-23.21', '32.77', '176.25',
                  '-165.30']
        for x in range(1, 8):
            assert '%.2f' % phi(x, 14000, 6, 0, slittype=1) == res3_1[x - 1]

        res3_2 = ['0.00', '12.74', '-72.78', '66.79', '-57.23', '-93.75',
                  '104.70']
        for x in range(1, 8):
            assert '%.2f' % phi(x, 14000, 6, 0, slittype=2) == res3_2[x - 1]

        assert '%.2f' % phi(5, 14000, ratio=5, ilambda=6) == '98.22'
        assert '%.2f' % phi(5, 14000, ratio=5, slittype=1, ilambda=6) == \
            '170.22'

    def test_t1(self):
        for x, expected in [
            (2, 0.000152),
            (3, 0.005152),
            (4, 0.012062),
            (5, 0.012176),
            (6, 0.015053),
            (7, 0.015167)
        ]:
            assert t1(1, x, ilambda=6) == pytest.approx(expected, abs=1e-6)

    def test_t2(self):
        for x, expected in [
            (2, 0.017138),
            (3, 0.012138),
            (4, 0.005228),
            (5, 0.005114),
            (6, 0.002237),
            (7, 0.002123),
        ]:
            assert t2(x, ilambda=6) == pytest.approx(expected, abs=1e-6)

    def test_eres1(self):
        def check_results(res, expected, precision):
            for v, e in zip(res, expected):
                assert v == pytest.approx(e, abs=precision)

        for wl, speed, st, crc, expected in [
            (6, 0, 0, 1, (0, 0)),
            (6, 14000, 0, 0, (0.000096, 0.000128)),
            (6, 14000, 0, 1, (0.000048, 0.000064)),
            (6, 14000, 1, 1, (0.000024, 0.000032)),
            (6, 14000, 2, 1, (0.000037, 0.000050)),
        ]:
            check_results(Eres1(wl, speed, st, crc), expected, 1e-6)

    def test_delay_calculations(self):
        for wl, speed, ratio, st, ch5_90deg, expected in [
            (6, 14000, 5, 0, False, 1094),
            (6, 14000, 5, 1, False, 22),
            (6, 14000, 5, 0, True, 1897),
            (6, 14000, 6, 0, False, 1147),
            (6, 14000, 6, 0, True, 2004),
        ]:
            assert calculateChopperDelay(wl, speed, ratio, st, ch5_90deg) == \
                expected

    def test_frametime_calculations(self):
        for speed, ratio, expected in [
            (14000, 5, 0.0107143),
            (0, 1, 0.052),
        ]:
            assert calculateFrameTime(speed, ratio) == pytest.approx(expected,
                                                                     abs=1e-7)

    def test_counterdelay_calculations(self):
        for wl, speed, ratio, delay, ch5_90deg_offset, expected in [
            (6, 14000, 5, 0, False, 129070*5e-8),
            (6, 14000, 5, 1, False, 200499*5e-8),
            (6, 14000, 5, 0, True, 155856*5e-8),
            (6, 14000, 6, 0, False, 127999*5e-8),
            (6, 14000, 6, 0, True, 153713*5e-8),
        ]:
            assert calculateCounterDelay(wl, speed, ratio, delay,
                                         ch5_90deg_offset) == pytest.approx(
                                             expected, abs=5e-8)

    def test_resolution_analysis(self):
        chSpeed = 14000
        chWL = 6.
        chRatio = 4
        chST = 1
        ra = ResolutionAnalysis(chSpeed, chWL, chRatio, chST)

        assert pytest.approx(ra.E0, abs=5e-5) == 2.2723
        assert pytest.approx(ra.q_low_0, abs=5e-5) == 0.1386
        assert pytest.approx(ra.q_high_0, abs=5e-5) == 1.9629
        assert pytest.approx(ra.dE_min, abs=5e-5) == -1.0723
        assert pytest.approx(ra.dE_el, abs=5e-5) == 32.9835
