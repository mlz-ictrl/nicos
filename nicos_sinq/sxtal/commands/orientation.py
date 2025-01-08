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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

'''
TODO This file should be removed once the functions in
`nicos_sinq/zebra/commands/refineub.py` have had more real-world testing and
tests have been added to the test-suite for them
'''

import numbers

import numpy as np
import scipy.optimize

from nicos import session
from nicos.commands import helparglist, hiddenusercommand, usercommand
from nicos.core.errors import ComputationError

from nicos_sinq.sxtal.cell import Cell, cellFromUBX
from nicos_sinq.sxtal.singlexlib import calculateBMatrix, \
    matFromTwoVectors as complete_matrix, normalize_vector as _norm, \
    reflectionToHC

__all__ = ['RefineMatrix', 'AcceptRefinement', 'LoadRafin', 'LoadRafnb']


def eulerToRotmat(R):
    """Calculate Euler angles from a rotation matrix (U matrix).

    http://www.staff.city.ac.uk/~sbbh653/publications/euler.pdf
    """
    if abs(R[2, 0]) != 1:
        theta1 = -np.arcsin(R[2, 0])
        costh1 = np.cos(theta1)
        psi1 = np.arctan2(R[2, 1]/costh1, R[2, 2]/costh1)
        phi1 = np.arctan2(R[1, 0]/costh1, R[0, 0]/costh1)
        # -- second solution:
        # theta2 = np.pi - theta1
        # costh2 = np.cos(theta2)
        # psi2 = np.arctan2(R[2,1]/costh2, R[2,2]/costh2)
        # phi2 = np.arctan2(R[1,0]/costh2, R[0,0]/costh2)
        return psi1, theta1, phi1
    else:
        phi = 0
        if R[2, 0] == -1:
            theta = np.pi/2
            psi = phi + np.arctan2(R[0, 1], R[0, 2])
        else:
            theta = -np.pi/2
            psi = -phi + np.arctan2(-R[0, 1], -R[0, 2])
        return psi, theta, phi


# The matrices below are different from the rotations in singlexlib
def xRot(a, typecode='d'):
    """Construct a rotation matrix rotating 'a' around the X axis"""
    sa = np.sin(a)
    ca = np.cos(a)
    return np.array([[1.0, 0, 0], [0, ca, sa], [0, -sa, ca]], typecode)


def yRot(a, typecode='d'):
    """Construct a rotation matrix rotating 'a' around the Y axis"""
    sa = np.sin(a)
    ca = np.cos(a)
    return np.array([[ca, 0, -sa], [0, 1.0, 0], [sa, 0, ca]], typecode)


def zRot(a, typecode='d'):
    """Construct a rotation matrix rotating 'a' around the Z axis"""
    sa = np.sin(a)
    ca = np.cos(a)
    return np.array([[ca, sa, 0], [-sa, ca, 0], [0, 0, 1.0]],
                    typecode)


class RefinementParams:
    def __init__(self):
        self.couples = {}
        self.params = {}
        self.errors = {}
        self.varnames = []
        self.varinit = []
        self.chi2 = 0.

    def __getattr__(self, name):
        return self.params[name]

    def update(self, varying):
        for i, value in enumerate(varying):
            name = self.varnames[i]
            self.params[name] = value
            for other in self.couples.get(name, ()):
                self.params[other] = value

    def updateErrors(self, errors):
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


