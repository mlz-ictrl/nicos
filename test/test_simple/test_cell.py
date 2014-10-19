#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Tests for the cell.py HKL transformation routines."""

from __future__ import print_function

from numpy import array

from nicos import session
from nicos.core.sessions.utils import MASTER

from test.utils import assertAlmostEqual


def setup_module():
    session.loadSetup('scanning')
    session.setMode(MASTER)


def teardown_module():
    session.unloadSetup()


def tscan(Qh, Qk, Ql, ny, dQh, dQk, dQl, dny, numsteps, SM, SC, sense, sample):
    Qhkl = array([Qh, Qk, Ql], float)
    dQhkl = array([dQh, dQk, dQl], float)
    print('  ' + ('%-9s' * 14) % (
        'h', 'k', 'l', 'ny', 'ki', 'kf', 'phi', 'psi', 'alpha',
        'hcalc', 'kcalc', 'lcalc', 'nycalc', 'dval'))
    for _ in range(numsteps):
        Qhkl += dQhkl
        ny += dny
        angles = sample.cal_angles(Qhkl, ny, SM, SC, sense, False)
        hklr = sample.angle2hkl(angles[:4], False)
        nyr = sample.cal_ny(angles[0], angles[1])
        dval = sample.cal_dvalue_real(Qhkl)
        print(('%7.3f  ' * 14) % (tuple(Qhkl) + (ny,) + tuple(angles) +
                                  tuple(hklr) + (nyr, dval)))
        for i in range(3):
            assertAlmostEqual(Qhkl[i], hklr[i])
        assertAlmostEqual(ny, nyr)


def test_cell():
    sample = session.getDevice('Sample')
    sample.lattice = [3.8184, 3.8184, 3.8184]
    sample.angles = [90, 90, 90]
    sample.orient1 = [1, 1, 0]
    sample.orient2 = [-1, 1, 0]
    sample.psi0 = -0.0
    sense = 1
    print('## CKI')
    tscan(1,   1, 0, 1,  0.005, 0.005, 0, 0,   21, 'CKI',  2.662, sense, sample)
    print('## CKF')
    tscan(1,   1, 0, 1,  0.005, 0.005, 0, 0,   21, 'CKF',  2.662, sense, sample)
    print('## CPHI')
    tscan(1.5, 1, 0, 5,  0,     0,     0, 0.1, 21, 'CPHI', 30,    sense, sample)
    print('## CPSI')
    tscan(1.5, 1, 0, 5,  0,     0,     0, 0.1, 21, 'CPSI', 300,   sense, sample)
