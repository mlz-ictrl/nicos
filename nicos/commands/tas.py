#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TAS commands for NICOS."""

from numpy import ndarray

from nicos import session
from nicos.core import Measurable, Moveable, Readable, UsageError, NicosError
from nicos.core.spm import spmsyntax, Bare
from nicos.core.scan import QScan
from nicos.devices.tas.mono import to_k
from nicos.devices.tas.rescalc import resmat
from nicos.devices.tas.spectro import TAS, THZ2MEV
from nicos.devices.tas.plotting import plot_hklmap, plot_resatpoint, \
    plot_resscan
from nicos.devices.tas.spurions import check_acc_bragg, check_ho_spurions, \
    check_powderrays, alu_hkl, copper_hkl
from nicos.commands import usercommand, hiddenusercommand, helparglist
from nicos.commands.scan import _infostr, ADDSCANHELP2, cscan
from nicos.commands.device import maw, read
from nicos.commands.output import printinfo, printwarning
from nicos.commands.analyze import gauss
from nicos.pycompat import iteritems, string_types, number_types
from nicos.pycompat import xrange as range  # pylint: disable=W0622


__all__ = [
    'qscan', 'qcscan', 'Q', 'calpos', 'pos', 'rp',
    'acc_bragg', 'ho_spurions', 'alu', 'copper',
    'rescal', 'resplot', 'hklplot', 'checkalign',
]


def _getQ(v, name):
    try:
        if len(v) == 4:
            return list(v)
        elif len(v) == 3:
            return [v[0], v[1], v[2], 0]
        else:
            raise TypeError
    except TypeError:
        raise UsageError('%s must be a sequence of (h, k, l) or (h, k, l, E)'
                         % name)


def _handleQScanArgs(args, kwargs, Q, dQ, scaninfo):
    preset, detlist, envlist, move, multistep = {}, [], None, [], []
    for arg in args:
        if isinstance(arg, string_types):
            scaninfo = arg + ' - ' + scaninfo
        elif isinstance(arg, number_types):
            preset['t'] = arg
        elif isinstance(arg, Measurable):
            detlist.append(arg)
        elif isinstance(arg, Readable):
            if envlist is None:
                envlist = []
            envlist.append(arg)
        else:
            raise UsageError('unsupported qscan argument: %r' % arg)
    for key, value in iteritems(kwargs):
        if key == 'h' or key == 'H':
            Q[0] = value
        elif key == 'k' or key == 'K':
            Q[1] = value
        elif key == 'l' or key == 'L':
            Q[2] = value
        elif key == 'E' or key == 'e':
            Q[3] = value
        elif key == 'dh' or key == 'dH':
            dQ[0] = value
        elif key == 'dk' or key == 'dK':
            dQ[1] = value
        elif key == 'dl' or key == 'dL':
            dQ[2] = value
        elif key == 'dE' or key == 'de':
            dQ[3] = value
        elif key in session.devices and \
                isinstance(session.devices[key], Moveable):
            if isinstance(value, list):
                if multistep and len(value) != len(multistep[-1][1]):
                    raise UsageError('all multi-step arguments must have the '
                                     'same length')
                multistep.append((session.devices[key], value))
            else:
                move.append((session.devices[key], value))
        else:
            preset[key] = value
    return preset, scaninfo, detlist, envlist, move, multistep, Q, dQ


@usercommand
@helparglist('Q, dQ, numpoints, ...')
@spmsyntax(Bare, Bare, Bare)
def qscan(Q, dQ, numpoints, *args, **kwargs):
    """Perform a single-sided Q scan.

    The *Q* and *dQ* arguments can be lists of 3 or 4 components, or a `Q`
    object.

    Example:

    >>> qscan((1, 0, 0, 0), (0, 0, 0, 0.1), 11, kf=1.55, mon1=100000)

    will perform an energy scan at (100) from 0 to 1 meV (or THz, depending on
    the instrument setting) with the given constant kf and the given monitor
    counts per point.

    The special "plot" parameter can be given to plot the scan instead of
    running it:

    * plot='res'  -- plot resolution ellipsoid along scan
    * plot='hkl'  -- plot position of scan points in scattering plane
    """
    Q, dQ = _getQ(Q, 'Q'), _getQ(dQ, 'dQ')
    scanstr = _infostr('qscan', (Q, dQ, numpoints) + args, kwargs)
    plotval = kwargs.pop('plot', None)
    preset, scaninfo, detlist, envlist, move, multistep, Q, dQ = \
        _handleQScanArgs(args, kwargs, Q, dQ, scanstr)
    if all(v == 0 for v in dQ) and numpoints > 1:
        raise UsageError('scanning with zero step width')
    values = [[(Q[0]+i*dQ[0], Q[1]+i*dQ[1], Q[2]+i*dQ[2], Q[3]+i*dQ[3])]
              for i in range(numpoints)]
    if plotval == 'res':
        resscan(*(p[0] for p in values), kf=kwargs.get('kf'),
                ki=kwargs.get('ki'))
    elif plotval == 'hkl':
        hklplot(scan=[p[0] for p in values], kf=kwargs.get('kf'),
                ki=kwargs.get('ki'))
    else:
        scan = QScan(values, move, multistep, detlist, envlist, preset,
                     scaninfo)
        scan.run()


