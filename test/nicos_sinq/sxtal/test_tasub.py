#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#   Jakob Lass <jakob.lass@psi.ch>
#
# *****************************************************************************
"""
This is part of the TAS library which implemnts Mark Lumsden's UB matrix
algorithm for triple axis. See J. Appl. Cryst. (2005). 38, 405-411
https://doi.org/10.1107/S0021889805004875 for reference.

The original implementation was in ANSII-C by Mark Koennecke at PSI.
This implementation has been ported from C to python by Jakob Lass, then
also at PSI
"""
import numpy as np

from nicos_sinq.sxtal.cell import Cell, directToReciprocalLattice
from nicos_sinq.sxtal.tasublib import KToEnergy, calcPlaneNormal, \
    calcScatteringPlaneNormal, calcTasQAngles, calcTasUBFromTwoReflections, \
    calcTasUVectorFromAngles, calcTheta, calcTwoTheta, energyToK, \
    makeAuxReflection, matFromTwoVectors, tasAngleBetween, \
    tasAngleBetweenReflections, tasQEPosition, tasReflection, \
    tasReflectionToHC, tasReflectionToQC, uFromAngles
from nicos_sinq.sxtal.trigd import Acosd, Asind, Atand, Atand2, Cosd, Cotd, \
    Rtand, Sign, Sind, Tand, rtan


def test_Cell_error():
    cell = Cell(-10, -0.1, -0.2, -0., -0., -90)
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Ignore the warnings temporary
            reciprocal = directToReciprocalLattice(cell)
            reciprocal.a = 26.  # Only to satisfy pylint, flake8
        assert False  # pragma: no cover
    except AttributeError as e:
        str(e)
        assert True


def test_Cell_init():
    cell = Cell()  # Default cell object

    for length in ['a', 'b', 'c']:
        assert(getattr(cell, length) == 1.0)
    for length in ['alpha', 'beta', 'gamma']:
        assert(getattr(cell, length) == 90.0)

    nonStandard = {'a': 10, 'b': 11, 'c': 0.2,
                   'alpha': 60, 'beta': 90.1,
                   'gamma': 120}

    nonStandardCell = Cell(**nonStandard)

    for key, value in nonStandard.items():
        assert(getattr(nonStandardCell, key) == value)

    cellString = str(cell)
    wantedString = "cell.Cell(a=1.0, b=1.0, c=1.0, " \
                   "alpha=90.0, beta=90.0, gamma=90.0)"
    assert(cellString == wantedString)


def test_Cell_reciprocal():
    # The default cell is equal to its reciprocal with
    # lattice vectors multiplied with 1/(2*pi)

    defaultCell = Cell()
    reciprocal = directToReciprocalLattice(defaultCell)
    for length in ['a', 'b', 'c']:
        assert(np.all(np.isclose(getattr(reciprocal, length), 2*np.pi)))
    for length in ['alpha', 'beta', 'gamma']:
        assert(np.all(np.isclose(getattr(reciprocal, length), 90.0)))

    # Back and forth is the same
    defaultCell2 = reciprocal.reciprocalToDirectLattice()

    assert defaultCell == defaultCell2


def test_Cell_BMatrix():

    # B matrix for 6.11, 6.11, 11.35, 90.0, 90.0, 120.0 as calculated by six
    BFromSix = np.array([[+0.188985358, +0.094492679, +0.000000000],
                         [+0.000000000, +0.163666121, +0.000000000],
                         [+0.000000000, +0.000000000, +0.088105727]])*2*np.pi

    lattice = Cell(6.11, 6.11, 11.35, 90.0, 90.0, 120.0)
    B = lattice.calculateBMatrix()
    print(B)
    print(BFromSix)
    assert(np.all(np.isclose(B, BFromSix, atol=1e-9)))


def test_Cell_CellFromUBMatrix():

    latticeCostants = 20*np.random.rand(3)+1.0
    angles = 90*np.random.rand(3)

    # To ensure possitive volumen
    a = Cosd(angles[0])
    b = Cosd(angles[1])

    lowerLimit = a*b - np.sqrt((a**2 - 1)*(b**2 - 1))
    upperLimit = np.sqrt((a**2 - 1)*(b**2 - 1)) + a*b
    angles[2] = Acosd(0.5*(lowerLimit+upperLimit))

    arguments = list(latticeCostants)+list(angles)

    lattice = Cell(*arguments)
    B = lattice.calculateBMatrix()

    lattice2 = Cell(UB=B)
    print(lattice)
    print(lattice2)
    assert(lattice == lattice2)


