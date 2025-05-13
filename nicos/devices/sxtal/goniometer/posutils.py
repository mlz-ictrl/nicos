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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
Utility functions for position module
"""

import numpy as np


def sign(x):
    return np.copysign(1, x)


def matvec(m, v):
    """Multiply a matrix with a 3D vector, or any array of vectors"""
    v = np.array(v, copy=0)
    ax = list(range(1, len(v.shape))) + [0]
    return np.transpose(np.inner(m, v), axes=ax)


def vectorangle(v1, v2):
    """Determine the angle between two 3D vectors (or arrays of vectors)."""
    c = np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2)
    return np.arccos(np.clip(c, -1, 1))


def directionangle(v1, v2):
    """Calculate the angle between two directions (0-90 degrees)"""
    d = vectorangle(v1, v2)
    if d < np.pi / 2:
        return d
    else:
        return np.pi - d


def Xrot(a, typecode='d'):
    """Construct a rotation matrix rotating 'a' around the X-axis"""
    sa = np.sin(a)
    ca = np.cos(a)
    return np.array([[1.0, 0, 0], [0, ca, sa], [0, -sa, ca]], typecode)


def Yrot(a, typecode='d'):
    """Construct a rotation matrix rotating 'a' around the Y-axis"""
    sa = np.sin(a)
    ca = np.cos(a)
    return np.array([[ca, 0, -sa], [0, 1.0, 0], [sa, 0, ca]], typecode)


def Zrot(a, typecode='d'):
    """Construct a rotation matrix rotating 'a' around the Z-axis"""
    sa = np.sin(a)
    ca = np.cos(a)
    return np.array([[ca, sa, 0], [-sa, ca, 0], [0, 0, 1.0]], typecode)


def Vrot(v, a, typecode='d'):
    """
     Create a rotation matrix corresponding to the rotation around a general
     axis by a specified angle.

     R = dd^T + cos(a) (I - dd^T) + sin(a) skew(d)

     Parameters:

         angle : float a
         direction : array d
     """
    v /= np.linalg.norm(v)
    eye = np.eye(3, dtype=np.float64)
    ddt = np.outer(v, v)
    skew = np.array([[0, v[2], -v[1]],
                     [-v[2], 0, v[0]],
                     [v[1], -v[0], 0]], dtype=np.float64)

    mtx = ddt + np.cos(a) * (eye - ddt) + np.sin(a) * skew
    return mtx


def samematrix(m1, m2, crit=0.05):
    """Compare matrices, return 1 if they are approximately identical."""
    return np.maximum.reduce(np.absolute(np.ravel(m1 - m2))) < crit


def integermatrix(m, crit=0.1):
    """Return 1 if m is approximately consisting of integer coefficients."""
    v = np.ravel(m)
    v = np.absolute(v) % 1.0
    for i in range(len(v)):
        if v[i] > 0.5:
            v[i] = v[i] - 1.0
    x = np.maximum.reduce(np.absolute(v))
    return x < crit


def normalangle(val):
    while val > np.deg2rad(180):
        val -= np.deg2rad(360)
    while val < -np.deg2rad(180):
        val += np.deg2rad(360)
    return val


def absdif(p0, p1):
    """
    Calculate "Rotational" difference between two positions in 'radians'.
    """
    p0 = p0.asE()
    p1 = p1.asE()

    rotmat = np.dot(p0.asG().matrix, np.linalg.inv(p1.asG().matrix))
    trace = np.trace(rotmat)
    cosang = 0.5 * trace - 0.5
    if cosang >= 1.0:
        ang = 0.0
    elif cosang <= -1.0:
        ang = np.pi
    else:
        ang = np.arccos(0.5 * trace - 0.5)
    return np.sqrt((p0.theta - p1.theta) ** 2 + ang ** 2)


def equal(p0, p1, crit=1.e-4):
    """Are the two positions identical?
    """
    return absdif(p0, p1) < crit