@usercommand
@helparglist('Q, dQ, numperside, ...')
@spmsyntax(Bare, Bare, Bare)
def qcscan(Q, dQ, numperside, *args, **kwargs):
    """Perform a centered Q scan.

    The *Q* and *dQ* arguments can be lists of 3 or 4 components, or a `Q`
    object.

    Example:

    >>> qcscan((1, 0, 0, 1), (0.001, 0, 0, 0), 20, mon1=1000)

    will perform a longitudinal scan around (100) with the given monitor counts
    per point.

    The special "plot" parameter can be given to plot the scan instead of
    running it:

    * plot='res'  -- plot resolution ellipsoid along scan
    * plot='hkl'  -- plot position of scan points in scattering plane
    """
    Q, dQ = _getQ(Q, 'Q'), _getQ(dQ, 'dQ')
    scanstr = _infostr('qcscan', (Q, dQ, numperside) + args, kwargs)
    plotval = kwargs.pop('plot', None)
    preset, scaninfo, detlist, envlist, move, multistep, Q, dQ = \
        _handleQScanArgs(args, kwargs, Q, dQ, scanstr)
    if all(v == 0 for v in dQ) and numperside > 0:
        raise UsageError('scanning with zero step width')
    values = [[(Q[0]+i*dQ[0], Q[1]+i*dQ[1], Q[2]+i*dQ[2], Q[3]+i*dQ[3])]
              for i in range(-numperside, numperside+1)]
    if plotval == 'res':
        resscan(*(p[0] for p in values), kf=kwargs.get('kf'),
                ki=kwargs.get('ki'))
    elif plotval == 'hkl':
        hklplot(scan=[p[0] for p in values], kf=kwargs.get('kf'),
                ki=kwargs.get('ki'))
    else:
        scan = QScan(values, move, multistep, detlist, envlist, preset,
                     scaninfo)
        scan.run()

qscan.__doc__ += ADDSCANHELP2.replace('scan(dev, ', 'qscan(Q, dQ, ')
qcscan.__doc__ += ADDSCANHELP2.replace('scan(dev, ', 'qcscan(Q, dQ, ')


class Q(ndarray):
    def __repr__(self):
        return str(self)

_Q = Q


@usercommand
@helparglist('[h, k, l, E]')
def Q(*args, **kwds):  # pylint: disable=E0102
    """A Q-E vector object that can be used for calculations.

    Use as follows:

    To create a Q vector (1, 0, 0) with energy transfer 0 or 5:

    >>> q = Q(1)
    >>> q = Q(1, 0, 0)
    >>> q = Q(1, 0, 0, 5)
    >>> q = Q(h=1, E=5)

    To create a Q vector from another Q vector, adjusting one or more entries:

    >>> q2 = Q(q, h=2, k=1)
    >>> q2 = Q(q, E=0)

    You can then use the Q-E vectors in scanning commands:

    >>> qscan(q, q2, 5, t=10)
    """
    q = _Q(4)
    q[:] = 0.
    if not args and not kwds:
        return q
    if len(args) == 1:
        try:
            nlen = len(args[0])
        except TypeError:
            q[0] = args[0]
        else:
            for i in range(nlen):
                q[i] = args[0][i]
    elif len(args) > 4:
        raise UsageError('1 to 4 Q/E components are allowed')
    else:
        for i in range(len(args)):
            q[i] = args[i]
    if 'h' in kwds:
        q[0] = kwds['h']
    elif 'H' in kwds:
        q[0] = kwds['H']
    if 'k' in kwds:
        q[1] = kwds['k']
    elif 'K' in kwds:
        q[1] = kwds['K']
    if 'l' in kwds:
        q[2] = kwds['l']
    if 'L' in kwds:
        q[2] = kwds['L']
    if 'E' in kwds:
        q[3] = kwds['E']
    elif 'e' in kwds:
        q[3] = kwds['e']
    return q