def test_Sign():
    values = 1-2*np.random.rand(20)
    assert(np.all(np.sign(values) == Sign(values)))


def test_Sind():
    # values between -2 pi and 2 pi
    values = 2*np.pi*(1-2*np.random.rand(200))
    radian = np.sin(values)
    degree = Sind(values*180.0/np.pi)

    assert(np.all(np.isclose(radian, degree)))


def test_Cosd():
    # values between -2 pi and 2 pi
    values = 2*np.pi*(1-2*np.random.rand(200))
    radian = np.cos(values)
    degree = Cosd(values*180.0/np.pi)

    assert(np.all(np.isclose(radian, degree)))


def test_Tand():
    values = 2*np.pi*(1-2*np.random.rand(200))
    radian = np.tan(values)
    degree = Tand(values*180.0/np.pi)

    assert(np.all(np.isclose(radian, degree)))


def test_Cotd():
    # values between -2 pi and 2 pi
    values = 2*np.pi*(1-2*np.random.rand(200))
    radian = np.reciprocal(np.tan(values))
    degree = Cotd(values*180.0/np.pi)

    assert(np.all(np.isclose(radian, degree)))


def test_Atand():
    # values between -20000 and 20000
    values = 20000*(1-2*np.random.rand(200))

    radian = np.arctan(values)*180.0/np.pi
    degree = Atand(values)

    assert(np.all(np.isclose(radian, degree)))


def test_Atand2():
    # values between -20000 and 20000
    x = 20000*(1-2*np.random.rand(200))
    y = 20000*(1-2*np.random.rand(200))

    radian = np.arctan2(x, y)*180.0/np.pi
    degree = Atand2(x, y)

    assert(np.all(np.isclose(radian, degree)))


def test_Asind():
    # values between -1 and 1
    values = 1-2*np.random.rand(200)

    radian = np.arcsin(values)*180.0/np.pi
    degree = Asind(values)

    assert(np.all(np.isclose(radian, degree)))


def test_Acosd():
    # values between -1 and 1
    values = 1-2*np.random.rand(200)

    radian = np.arccos(values)*180.0/np.pi
    degree = Acosd(values)

    assert(np.all(np.isclose(radian, degree)))


def test_rtan():
    assert(np.isclose(rtan(1.0, 2.0), 0.463647609))
    assert(np.isclose(rtan(1.0, -2.0), 2.677945045))
    assert(np.isclose(rtan(-1.0, 2.0), -0.463647609))
    assert(np.isclose(rtan(-1.0, -2.0), -2.677945045))
    assert(np.isclose(rtan(2.0, 1.0), 1.107148718))
    assert(np.isclose(rtan(2.0, -1.0), 2.034443936))
    assert(np.isclose(rtan(-2.0, 1.0), -1.107148718))
    assert(np.isclose(rtan(-2.0, -1.0), -2.034443936))
    assert(np.isclose(rtan(0.0, 0.0), 0.0))
    assert(np.isclose(rtan(1.0, 0.0), np.pi/2.0))
    assert(np.isclose(rtan(-1.0, 0.0), -np.pi/2.0))

    x, y = 10*(1-2*np.random.rand(2))
    radians = rtan(y, x)
    degrees = Rtand(y, x)
    assert(np.isclose(np.deg2rad(degrees), radians))


def test_energyToK():
    energy = 5.00
    K = energyToK(energy)
    print(K)
    assert (np.isclose(K, 1.553424415003))  # 1.5533785355359282))

    energy2 = KToEnergy(K)
    assert (np.isclose(energy2, energy))


def test_tasReflectionToHC():
    lattice = Cell(12.32, 3.32, 9.8, 93, 45, 120)
    B = lattice.calculateBMatrix()
    energy = 5.00
    K = energyToK(energy)

    reflection = tasReflection(
        ki=K, kf=K, qh=2, qk=0, ql=-1)
    hc = tasReflectionToHC(reflection, B)

    result = np.array([+0.434561180, -0.005347733, -0.102040816]) * 2 * np.pi

    assert (np.all(np.isclose(hc, result)))