class orient:
    def __init__(  # pylint: disable=too-many-positional-arguments
                 self, inst, a, b=None, c=None,
                 alpha=90.0, beta=90.0, gamma=90.0):

        if isinstance(a, Cell):
            self.cell = a
        else:
            self.cell = Cell(a, b, c, alpha, beta, gamma)
        self.inst = inst

    def tupleToDict(self, hkl):
        return {
            'h': hkl[0],
            'k': hkl[1],
            'l': hkl[2],
        }

    def reorient(self, hkl1, pos1, hkl2, pos2):
        """Calculate orientation matrix from two indexed positions.

        hkl1: index of reflection 1
        pos1: position of reflection 1 (tuple of angles)
        hkl2: index of reflection 2
        pos2: position of reflection 2
        """
        gmat = calculateBMatrix(self.cell)
        cv_h1 = reflectionToHC(self.tuple2Dict(hkl1), gmat)
        cv_h2 = reflectionToHC(self.tupleToDict(hkl2), gmat)

        cv_p1 = self.inst._convertPos(pos1)
        cv_p2 = self.inst._convertPos(pos2)

        bmat = _norm(complete_matrix(cv_p1, cv_p2))
        amat = _norm(complete_matrix(cv_h1, cv_h2))

        amat_i = np.linalg.inv(amat)
        temp = np.dot(bmat, amat_i)
        omat_t = np.dot(temp, gmat)
        omat = np.transpose(omat_t)
        cell = cellFromUBX(omat)
        return cell

    def getNewUB(self, p):
        # reconstruct UB matrix
        Umat = zRot(-p.phi).dot(yRot(-p.theta)).dot(xRot(-p.psi))
        cp = Cell(p.a, p.b, p.c, p.alpha, p.beta, p.gamma)
        Bmat = calculateBMatrix(cp)
        return Umat.dot(Bmat).T

    def addCell(self, p, kwds):
        cell_param = ['a', 'b', 'c', 'alpha', 'beta', 'gamma']

        # By carefully controlling the order in which cell parameters are
        # added to p, I enable arbitrary constraints
        for key, val in kwds.items():
            if key in cell_param and isinstance(val, numbers.Number):
                p.add(key, val, kwds)
                cell_param.remove(key)

        # Add the unprocessed cell constants
        for par in cell_param:
            p.add(par, getattr(self.cell, par), kwds)

    def refineOrientation(  # pylint: disable=too-many-positional-arguments
            self, poslist, kwds, lambda0, axes, offsets):
        """Simple least-squares optimization.

        poslist: list of tuples (hkl, centered position)
        """
        # get Euler angles from U matrix
        Bmat = calculateBMatrix(self.cell)
        UB = session.experiment.sample.getUB()
        Umat = UB.dot(np.linalg.inv(Bmat))
        psi, theta, phi = eulerToRotmat(Umat)

        if len(poslist) < 2:
            raise ComputationError('Need at least two reflections')

        p = RefinementParams()

        # these are always varying
        p.add('psi', psi, {})
        p.add('theta', theta, {})
        p.add('phi', phi, {})

        # cell params
        self.addCell(p, kwds)

        # wavelength
        p.add('wavelength', lambda0, kwds)

        # axis offsets
        for axis, offset in zip(axes, offsets):
            p.add('delta_' + axis.name, offset, kwds)

        def getNewCell(p):
            cp = Cell(p.a, p.b, p.c, p.alpha, p.beta, p.gamma)
            return cp

        def residuals(varying):
            p.update(varying)
            ubmatrix = self.getNewUB(p)
            errors = []
            for (hkl, mpos) in poslist:
                # I am using the difference of the z1 Vectors here
                cpos = ubmatrix.dot(np.array(list(hkl), dtype='float64'))
                # Apply refined offsets to angles
                tpos = []
                for axis, pos in zip(axes, mpos):
                    tpos.append(pos + getattr(p, 'delta_' + axis.name))
                cmeas = self.inst._convertPos(tuple(tpos), p.wavelength)
                err = np.array(cmeas) - cpos
                # use difference² for the vectors
                errors.append(np.power(err, 2).sum())
            return errors

        popt, pcov, infodict, errmsg, ier = \
            scipy.optimize.leastsq(residuals, p.varinit,
                                   full_output=1)
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
        p.updateErrors(np.sqrt(pcov[i, i]) for i in range(len(popt)))
        p.chi2 = sum(np.power(residuals(popt), 2)) / nfree
        return getNewCell(p), p


