#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Module with Cryopad specific calculations for POLI.

NOTE: All angles are taken and returned in degrees.

From IgorPro routines in Cryopad.c.
"""

from nicos.core import ComputationError

from numpy import sin, cos, radians, degrees, arcsin, arccos, arctan2, \
    sqrt, isnan

# Polarization directions, mapped to (theta, phi) polar angles.
DIRECTIONS = {
    '+x': (90, 0),
    '-x': (90, 180),
    '+y': (90, 90),
    '-y': (90, -90),
    '+z': (0, 0),
    '-z': (180, 0),
}


def to_range(x):
    """Move x within the angular range -180...180 deg."""
    while x < -180:
        x += 360
    while x > 180:
        x -= 360
    return x


def currents_to_angles(coeff, i1, i2, lam_in, lam_out, gamma):
    """Return precession angles (chi1, chi2) for the actual currents (i1, i2)
    and the given in/out wavelengths and scattering angle.
    """
    if coeff[4] != 0 or coeff[5] != 0:
        gamma = 2 * radians(gamma)
        coeff2 = coeff[2] + coeff[4] * gamma**2 + coeff[5] * gamma**4
    else:
        coeff2 = 0
    chi1 = lam_in * (coeff[0] * i1 + coeff[1] * i2)
    chi2 = lam_out * (coeff2 * i1 + coeff[3] * i2)
    return to_range(chi1), to_range(chi2)


def angles_to_currents(coeff, chi1, chi2, lam_in, lam_out, gamma):
    """Return currents (i1, i2) for the precession angles (chi1, chi2)
    and the given in/out wavelengths and scattering angle.
    """
    if coeff[4] != 0 or coeff[5] != 0:
        # for Cryopad-II
        gamma = 2 * radians(gamma)
        coeff2 = coeff[2] + coeff[4] * gamma**2 + coeff[5] * gamma**4
    else:
        coeff2 = 0
    det = (lam_in * coeff[0] * lam_out * coeff[3] -
           lam_out * coeff2 * lam_in * coeff[1])
    if det == 0:
        raise ComputationError('lambda matrix determinant is null')
    i1 = (lam_out * coeff[3] * chi1 - lam_in * coeff[1] * chi2) / det
    i2 = (lam_in * coeff[0] * chi2 - lam_out * coeff2 * chi1) / det
    return i1, i2


def pol_in_from_angles(sense, theta_in, chi_in, lam_in, lam_out, gamma):
    """Return the orthogonal components of the incident polarization from the
    incident nutator and precession angles (theta_in, chi_in), and the
    scattering angle gamma.
    """
    theta_in, chi_in, gamma = radians(theta_in), radians(chi_in), radians(gamma)
    psi = _get_psi(sense, lam_in, lam_out, gamma)
    x = (-sense * cos(theta_in) * sin(chi_in) * sin(psi) +
         sense * cos(psi) * sin(theta_in))
    y = (-sense * cos(theta_in) * sin(chi_in) * cos(psi) -
         sense * sin(psi) * sin(theta_in))
    z = cos(theta_in) * cos(chi_in)
    return x, y, z


def pol_out_from_angles(sense, theta_out, chi_out, lam_in, lam_out, gamma):
    """Return the orthogonal components of the outgoing polarization from the
    outgoing nutator and precession angles (theta_out, chi_out), the sample
    angle psi and the scattering angle gamma.
    """
    theta_out, chi_out, gamma = radians(theta_out), radians(chi_out), radians(gamma)
    psi = _get_psi(sense, lam_in, lam_out, gamma)
    x = (-sense * cos(theta_out) * sin(chi_out) * sin(gamma - psi) +
         sense * cos(gamma - psi) * sin(theta_out))
    y = (sense * cos(theta_out) * sin(chi_out) * cos(gamma - psi) +
         sense * sin(gamma - psi) * sin(theta_out))
    z = cos(theta_out) * cos(chi_out)
    return x, y, z


def polar_angles_from_xyz(x, y, z):
    """Return polar angles from orthogonal components."""
    theta = degrees(arccos(z / sqrt(x*x + y*y + z*z)))
    # if theta around 0 or 180, phi does not matter,
    # but we need it to be zero to match the presets for +/-z
    if abs(theta) < 0.5 or abs(theta - 180) < 0.5:
        phi = 0
    else:
        phi = degrees(arctan2(y, x))
    return to_range(theta), to_range(phi)


def _get_psi(sense, lam_in, lam_out, gamma):
    # internal: calculate sample angle
    if lam_in == lam_out:
        return gamma/2.0
    ki, kf = 1./lam_in, 1./lam_out
    q2 = ki**2 + kf**2 - 2*ki*kf*cos(gamma)
    psi = sense * arcsin(0.5*(ki**2 - kf**2 + q2) / (ki * sqrt(q2)))
    return 0. if isnan(psi) else psi


def cryopad_in(sense, lam_in, lam_out, gamma, theta, phi):
    """Return the incident nutator and precession angle for given wavelengths,
    scattering and spherical polarization angles.
    """
    gamma, theta, phi = radians(gamma), radians(theta), radians(phi)
    psi = _get_psi(sense, lam_in, lam_out, gamma)

    theta_in = sense * arcsin(cos(psi + phi) * sin(theta))

    y = sin(psi + phi) * sin(theta)
    x = cos(theta)
    if abs(y) < 0.0001 and abs(x) < 0.0001:
        return 0
    chi_in = -sense * arctan2(y, x)
    return to_range(degrees(theta_in)), to_range(degrees(chi_in))


def cryopad_out(sense, lam_in, lam_out, gamma, theta, phi):
    """Return the outgoing nutator and precession angle for given wavelengths,
    scattering and spherical polarization angles.
    """
    gamma, theta, phi = radians(gamma), radians(theta), radians(phi)
    psi = _get_psi(sense, lam_in, lam_out, gamma)

    theta_out = sense * arcsin(cos(gamma - psi - phi) * sin(theta))

    y = sin(gamma - psi - phi) * sin(theta)
    x = cos(theta)
    if abs(y) < 0.0001 and abs(x) < 0.0001:
        return 0
    chi_out = -sense * arctan2(y, x)
    return to_range(degrees(theta_out)), to_range(degrees(chi_out))


def optimize_angles(theta, chi):
    """Change setpoints so that precession currents are minimized."""
    if chi > 90.0:
        theta = 180. - theta
        chi = chi - 180.
    elif chi < -90:
        theta = 180. - theta
        chi = chi + 180.
    return theta, chi


def curved_meissner_correction(theta_out):
    """Return the correction (angular offset) for aberration in outgoing
    nutator due to the curved Meissner screen.
    """
    return -0.6 * sin(2 * radians(theta_out))
