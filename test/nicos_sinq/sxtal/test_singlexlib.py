#  -*- coding: utf-8 -*-
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
#   Mark.Koennecke@psi.ch
#
# *****************************************************************************
"""
A test suite for the singlexlib for single crystal diffraction
"""

import numpy as np

from nicos_sinq.sxtal.cell import Cell
from nicos_sinq.sxtal.singlexlib import angleBetweenReflections, \
    biToNormalBeam, calcNBUBFromCellAndReflections, \
    calcUBFromCellAndReflections, calculateBMatrix, rotatePsi, z1FromAngles, \
    z1FromNormalBeam, z1ToBisecting, z1ToNormalBeam


def test_bisecting_angles():
    ub = np.array([[0.016169, 0.011969, 0.063195],
                   [-0.000545, 0.083377, -0.009117],
                   [-0.162051, 0.000945, 0.006321]],
                  dtype='float64')
    hkl = np.array([-2., -2., 4])
    z1 = ub.dot(hkl)
    theta, chi, phi = z1ToBisecting(1.179, z1)
    assert(abs(np.rad2deg(theta) - 15.29352) < .01)
    assert(abs(np.rad2deg(chi) - 129.053604) < .01)
    assert (abs(np.rad2deg(phi) - 134.191132) < .01)


def test_bisecting_z1():
    ub = np.array([[0.016169, 0.011969, 0.063195],
                   [-0.000545, 0.083377, -0.009117],
                   [-0.162051, 0.000945, 0.006321]],
                  dtype='float64')
    hkl = np.array([-2., -2., 4])
    z1 = ub.dot(hkl)

    z1test = z1FromAngles(1.179, np.deg2rad(30.58704),
                          np.deg2rad(15.293520),
                          np.deg2rad(129.053604),
                          np.deg2rad(134.191132))

    for isval, shouldval in zip(z1test, z1):
        assert(abs(isval - shouldval) < .0001)

    ubinv = np.linalg.inv(ub)
    hkl = ubinv.dot(z1)
    assert(abs(hkl[0] - -2.) < .0001)
    assert (abs(hkl[1] - -2.) < .0001)
    assert (abs(hkl[2] - 4.) < .0001)


def test_psi_rotation():
    psiom, psichi, psiphi = rotatePsi(np.deg2rad((15.2935)),
                                      np.deg2rad(129.0536),
                                      np.deg2rad(134.191132),
                                      np.deg2rad(30.))
    assert(abs(np.rad2deg(psiom) - 37.374298) < .001)
    assert (abs(np.rad2deg(psichi) - 123.068192) < .001)
    assert (abs(np.rad2deg(psiphi) - 170.8209099) < .001)


def test_z1_to_nb():
    ub = np.array([[0.016169, 0.011969, 0.063195],
                   [-0.000545, 0.083377, -0.009117],
                   [-0.162051, 0.000945, 0.006321]],
                  dtype='float64')
    hkl = np.array([-2., -2., 4])
    z1 = ub.dot(hkl)

    gamma, om, nu = z1ToNormalBeam(1.179, z1)
    assert(abs(np.rad2deg(gamma) - 19.3234) < .01)
    assert (abs(np.rad2deg(om) - -21.0583) < .01)
    assert (abs(np.rad2deg(nu) - 24.1858) < .01)


def test_bi_to_nb():
    gamma, om, nu = biToNormalBeam(np.deg2rad(30.56),
                                   np.deg2rad(15.28),
                                   np.deg2rad(129.047),
                                   np.deg2rad(134.188))
    assert (abs(np.rad2deg(gamma) - 19.3018) < .01)
    assert (abs(np.rad2deg(om) - 109.458) < .01)
    assert (abs(np.rad2deg(nu) - 24.1633) < .01)


def test_nb_to_z1():
    ub = np.array([[0.016169, 0.011969, 0.063195],
                   [-0.000545, 0.083377, -0.009117],
                   [-0.162051, 0.000945, 0.006321]],
                  dtype='float64')
    hkl = np.array([-2., -2., 4])
    z1 = ub.dot(hkl)

    z1test = z1FromNormalBeam(1.179,
                              np.deg2rad(19.3234),
                              np.deg2rad(-21.0583),
                              np.deg2rad(24.1858))
    for isval, shouldval in zip(z1test, z1):
        assert(abs(isval - shouldval) < .0001)


def test_ub_calc():
    cell = Cell(5.402, 5.402, 12.3228)
    r1 = {'h': 2., 'k': 2., 'l': 0, 'stt': 35.8,
          'om': 17.90, 'chi': 180.642, 'phi': 86.229}
    r2 = {'h': 0., 'k': 0., 'l': 3., 'stt': 16.498,
          'om': 8.249, 'chi': 268.331, 'phi': 333.714}
    ub_expected = np.array([[.1215666, -.138694, -0.0021278],
                            [-.1386887, -.121654, .0010515],
                            [-.0049867, .0020612, -.081156]],
                           dtype='float64')

    ub = calcUBFromCellAndReflections(cell, r1, r2)

    for calc, exp in zip(np.nditer(ub), np.nditer(ub_expected)):
        assert(abs(calc - exp) < .001)


def test_ub_nb_calc():
    cell = Cell(9.663, 9.663, 9.663, 81.496, 81.496, 81.496)
    r1 = {'h': 1., 'k': -2., 'l': 1, 'gamma': 13.60,
          'om': -102.52, 'nu': 12.40}
    r2 = {'h': 1., 'k': 1., 'l': 1., 'gamma': 10.62179,
          'om': -14.005692, 'nu': 0.84147}
    ub_expected = np.array([[0.0211, 0.0773564, 0.04842],
                            [-.1007840, 0.043792, 0.00344],
                            [-.0225, -.0568516, .09368]],
                           dtype='float64')

    ub = calcNBUBFromCellAndReflections(cell, r1, r2)

    for calc, exp in zip(np.nditer(ub), np.nditer(ub_expected)):
        assert(abs(calc - exp) < .001)


def test_angle_between_reflections():
    cell = Cell(9.663, 9.663, 9.663, 81.496, 81.496, 81.496)
    r1 = {'h': 1., 'k': 0., 'l': 0.}
    r2 = {'h': 0., 'k': 1., 'l': 0.}
    B = calculateBMatrix(cell)
    angle = angleBetweenReflections(B, r1, r2)
    assert(abs(np.rad2deg(angle) - 97.40) < .01)
