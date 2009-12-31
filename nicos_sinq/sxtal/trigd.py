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


def Sign(d):
    """Returns sign of provided array"""

    return np.sign(d)


def Sind(d):
    """Returns sine in degrees of array d"""

    return np.sin(np.deg2rad(d))


def Tand(d):
    """Returns tangent in degrees of array d"""

    return np.tan(np.deg2rad(d))


def Cosd(d):
    """Returns cosine in degrees of array d"""

    return np.cos(np.deg2rad(d))


def Cotd(d):
    """Returns cotangent in degrees of array d"""

    return np.reciprocal(np.tan(np.deg2rad(d)))


def Atand(d):
    """Returns argus tangents in degrees of array d"""

    return np.rad2deg(np.arctan(d))


def Atand2(x, y):
    """Returns argus tangents 2 in degrees of array x,y"""

    return np.rad2deg(np.arctan2(x, y))


def Acosd(d):
    """Returns argus cosine in degrees of array d"""

    return np.rad2deg(np.arccos(d))


def Asind(d):
    """Returns argus sine in degrees of array d"""

    return np.rad2deg(np.arcsin(d))


def rtan(y, x):
    """a quadrant dependent tangents in radians!"""
    if np.all(np.isclose([x, y], [0.0, 0.0])):
        return 0.0
    if np.isclose(x, 0.0):
        if y < 0.0:
            return -np.pi/2.0
        else:
            return np.pi/2.0
    if np.abs(y) < np.abs(x):
        val = np.arctan(np.abs(y/x))
        if x < 0.0:
            val = np.pi-val
        if y < 0.0:
            val = -val
        return val
    else:
        val = np.pi/2.0 - np.arctan(np.abs(x/y))
        if x < 0.0:
            val = np.pi - val
        if y < 0.0:
            val = -val
        return val


def Rtand(y, x):
    """a quadrant dependent tangents in degrees"""
    radians = rtan(y, x)
    return np.rad2deg(radians)


def angleBetween(v1, v2):
    # The np.sqrt(v.dot(v)) is the recommended way to
    # calculate the length of a vector
    v1len = np.sqrt(v1.dot(v1))
    v2len = np.sqrt(v2.dot(v2))
    angle = v1.dot(v2)/(v1len * v2len)
    v3 = np.cross(v1, v2)
    angles = np.sqrt(v3.dot(v3)) / (v1len * v2len)
    return rtan(angles, angle)