def _convert_qe_args(args, kwds, funcname):
    def convert_args():
        nargs = len(args)
        try:
            # is first arg a sequence?
            narg1 = len(args[0])
        except TypeError:
            # no: expect 3 to 5 single number arguments
            if nargs == 3:
                return args + (0, None)
            elif nargs == 4:
                return args + (None,)
            elif nargs == 5:
                return args
        else:
            # yes: sequence with either 3 or 4 items
            if narg1 == 3:
                # only Q given: expect optional E and SC
                if nargs == 1:
                    return tuple(args[0]) + (0, None)
                elif nargs == 2:
                    return tuple(args[0]) + (args[1], None)
                elif nargs == 3:
                    return tuple(args[0]) + args[1:]
            elif narg1 == 4:
                # Q-E tuple given, expect optional SC
                if nargs == 1:
                    return tuple(args[0]) + (None,)
                elif nargs == 2:
                    return tuple(args[0]) + (args[1],)
        # fallthrough for any invalid combination
        raise UsageError('invalid arguments for %s()' % funcname)
    pos = convert_args() + (None,)
    if 'ki' in kwds:
        pos = pos[:4] + (kwds['ki'], 'CKI')
    if 'kf' in kwds:
        pos = pos[:4] + (kwds['kf'], 'CKF')
    return pos


@usercommand
@helparglist('h, k, l, E[, SC]')
def calpos(*args, **kwds):
    """Calculate instrument position for a given (Q, E) position.

    Can be called with 3 to 5 arguments:

    >>> calpos(1, 0, 0)             # H, K, L
    >>> calpos(1, 0, 0, -4)         # H, K, L, E
    >>> calpos(1, 0, 0, -4, 2.662)  # H, K, L, E, scanconstant

    or with a Q-E vector:

    >>> calpos(Q(1, 0, 0, -4))         # Q-E vector
    >>> calpos(Q(1, 0, 0, -4), 2.662)  # Q-E vector and scanconstant

    Constant ki or kf can be given as keywords:

    >>> calpos(1, 0, 0, 4, kf=1.5)
    """
    instr = session.instrument
    if not isinstance(instr, TAS):
        raise NicosError('your instrument device is not a triple axis device')
    if not args:
        raise UsageError('calpos() takes at least one argument')
    pos = _convert_qe_args(args, kwds, 'calpos')
    instr._calpos(pos)


@usercommand
@helparglist('[phi, psi[, ki, kf][, E]]')
def pos2hkl(phi=None, psi=None, **kwds):
    """Calculate (Q, E) for a given instrument position.

    Without arguments, prints the current (Q, E).  ``rp()`` is an alias.

    >>> pos2hkl()
    >>> rp()

    The first two arguments are the sample 2-theta and theta angles.  The mono
    and ana values can be left out to use the current values:

    >>> pos2hkl(41.5, 29.2)  # phi and psi at current mono/ana position

    You can also give a certain energy, which uses the current scan mode and
    constant to calculate ki and kf:

    >>> pos2hkl(41.5, 29.2, E=2)

    Finally, you can give explicit values for ki and kf:

    >>> pos2hkl(41.5, 29.2, ki=1.83, kf=1.56)
    """
    instr = session.instrument
    if not isinstance(instr, TAS):
        raise NicosError('your instrument device is not a triple axis device')
    if not phi:
        read(instr)
    else:
        instr._reverse_calpos(phi, psi, **kwds)

rp = pos2hkl


