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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""Tools for handling orientation calculations."""

import numpy as np
import scipy.optimize

from nicos.devices.sxtal.xtal.sxtalcell import SXTalCell, matrixfromcell
from nicos.devices.sxtal.goniometer.base import PositionFactory
from nicos.devices.sxtal.goniometer.posutils import Xrot, Yrot, Zrot
from nicos.core.errors import ComputationError


def _norm(mat):
    """Calculate matrix of norm 1."""
    return mat / np.linalg.norm(mat, axis=0)


def complete_matrix(vec1, vec2):
    """Create a (orthogonal) 3x3-matrix from two non-colinear vectors."""
    vec3 = np.cross(vec1, vec2)
    mat = np.array((vec1, vec2, vec3))
    vec2 = np.cross(mat[2], mat[0])
    mat[1] = vec2
    mat_t = np.transpose(mat)
    return mat_t


def euler_from_rotmat(R):
    """Calculate Euler angles from a rotation matrix (U matrix).

    http://www.staff.city.ac.uk/~sbbh653/publications/euler.pdf
    """
    if abs(R[2,0]) != 1:
        theta1 = -np.arcsin(R[2,0])
        costh1 = np.cos(theta1)
        psi1 = np.arctan2(R[2,1]/costh1, R[2,2]/costh1)
        phi1 = np.arctan2(R[1,0]/costh1, R[0,0]/costh1)
        # -- second solution:
        # theta2 = np.pi - theta1
        # costh2 = np.cos(theta2)
        # psi2 = np.arctan2(R[2,1]/costh2, R[2,2]/costh2)
        # phi2 = np.arctan2(R[1,0]/costh2, R[0,0]/costh2)
        return psi1, theta1, phi1
    else:
        phi = 0
        if R[2,0] == -1:
            theta = np.pi/2
            psi = phi + np.arctan2(R[0,1], R[0,2])
        else:
            theta = -np.pi/2
            psi = -phi + np.arctan2(-R[0,1], -R[0,2])
        return psi, theta, phi


class RefinementParams(object):
    def __init__(self):
        self.couples = {}
        self.params = {}
        self.errors = {}
        self.varnames = []
        self.varinit = []

    def __getattr__(self, name):
        return self.params[name]

    def update(self, varying):
        for i, value in enumerate(varying):
            name = self.varnames[i]
            self.params[name] = value
            for other in self.couples.get(name, ()):
                self.params[other] = value

    def update_errors(self, errors):
        for i, value in enumerate(errors):
            name = self.varnames[i]
            self.errors[name] = value
            for other in self.couples.get(name, ()):
                self.errors[other] = value

    def add(self, name, initval, kwds):
        if name in kwds:
            fixed = kwds[name]
            if fixed in self.params:
                self.couples.setdefault(fixed, []).append(name)
                self.params[name] = self.params[fixed]
            else:
                self.params[name] = kwds[name]
        else:
            self.params[name] = initval
            self.varnames.append(name)
            self.varinit.append(initval)
        self.errors[name] = 0.0


class orient(object):
    def __init__(self, a, b=None, c=None, alpha=90.0, beta=90.0, gamma=90.0):
        if isinstance(a, SXTalCell):
            self.cell = a
        else:
            self.cell = SXTalCell.fromabc(a, b, c, alpha, beta, gamma)

    def Reorient(self, hkl1, pos1, hkl2, pos2):
        """Calculate orientation matrix from two indexed positions.

        hkl1: index of reflection 1
        pos1: position of reflection 1 (goniometer.position object)
        hkl2: index of reflection 2
        pos2: position of reflection 2
        """
        gmat = self.cell.CMatrix()
        cv_h1 = self.cell.CVector(hkl1)
        cv_h2 = self.cell.CVector(hkl2)

        cv_p1 = np.array(pos1.asC().c)
        cv_p2 = np.array(pos2.asC().c)

        bmat = _norm(complete_matrix(cv_p1, cv_p2))
        amat = _norm(complete_matrix(cv_h1, cv_h2))

        amat_i = np.linalg.inv(amat)
        temp = np.dot(bmat, amat_i)
        omat_t = np.dot(temp, gmat)
        omat = np.transpose(omat_t)
        cell = SXTalCell(omat)
        return cell

    def RefineOrientation(self, poslist, kwds, lambda0, axes, offsets):
        """Simple least-squares optimization.

        poslist: list of tuples (centered position, hkl, intensity)
        """
        # get Euler angles from U matrix
        init_p = self.cell.cellparams()
        Bmat = matrixfromcell(init_p.a, init_p.b, init_p.c,
                              init_p.alpha, init_p.beta, init_p.gamma)
        Umat = self.cell.rmat.T.dot(np.linalg.inv(Bmat))
        psi, theta, phi = euler_from_rotmat(Umat)

        if len(poslist) < 2:
            raise ComputationError('Need at least two reflections')
        postype = poslist[0][0].ptype.upper()

        p = RefinementParams()

        # these are always varying
        p.add('psi', psi, {})
        p.add('theta', theta, {})
        p.add('phi', phi, {})

        # cell params
        p.add('a', init_p.a, kwds)
        p.add('b', init_p.b, kwds)
        p.add('c', init_p.c, kwds)
        p.add('alpha', init_p.alpha, kwds)
        p.add('beta', init_p.beta, kwds)
        p.add('gamma', init_p.gamma, kwds)

        # wavelength
        p.add('wavelength', lambda0, kwds)

        # axis offsets
        for axis, offset in zip(axes, offsets):
            p.add('delta_' + axis, offset, kwds)

        def get_new_cell(p):
            # reconstruct UB matrix
            Umat = Zrot(-p.phi).dot(Yrot(-p.theta)).dot(Xrot(-p.psi))
            Bmat = matrixfromcell(p.a, p.b, p.c, p.alpha, p.beta, p.gamma)
            return SXTalCell(Umat.dot(Bmat).T)

        def residuals(varying):
            p.update(varying)
            cell = get_new_cell(p)
            errors = []
            for (mpos, hkl, _) in poslist:
                cpos = PositionFactory('c', c=cell.CVector(hkl))
                cpos = getattr(cpos, 'as' + postype)(p.wavelength)
                errors.append(7.0 * (cpos.omega - mpos.omega))
                for axis in axes:
                    errors.append(4.0 * (
                        getattr(cpos, axis) +
                        np.radians(getattr(p, 'delta_' + axis)) -
                        getattr(mpos, axis)))
            return errors

        popt, pcov, infodict, errmsg, ier = \
            scipy.optimize.leastsq(residuals, p.varinit, full_output=1)
        nfree = len(poslist) - len(p.varinit)
        if pcov is not None and nfree > 0:
            cost = np.sum(infodict['fvec']**2)
            s_sq = cost / nfree
            pcov = pcov * s_sq
        else:
            pcov = np.zeros((len(popt), len(popt)), dtype=float)
            pcov.fill(float('inf'))
        if ier not in [1, 2, 3, 4]:
            raise ComputationError('Optimization failed: %s' % errmsg)

        p.update(popt)
        p.update_errors(pcov[i,i] for i in range(len(popt)))
        return get_new_cell(p), p
