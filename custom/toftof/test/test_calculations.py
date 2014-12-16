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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF chopper calculation tests."""

from nicos.toftof.calculations import phi1, phi, alpha, t1, t2, Eres1,\
    speedRatio, calculateChopperDelay, calculateCounterDelay,\
    calculateTimeInterval


def test_basic_calculations():

    assert '%.4f' % alpha == '252.7784'

    r = [0, 1.0, 0.5, 0, 0.75, 0.8, 0, 0, 0.875, 0, 0.7]
    for i in [1, 2, 4, 5, 8, 10]:
        assert speedRatio(i) == r[i]

    res1 = ['0.00', '12.74', '432.78', '1013.21', '1022.77', '1264.45', '1274.00']
    for x in range(1, 8):
        assert '%.2f' % phi1(x, 14000, ilambda=6) == res1[x - 1]

    assert '%.2f' % phi1(5, 7000, ilambda=6) == '511.38'

    res2 = ['0.00', '-12.74', '-72.78', '66.79', '-57.23', '176.25', '166.70']
    for x in range(1, 8):
        assert '%.2f' % phi(x, 14000, ilambda=6) == res2[x - 1]

    res3 = ['0.00', '-12.74', '-162.78', '-23.21', '32.77', '176.25', '166.70']
    for x in range(1, 8):
        assert '%.2f' % phi(x, 14000, ilambda=6, slittype=1) == res3[x - 1]

    assert '%.2f' % phi(5, 14000, ratio=5, ilambda=6) == '98.22'
    assert '%.2f' % phi(5, 14000, ratio=5, slittype=1, ilambda=6) == '170.22'

    res4 = ['0.000152', '0.005152', '0.012062', '0.012176', '0.015053',
            '0.015167']
    for x in range(2, 8):
        assert '%.6f' % t1(1, x, ilambda=6) == res4[x - 2]

    res5 = ['0.017138', '0.012138', '0.005228', '0.005114', '0.002237',
            '0.002123']
    for x in range(2, 8):
        assert '%.6f' % t2(x, ilambda=6) == res5[x - 2]

    assert '%f, %f' % Eres1(6, 14000, crc=0) == '0.000096, 0.000128'
    assert '%f, %f' % Eres1(6, 14000, crc=1) == '0.000048, 0.000064'

def test_delay_calculations():

    assert calculateChopperDelay(6, 14000, 5, 0, False) == 1094
    assert calculateChopperDelay(6, 14000, 5, 1, False) == 22

    assert calculateCounterDelay(6,14000,5,0,False) == 129070

    assert '%.7f' % calculateTimeInterval(14000, 5) == '0.0107143'