def test_tasReflection_initialization():
    tR = tasReflection(ki=1.5, kf=2.5, qh=1, qk=2, ql=3, qm=2.0,
                       monochromator_two_theta=72,
                       a3=0.0, sample_two_theta=60.6,
                       sgl=0.1, sgu=-0.1, analyzer_two_theta=50.0)

    for key, val in {'ki': 1.5, 'kf': 2.5, 'qh': 1,
                     'qk': 2, 'ql': 3, 'qm': 2.0,
                     'monochromator_two_theta': 72, 'a3': 0.0,
                     'sample_two_theta': 60.6,
                     'sgl': 0.1, 'sgu': -0.1,
                     'analyzer_two_theta': 50.0}.items():
        assert (np.isclose(getattr(tR, key), val))

    qe = tasQEPosition(1.25, 2.0, -3, 2, -0, 1.2)
    angles = tR.angles

    tR2 = tasReflection(qe, angles)

    angles2 = tR2.angles
    qe2 = tR2.qe
    for key in ['monochromator_two_theta', 'a3', 'sample_two_theta',
                'sgl', 'sgu', 'analyzer_two_theta']:
        assert (np.isclose(getattr(angles2, key), getattr(angles, key)))

    for key, val in {'ki': 1.25, 'kf': 2.0,
                     'qh': -3, 'qk': 2, 'ql': -0, 'qm': 1.2}.items():
        assert (np.isclose(getattr(qe, key), val))
        assert (np.isclose(getattr(qe, key), getattr(qe2, key)))

    # pylint: disable=pointless-statement
    try:
        tR2.notExisting
        assert (False)
    except AttributeError as e:
        str(e)
        assert True


def test_calcTheta():
    #  in the case of elastic scattering, theta = 0.5*2theta

    ki = energyToK(5.0)
    kf = ki
    tTheta = 90.0
    theta = calcTheta(ki, kf, tTheta)
    assert (np.isclose(theta, 0.5 * tTheta))

    ThetaSix = 61.969840817
    ki = 2.0
    kf = 1.0
    tTheta = 42.0
    assert (np.isclose(calcTheta(ki=ki, kf=kf, two_theta=tTheta), ThetaSix))


def test_tasAngleBetween():
    v1 = np.array([1, 0, 0])
    v2 = np.array([0, 1, 1])
    v3 = np.array([1, 0, 1])

    # pylint: disable=arguments-out-of-order
    assert (np.isclose(tasAngleBetween(v1, v1), 0.0))
    assert (np.isclose(tasAngleBetween(v1, v2), 90.0))
    assert (np.isclose(tasAngleBetween(v2, v1), 90.0))
    assert (np.isclose(tasAngleBetween(v1, v3), 45.0))
    assert (np.isclose(tasAngleBetween(v3, v1), 45.0))
    assert (np.isclose(tasAngleBetween(v2, v3), 60.0))
    assert (np.isclose(tasAngleBetween(v3, v2), 60.0))


def test_tasAngleBetweenReflections():
    lattice = Cell(6.11, 6.11, 11.35, 90.0, 90.0, 120.0)
    B = lattice.calculateBMatrix()

    r1 = tasReflection(qh=1.0, qk=-2.0, ql=0.0)
    r2 = tasReflection(qh=-1.5, qk=1.1, ql=1.0)

    angle = tasAngleBetweenReflections(B, r1, r2)
    assert (np.isclose(angle, 131.993879212))


def test_uFromAngles():
    res1 = np.array([1.000000000, 0.000000000, 0.000000000])
    res2 = np.array([0.743144825, -0.669130606, 0.000000000])
    res3 = np.array([0.960176274, -0.223387216, 0.167808444])
    res4 = np.array([+0.974425454, -0.220358460, -0.044013456])
    res5 = np.array([0.974425454, 0.220358460, 0.044013456])
    res6 = np.array([0.974425454, 0.220358460, -0.044013456])

    results = [res1, res2, res3, res4, res5, res6]

    params = [[0.0, 0.0, 0.0], [42.0, 0.0, 0.0], [12.0, -5.0, 11.0],
              [12.0, 11.0, -5.0], [-12.0, 11.0, 5.0], [-12.0, -11.0, -5.0]]

    for par, res in zip(params, results):
        print(par, res)
        assert (np.all(np.isclose(uFromAngles(*par), res)))


