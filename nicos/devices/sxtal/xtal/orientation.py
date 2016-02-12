#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2016 by the NICOS contributors (see AUTHORS)
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
#   pedersen
#
# *****************************************************************************

"""
Tools for handling orientation calculations
"""

import numpy as np
import scipy.optimize

from nicos.devices.sxtal.xtal.sxtalcell import SXTalCell


def _norm(mat):
    '''
    calculate matrix of norm 1
    @param mat: Matrix
    @type mat: array (3x3)
    '''

    return mat / np.linalg.norm(mat, axis=0)


def _CompleteMatrix(vec1, vec2):
    '''
    Create a (orthogonal)  3x3-matrix from two non-colinear vectors
    '''
    vec3 = np.cross(vec1, vec2)
    mat = np.array((vec1, vec2, vec3))
    vec2 = np.cross(mat[2], mat[0])
    mat[1] = vec2
    mat_t = np.transpose(mat)
    return mat_t


class orient(object):
    def __init__(self, a, b=None, c=None, alpha=90.0, beta=90.0, gamma=90.0):
        self.cell = SXTalCell.fromabc(a, b, c, alpha, beta, gamma)

    def Reorient(self, hkl1, pos1, hkl2, pos2):
        '''
        Calculate orientation matrix from two indexed positions
        hkl1: index of reflection 1
        pos1: position of reflection 1 (goniometer.position object)
        hkl2: index of reflection 2
        pos2: position of reflection 2
        '''

        gmat = self.cell.CMatrix()
        cv_h1 = self.cell.CVector(hkl1)
        cv_h2 = self.cell.CVector(hkl2)

        cv_p1 = np.array(pos1.as_C().c)
        cv_p2 = np.array(pos2.as_C().c)

        bmat = _norm(_CompleteMatrix(cv_p1, cv_p2))
        amat = _norm(_CompleteMatrix(cv_h1, cv_h2))

        amat_i = np.linalg.inv(amat)
        temp = np.dot(bmat, amat_i)
        omat_t = np.dot(temp, gmat)
        omat = np.transpose(omat_t)
        cell = SXTalCell(omat)
        return cell

    def RefineOrientation(self, reflexlist):
        '''Simple least-squares optimization

         *reflexlist: list of tuples (hkl, centered position)
         '''
        ubmat = self.cell.CMatrix()
        hkls = [r[0] for r in reflexlist]
        cmeas = [p[1].asC().c for p in reflexlist]
        cmeas = np.array(cmeas)

        def residual(ubmatrix, cobs, hkli):
            ubmatrix = ubmatrix.reshape(3, 3)
            ccalc = [ubmatrix.dot(np.array(hkl)) for hkl in hkli]
            l = len(ccalc)
            ccalc = np.array(ccalc).reshape(l, 3)
            err = np.array(cobs) - ccalc
            return np.power(err, 2).sum()

        ubmat = scipy.optimize.fmin(residual, np.array(ubmat).flatten(), args=(cmeas, hkls))
        ubmat = ubmat.reshape(3, 3)
        new_cell = SXTalCell(np.transpose(ubmat))
        return new_cell
