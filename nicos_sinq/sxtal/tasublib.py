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
from copy import deepcopy

import numpy as np

from nicos_sinq.sxtal.singlexlib import matFromTwoVectors
from nicos_sinq.sxtal.trigd import Acosd, Atand2, Cosd, Rtand, Sind, \
    angleBetween


def tasAngleBetween(v1, v2):
    return np.rad2deg(angleBetween(v1, v2))

def fmod(x, y):
    s = np.sign(x)
    res = s*np.mod(np.abs(x), y)
    return res


class tasQEPosition():
    def __init__(self, ki, kf, qh, qk, ql, qm):
        self.ki = ki
        self.kf = kf
        self.qh = qh
        self.qk = qk
        self.ql = ql
        self.qm = qm


class tasAngles():
    def __init__(self, monochromator_two_theta, a3,
                 sample_two_theta, sgl, sgu,
                 analyzer_two_theta):
        self.monochromator_two_theta = monochromator_two_theta
        self.a3 = a3
        self.sample_two_theta = sample_two_theta
        self.sgu = sgu
        self.sgl = sgl
        self.analyzer_two_theta = analyzer_two_theta


class tasReflection():
    def __init__(self, qe=None, angles=None, ki=None, kf=None,
                 qh=None, qk=None, ql=None, qm=None,
                 monochromator_two_theta=None, a3=None,
                 sample_two_theta=None,
                 sgl=None, sgu=None, analyzer_two_theta=None):
        if isinstance(qe, tasReflection):
            self.qe = deepcopy(qe.qe)
            self.angles = deepcopy(qe.angles)
        else:
            if qe is None:
                self.qe = tasQEPosition(ki, kf, qh, qk, ql, qm)
            else:
                self.qe = qe
            if angles is None:
                self.angles = tasAngles(monochromator_two_theta,
                                        a3, sample_two_theta,
                                        sgl, sgu,
                                        analyzer_two_theta)
            else:
                self.angles = angles

    def __getattr__(self, key):
        # if key in ['qe','angles']: # Is automatically tested
        #    return self.__dict__[key]
        if key in self.qe.__dict__.keys():
            return getattr(self.qe, key)
        elif key in self.angles.__dict__.keys():
            return getattr(self.angles, key)
        else:
            raise AttributeError(
                "'tasReflection' object hs no attribute '{}'".format(key))


ECONST = 2.072  # 2.072122396


def energyToK(energy):
    """Convert energy in meV to K in q/A"""
    return np.sqrt(energy / ECONST)


def KToEnergy(K):
    """Convert K in 1/A to E in meV"""
    return ECONST*np.power(K, 2.0)


def tasReflectionToHC(r, B):
    """Calculate HC from HKL and B matrix"""
    return tasHKLToHC(r.qh, r.qk, r.ql, B)


def tasHKLToHC(qh, qk, ql, B):
    """Calculate HC from reflection r and B matrix"""
    h = np.array([qh, qk, ql])
    hc = np.dot(B, h)
    return hc


def calcTheta(ki, kf, two_theta):
    """
                  |ki| - |kf|cos(two_theta)
    tan(theta) = --------------------------
                   |kf|sin(two_theta)
    """
    return Rtand(np.abs(ki) - np.abs(kf) * Cosd(two_theta),
                 np.abs(kf) * Sind(two_theta))


def tasAngleBetweenReflections(B, r1, r2):
    """Calculate angle between two reflections"""
    return tasAngleBetweenReflectionsHKL(B,
                                         r1.qh, r1.qk, r1.ql,
                                         r2.qh, r2.qk, r2.ql)


def tasAngleBetweenReflectionsHKL(B,
                                  h1, k1, l1,
                                  h2, k2, l2):
    """Calculate angle between two reflections"""
    v1 = np.array([h1, k1, l1])
    v2 = np.array([h2, k2, l2])

    chi1 = np.einsum('ij,j...->i...', B, v1)
    chi2 = np.einsum('ij,j...->i...', B, v2)

    angle = tasAngleBetween(chi1, chi2)
    return angle


def uFromAngles(om, sgu, sgl):
    u = np.array([Cosd(om)*Cosd(sgl),
                  -Sind(om)*Cosd(sgu)+Cosd(om)*Sind(sgl)*Sind(sgu),
                  Sind(om)*Sind(sgu)+Cosd(om)*Sind(sgl)*Cosd(sgu)])
    return u


def calcTasUVectorFromAngles(rr):
    ss = np.sign(rr.sample_two_theta)

    r = tasReflection(rr)
    r.sample_two_theta = np.abs(r.sample_two_theta)
    theta = calcTheta(r.ki, r.kf, r.sample_two_theta)

    om = r.angles.a3 - ss*theta
    m = uFromAngles(om, r.angles.sgu, ss*r.angles.sgl)
    return m


def tasReflectionToQC(r, UB):
    return tasReflectionToQCHKL(r.qh, r.qk, r.ql, UB)


def tasReflectionToQCHKL(h, k, l, UB):
    Q = np.array([h, k, l])
    return np.einsum('ij,j...->i...', UB, Q)


def makeAuxReflection(B, r1, ss, hkl):
    r2 = tasReflection(r1)
    r2.qe.qh, r2.qe.qk, r2.qe.ql = hkl

    theta = calcTheta(r1.qe.ki, r1.qe.kf,
                      ss*r1.angles.sample_two_theta)
    om = r1.angles.a3 - ss*theta

    om += tasAngleBetweenReflectionsHKL(B, r1.qh, r1.qk,
                                        r1.ql, *hkl)

    QC = tasReflectionToHC(r2.qe, B)
    q = np.linalg.norm(QC)

    cos2t = np.divide(r1.ki * r1.ki + r1.kf * r1.kf - q * q,
                      (2. * np.abs(r1.ki) * np.abs(r1.kf)))
    if np.abs(cos2t) > 1.:
        raise RuntimeError('Scattering angle not closed!')

    r2.angles.sample_two_theta = ss * Acosd(cos2t)
    theta = calcTheta(r1.qe.ki, r1.qe.kf, ss*r2.angles.sample_two_theta)
    r2.angles.a3 = om + ss*theta

    r2.angles.a3 = fmod(r2.angles.a3 + ss*180., 360.) - ss*180.

    return r2