@usercommand
@helparglist('[h, k, l, E[, SC]]')
def pos(*args, **kwds):
    """Move the instrument to a given (Q, E), or the last `calpos()` position.

    Without arguments, moves to the last position sucessfully calculated with
    `calpos()`.  Examples:

    >>> pos()                       # last calpos() position
    >>> pos(1, 0, 0)                # H, K, L
    >>> pos(1, 0, 0, -4)            # H, K, L, E
    >>> pos(1, 0, 0, -4, 2.662)     # H, K, L, E, scanconstant
    >>> pos(Q(1, 0, 0, -4))         # Q-E vector
    >>> pos(Q(1, 0, 0, -4), 2.662)  # Q-E vector and scanconstant
    """
    instr = session.instrument
    if not isinstance(instr, TAS):
        raise NicosError('your instrument device is not a triple axis device')
    if not args:
        pos = instr._last_calpos
        if pos is None:
            raise NicosError('pos() with no arguments moves to the last '
                             'position calculated by calpos(), but no such '
                             'position has been stored')
    else:
        pos = _convert_qe_args(args, kwds, 'pos')
        instr._calpos(pos, checkonly=False)
    if pos[5] and pos[5] != instr.scanmode:
        instr.scanmode = pos[5]
    if pos[4] and pos[4] != instr.scanconstant:
        instr.scanconstant = pos[4]
    maw(instr, pos[:4])


@usercommand
@helparglist('h, k, l, E[, SC]')
def acc_bragg(h, k, l, ny, sc=None):
    """Check accidental Bragg scattering conditions for type A or type M.

    Accidental Bragg scattering is checked at the given spectrometer position.
    """
    instr = session.instrument
    for line in check_acc_bragg(instr, h, k, l, ny, sc, verbose=True):
        printinfo(line)


@usercommand
@helparglist('[kf[, dEmin, dEmax]]')
def ho_spurions(kf=None, dEmin=0, dEmax=20):
    """Calculation of elastic spurions due to higher order neutrons.

    *kf* is the final wavevector to use for calculation.  *dEmin* and *dEmax*
    are the minimum and maximum energy transfer to list.
    """
    instr = session.instrument
    if kf is None:
        ana = instr._attached_ana
        kf = to_k(ana.read(), ana.unit)
    printinfo('calculation of potential weak spurions due to higher harmonic '
              'ki / kf combinations')
    printinfo('calculated for kf = %6.3f A-1' % kf)
    for line in check_ho_spurions(kf, dEmin, dEmax):
        printinfo(line)


@usercommand
@helparglist('[ki, phi]')
def alu(ki=None, phi=None):
    """Print powder ray positions of Al."""
    powderrays(alu_hkl, ki, phi)


@usercommand
@helparglist('[ki, phi]')
def copper(ki=None, phi=None):
    """Print powder ray positions of Cu."""
    powderrays(copper_hkl, ki, phi)


def powderrays(dlist, ki=None, phi=None):
    """Calculate powder ray positions."""
    instr = session.instrument
    if ki is None:
        mono = instr._attached_mono
        ki = to_k(mono.read(), mono.unit)
    for line in check_powderrays(ki, dlist, phi):
        printinfo(line)


def _resmat_args(args, kwds):
    instr = session.instrument
    cell = instr._attached_cell
    mono = instr._attached_mono
    ana = instr._attached_ana

    if not args:
        pos = instr.read(0)
    elif len(args) == 4:
        pos = args
    elif len(args) == 3:
        pos = args + (0.,)
    elif len(args) == 1 and isinstance(args[0], _Q):
        pos = args[0]
    else:
        raise UsageError('unsupported arguments')

    if 'kf' in kwds and kwds['kf'] is not None:
        const = kwds['kf']
        mode = 'CKF'
    elif 'ki' in kwds and kwds['ki'] is not None:
        const = kwds['ki']
        mode = 'CKI'
    else:
        const = instr.scanconstant
        mode = instr.scanmode

    cfg = instr._getResolutionParameters()

    ny = pos[3] if instr.energytransferunit == 'THz' else pos[3] / THZ2MEV

    if mode == 'CKI':
        ki = const
        kf = cell.cal_kf(ny, ki)
    else:
        kf = const
        ki = cell.cal_ki1(ny, kf)
    if cfg[23] == 0 and mono.focmode in ('horizontal', 'double'):
        cfg[23] = mono._calcurvature(cfg[19], cfg[20], ki)
    if cfg[24] == 0 and mono.focmode in ('vertical', 'double'):
        cfg[24] = mono._calcurvature(cfg[19], cfg[20], ki, vertical=True)
    if cfg[25] == 0 and ana.focmode in ('horizontal', 'double'):
        cfg[25] = ana._calcurvature(cfg[21], cfg[22], ki)
    if cfg[26] == 0 and ana.focmode in ('vertical', 'double'):
        cfg[26] = ana._calcurvature(cfg[21], cfg[22], ki, vertical=True)

    collimation = instr._getCollimation()
    par = {
        'dm': instr._attached_mono.dvalue,
        'da': instr._attached_ana.dvalue,
        'sm': instr.scatteringsense[0],
        'ss': instr.scatteringsense[1],
        'sa': instr.scatteringsense[2],
        'etam': instr._attached_mono.mosaic * 60,
        'etas': cell.mosaic * 60,
        'etaa': instr._attached_ana.mosaic * 60,
        'alpha1': collimation[0],  # in minutes
        'alpha2': collimation[1],
        'alpha3': collimation[2],
        'alpha4': collimation[3],
        'beta1': collimation[4],
        'beta2': collimation[5],
        'beta3': collimation[6],
        'beta4': collimation[7],
        'k': const,
        'kfix': 1 if mode == 'CKI' else 2,
        'as': cell.lattice[0],
        'bs': cell.lattice[1],
        'cs': cell.lattice[2],
        'aa': cell.angles[0],
        'bb': cell.angles[1],
        'cc': cell.angles[2],
        'ax': cell.orient1[0],
        'ay': cell.orient1[1],
        'az': cell.orient1[2],
        'bx': cell.orient2[0],
        'by': cell.orient2[1],
        'bz': cell.orient2[2],
        'qx': pos[0],
        'qy': pos[1],
        'qz': pos[2],
        'en': ny * THZ2MEV,
    }

    return cfg, par