def test_calcTasUVectorFromAngles():
    tR = tasReflection(ki=1.5, kf=2.5, qh=1, qk=2, ql=3, qm=2.0,
                       monochromator_two_theta=72, a3=10.0,
                       sample_two_theta=-60.6,
                       sgu=0.1, sgl=-0.1, analyzer_two_theta=50.0)

    assert (np.all(np.isclose(calcTasUVectorFromAngles(tR),
                              np.array([+0.955598330, -0.294664334,
                                        +0.002182125]))))


def test_tasReflectionToQC():
    r = tasQEPosition(ki=1.5, kf=2.5, qh=1, qk=2, ql=3, qm=2.0)
    lattice = Cell(6.11, 6.11, 11.35, 90.0, 90.0, 120.0)
    B = lattice.calculateBMatrix()

    Q = tasReflectionToQC(r, B)
    assert (np.all(
        np.isclose(Q,
                   np.array([+0.377970716, +0.327332242, +0.264317181])
                   * 2 * np.pi)))


def test_calcTwoTheta():
    lattice = Cell(6.11, 6.11, 11.35, 90.0, 90.0, 120.0)
    B = lattice.calculateBMatrix()

    hkl = [[0, 0, 0], [1, 0, 0],
           [0, 1, 0], [-1, 0, 0],
           [0, -1, 0], [0, 0, 1],
           [0, 0, -1], [2, -1, 3]]
    result = [0.0, 44.93975435373514, 44.93975435373514,
              44.93975435373514, 44.93975435373514,
              20.52777682289506,
              20.52777682289506, 116.61092637820377]
    for (h, k, ll), res in zip(hkl, result):

        qm = np.linalg.norm(np.dot(B, [h, k, ll]))
        r1 = tasReflection(ki=1.553424, kf=1.553424, qh=h, qk=k, ql=ll,
                           qm=qm, monochromator_two_theta=74.2, a3=0.0,
                           sample_two_theta=-200, sgu=0.0, sgl=0.0,
                           analyzer_two_theta=74.2)

        tt = calcTwoTheta(B, r1, 1)

        if not np.isclose(tt, res):
            print('Two theta for ({},{},{})={} '
                  'but expected {}'.format(h, k, ll, tt, res))
            assert False

    try:
        h, k, ll = 10, -10, 10
        qm = np.linalg.norm(np.dot(B, [h, k, ll]))  # HKL is far out of reach
        r1 = tasReflection(ki=1.553424, kf=1.553424, qh=h, qk=k, ql=ll, qm=qm,
                           monochromator_two_theta=74.2, a3=0.0,
                           sample_two_theta=-200,
                           sgu=0.0, sgl=0.0, analyzer_two_theta=74.2)
        tt = calcTwoTheta(B, r1, 1)
        assert False
    except RuntimeError:
        assert True


def test_matFromTwoVectors():
    v1 = np.array([1, 0, 0])
    v2 = np.array([0, 1, 0])

    assert (np.all(np.isclose(matFromTwoVectors(v1, v2),
                              np.diag([1, -1, 1]))))

    v1 = np.array([0, 1, 0])
    v2 = np.array([0, 0, 1])
    result = np.array([[0, 0, 1], [1, 0, 0], [0, -1, 0]])

    assert (np.all(np.isclose(matFromTwoVectors(v1, v2),
                              result)))

    v1 = np.array([0, 1, 2])
    v2 = np.array([0, 2, 1])
    result = np.array([[0, 0, -1], [0.4472136, -0.89442719, 0],
                       [0.89442719, 0.4472136, 0]])
    assert (np.all(np.isclose(matFromTwoVectors(v1, v2), result)))


