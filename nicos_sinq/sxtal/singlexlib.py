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
#
# *****************************************************************************
"""
This is a library of functions for single crystal diffraction.
The bisecting four circle and normal beam geometry are covered.

The coordinate systems used are described in  Busing, Levy,
Acta Cryst (1967),22, 457 ff.

 Generally we have:

 Z = [OM][CHI][PHI][UB]h

 where: Z is  a vector in the diffractometer coordinate system
        OM CHI PHI are rotation matrices around the respective angles
        UB is the UB matrix
        h is the reciprocal lattice vector.

 The vector Z cannot only be expressed in terms of the angles stt, om, chi,
 and phi put also by polar coordinates gamma and nu.

This library is a python translation of a ANSII-C library for the
same purpose used in SICS. And this C library in turn is a translation
from original Fortran code by Garry McIntyre, ILL and from TASMAD
"""

from math import acos, asin, atan2, cos, floor, pi, sin, sqrt

import numpy as np

from nicos_sinq.sxtal.cell import Cell
from nicos_sinq.sxtal.trigd import angleBetween, rtan


def psimat(psi):
    """
    Build a Busing & Levy PSI matrix, psi must be in radians
    """
    result = np.zeros((3, 3,), dtype='float64')
    result[0][0] = 1.
    result[1][1] = cos(psi)
    result[1][2] = sin(psi)
    result[2][1] = -result[1][2]
    result[2][2] = result[1][1]
    return result


def chimat(chi):
    """
    Build a Busing & Levy CHI matrix. Input is
    in radians
    """
    result = np.zeros((3, 3,), dtype='float64')
    result[0][0] = cos(chi)
    result[0][2] = sin(chi)
    result[1][1] = 1.
    result[2][0] = -sin(chi)
    result[2][2] = cos(chi)
    return result


def phimat(phi):
    """
    Build a Busing & Levy PHI matrix. Input is in radians
    """
    result = np.zeros((3, 3,), dtype='float64')
    result[0][0] = cos(phi)
    result[0][1] = sin(phi)
    result[1][0] = -sin(phi)
    result[1][1] = cos(phi)
    result[2][2] = 1.
    return result


def turnEquatorial(z1):
    """
    Turn the vector z1 into the equatorial plane
    @param z1 3 component numpy array
    @return tuple of (chi, phi) in radians
    """
    if abs(z1[0]) < .0001 and abs(z1[1]) < .0001:
        if z1[2] < 0:
            return -pi/2., 0
        return pi/2., 0
    phi = rtan(z1[1], z1[0])
    chi = rtan(z1[2], sqrt(z1[0]**2 + z1[1]**2))
    return chi, phi


def calcTheta(wavelength, z1):
    """
    Calculates the d spacing and the theta angle for a scattering
    vector z1
    @param wavelength
    @param z1 A 3 component numpy array representing the scattering
              vector
    @param A tuple consisting of the d-value and the theta angle in
           radians
    """
    dstar = sqrt(z1[0]**2 + z1[1]**2 + z1[2]**2)
    if dstar < .0001:
        return 0., 0.

    d = 1./dstar
    sintheta = wavelength * dstar/2.
    if abs(sintheta) > 1.:
        return .0, .0
    theta = asin(sintheta)
    return d, theta


def z1ToBisecting(wavelength, z1):
    """
    Calculates the four circle angles om, chi, phi for
    scattering vector z1
    @param wavelength
    @param z1 A scattering vector as a numpy array with 3 elements
    @return a tuple of theta, chi, phi in radians
    """
    d, theta = calcTheta(wavelength, z1)
    if d == .0:
        return .0, .0, .0
    chi, phi = turnEquatorial(z1)
    return theta, pi - chi, pi + phi


def z1fromz2(z2, phi):
    """
    Calculate Z1 = [PHI]T*Z2
    @param z2 The z2 vector as numpy three element array
    @param phi The phi-angle in radians
    @return The z1 vector
    """
    chim = phimat(phi).transpose()
    return chim.dot(z2)