def calcTwoTheta(B, ref, ss):
    QC = tasReflectionToHC(ref, B)

    q = np.linalg.norm(QC)

    cos2t = np.divide(ref.ki * ref.ki + ref.kf * ref.kf - q * q,
                      (2. * np.abs(ref.ki) * np.abs(ref.kf)))

    if np.abs(cos2t) > 1.:
        raise RuntimeError(
            'Calculated abs(cos2t) value {} bigger than 1!'
            ' Scattering angle not closed'.format(np.abs(cos2t)))

    value = ss * Acosd(cos2t)
    return value


def calcPlaneNormal(r1, r2):
    u1 = calcTasUVectorFromAngles(r1)
    u2 = calcTasUVectorFromAngles(r2)
    planeNormal = np.cross(u1, u2)
    planeNormal *= 1.0/np.linalg.norm(planeNormal)

    # In TasCode code is commented out performing check
    # for sign of planeNormal[2] is performed.
    # If negative, z component negated.

    planeNormal[2] = np.abs(planeNormal[2])
    return planeNormal


def calcTasUBFromTwoReflections(cell, r1, r2,):

    B = cell.calculateBMatrix()

    h1 = tasReflectionToHC(r1.qe, B)
    h2 = tasReflectionToHC(r2.qe, B)

    HT = matFromTwoVectors(h1, h2)

    #   calculate U vectors and UT matrix

    u1 = calcTasUVectorFromAngles(r1)
    u2 = calcTasUVectorFromAngles(r2)

    UT = matFromTwoVectors(u1, u2)

    #   UT = U * HT

    U = np.dot(UT, HT.T)

    UB = np.dot(U, B)

    return UB


def buildRMatrix(UB, planeNormal, qe):
    U1V = tasReflectionToQC(qe, UB)

    U1V *= 1.0/np.linalg.norm(U1V)
    U2V = np.cross(planeNormal, U1V)

    if np.linalg.norm(U2V) < .0001:
        raise RuntimeError('Found vector is too short')
    TV = buildTVMatrix(U1V, U2V)

    TVINV = np.linalg.inv(TV)
    return TVINV


def buildTVMatrix(U1V, U2V):
    U2V *= 1.0/np.linalg.norm(U2V)
    T3V = np.cross(U1V, U2V)
    T3V *= 1.0/np.linalg.norm(T3V)

    T = np.zeros((3, 3))

    for i in range(3):
        T[i][0] = U1V[i]
        T[i][1] = U2V[i]
        T[i][2] = T3V[i]

    return T


def calcTasQAngles(UB, planeNormal, ss, a3offset, qe):

    R = buildRMatrix(UB, planeNormal, qe)
    angles = tasAngles(0, 0, 0, 0, 0, 0)

    cossgl = np.sqrt(R[0][0]*R[0][0]+R[1][0]*R[1][0])
    angles.sgl = ss*Atand2(-R[2][0], cossgl)
    if np.abs(angles.sgl - 90.) < .5:
        raise RuntimeError('Combination of UB and Q is not valid')

    #    Now, this is slightly different then in the publication by M. Lumsden.
    #    The reason is that the atan2 helps to determine the sign of om
    #    whereas the sin, cos formula given by M. Lumsden yield ambiguous signs
    #    especially for om.
    #    sgu = atan(R[2][1],R[2][2]) where:
    #    R[2][1] = cos(sgl)sin(sgu)
    #    R[2][2] = cos(sgu)cos(sgl)
    #    om = atan(R[1][0],R[0][0]) where:
    #    R[1][0] = sin(om)cos(sgl)
    #    R[0][0] = cos(om)cos(sgl)
    #    The definitions of the R components are taken from M. Lumsden
    #    R-matrix definition.

    om = Atand2(R[1][0]/cossgl, R[0][0]/cossgl)
    angles.sgu = Atand2(R[2][1]/cossgl, R[2][2]/cossgl)

    QC = tasReflectionToQC(qe, UB)

    q = np.linalg.norm(QC)

    cos2t = (qe.ki * qe.ki + qe.kf * qe.kf -
             q * q) / (2. * np.abs(qe.ki) * np.abs(qe.kf))
    if np.abs(cos2t) > 1.:
        raise RuntimeError('Scattering angle cannot '
                           'be closed, cos2t =  ', cos2t)
    theta = calcTheta(qe.ki, qe.kf, Acosd(cos2t))
    angles.sample_two_theta = ss * Acosd(cos2t)

    angles.a3 = om + ss*theta + a3offset
    #
    #    put a3 into -180, 180 properly. We can always turn by 180
    #    because the scattering geometry is symmetric in this respect.
    #    It is like looking at the scattering plane from the other side

    angles.a3 = fmod(angles.a3 + ss*180., 360.) - ss*180.
    return angles


def calcScatteringPlaneNormal(qe1, qe2):
    v1 = [qe1.qh, qe1.qk, qe1.ql]
    v2 = [qe2.qh, qe2.qk, qe2.ql]

    planeNormal = np.cross(v1, v2)
    planeNormal *= 1.0/np.linalg.norm(planeNormal)

    return planeNormal