def test_calcTasUBFromTwoReflections():
    lattices = []
    r1s = []
    r2s = []
    UBs = []

    # YMnO3, Eu
    latticeYMnO3 = Cell(6.11, 6.11, 11.35, 90.0, 90.0, 120.0)
    Ei = 5.0
    ki = energyToK(Ei)
    Ef = 4.96
    kf = energyToK(Ef)

    r1 = tasReflection(ki=ki, kf=kf, qh=0, qk=-1, ql=0,
                       a3=-60, sample_two_theta=-45.23, sgl=0, sgu=0)
    r2 = tasReflection(ki=ki, kf=kf, qh=1, qk=0, ql=0,
                       a3=0, sample_two_theta=-45.23, sgl=0, sgu=0)

    UB = np.array([[0.023387708, -0.150714153, 0.0],
                   [-0.187532612, -0.114020655, -0.0],
                   [0.0, -0.0, -0.088105727]])

    lattices.append(latticeYMnO3)
    r1s.append(r1)
    r2s.append(r2)
    UBs.append(UB)

    # PbTi
    latticePbTi = Cell(9.556, 9.556, 7.014, 90.0, 90.0, 90.0)
    Ei = 5.0000076

    ki = energyToK(Ei)
    Ef = 4.924756

    kf = energyToK(Ef)

    r1 = tasReflection(ki=ki, kf=kf, qh=0, qk=0, ql=2,
                       a3=74.2, sample_two_theta=-71.1594, sgl=0, sgu=0)
    r2 = tasReflection(ki=ki, kf=kf, qh=1, qk=1, ql=2,
                       a3=41.33997, sample_two_theta=-81.6363, sgl=0, sgu=0)

    UB = np.array([[0.06949673, 0.0694967, -0.048957292],
                   [-0.025409263, -0.025409255, -0.13390279],
                   [-0.07399609, 0.07399613, -4.2151984E-9]])

    lattices.append(latticePbTi)
    r1s.append(r1)
    r2s.append(r2)
    UBs.append(UB)

    # SecuO3
    latticeSeCuo = Cell(7.725, 8.241, 8.502, 90.0, 99.16, 90.0)
    Ei = 5.0000076

    ki = energyToK(Ei)
    Ef = 4.9221945
    kf = energyToK(Ef)

    r1 = tasReflection(ki=ki, kf=kf, qh=2, qk=1, ql=0,
                       a3=47.841908, sample_two_theta=-72.0, sgl=0, sgu=0)
    r2 = tasReflection(ki=ki, kf=kf, qh=2, qk=-1, ql=0,
                       a3=-1.8000551, sample_two_theta=-72.0, sgl=0, sgu=0)

    UB = np.array([[0.066903256, -0.10436039, 0.009677114],
                   [-0.11276933, -0.061914437, -0.016311338],
                   [-0.0, 0.0, -0.11761938]])

    lattices.append(latticeSeCuo)
    r1s.append(r1)
    r2s.append(r2)
    UBs.append(UB)

    for lat, r1, r2, UBSix in zip(lattices, r1s, r2s, UBs):
        UB = calcTasUBFromTwoReflections(lat, r1, r2)
        assert (np.all(np.isclose(UB, UBSix * 2 * np.pi, atol=1e-6)))


def test_calcPlaneNormal():
    lattice = Cell(6.11, 6.11, 11.35, 90.0, 90.0, 120.0)
    B = lattice.calculateBMatrix()

    HKL1 = [[1, 0, 0], [1, 1, 0], [1, 0, 0]]
    HKL2 = [[0, 1, 0], [1, -1, 0], [0, 0, 1]]
    result = [[0, 0, 1], [0, 0, 1], [0, 0, 1]]

    for hkl1, hkl2, res in zip(HKL1, HKL2, result):

        qm = np.linalg.norm(np.dot(B, hkl1))
        r1 = tasReflection(ki=1.553424, kf=1.553424,
                           qh=hkl1[0], qk=hkl1[1], ql=hkl1[2], qm=qm,
                           monochromator_two_theta=74.2,
                           a3=0.0, sample_two_theta=-200,
                           sgu=0.0, sgl=0.0,
                           analyzer_two_theta=74.2)
        tt = calcTwoTheta(B, r1, 1)
        r1.angles.sample_two_theta = tt
        r1.angles.a3 = calcTheta(r1.ki, r1.kf, tt)
        print('r1.a3: ', r1.a3)

        qm = np.linalg.norm(np.dot(B, hkl2))
        r2 = tasReflection(ki=1.553424, kf=1.553424,
                           qh=hkl2[0], qk=hkl2[1], ql=hkl2[2], qm=qm,
                           monochromator_two_theta=74.2,
                           a3=0.0, sample_two_theta=-200,
                           sgu=0.0, sgl=0.0,
                           analyzer_two_theta=74.2)
        tt = calcTwoTheta(B, r2, 1)
        r2.angles.sample_two_theta = tt
        r2.angles.a3 = calcTheta(r2.ki, r2.kf, tt) +\
            tasAngleBetweenReflections(B, r1, r2)
        print('r2.a3: ', r2.a3)

        planeNormal = calcPlaneNormal(r1, r2)
        if not np.all(np.isclose(planeNormal, res)):
            print('Plane normal for {} and {} = '
                  '{} but expected {}'.format(hkl1, hkl2, planeNormal, res))
            assert False