def z1fromz3(z3, chi, phi):
    """
    Calculate Z1 = [PHI]T * [CHI]T * Z3
    @param The z3 vector
    @param chi angle in radians
    @param phi angle in radians
    @return The z1 vector
    """
    chim = chimat(chi).transpose()
    z2 = chim.dot(z3)
    return z1fromz2(z2, phi)


def z1fromz4(z4, om, chi, phi):
    """
    Calculate Z1 = [PHI]T*[CHI]T*[OM]T*Z4
    @param The z4 vector
    @param om angle in radians
    @param chi angle in radians
    @param phi angle in radians
    @return The z1 vector
    """
    oma = phimat(om).transpose()
    z3 = oma.dot(z4)
    return z1fromz3(z3, chi, phi)


def z1FromAngles(wavelength, stt, om, chi, phi):
    """
    Calculate the scattering vector z1 from angles
    @param wavelength
    @param om angle in radians
    @param chi angle in radians
    @param phi angle in radians
    @return The z1 vector
    """
    th = stt/2.
    z4 = np.array([
        (2. * sin(th) * cos(th)) / wavelength,
        (-2. * sin(th) * sin(th)) / wavelength,
        .0
    ], dtype='float64')
    return z1fromz4(z4, om, chi, phi)


def rotatePsi(om, chi, phi, psi):
    """
    Rotate the scattering vector define by om, chi, phi by psi
    on the scattering cone
    @param Input om
    @param Input chi
    @param Input phi
    @param Input psi
    @return A tuple of om, chi, phi with psi rotation applied
    """
    r0 = chimat(chi).dot(phimat(phi))
    psim = psimat(psi)
    r0psi = psim.dot(r0)
    psichi = rtan(sqrt(r0psi[2][0]**2 + r0psi[2][1]**2), r0psi[2][2])
    psiphi = rtan(-r0psi[2][1], -r0psi[2][0])
    psiom = om + rtan(-r0psi[1][2], r0psi[0][2])
    return psiom, psichi, psiphi

# ====================== normal beam geometry =================================


def sign(a, b):
    if b >= .0:
        return abs(a)
    return -abs(a)


def z1ToNormalBeam(wavelength, z1):
    """
    Calculate the normal beam angles gamm, omega, nu for
    a scattering vector
    @param wavelength
    @param z1, the scattering vector
    @return A tuple of gamma, omega, nu in the case of
            success, 0,0,0, on failure
    """
    d, theta = calcTheta(wavelength, z1)
    if d == .0:
        return 0, 0, 0
    # Everything on omega axis is blind...
    a = sqrt(z1[0]**2 + z1[1]**2)
    if abs(a) < .0001:
        return 0, 0, 0
    sint = sin(theta)
    b = 2*sint**2/(wavelength * a)
    if b > 1.:
        return 0, 0, 0
    a = -atan2(z1[1], -z1[0])
    b = -asin(b)
    om = a + b
    oma = phimat(om)
    znew = oma.dot(z1)
    if znew[0] < 0:
        om = om - 2. * atan2(-znew[0], -znew[1])
    b = (sign(180, om) + om)/360.
    b = sign(1, b) * floor(abs(b))
    om = om - 2*pi * b
    nu = asin(wavelength * z1[2])
    gamma = acos(cos(2. * theta)/cos(nu))
    return gamma, om, nu


def biToNormalBeam(stt, omega, chi, phi):
    """
    Calculate teh normal beam angles gamm, omega, nu
    from the bisecting positions stt, om, chi, phi
    @param stt two theta
    @param omega
    @param chi
    @param chi
    @return gamma, om, nu angles in radians or 0, 0, 0 in case
            of an error
    """
    sint = sin(stt/2.)

    nu = 2. * sin(chi) * sint
    if nu > 1.:
        return 0, 0, 0
    nu = asin(nu)
    nu = abs(nu) * sign(1., chi)

    gamma = cos(stt) / cos(nu)
    if abs(gamma) > 1.:
        return 0, 0, 0
    gamma = acos(gamma)
    gamma = gamma * sign(1., stt)

    ddel = asin(sint/cos(chi))
    omnb = ddel + phi
    if abs(omnb) > pi:
        if omnb < - pi:
            omnb += 2 * pi
        if omnb > pi:
            omnb -= 2 * pi
    return gamma, omnb, nu