def showDiffs(newub, poslist):
    session.log.info('************ Difference List ****************')
    inst = session.instrument
    cpos = newub.dot(np.array(list(poslist[0][0]), dtype='float64'))
    newpos = inst._extractPos(cpos)
    header = '   H     K     L  '
    header2 = '                   '
    cols = ['old', 'new', 'diff']
    for p in newpos:
        header += p[0].center(27) + ' '
        for c in cols:
            header2 += c.rjust(9)
        header2 += ' '
    session.log.info(header)
    session.log.info(header2)
    try:
        for rfl in poslist:
            cpos = newub.dot(np.array(list(rfl[0]), dtype='float64'))
            newpos = inst._extractPos(cpos)
            line = ''
            for q in rfl[0]:
                line += '%6.1f' % q
            line += ' '
            for ang, oldang in zip(newpos, rfl[1]):
                newang = ang[1]
                line += '%9.3f' % oldang
                line += '%9.3f' % newang
                line += '%9.3f' % (oldang - newang)
                line += ' '
            session.log.info(line)
    except Exception as e:
        session.log.error('Exception %s while printing difference list', e)


@usercommand
@helparglist('param=value, ...')
def RefineMatrix(listname='ublist', **kwds):
    """Refine the UB matrix with the given parameters.

    All given parameters are constant, all others are free.

    Possible parameters:

    * ``a``: first lattice parameter in Angstroem
    * ``b``: second lattice parameter, can also be ``'a'``
    * ``c``: third lattice parameter, can also be ``'a'``
    * ``alpha``: first angle in degrees
    * ``beta``: second angle, can also be ``'alpha'``
    * ``gamma``: third angle, can also be ``'alpha'``
    * ``wavelength`` in Angstroem
    * ``delta_gamma``, ``delta_nu``: offsets for detector axes

    Examples::

       # refine wavelength and angle offsets
       >>> RefineMatrix(a=6.12, b='a', c='a', alpha=90, beta=90, gamma=120)

       # refine lattice parameter a = b = c
       >>> RefineMatrix(alpha=90, beta=90, gamma=90, wavelength=1.15,
                        delta_gamma=0, delta_nu=0)

       # use a different peak list
       >>> RefineMatrix('listname', ...)
    """
    sample = session.experiment.sample
    instr = session.instrument

    rfl = sample.getRefList(listname)
    if not rfl:
        session.log.warning('Position list %r does not exist', listname)
        return
    # Reformat reflection data to match the format required by this code
    posl = []
    try:
        for r in rfl.generate(0):
            posl.append(tuple([r[0], r[1]]))
    except StopIteration:
        pass

    init_lambda = instr.wavelength
    motors = instr.get_motors()
    init_offsets = [mot.offset for mot in motors]

    RefineMatrix._last_result = None
    session.log.info('Refining matrix with %d reflections from position '
                     'list...', len(posl))

    o = orient(instr, sample.getCell())
    new_cell, p = o.refineOrientation(posl, kwds, init_lambda, motors,
                                      init_offsets)
    ubnew = o.getNewUB(p)

    session.log.info('')
    session.log.info('Cell parameters:')
    session.log.info('Initial:    a = %8.4f   b = %8.4f   c = %8.4f   '
                     'alpha= %7.3f   beta = %7.3f   gamma = %7.3f',
                     *[sample.a, sample.b, sample.c, sample.alpha,
                       sample.beta, sample.gamma])
    session.log.info('Final:      a = %8.4f   b = %8.4f   c = %8.4f   '
                     'alpha = %7.3f   beta = %7.3f   gamma = %7.3f',
                     p.a, p.b, p.c, p.alpha, p.beta, p.gamma)
    session.log.info('Errors: +/-     %8.4f       %8.4f       %8.4f   '
                     '    %7.3f       %7.3f       %7.3f',
                     p.errors['a'], p.errors['b'], p.errors['c'],
                     p.errors['alpha'], p.errors['beta'], p.errors['gamma'])

    session.log.info('')
    for mot in motors:
        session.log.info('%s: Initial: %8.4f, Final: %8.4f, Errors: %8.4f',
                         mot.name + '_offset', mot.offset,
                         p.params['delta_' + mot.name],
                         p.errors['delta_' + mot.name])

    session.log.info('')
    session.log.info('Reduced ch**2 (chi**2/NDF): %8.4f', p.chi2)

    session.log.info('')
    session.log.info('New UB matrix:')
    for row in ubnew:  # pylint: disable=not-an-iterable
        session.log.info(' %8.4f %8.4f %8.4f', *row)

    session.log.info('')
    showDiffs(ubnew, posl)

    session.log.info('Use AcceptRefinement() to use this refined data.')

    results = [new_cell, ]
    for mot in motors:
        results.append(p.params['delta_' + mot.name])
    results.append(ubnew)

    RefineMatrix._last_result = tuple(results)


