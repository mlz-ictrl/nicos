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

from nicos_sinq.sxtal.trigd import Acosd, Cosd, Sind


def defaultValue(obj, value):
    """return object if not None else return value"""
    return value if obj is None else obj


def directToReciprocalLattice(directLattice):
    """Calculate reciprocal lattice from direct lattice"""

    reciprocal = Cell()
    alfa = directLattice.alpha
    beta = directLattice.beta
    gamma = directLattice.gamma

    cos_alfa = Cosd(alfa)
    cos_beta = Cosd(beta)
    cos_gamma = Cosd(gamma)

    sin_alfa = Sind(alfa)
    sin_beta = Sind(beta)
    sin_gamma = Sind(gamma)

    reciprocal.alpha = Acosd((cos_beta * cos_gamma - cos_alfa) /
                             sin_beta / sin_gamma)
    reciprocal.beta = Acosd((cos_alfa * cos_gamma - cos_beta) /
                            sin_alfa / sin_gamma)
    reciprocal.gamma = Acosd((cos_alfa * cos_beta - cos_gamma) /
                             sin_alfa / sin_beta)

    ad = directLattice.a
    bd = directLattice.b
    cd = directLattice.c

    arg = 1 + 2 * cos_alfa * cos_beta * cos_gamma - cos_alfa * cos_alfa -\
        cos_beta * cos_beta - cos_gamma * cos_gamma
    if (arg < 0.0):
        raise AttributeError('Reciprocal lattice has negative volume!')
    vol = ad * bd * cd * np.sqrt(arg)/(2 * np.pi)
    reciprocal.a = bd * cd * sin_alfa / vol
    reciprocal.b = ad * cd * sin_beta / vol
    reciprocal.c = bd * ad * sin_gamma / vol

    return reciprocal


reciprocalToDirectLattice = directToReciprocalLattice
reciprocalToDirectLattice.__doc__ = \
    "Calculate direct lattice from reciprocal lattice"


def calculateBMatrix(direct):
    """Calculate B matrix from lattice"""

    reciprocal = direct.directToReciprocalLattice()
    B = np.zeros((3, 3))
    B[0, 0] = reciprocal.a
    B[0, 1] = reciprocal.b * Cosd(reciprocal.gamma)
    B[0, 2] = reciprocal.c * Cosd(reciprocal.beta)
    #    middle row
    B[1, 1] = reciprocal.b * Sind(reciprocal.gamma)
    B[1, 2] = -reciprocal.c * Sind(reciprocal.beta) * Cosd(direct.alpha)

    #    bottom row
    B[2, 2] = 2 * np.pi / direct.c

    return B


def cellFromUB(UB):
    GINV = np.einsum('ji,jk->ik', UB, UB)
    G = np.linalg.inv(GINV)*(2*np.pi)**2
    a = np.sqrt(G[0][0])
    b = np.sqrt(G[1][1])
    c = np.sqrt(G[2][2])
    alpha = Acosd(G[1][2] / (b * c))

    beta = Acosd(G[2][0] / (a * c))
    gamma = Acosd(G[0][1] / (a * b))  # Change c -> b
    return Cell(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)


class Cell():
    """Cell object to hold information about crystal cell structures"""

    def __init__(self, a=None, b=None, c=None,
                 alpha=None, beta=None, gamma=None,
                 UB=None):
        """
        There are two ways to initialize the cell:
        a) a UB is given as a keyword argument. In that case the cell is
           derived from the UB
        b) The actual lattice constants are given. Values NOT specified are
           defaulted to 1.0 (lattice dimensions) or 90. (angles)
        """
        if UB is None:
            self.a = defaultValue(a, 1.0)
            self.b = defaultValue(b, self.a)
            self.c = defaultValue(c, defaultValue(b, self.a))

            self.alpha = defaultValue(alpha, 90.0)
            self.beta = defaultValue(beta, 90.0)
            self.gamma = defaultValue(gamma, 90.0)
        else:
            _cell = cellFromUB(UB)
            self.a, self.b, self.c, self.alpha, self.beta, self.gamma = \
                _cell.a, _cell.b, _cell.c, _cell.alpha, _cell.beta, _cell.gamma

    def __str__(self):
        returnString = 'cell.Cell('
        keyString = []
        for key in ['a', 'b', 'c', 'alpha', 'beta', 'gamma']:
            keyString.append('{:}={:.1f}'.format(key, getattr(self, key)))
        returnString += ', '.join(keyString)+')'
        return returnString

    def __eq__(self, other):
        keys = ['a', 'b', 'c', 'alpha', 'beta', 'gamma']
        selfValues = [getattr(self, key) for key in keys]
        otherValues = [getattr(other, key) for key in keys]
        return np.all(np.isclose(selfValues, otherValues))

    directToReciprocalLattice = directToReciprocalLattice
    reciprocalToDirectLattice = reciprocalToDirectLattice
    calculateBMatrix = calculateBMatrix