@usercommand
@helparglist('[h, k, l[, E]] [, ki|kf=const]')
def rescal(*args, **kwds):
    """Calculate and print resolution at the current or the given Q/E point.

    Example:

    >>> rescal()           # display resolution at current Q/E point
    >>> rescal(1, 1, 0)    # display resolution at the given point
    >>> rescal(1, 1, 0, 5, kf=2.66)  # at the given point with const kf = 2.66

    Obviously, several sample and spectrometer parameters must be set correctly
    for the resolution calculation to work.
    """
    for line in str(resmat(*_resmat_args(args, kwds))).splitlines():
        printinfo(line)


@usercommand
@helparglist('[h, k, l[, E]] [, ki|kf=const]')
def resplot(*args, **kwds):
    """Calculate and plot resolution at the current or the given Q/E point.

    Example:

    >>> resplot()           # plot resolution at current Q/E point
    >>> resplot(1, 1, 0)    # plot resolution at the given point
    >>> resplot(1, 1, 0, 5, kf=2.66)  # at the given point with const kf = 2.66

    Obviously, several sample and spectrometer parameters must be set correctly
    for the resolution calculation to work.
    """
    cfg, par = _resmat_args(args, kwds)
    printinfo('plotting resolution in separate window, please wait...')
    session.clientExec(plot_resatpoint, (cfg, par))


@hiddenusercommand
@helparglist('hkle1, hkle2, ...')
def resscan(*hkles, **kwds):
    """Calculate and plot resolution at every given point.

    This is usually used via the `qscan()` and `qcscan()` commands with the
    plot='res' parameter.
    """
    if not hkles:
        raise UsageError('use qscan(..., plot="res") to plot scan resolution')
    cfg, par = _resmat_args(hkles[0], kwds)
    printinfo('plotting scan resolution in separate window, please wait...')
    session.clientExec(plot_resscan, (cfg, par, hkles))