def z4FromNormalBeam(wavelength, gamma, nu):
    """
    This is basically a conversion from polar
    to x,y ,z coordinates
    """
    z4 = np.zeros((3,), dtype='float64')
    z4[0] = (sin(gamma) * cos(nu)) / wavelength
    z4[1] = (cos(gamma) * cos(nu) - 1.) / wavelength
    z4[2] = sin(nu) / wavelength
    return z4


def z1FromNormalBeam(wavelength, gamma, omega, nu):
    """
    Calculate the scattering vector z1 from normal beam
    angles. All angles in radians
    @param wavelength
    @param gamma
    @param omega
    @param nu
    @return The z1 vector or none
    """
    z4 = z4FromNormalBeam(wavelength, gamma, nu)
    oma = phimat(omega).transpose()
    z1 = oma.dot(z4)
    return z1

#  UB Matrix Calculation
# Reflections are kept in a dictionary with h, k, l and the angles
# Some of the NB code has been lifted from the ILL program rafinb
#


def UVectorFromAngles(reflection):
    """
    Calculate the B&L U vector from bisecting geometry
    angles
    """
    u = np.zeros((3,), dtype='float64')

    # The tricky bit is set again: Busing & Levy's omega is 0 in
    # bisecting position. This is why we have to correct for
    # stt/2 here
    om = np.deg2rad(reflection['om'] - reflection['stt']/2.)
    chi = np.deg2rad(reflection['chi'])
    phi = np.deg2rad(reflection['phi'])
    u[0] = cos(om) * cos(chi) * cos(phi) - sin(om) * sin(phi)
    u[1] = cos(om) * cos(chi) * sin(phi) + sin(om) * cos(phi)
    u[2] = cos(om) * sin(chi)
    return u


def UNBVectorFromAngles(reflection):
    """"
    Calculate the B&L U vector from normal beam geometry angles
    """
    u = np.zeros((3,), dtype='float64')
    gamma = np.deg2rad(reflection['gamma'])
    om = np.deg2rad(reflection['om'])
    nu = np.deg2rad(reflection['nu'])
    u[0] = sin(gamma) * cos(om) * cos(nu) + \
        sin(om) * (1. - cos(gamma) * cos(nu))
    u[1] = sin(gamma) * sin(om) * cos(nu) - \
        cos(om) * (1. - cos(gamma) * cos(nu))
    u[2] = sin(nu)
    return u


def reflectionToHC(reflection, B):
    """
    Calculate the B&L HC vector for this reflection
    """
    h = np.array([reflection['h'], reflection['k'], reflection['l']],
                 dtype='float64')
    return B.dot(h)


def directToReciprocalLattice(cell):
    """
    caclulate the reciprocal lattice from the
    direct one
    """
    reciprocal = Cell()

    alfa = np.deg2rad(cell.alpha)
    beta = np.deg2rad(cell.beta)
    gamma = np.deg2rad(cell.gamma)

    cos_alfa = cos(alfa)
    cos_beta = cos(beta)
    cos_gamma = cos(gamma)

    sin_alfa = sin(alfa)
    sin_beta = sin(beta)
    sin_gamma = sin(gamma)

    reciprocal.alpha = \
        acos((cos_beta * cos_gamma - cos_alfa) / sin_beta / sin_gamma)
    reciprocal.beta = \
        acos((cos_alfa * cos_gamma - cos_beta) / sin_alfa / sin_gamma)
    reciprocal.gamma =\
        acos((cos_alfa * cos_beta - cos_gamma) / sin_alfa / sin_beta)

    ad = cell.a
    bd = cell.b
    cd = cell.c

    arg = 1 + 2 * cos_alfa * cos_beta * cos_gamma - cos_alfa * \
        cos_alfa - cos_beta * cos_beta - cos_gamma * cos_gamma
    if arg < 0.0:
        return None
    vol = ad * bd * cd * sqrt(arg)
    reciprocal.a = bd * cd * sin_alfa / vol
    reciprocal.b = ad * cd * sin_beta / vol
    reciprocal.c = bd * ad * sin_gamma / vol
    return reciprocal