RefineMatrix._last_result = None


@usercommand
def AcceptRefinement():
    """Accept the last refinement performed by `RefineMatrix()`.

    Example:

    >>> AcceptRefinement()
    """
    sample = session.experiment.sample

    if RefineMatrix._last_result is None:
        session.log.error('No refinement performed yet.')
        return

    results = RefineMatrix._last_result

    cell = results[0]
    sample.a = cell.a
    sample.b = cell.b
    sample.c = cell.c
    sample.alpha = cell.alpha
    sample.beta = cell.beta
    sample.gamma = cell.gamma
    idx = 1
    for mot in session.instrument.get_motors():
        mot.offset = results[idx]
        idx += 1
    sample.ubmatrix = list(results[-1].flatten())


@hiddenusercommand
def LoadRafin(filename):
    """
    Load a rafin input file. This is helper code for testing the UB
    matrix refinement against a software known to work
    :param filename:
    """
    sample = session.experiment.sample
    ref = sample.getRefList()
    ref.clear()
    with open(filename, 'r', encoding='utf-8') as fin:
        fin.readline()
        fin.readline()
        fin.readline()
        fin.readline()
        celline = fin.readline()
        comp = celline.split()
        sample.a = comp[1]
        sample.b = comp[3]
        sample.c = comp[5]
        sample.alpha = comp[7]
        sample.beta = comp[9]
        sample.gamma = comp[11]
        line = fin.readline()
        while line:
            cleanline = ' '.join(line.split())
            cleansplit = cleanline.split()
            if len(cleansplit) < 7:
                break
            floats = [float(x) for x in cleansplit]
            hkl = tuple(floats[0:3])
            ang = tuple(floats[3:7])
            ref.append(hkl, ang)
            line = fin.readline()


@hiddenusercommand
def LoadRafnb(filename):
    """
    Load a rafnb input file. This is helper code for testing the UB
    matrix refinement against a software known to work
    :param filename:
    """
    sample = session.experiment.sample
    ref = sample.getRefList()
    ref.clear()
    with open(filename, 'r', encoding='utf-8') as fin:
        fin.readline()
        fin.readline()
        fin.readline()
        fin.readline()
        celline = fin.readline()
        comp = celline.split()
        sample.a = comp[1]
        sample.b = comp[3]
        sample.c = comp[5]
        sample.alpha = comp[7]
        sample.beta = comp[9]
        sample.gamma = comp[11]
        line = fin.readline()
        while line:
            cleanline = ' '.join(line.split())
            cleansplit = cleanline.split()
            if len(cleansplit) < 6:
                break
            floats = [float(x) for x in cleansplit]
            hkl = tuple(floats[0:3])
            ang = tuple(floats[3:6])
            ref.append(hkl, ang)
            line = fin.readline()
