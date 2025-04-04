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
#   Nicolai Amin <nicolai.amin@psi.ch>
#
# *****************************************************************************

from math import cos, sin, sqrt

import numpy as np

from nicos import session
from nicos.commands import helparglist, usercommand

from nicos_sinq.sxtal.commands import ListRef
from nicos_sinq.sxtal.instrument import KappaSXTal
from nicos_sinq.sxtal.singlexlib import calculateBMatrix as genB
from nicos_sinq.zebra.devices.sinqxtal import SinqEuler, SinqNB

__all__ = ['RefineUB']


# Normalize vector
def normv(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return 0, v
    return norm,  v / norm


# The matrices below are different from the rotations in singlexlib
def xRot(a, typecode='d'):
    """Construct a rotation matrix rotating 'a' around the X axis"""
    a *= np.pi/180
    sa = np.sin(a)
    ca = np.cos(a)
    return np.array([[1.0, 0, 0], [0, ca, sa], [0, -sa, ca]], typecode)


def yRot(a, typecode='d'):
    """Construct a rotation matrix rotating 'a' around the Y axis"""
    a *= np.pi/180
    sa = np.sin(a)
    ca = np.cos(a)
    return np.array([[ca, 0, -sa], [0, 1.0, 0], [sa, 0, ca]], typecode)


def zRot(a, typecode='d'):
    """Construct a rotation matrix rotating 'a' around the Z axis"""
    a *= np.pi/180
    sa = np.sin(a)
    ca = np.cos(a)
    return np.array([[ca, sa, 0], [-sa, ca, 0], [0, 0, 1.0]],
                    typecode)


def Rot(r, typecode='d'):
    """Construction of full rotation matrix"""
    X = xRot(r[0])
    Y = yRot(r[1])
    Z = zRot(r[2])
    return Z @ Y @ X


def couple(  # pylint: disable=too-many-positional-arguments
        hkls, obs, instr, sample, min_angle, refs=None):
    """"
    Couple function to find the optimal two reflections to run RefineUB on
    """
    PHIF = 0
    V3MX = 0
    idxs = [-1, -1]
    cell = sample.getCell()
    B = genB(cell)
    if refs is not None:
        hkls = [hkls[i] for i in refs]
    for i in range(len(hkls)-1):
        for j in range(i+1, len(hkls)):
            h1 = hkls[i]
            V1 = np.matmul(B, h1)
            h2 = hkls[j]
            V2 = np.matmul(B, h2)
            V3 = prodv(V1, V2)
            V1M, V1 = normv(V1)
            V2M, V2 = normv(V2)
            V3M, V3 = normv(V3)
            V12M = V1M * V2M

            if abs(V12M) < 10**(-5):
                continue
            if abs(V3M/V12M) <= 1:
                PHI = np.arcsin(V3M/V12M)
            else:
                continue

            PHI = np.abs(PHI % np.pi)

            if np.pi/2 <= PHI:
                PHI = np.pi - abs(PHI)

            if PHI < min_angle*np.pi/180:
                continue

            if ((45 < abs(obs[i, 2])) and (abs(obs[i, 2]) < 135) and
                    (45 < abs(obs[j, 2])) and (abs(obs[j, 2]) < 135)):
                continue

            if V3M < V3MX:
                continue

            PHIF = PHI
            V3MX = V3M
            idxs = [i, j]

    if idxs == [-1, -1]:
        if refs is not None:
            session.log.error(
                'Two selected reflections are less than %i degrees seperated' +
                '\n Please choose others',
                min_angle)
            raise TypeError()
        else:
            session.log.error(
                'No two reflections are more than %i degrees seperated' +
                '\n Please measure more Peaks', min_angle)
            raise TypeError()

    else:
        session.log.info(
            'Orienting Ref 1. %i  %i %i %i',
            idxs[0],
            hkls[idxs[0], 0],
            hkls[idxs[0], 1],
            hkls[idxs[0], 2])
        session.log.info(
            'Orienting Ref 2. %i  %i %i %i',
            idxs[1],
            hkls[idxs[1], 0],
            hkls[idxs[1], 1],
            hkls[idxs[1], 2])
        session.log.info('Angle: %f', PHIF*180/np.pi)

        return (idxs[0], idxs[1])


def UNBVectorFromAngles(reflection):
    """"
    Calculate the B&L U vector from normal beam geometry angles
    Not using normal function as it uses wrong references
    """
    u = np.zeros((3,), dtype='float64')
    gamma = np.deg2rad(reflection[0])
    om = np.deg2rad(reflection[1])
    nu = np.deg2rad(reflection[2])
    u[0] = sin(gamma) * cos(om) * cos(nu) + \
        sin(om) * (1. - cos(gamma) * cos(nu))
    u[1] = sin(gamma) * sin(om) * cos(nu) - \
        cos(om) * (1. - cos(gamma) * cos(nu))
    u[2] = sin(nu)
    return u


def UVectorFromAngles(instr, hkl, reflection):
    """
    Calculate the B&L U vector from normal beam geometry angles
    Not using normal function as it uses wrong references
    """
    u = np.zeros((3, ), dtype='float64')

    # The tricky bit is set again: Busing & Levy's omega is 0 in
    # bisecting position. This is why we have to correct for
    # stt/2 here
    sign = np.sign(reflection[0])

    hkld = np.sqrt(hkl[0]**2 + hkl[1]**2 + hkl[2]**2)
    theta = np.arcsin(hkld*instr.wavelength/2)

    om = sign*np.deg2rad(reflection[1]) - theta
    chi = sign*np.deg2rad(reflection[2])
    phi = np.deg2rad(reflection[3]) + (sign-1)*np.pi/2

    u[0] = cos(om) * cos(chi) * cos(phi) - sin(om) * sin(phi)
    u[1] = cos(om) * cos(chi) * sin(phi) + sin(om) * cos(phi)
    u[2] = cos(om) * sin(chi)
    return u


def UKVectorFromAngles(reflection):
    """
    Calculate the B&L U vector from normal beam geometry angles
    Not using normal function as it uses wrong references
    """
    session.log.warning("Kappa not implemented yet")
    return 0


# TODO This is such a shitty way of doing this, but is the best i know right
# now Should be done better in the future
def vecori(v1, v2, dials):
    """
    Function to rotate calculated orienting reflections such
    that they are in plane with the actual reflections
    """
    RAD2DEG = 180/np.pi
    dials = np.array(dials) / RAD2DEG
    VN = prodv(v1, v2)
    VXM, VX = normv(v1)  # pylint: disable=unused-variable
    VZM, VZ = normv(VN)  # pylint: disable=unused-variable
    VYM, VY = normv(prodv(VZ, VX))  # pylint: disable=unused-variable

    for i in range(3):
        j = (1+i) % 3
        k = (2+i) % 3
        B = np.zeros((3, 3))
        B[:, i] = VX
        B[:, j] = VY
        B[:, k] = VZ
        BI = B.T
        V01 = BI @ v1
        V02 = BI @ v2
        # Small angle approximation for dials
        CE = 1 - dials[i]**2 / 2
        SE = dials[i]
        C = np.array([[1, 0, 0], [0, CE, SE], [0, -SE, CE]])
        V001 = C @ V01
        V002 = C @ V02
        v1 = B @ V001
        v2 = B @ V002
    return v1, v2


def prodv(v1, v2):
    """
    Function to calculate the cross product of two vectors
    """
    v3 = np.zeros(3)
    v3[0] = v1[1]*v2[2] - v1[2]*v2[1]
    v3[1] = v1[2]*v2[0] - v1[0]*v2[2]
    v3[2] = v1[0]*v2[1] - v1[1]*v2[0]
    return v3


def tr1p(X, Y):
    """
    Function to create a vector space
    """
    # Normalize X
    XM, XX = normv(X)  # pylint: disable=unused-variable

    # Calculate Z
    Z = prodv(X, Y)
    ZM, ZZ = normv(Z)  # pylint: disable=unused-variable

    # Calculate cross product of Z and X
    YY = prodv(ZZ, XX)
    XYZ = np.column_stack((XX, YY, ZZ))

    return XYZ


# Function to calculate and set a UB matrix
def newUB(  # pylint: disable=too-many-positional-arguments
          instr, sample, rfl, offsets, disps, dials, refine_type):
    """
    Function to calculate UB matrix from two orienting reflections
    args:
        instr   - instrument that this is run on
        sample  - sample that is being tested
        rfl     - list of reflections that have been measured
        offsets - motor offsets for the reflections
        dials   - rotation of the UB matrix. Only used in the optimization.
    """
    r1_temp = rfl.get_reflection(instr.orienting_reflections[0])
    r2_temp = rfl.get_reflection(instr.orienting_reflections[1])
    r11 = (r1_temp[0])  # hkl of reflection 1
    r21 = (r2_temp[0])  # hkl of reflection 2
    r12 = tuple(
        r1_temp[1][i] - offsets[i] +
        displacements(refine_type, r1_temp[1][i]-offsets[i], disps, i)
        for i in range(len(offsets))
    )  # angles of reflection 1
    r22 = tuple(
        r2_temp[1][i] - offsets[i] +
        displacements(refine_type, r2_temp[1][i]-offsets[i], disps, i)
        for i in range(len(offsets))
    )  # angles of reflection 2

    B = genB(sample.getCell())  # B matrix
    if not B.any():
        return None
    h1 = B.dot(r11)  # hkl of reflection 1 in reciprocal space
    h2 = B.dot(r21)  # hkl of reflection 2 in reciprocal space

    # HT = matFromTwoVectors(h1, h2) TODO this isn't used?

    if refine_type == "NB":
        u1 = UNBVectorFromAngles(r12)
        u2 = UNBVectorFromAngles(r22)
        u1, u2 = vecori(u1, u2, dials)
        TR1PC = tr1p(h1, h2)
        TTR1PC = TR1PC.T
        TR1PO = tr1p(u1, u2)
        U = np.dot(TR1PO, TTR1PC)
        sample.ubmatrix = list(np.dot(U, B).flatten())
    elif refine_type == "Euler":
        u1 = UVectorFromAngles(instr, h1, r12)
        u2 = UVectorFromAngles(instr, h2, r22)
        u1, u2 = vecori(u1, u2, dials)
        TR1PC = tr1p(h1, h2)
        TRIPO = tr1p(u1, u2)
        TR1PCT = np.linalg.inv(TR1PC)
        U = np.dot(TRIPO, TR1PCT)
        sample.ubmatrix = list(np.dot(U, B).flatten())
    elif refine_type == "Kappa":
        u1 = UKVectorFromAngles(r12)
        u2 = UKVectorFromAngles(r22)


def displacements(refine_type, angle, disps, index):
    DEG2RAD = np.pi/180

    disp = 0
    if refine_type == "NB":

        D = session.getDevice('detdist').target

        if index == 2:
            disp += np.arcsin(np.sin(angle * DEG2RAD) * disps[2] / D) / DEG2RAD
        if index == 1:
            disp += np.arcsin(
                        np.sin(angle * DEG2RAD +
                               np.arctan2(disps[0], disps[1])) *
                        np.sqrt(disps[1] ** 2 + disps[0] ** 2) / D
                    ) / DEG2RAD
    return disp


def slect(val1, val2, ref):
    def normalize(val):
        return (val + np.pi) % (2*np.pi) - np.pi

    def diff(val1, ref):
        return abs(normalize(val1)-normalize(ref))

    diff1 = diff(val1, ref)
    diff2 = diff(val2, ref)

    if diff1 < diff2:
        return val1
    return val2


def treq(A, B, C):
    """
    solves the equation A*cos(X)+B*sin(X) = C
    """
    eta = np.arctan2(B, A)
    bss = np.abs(A**2+B**2-C**2)
    if bss < 10**(-5):
        bss = 0
    bs = np.sqrt(bss)
    gam = np.arctan2(bs, C)
    return eta+gam, eta-gam


# Calculation of euler angles if not bisecting.
def calc_euler_angles(sample, instr, hkl, obs, offsets):
    calc = np.zeros(4)

    UB = np.reshape(sample.ubmatrix, (3, 3))
    h01 = UB @ hkl
    hkl, h02 = normv(h01)

    if hkl < 0.000001:
        session.log.error("HKL is too small for calculation")
        raise TypeError()

    l = instr.wavelength  # noqa: E741
    sintheta = hkl * l / 2.0
    if abs(sintheta) > 1.0:
        session.log.error("Calculated Sin(theta) > 1")
        raise TypeError()

    tt = np.arcsin(sintheta)

    cor_obs = np.zeros(4)
    sig = np.sign(obs[0])
    for i in range(3):
        cor_obs[i] = sig * (obs[i] - offsets[i])

    if sig == -1:
        cor_obs[3] = obs[3] - np.sign(obs[3]) * 180
    else:
        cor_obs[3] = obs[3]

    stt1 = 2.0 * tt
    stt2 = -2.0 * tt
    calc[0] = slect(stt1, stt2, cor_obs[0]*np.pi/180)

    cp = np.cos(cor_obs[3]*np.pi/180)
    sp = np.sin(cor_obs[3]*np.pi/180)
    ph = np.array([[cp, sp, 0.0], [-sp, cp, 0.0], [0.0, 0.0, 1.0]])

    h03 = ph @ h02
    chi = np.arctan2(h03[2], h03[0])

    chi1 = chi
    chi2 = chi + np.pi
    calc[2] = slect(chi1, chi2, cor_obs[2]*np.pi/180)

    chi = calc[2]
    cc = np.cos(chi)
    sc = np.sin(chi)
    ch = np.array([[cc, 0.0, sc], [0.0, 1.0, 0.0], [-sc, 0.0, cc]])

    h04 = ch @ h03
    om1, om2 = treq(-h04[1], h04[0], sintheta)
    calc[1] = slect(om1, om2, cor_obs[1]*np.pi/180)

    for i in range(3):
        calc[i] = sig * calc[i] + offsets[i]*np.pi/180
    calc[3] = obs[3]*np.pi/180

    psiy = -np.sin(cor_obs[1]*np.pi/180 - tt) * np.sin(cor_obs[2]*np.pi/180)
    psix = np.cos(cor_obs[2]*np.pi/180)
    psi = np.arctan2(psiy, psix)

    return calc*180/np.pi, psi


# Residual function for optimization. Calculates positions of reflections
# and finds the difference between the observed values and calculated
# values.
def residuals(  # pylint: disable=too-many-positional-arguments
        param, sample, instr, limits, rfl, hkls, obs, refine_type, verbose):
    """
    Function that calculates the total absolute difference between
    calculated and observed reflections.
    args;
        param   - parameters that can be varied
                  set up to be [cell, motor offset, dials]
        instr   - instrument that this is run on
        sample  - sample that is being tested
        limits  - limits to make sure that coupled values are coupled
        rfl     - list of reflections that have been measured
        hkl     - hkl reflections to compare to
        obs     - observed angles to compare to
        refine_type - which refinement NB, Euler, Kappa
    """
    # If there are coupled parameters, this will set them to be the same value
    # it is coupled to.
    for i, lim in enumerate(limits):
        if lim > 1:
            con = lim-2
            param[i] = param[con]

    # Set cell paramters to calculate UB matrix correctly
    sample.a = param[0]
    sample.b = param[1]
    sample.c = param[2]
    sample.alpha = param[3]
    sample.beta = param[4]
    sample.gamma = param[5]

    # Split up offsets and dials
    offsets = np.array(param[6:len(param)-6])
    disps = param[-6:-3]
    dials = param[-3:]

    # Calculate new UB matrix
    newUB(instr, sample, rfl, offsets, disps, dials, refine_type)

    # Lists to fill up with data. Calc is not used at the moment
    # but can be used as a debugging tool to compare to fortran rafin
    calc = []
    diff = []

    # Loop through reflections
    for i, hkl in enumerate(hkls):
        # Calculate positions of angles
        if refine_type == "NB":
            poslist = np.array(instr._extractPos(instr._calcPos(hkl)))
        if refine_type == "Euler":
            poslist, psi = calc_euler_angles(  # noqa: E501 pylint: disable=unused-variable
                sample,
                instr,
                hkl,
                obs[i],
                offsets)
        diff_temp = []
        calc_temp = []
        for j, ang in enumerate(poslist):
            if refine_type == "NB":
                a = float(ang[1]) + offsets[j]
                a += displacements(refine_type, a, disps, j)
                if a > 180:
                    calc_temp.append(a-360)
                elif a < -180:
                    calc_temp.append(a+360)
                else:
                    calc_temp.append(a)
            if refine_type == "Euler":
                a = float(ang)
                a += displacements(refine_type, a, disps, j)
                calc_temp.append(a)

            diff_temp.append((obs[i, j]-a + 180) % 360 - 180)

        diff.append(diff_temp)
        calc.append(calc_temp)

    # Return cost function
    calc = np.array(calc)
    diff = np.array(diff)

    if verbose == 1:
        session.log.info('------------------------------------------------')
        motors = instr.get_motors()

        session.log.info(
            ' H   K   L   {:^27}  {:^29}  {:^29}'.format(motors[0].name,
                                                         motors[1].name,
                                                         motors[2].name))

        session.log.info(  # pylint: disable=logging-not-lazy
            '        ' +
            '  {:^8} {:^8} {:^9}'.format('obs', 'calc', 'diff') +
            '  {:^9} {:^9} {:^9}'.format('obs', 'calc', 'diff') +
            '  {:^9} {:^9} {:^9}'.format('obs', 'calc', 'diff'))

        for i, hkl in enumerate(hkls):
            session.log.info(
                '{:>2d}  {:>2d}  {:>2d}  '.format(int(hkl[0]),
                                                  int(hkl[1]),
                                                  int(hkl[2])) +
                '{:>8.4f} {:>8.4f} {:>9f}  '.format(obs[i, 0],
                                                    calc[i, 0],
                                                    diff[i, 0]) +
                '{:>9.4f} {:>9.4f} {:>9f}  '.format(obs[i, 1],
                                                    calc[i, 1],
                                                    diff[i, 1]) +
                '{:>9.4f} {:>9.4f} {:>9f}'.format(obs[i, 2],
                                                  calc[i, 2],
                                                  diff[i, 2]))

        session.log.info('------------------------------------------------')

        session.log.info(
            '          ' +
            '  {:^8} {:^8} {:>9f}'.format('',
                                          'Mean dev',
                                          np.average(np.abs(diff[:, 0]))) +
            '  {:^8} {:^9} {:>9f}'.format('',
                                          'Mean dev',
                                          np.average(np.abs(diff[:, 1]))) +
            '  {:^8} {:^9} {:>9f}'.format('',
                                          'Mean dev',
                                          np.average(np.abs(diff[:, 2]))))

    return calc, diff


# Function to set the initial guess and bounds for the least squares method
def p0_bounds(limits, instr, sample):
    """
    Function to define the initial guess for the least squares method
    as well as the boundaries which the method has to keep the the parameters
    args;
        limits  - limits set by the user to define which variables should
                  change and which should not. List of binaries
        instr   - instrument that this is run on
        sample  - sample that is being tested
    """
    # The least-squares method requires the parameters to have some wiggle room
    # and a good approximation for 0 is 10^-10 :)
    eps = 1e-10

    # Get unit cell parameters
    cell = sample.getCell()
    cell_init = [cell.a, cell.b, cell.c, cell.alpha, cell.beta, cell.gamma]

    # Get amount of motors
    motors = instr.get_motors()
    init_offsets = [mot.offset for mot in motors]

    # Set initial sample displacement
    disp_array = [0, 0, 0]

    # Set initial dial rotations
    rotation_array = [0, 0, 0]

    # Collect them all
    parameters = cell_init + init_offsets + disp_array + rotation_array

    # Setting bounds for each parameter depending on limits input
    lower = []
    upper = []
    for i in range(len(parameters)):
        # Limits for unit cell lengths
        if i < len(cell_init)/2:
            if limits[i] != 0:
                lower.append(0)
                upper.append(np.inf)
            else:
                lower.append(parameters[i])
                upper.append(parameters[i]+eps)

        # Limits for unit cell angles
        elif i < len(cell_init):
            if limits[i] != 0:
                lower.append(0)
                upper.append(180)
            else:
                lower.append(parameters[i])
                upper.append(parameters[i]+eps)

        # Limits for motor offsets
        elif i < len(cell_init)+len(init_offsets):
            if limits[i] == 1:
                lower.append(-180)
                upper.append(180)
            else:
                lower.append(parameters[i])
                upper.append(parameters[i]+eps)

        # limits for sample displacement
        elif i < len(cell_init)+len(init_offsets):
            if limits[i] == 1:
                lower.append(-20)
                upper.append(20)
            else:
                lower.append(parameters[i])
                upper.append(parameters[i]+eps)
        # Limits for dials
        else:
            lower.append(-180)
            upper.append(180)

    return parameters, (lower, upper)


def SID(X):
    """
    Safe inverse and determinant of matrix
    """
    n = X.shape[1] - 1
    AMAT = X[:, :n]
    VVEC = X[:, n]
    AMAT_inv = np.linalg.inv(AMAT)
    D = np.linalg.det(AMAT)
    solution = np.dot(AMAT_inv, VVEC)
    A_inv_aug = np.column_stack((AMAT_inv, solution))
    return A_inv_aug, D


def refinement(  # pylint: disable=too-many-positional-arguments
        func, p0, sample, instr, limits, rfl, hkls, obs, bounds, refine_type,
        max_nfev=5, eps=0.001, verbose=0):
    """
    Function to refine the parameters. Algorithm is the same as that of Rafin
    Should nearly always converge
    args;
        verbose     - (0/1/2) How much should the function print
        replace     - (0/1) Should the function replace the cell paramters
                            and UB matrix
        max_nfev    - Amount of cycles (5)
        eps         - Magnitude of finit increase (0.001)
    """
    # Radians to Degrees
    RAD2DEG = 180/np.pi
    verb = int(verbose > 1)
    # Find which parameters to change
    p_idxs = np.where(np.array(limits) == 1)[0]

    # Matrix sizes
    NP = len(p_idxs)
    NOL = len(hkls)

    # Print information from initial cycle
    session.log.info('')
    session.log.info('')
    session.log.info('Cycle Init')
    calc0, c0 = residuals(
        p0,
        sample,
        instr,
        limits,
        rfl,
        hkls,
        obs,
        refine_type,
        1)

    # Cost and deviation arrays
    cost = []
    dev = []
    for i in range(max_nfev):
        if verbose > 0:
            session.log.info('')
            session.log.info('')
            session.log.info('Cycle %d', i)

        # Calculated reflections and cost for initial paramters
        calc0, c0 = residuals(
            p0,
            sample,
            instr,
            limits,
            rfl,
            hkls,
            obs,
            refine_type,
            verb)

        if refine_type == "Euler":
            c0 = c0[:, :3]

        cost.append(sum(((c0/RAD2DEG).flatten())**2))
        dev.append(np.sqrt(cost[i]/(3*NOL)))
        DYC = np.zeros((NP, NOL, 3))
        VVEC = np.zeros((NP, 1))
        AMAT = np.zeros((NP, NP))
        DELP = np.zeros(NP)

        # Slightly vary parameters and calculate differences
        for j in range(NP):
            p0[p_idxs[j]] += eps

            calc, c = residuals(  # pylint: disable=unused-variable
                p0,
                sample,
                instr,
                limits,
                rfl,
                hkls,
                calc0,
                refine_type,
                0)

            if refine_type == "Euler":
                c = c[:, :3]
            p0[p_idxs[j]] -= eps
            DYC[j] = -c/eps/RAD2DEG

        # Calculate two structures:
        # VVEC - The gradient of cost multiplied by the cost for each change
        # AMAT - Matrix of how each parameter change affects each other
        #
        # The specifics here is to find a pseudo-gradient for the system and
        # then minimize with respect to it by finding the inverse and solving
        # the system
        for I in range(NP):  # noqa: E741
            VVEC[I] = np.sum(np.multiply(DYC[I], c0/RAD2DEG))
            for J in range(NP):
                AMAT[I, J] = np.sum(np.multiply(DYC[I], DYC[J]))
        X = np.hstack((AMAT, VVEC))

        # Find the inverse and determinant
        X, D = SID(X)
        if verbose > 0:
            session.log.info(
                "Sums: %5f, Std.Dev.: %5f, Deter.: %5e",
                cost[i],
                dev[i],
                D)
        PDELP = 0

        # DELP is the amount that each parameter should change by
        # PDELP is correlated to the variance in the parameter
        for I in range(NP):  # noqa: E741
            DELP[I] = X[I, -1]
            PDELP += DELP[I]*VVEC[I]
            p0[p_idxs[I]] += X[I, -1]

        # Print change in parameter
        if verbose > 0:
            pr = ' '.join(['{:8.5f}'.format(i) for i in DELP])
            session.log.info("Change in P: %s", pr)
            pr = ' '.join(['{:8.5f}'.format(i) for i in np.array(p0)[p_idxs]])
            session.log.info("New Paras: %s", pr)

        # Convergence possibility either cost is not lowering or the parameters
        # aren't
        if i > 2:
            if (cost[i-1]/cost[i-1] - 1 <= 10**(-6)):
                session.log.info("Converged with respect to residuals")
                break
        if any(np.abs(DELP) < 10**(-6)):
            session.log.info("Converged with respect to parameters")
            break

    # Log Final cycle, costs and return the new values, vairances and
    # correlations
    session.log.info('')
    session.log.info('')
    session.log.info('Cycle Final')

    calc0, c0 = residuals(
        p0,
        sample,
        instr,
        limits,
        rfl,
        hkls,
        obs,
        refine_type,
        1)

    cost.append(sum(c0.flatten()**2))
    var = np.zeros(NP)
    cor = np.zeros((NP, NP))
    FT = 3*NOL-NP
    for i in range(NP):
        var[i] = AMAT[i, i]*(cost[-1]-PDELP)/FT
        for j in range(NP):
            cor[i, j] = AMAT[i, j]/sqrt(AMAT[i, i]*AMAT[j, j])
    return cost, p0, np.sqrt(var), cor


@usercommand
@helparglist('a, [b, ...], ..., orienting_refs=None, ignore_refs=None, ' +
             'verbose=1, replace=False, min_angle=45, ncyc=5, eps=0.001')
def RefineUB(*args, orienting_refs=None, ignore_refs=None, verbose=1,
             replace=False, min_angle=45, ncyc=5, eps=0.001):
    """Estimates an initial Uab matrix from a list of reflections and
    determines search boundaries for refinement of the matrix.

    Function to define the initial guess for the least squares method as well
    as the boundaries within which the method has to keep the parameters. When
    running, input can be a list of any type containing the parameters that
    should be varied. If variables should be dependant on other, then the shape
    of the list should be as follows ``(a,[b,c])``, where ``b`` and ``c`` now
    are forced to be the same value as ``a``.

    The method is inspired by the paper

    "Angle calculations for 3- and 4-circle X-ray and neutron diffractometers"
    DOI: https://doi.org/10.1107/S0365110X67000970

    in addition to an old Fortran program Refin.

    Supported parameters are the following:

    * ``*args``: Which parameters should be varied ``(a, b, c, etc.)``
                 Will give warning if input is not a parameter to vary
                 Possible parameters: ``a``, ``b``, ``c``, ``alpha``,
                 ``beta``, ``gamma``, motor names, (``stt``, ``som``, etc.)
    * ``orienting_refs``: If not ``None``, chooses the two orienting
                          reflections for the UB matrix
                          Still have to be further away than the ``min_angle``
    * ``ignore_refs``: Reflections to ignore
    * ``verbose``: ``(0/1/2)`` How much should the function print
    * ``replace``: ``(0/1)`` Should the function replace the cell parameters
                   and UB matrix
    * ``min_angle``: Minimum angle between orienting reflection ``(45)``
    * ``ncyc``: Amount of cycles ``(10)``
    * ``eps``: Magnitude of finit increase

    Examples::

        # once happy with the contents of RefList(), refined the orientation
        # matrix using for instance:

        RefineUB('a', ['b'], 'c', ncyc=10, verbose=2)

        # Here the lattice constants are refined but 'b' is constrained to be
        # equal to 'a'; 'ncyc' is the max number of refinement cycles and
        # verbose 2 gives maximal output.

        # You may also include motor offsets simply by adding their names,
        # e.g.:

        RefineUB('a', ['b'], 'c', 'stt', 'om', 'chi', verbose=2, ncyc=10)

        # If you want RefineUB to update the orientation matrix and all other
        # refined parameters (including motor offsets) in Nicos, add
        # replace=True, for instance:

        RefineUB('a', ['b'], 'c', 'stt', 'om', 'chi',
                 verbose=2, ncyc=10, replace=True)
    """

    if ignore_refs is None:
        ignore_refs = []

    # Get sample, instrument, reflection list and motors
    sample = session.experiment.sample
    instr = session.instrument
    rfl = sample.getRefList()
    motors = instr.get_motors()

    # Get instrument mode
    if isinstance(instr, SinqNB):
        refine_type = "NB"
    elif isinstance(instr, SinqEuler):
        refine_type = "Euler"
    # TODO changed from SinqKappa as it doesn't exist
    elif isinstance(instr, KappaSXTal):
        refine_type = "Kappa"
    else:
        session.log.warning(
            'Instrument mode not found (not NB, Euler or Kappa). ' +
            'Resorting to NB, but please fix')
        refine_type = "NB"

    # For normal beam, omega cannot be optimized. This is due to the fact that
    # a rotation in omega is arbitrary, and will cause no difference in the
    # calculated angles. It will however, completely mess up the inversion of
    # gradient matrix, causing a singular matrix after enough iterations.
    if ("om" in args) and (refine_type == "NB"):
        session.log.error(
            'It is not possible to optimize omega. ' +
            'Please pick another angle to optimize')
        raise TypeError()

    # Setting initial parameter guess, as well as which parameters can vary
    # using p0_bounds()
    names = ["a", "b", 'c', 'alpha', 'beta', 'gamma'] +\
            [mot.name for mot in motors] +\
            ['dx', 'dy', 'dz']
    limits = [0]*len(names)
    for i, arg in enumerate(args):
        if isinstance(arg, list):
            for j in arg:
                if j in names:
                    idx = names.index(j)
                    idx_base = names.index(args[i-1])
                    limits[idx] = 2+idx_base
                else:
                    # Will alert if a variable is set incorrectly
                    session.log.warning(
                        'Coupled Variable "%s" does not exist', j)
        else:
            if arg in names:
                idx = names.index(arg)
                limits[idx] = 1
            else:
                # Will alert if a variable is set incorrectly
                session.log.warning('Variable "%s" does not exist', arg)
    names += ["Rotation X", "Rotation Y", "Rotation Z"]
    limits += [1, 1, 1]
    p0, bounds = p0_bounds(limits, instr, sample)  # noqa:E501 pylint: disable=unused-variable
    p_init = p0.copy()

    # Print before
    session.log.info('*** PyRefin *** version 1.0, N. Amin 16-Aug-2024')
    session.log.info('-------------------- TITLE ---------------------')
    session.log.info(sample.name)
    session.log.info('------------------------------------------------')
    session.log.info('')
    session.log.info('Verbosity: \t\t\t %d', verbose)
    session.log.info('Replace: \t\t\t %d', replace)
    session.log.info('Min angle coupling: \t\t %d', 45)
    session.log.info('Max cycles: \t\t\t %d', 10)
    session.log.info('')
    session.log.info('Wavelength: \t\t\t %d', instr.wavelength)

    # Print which mode zebra is in
    session.log.info('')
    session.log.info('Will refine %s UB Matrix', refine_type)
    session.log.info('')

    # Print Parameters
    session.log.info('Cell Parameters:')
    for i in range(6):
        n = names[i]
        session.log.info('\t %s = %f \t varying = %f', n, p0[i], limits[i])
    session.log.info('Motor offsets:')
    for mot in motors:
        n = mot.name

        session.log.info(
            '\t %s = %f \t\t varying = %f',
            n,
            p0[names.index(n)],
            limits[names.index(n)])

    session.log.info('Sample Displacement:')
    for i in range(6 + len(motors), 6 + len(motors) + 3):
        n = names[i]
        session.log.info(
            '\t %s = %f \t\t varying = %f',
            n,
            p0[names.index(n)],
            limits[names.index(n)])

    session.log.info('')
    session.log.info('')

    # Get information out of reflection list
    hkls = []
    obs = []
    for i, r in enumerate(rfl.generate(0)):
        if i in ignore_refs:
            continue
        hkl_temp = []
        for q in r[0]:
            hkl_temp.append(q)
        hkls.append(hkl_temp)
        obs_temp = []
        for i, a in enumerate(r[1]):
            obs_temp.append(a)
        obs.append(obs_temp)
    hkls = np.array(hkls)
    obs = np.array(obs)

    # Print reflections
    session.log.info('')
    session.log.info('Reflections:')
    if refine_type == "Euler":

        session.log.info(  # pylint: disable=logging-not-lazy
            ' H   K   L  ' +
            '{:^9}  {:^9}  {:^9}  {:^9}'.format("2Theta",
                                                "Omega",
                                                "Chi",
                                                "Phi"))

        for i in range(len(hkls)):
            session.log.info(  # pylint: disable=logging-not-lazy
                '{:>2d}  {:>2d}  {:>2d}  '.format(int(hkls[i, 0]),
                                                  int(hkls[i, 1]),
                                                  int(hkls[i, 2])) +
                '{:>9.4f}  {:>9.4f}  {:>9.4f} {:>9.4f}'.format(obs[i, 0],
                                                               obs[i, 1],
                                                               obs[i, 2],
                                                               obs[i, 3]))

    elif refine_type == "NB":

        session.log.info(  # pylint: disable=logging-not-lazy
            ' H   K   L  ' +
            '{:^9}  {:^9}  {:^9}'.format("2Theta",
                                         "Omega",
                                         "Chi"))

        for i in range(len(hkls)):
            session.log.info(  # pylint: disable=logging-not-lazy
                '{:>2d}  {:>2d}  {:>2d}  '.format(int(hkls[i, 0]),
                                                  int(hkls[i, 1]),
                                                  int(hkls[i, 2])) +
                '{:>9.4f}  {:>9.4f}  {:>9.4f}'.format(obs[i, 0],
                                                      obs[i, 1],
                                                      obs[i, 2]))

    # Find orienting reflections to look at, calculate UB from there
    # reflections
    if orienting_refs is not None:
        if len(orienting_refs) == 2:
            instr.orienting_reflections = couple(
                hkls,
                obs,
                instr,
                sample,
                min_angle=min_angle,
                refs=orienting_refs)

            ListRef()

            newUB(
                instr,
                sample,
                rfl,
                [0] * len(motors),
                [0, 0, 0],
                [0, 0, 0],
                refine_type)
            init_UB = sample.ubmatrix

        else:
            session.log.info(
                'Not two orienting reflections found, finding own')
            instr.orienting_reflections = couple(
                hkls,
                obs,
                instr,
                sample,
                min_angle=min_angle)
            newUB(
                instr,
                sample,
                rfl,
                [0] * len(motors),
                [0, 0, 0],
                [0, 0, 0],
                refine_type)
            init_UB = sample.ubmatrix
    else:
        instr.orienting_reflections = couple(
            hkls,
            obs,
            instr,
            sample,
            min_angle=min_angle)
        newUB(
            instr,
            sample,
            rfl,
            [0] * len(motors),
            [0, 0, 0],
            [0, 0, 0],
            refine_type)
        init_UB = sample.ubmatrix

    # Rafin optimization model, which uses the residuals function to calculate
    # the optimal paramters, with initial guess p0. Uses inverse matrix
    # calculations and small steps to figure out which direction to move the
    # parameters in
    session.log.info('')
    cost, p1, perr, cor = refinement(  # pylint: disable=unused-variable
        residuals,
        p0,
        sample,
        instr,
        limits,
        rfl,
        hkls,
        obs,
        limits,
        refine_type,
        ncyc,
        eps,
        verbose)

    # Print results
    session.log.info('Parameter Final Values and Correlations:')
    num = 0
    for i in range(len(p0)):
        if limits[i] != 1:
            continue
        n = names[i]
        pr = ' '.join(['{:7.4f}'.format(i) for i in cor[num]])
        session.log.info(  # pylint: disable=logging-not-lazy
            '\t {:>10} = {:>6.4f} (± {:>6.4f})        {}'.format(n,
                                                                 p1[i],
                                                                 perr[num],
                                                                 pr))
        num += 1
    session.log.info('')
    session.log.info("Refined UB matrix.")
    for i in range(3):
        session.log.info(  # pylint: disable=logging-not-lazy
            ' {:>11.8f}  {:>11.8f}  {:>11.8f}'.format(sample.ubmatrix[i*3],
                                                      sample.ubmatrix[i*3+1],
                                                      sample.ubmatrix[i*3+2]))
        session.log.info('')

    # Replace parametes (or don't)
    if not replace:
        session.log.info('Not Replacing old values')
        sample.ubmatrix = init_UB
        sample.a = p_init[0]
        sample.b = p_init[1]
        sample.c = p_init[2]
        sample.alpha = p_init[3]
        sample.beta = p_init[4]
        sample.gamma = p_init[5]
    session.log.info("Done, Goodbye :)")