@usercommand
@helparglist('...')
def hklplot(**kwds):
    """Plot a representation of the scattering plane with accessible Q space.

    Keyword arguments that can be given:

    * E -- energy transfer to calculate for
    * ki -- ki for constant-ki mode (default is current spectrometer setup)
    * kf -- kf for constant-kf mode
    * hkl -- a (h, k, l) tuple to plot
    * tauX -- a propagation vector as a (dh, dk, dl) tuple to plot from every
      nuclear Bragg point

    Examples:

    >>> hklplot()     # basic plot of reciprocal space and nuclear Bragg peaks
    # plot the same, but at E = 1 (meV or THz)
    >>> hklplot(E=1)
    # plot the same, but at kf = 1.3 and E = 2
    >>> hklplot(kf=1.3, E=1)
    # also plot (1, 0.5, 0)
    >>> hklplot(hkl=(1, 0.5, 0))
    # also plot magnetic satellites tau1 and tau2 from each nuclear Bragg peak
    >>> hklplot(tau1=(0.28, 0.28, 0), tau2=(0.28, -0.28, 0))
    """
    cfg, par = _resmat_args((), kwds)
    tas = session.instrument
    tasinfo = {
        'actpos': tas.read(),
        'calpos': tas._last_calpos,
        'philim': tas._attached_phi.userlimits,
        'psilim': tas._attached_psi.userlimits,
        'monolim': tas._attached_mono.userlimits,
        'analim': tas._attached_ana.userlimits,
        'alphalim': tas._attached_alpha and tas._attached_alpha.userlimits,
        'phiname': tas._attached_phi.name,
        'psiname': tas._attached_psi.name,
    }
    for p in ['scanmode', 'scanconstant', 'energytransferunit',
              'scatteringsense', 'axiscoupling', 'psi360']:
        tasinfo[p] = getattr(tas, p)
    for p in ['lattice', 'angles', 'orient1', 'orient2',
              'psi0', 'spacegroup']:
        tasinfo[p] = getattr(tas._attached_cell, p)
    session.clientExec(plot_hklmap, (cfg, par, tasinfo, kwds))


@usercommand
@helparglist('(h, k, l), [psival]')
def setalign(hkl, psival=None):
    """Readjust Sample psi0 to the current value of the sample rotation axis
    or the given *psival* value.

    Example:

    >>> setalign((4, 0, 0))         # align so that 4,0,0 is "here"
    >>> setalign((4, 0, 0), 90.32)  # align so that 4,0,0 is on 90.32 deg
    """
    tas = session.instrument
    target = tuple(hkl) + (0,)
    psi = tas._attached_psi
    psicalc = tas._calpos(target + (None, None), printout=False)[3]
    if psival is None:
        psival = psi.read(0)
    diff = psicalc - psival
    sample = tas._attached_cell
    printinfo('adjusting %s.psi0 by %s to %s' % (
        sample, psi.format(diff, True), psi.format(sample.psi0 + diff, True)))
    sample.psi0 += diff
    newpsi = tas._calpos(target + (None, None), printout=False)[3]
    printinfo('%s is now at %s' % (tuple(hkl), psi.format(newpsi, True)))


@usercommand
@helparglist('(h, k, l), step, numpoints, ...')
def checkalign(hkl, step, numpoints, *args, **kwargs):
    """Readjust Sample psi0 to the fitted center of a sample rocking scan around
    the (h, k, l) position.  After the scan, moves back to (h, k, l).

    An additional a keyword "ycol" gives the Y column of the dataset to use for
    the Gaussian fit (see the help for `gauss()` for the meaning of this
    parameter).

    Examples:

    >>> checkalign((1, 1, 0), 0.05, 20)
    >>> checkalign((1, 1, 0), 0.05, 20, ycol='ctr2')

    You can also give a keyword argument "accuracy", which defines how much
    the old and new value have to differ in order to make an adjustment.  It
    defaults to 1/10 of the fitted FWHM.
    """
    tas = session.instrument
    ycol = kwargs.pop('ycol', -1)
    accuracy = kwargs.pop('accuracy', None)
    target = tuple(hkl) + (0,)
    tas.maw(target)
    psi = tas._attached_psi
    center = tas._calpos(target + (None, None), printout=False)[3]
    cscan(psi, center, step, numpoints, 'align check', *args, **kwargs)
    params, _ = gauss(ycol)
    # do not allow moving outside of the scanned region
    minvalue = center - step*numpoints
    maxvalue = center + step*numpoints
    if params is None:
        printwarning('Gaussian fit failed, psi0 unchanged')
    elif not minvalue <= params[0] <= maxvalue:
        printwarning('Gaussian fit resulted in center outside scanning area, '
                     'offset unchanged')
    else:
        # NOTE: this is the other way around compared to checkoffset
        diff = center - params[0]
        printinfo('center of Gaussian fit at %s' % psi.format(params[0], True))
        if accuracy is None:
            accuracy = params[2] * 0.1
        if abs(diff) < accuracy:
            printinfo('alignment ok within %.3f degrees, not changing psi0'
                      % accuracy)
            return
        sample = tas._attached_cell
        printwarning('adjusting %s.psi0 by %s' % (sample,
                                                  psi.format(diff, True)))
        sample.psi0 += diff
    tas.maw(target)
