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

from nicos.toftof.calculations import phi1, phi


def test_calculations():

    res1 = ['0.00', '12.74', '432.78', '1013.22', '1022.77', '1264.45', '1274.00']

    for x in range(1, 8):
        assert '%.2f' % phi1(x, 14000, ilambda=6) == res1[x - 1]

    assert '%.2f' % phi1(5, 7000, ilambda=6) == '511.39'

    res2 = ['0.00', '-12.74', '-72.78', '66.78', '-57.23', '176.25', '166.70']

    for x in range(1, 8):
        assert '%.2f' % phi(x, 14000, ilambda=6) == res2[x - 1]

    res3 = ['0.00', '-12.74', '-162.78', '-23.22', '32.77', '176.25', '166.70']

    for x in range(1, 8):
        assert '%.2f' % phi(x, 14000, ilambda=6, slittype=1) == res3[x - 1]

    assert '%.2f' % phi(5, 14000, ratio=5, ilambda=6) == '98.22'
    assert '%.2f' % phi(5, 14000, ratio=5, slittype=1, ilambda=6) == '170.22'