def calculateBMatrix(cell):
    """
    Calculate the B matrix. This calculation is subtly
    different then the one in cell.py as it is not
    normalized with 2*PI
    """
    reciprocal = directToReciprocalLattice(cell)
    if not reciprocal:
        return None

    B = np.zeros((3, 3), dtype='float64')
    # Top row
    B[0][0] = reciprocal.a
    B[0][1] = reciprocal.b * cos(reciprocal.gamma)
    B[0][2] = reciprocal.c * cos(reciprocal.beta)
    # middle row
    B[1][1] = reciprocal.b * sin(reciprocal.gamma)
    B[1][2] = -reciprocal.c * sin(reciprocal.beta) * \
        cos(np.deg2rad(cell.alpha))
    # Bottom row
    B[2][2] = 1. / cell.c

    return B


def normalize_vector(v):
    sqsum = .0
    for el in v:
        sqsum += el**2
    length = sqrt(sqsum)
    if length > .00001:
        return v / length
    return v


def matFromTwoVectors(v1, v2):
    a1 = normalize_vector(v1)

    a3 = np.cross(v1, v2)
    a3 = normalize_vector(a3)

    a2 = np.cross(a1, a3)

    result = np.zeros((3, 3), dtype='float64')

    for i in range(3):
        result[i][0] = a1[i]
        result[i][1] = a2[i]
        result[i][2] = a3[i]

    return result


def calcUBFromCellAndReflections(cell, r1, r2):
    """
    Calculate a B&L UB matrix from cell constants and two
    reflections. Bisecting geometry is assumed. Reflections come as
    dictionaries containing h, k, l, stt, om, chi, phi
    @param cell A dictionary containing a, b, c, alpha, beta, gamma
    @param r1 First reflection
    @param r2 Second reflection
    @return A UB matrix or None if the calculation is not possible
    """
    # calculate the B matrix and the HT matrix
    B = calculateBMatrix(cell)
    if not B.any():
        return None

    # build HT matrix
    h1 = reflectionToHC(r1, B)
    h2 = reflectionToHC(r2, B)
    HT = matFromTwoVectors(h1, h2)

    # Build UT matrix
    u1 = UVectorFromAngles(r1)
    u2 = UVectorFromAngles(r2)
    UT = matFromTwoVectors(u1, u2)

    # UT = U * HT
    HTT = HT.transpose()
    U = UT.dot(HTT)
    UB = U.dot(B)
    return UB


def calcNBUBFromCellAndReflections(cell, r1, r2):
    """
    Calculate a B&L UB matrix from cell constants and two
    reflections. Normal beam geometry is assumed. Reflections come as
    dictionaries containing h, k, l, gammo, om, bu
    @param cell A dictionary containing a, b, c, alpha, beta, gamma
    @param r1 First reflection
    @param r2 Second reflection
    @return A UB matrix or None if the calculation is not possible
    """
    # calculate the B matrix and the HT matrix
    B = calculateBMatrix(cell)
    if not B.any():
        return None

    # build HT matrix
    h1 = reflectionToHC(r1, B)
    h2 = reflectionToHC(r2, B)
    HT = matFromTwoVectors(h1, h2)

    # Build UT matrix
    u1 = UNBVectorFromAngles(r1)
    u2 = UNBVectorFromAngles(r2)
    UT = matFromTwoVectors(u1, u2)

    # UT = U * HT
    HTT = HT.transpose()
    U = UT.dot(HTT)
    UB = U.dot(B)
    return UB


def angleBetweenReflections(B, r1, r2):
    """
    Calculate the angle between two reflections
    Reflections are given as dictionaries
    @param B The B matrix
    @param r1 First reflection
    @param r2 Second reflection
    @return The angle between r1 and r2 in radians
    """
    h1 = np.array([r1['h'], r1['k'], r1['l']], dtype='float64')
    h2 = np.array([r2['h'], r2['k'], r2['l']], dtype='float64')
    ch1 = B.dot(h1)
    ch2 = B.dot(h2)
    return angleBetween(ch1, ch2)
