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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
import time
from os.path import basename

from nicos.utils import findResource

from nicos_sinq.devices.illasciisink import ILLAsciiScanfileReader


def test_tasp_scan_data():
    filename = findResource('test/nicos_sinq/devices/ill_scan.scn')
    reader = ILLAsciiScanfileReader(filename)
    sd = reader.scandata

    assert sd.scaninfo == 'sc qh 0 0 -1.15 3.1 dqh 0 0 0.025 0 np 15 mn 10000'
    assert sd.started == time.struct_time((2021, 12, 3, 15, 49, 35, 4, 337, 0))
    assert sd.filepaths == [basename(filename)]
    assert sd.counter == 6748

    assert sd.xnames == ['PNT', 'QH', 'QK', 'QL', 'EN', 'A3', 'A4']
    assert sd.ynames == ['M1', 'M2', 'TIME', 'CNTS', 'M3', 'M4']

    assert sd.xresults == [
        [1, 0.0001, 0.0000, -1.3251, 3.0990, 51.9993, 90.3597],
        [2, -0.0005, 0.0000, -1.3000, 3.0990, 51.1723, 88.1367],
        [3, -0.0002, 0.0000, -1.2751, 3.0990, 50.3473, 85.9597],
        [4, -0.0000, 0.0000, -1.2500, 3.0990, 49.5493, 83.8167]
    ]
    assert sd.yresults == [
        [10000, 12740, 21.12, 1, 51, 2869834],
        [10000, 12796, 21.03, 1, 43, 2857825],
        [10000, 12770, 30.13, 1, 58, 2831073],
        [10000, 12685, 21.31, 1, 44, 2845426],
    ]