def test_makeAuxReflection():
    lattice = Cell(12.32, 3.32, 9.8, 92, 91, 120)
    B = lattice.calculateBMatrix()

    E = 22
    ki = energyToK(E)
    h, k, ll = 1, 0, -1
    qm = np.linalg.norm(np.dot(B, [h, k, ll]))

    r1 = tasReflection(ki=ki, kf=ki, qh=h, qk=k, ql=ll, qm=qm,
                       monochromator_two_theta=74.2, a3=12.2,
                       sgu=0.0, sgl=0.0,
                       analyzer_two_theta=74.2)

    tt = calcTwoTheta(B, r1, -1)
    r1.angles.sample_two_theta = tt

    r2 = makeAuxReflection(B, r1, -1.0, [3, 1, -1])

    assert (np.isclose(r2.a3, 35.875022341))
    assert (np.isclose(r2.sample_two_theta, -64.129182823))

    try:
        r2 = makeAuxReflection(B, r1, -1.0, [30, 1, -1])
        assert False
    except RuntimeError:
        assert True


def test_calcTasQAngles():
    # SeCuO3
    latticeSeCuo = Cell(7.725, 8.241, 8.502, 90.0, 99.16, 90.0)
    Ei = 5.0000076

    ki = energyToK(Ei)
    Ef = 4.9221945
    kf = energyToK(Ef)

    r1 = tasReflection(ki=ki, kf=kf, qh=2, qk=1, ql=0, a3=47.841908,
                       sample_two_theta=-71.840689064, sgl=0, sgu=0)
    r2 = tasReflection(ki=ki, kf=kf, qh=2, qk=-1, ql=0,
                       a3=-1.819579944281713, sample_two_theta=-71.840689064,
                       sgl=0, sgu=0)
    UB = calcTasUBFromTwoReflections(latticeSeCuo, r1, r2)
    planeNormal = calcPlaneNormal(r1, r2)

    ss = -1
    a3Off = 0.0
    for (h, k, l), a3, a4 in zip([[r1.qh, r1.qk, r1.ql],
                                  [r2.qh, r2.qk, r2.ql]],
                                 [r1.a3, r2.a3],
                                 [r1.sample_two_theta, r2.sample_two_theta]):
        R = tasReflection(ki=ki, kf=kf, qh=h, qk=k, ql=l)
        qm = np.linalg.norm(np.dot(UB, [h, k, l]))

        qe = tasQEPosition(ki, kf, R.qh, R.qk, R.ql, qm=qm)
        angles = calcTasQAngles(UB, planeNormal, ss, a3Off, qe)

        assert (np.isclose(a3, angles.a3))
        assert (np.isclose(a4, angles.sample_two_theta))


def test_calcScatteringPlaneNormal():
    qe1 = tasQEPosition(1.0, 1.0, qh=1.0, qk=2.0, ql=3.0, qm=2)
    qe2 = tasQEPosition(1.0, 1.0, qh=2.0, qk=-2.0, ql=3.0, qm=2)
    planeNormal = calcScatteringPlaneNormal(qe1, qe2)
    print(planeNormal)
    assert (np.isclose(np.linalg.norm(planeNormal), 1.0))
    assert (np.all(np.isclose([0.87287156, 0.21821789, -0.43643578],
                              planeNormal)))
