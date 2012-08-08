#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

__version__ = "$Revision$"

from math import asin, pi

from numpy import ndarray

from nicos import session
from nicos.core import Measurable, Moveable, Readable, UsageError, NicosError
from nicos.scan import QScan
from nicos.tas.spectro import TAS, THZ2MEV
from nicos.commands import usercommand, hiddenusercommand, helparglist
from nicos.commands.scan import _infostr, ADDSCANHELP2
from nicos.commands.device import maw, read
from nicos.commands.output import printinfo


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
        if isinstance(arg, str):
            scaninfo = arg + ' - ' + scaninfo
        elif isinstance(arg, (int, long, float)):
            preset['t'] = arg
        elif isinstance(arg, Measurable):
            detlist.append(arg)
        elif isinstance(arg, Readable):
            if envlist is None:
                envlist = []
            envlist.append(arg)
        else:
            raise UsageError('unsupported qscan argument: %r' % arg)
    for key, value in kwargs.iteritems():
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
@helparglist('Q, dQ, numsteps, ...')
def qscan(Q, dQ, numsteps, *args, **kwargs):
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
    scanstr = _infostr('qscan', (Q, dQ, numsteps) + args, kwargs)
    plotval = kwargs.pop('plot', None)
    preset, scaninfo, detlist, envlist, move, multistep, Q, dQ = \
            _handleQScanArgs(args, kwargs, Q, dQ, scanstr)
    if all(v == 0 for v in dQ) and numsteps > 1:
        raise UsageError('scanning with zero step width')
    values = [[(Q[0]+i*dQ[0], Q[1]+i*dQ[1], Q[2]+i*dQ[2], Q[3]+i*dQ[3])]
               for i in range(numsteps)]
    if plotval == 'res':
        resscan(*(p[0] for p in values), kf=kwargs.get('kf'), ki=kwargs.get('ki'))
    elif plotval == 'hkl':
        hklplot(scan=[p[0] for p in values], kf=kwargs.get('kf'), ki=kwargs.get('ki'))
    else:
        scan = QScan(values, move, multistep, detlist, envlist, preset, scaninfo)
        scan.run()


@usercommand
@helparglist('Q, dQ, numperside, ...')
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
        resscan(*(p[0] for p in values), kf=kwargs.get('kf'), ki=kwargs.get('ki'))
    elif plotval == 'hkl':
        hklplot(scan=[p[0] for p in values], kf=kwargs.get('kf'), ki=kwargs.get('ki'))
    else:
        scan = QScan(values, move, multistep, detlist, envlist, preset, scaninfo)
        scan.run()

qscan.__doc__  += ADDSCANHELP2.replace('scan(dev, ', 'qscan(Q, dQ, ')
qcscan.__doc__ += ADDSCANHELP2.replace('scan(dev, ', 'qcscan(Q, dQ, ')


class Q(ndarray):
    def __repr__(self):
        return str(self)

_Q = Q

@usercommand
@helparglist('[h, k, l, E]')
def Q(*args, **kwds): # pylint: disable=E0102
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


@usercommand
@helparglist('h, k, l, E[, SC]')
def calpos(*args):
    """Calculate instrument position for a given (Q, E) position.

    Can be called with 3 to 5 arguments:

    >>> calpos(1, 0, 0)             # H, K, L
    >>> calpos(1, 0, 0, -4)         # H, K, L, E
    >>> calpos(1, 0, 0, -4, 2.662)  # H, K, L, E, scanconstant

    or with a Q-E vector:

    >>> calpos(Q(1, 0, 0, -4))         # Q-E vector
    >>> calpos(Q(1, 0, 0, -4), 2.662)  # Q-E vector and scanconstant
    """
    instr = session.instrument
    if not isinstance(instr, TAS):
        raise NicosError('your instrument device is not a triple axis device')
    if len(args) == 1:
        assert isinstance(args[0], (tuple, _Q))
        pos = tuple(args[0]) + (instr.scanconstant,)
    elif len(args) == 2:
        assert isinstance(args[0], (tuple, _Q))
        pos = tuple(args[0]) + (args[1],)
    elif len(args) == 3:
        pos = args + (0, instr.scanconstant)
    elif len(args) == 4:
        pos = args + (instr.scanconstant,)
    elif len(args) == 5:
        pos = args
    else:
        raise UsageError('calpos() takes at least one argument')
    return instr._calpos(pos)


@usercommand
@helparglist('[h, k, l, E[, SC]]')
def pos(*args):
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
    elif len(args) == 1:
        assert isinstance(args[0], (tuple, _Q))
        pos = tuple(args[0]) + (instr.scanconstant,)
    elif len(args) == 2:
        assert isinstance(args[0], (tuple, _Q))
        pos = tuple(args[0]) + (args[1],)
    elif len(args) == 3:
        pos = args + (0, instr.scanconstant)
    elif len(args) == 4:
        pos = args + (instr.scanconstant,)
    elif len(args) == 5:
        pos = args
    else:
        raise UsageError('pos() takes no arguments or 3-5 arguments')
    if pos[-1] != instr.scanconstant:
        instr.scanconstant = pos[-1]
    maw(instr, pos[:-1])


@usercommand
def rp():
    """Read the current (Q, E) position.

    Example:

    >>> rp()
    """
    instr = session.instrument
    if not isinstance(instr, TAS):
        raise NicosError('your instrument device is not a triple axis device')
    read(instr)


@usercommand
@helparglist('h, k, l, E[, SC]')
def acc_bragg(h, k, l, ny, sc=None):
    """Check accidental Bragg scattering conditions for type A or type M.

    Accidental Bragg scattering is checked at the given spectrometer position.
    """
    instr = session.instrument
    if sc is None:
        sc = instr.scanconstant
    res = instr._calpos([h, k, l, ny, sc], printout=False)
    if res is None:
        return
    # type M spurion given if falls on lattice vector
    hkl = tuple(instr._calhkl([res[1], res[1], res[2], res[3]]))
    printinfo('calculated lattice vector for type M spurion condition: '
              '[%.3f, %.3f, %.3f]' % hkl)
    # type A spurion given if falls on lattice vector
    hkl = tuple(instr._calhkl([res[0], res[0], res[2], res[3]]))
    printinfo('calculated lattice vector for type A spurion condition: '
              '[%.3f, %.3f, %.3f]' % hkl)
    printinfo('if one of the two above lattice vectors correspond to a Bragg '
              'peak, accidental Bragg scattering may occur')


@usercommand
@helparglist('[kf[, dEmin, dEmax]]')
def ho_spurions(kf=None, dEmin=0, dEmax=20):
    """Calculation of elastic spurions due to higher order neutrons.

    *kf* is the final wavevector to use for calculation.  *dEmin* and *dEmax*
    are the minimum and maximum energy transfer to list.
    """
    instr = session.instrument
    if kf is None:
        kf = instr._adevs['ana'].read()
    printinfo('calculation of potential weak spurions due to higher harmonic '
              'ki / kf combinations')
    printinfo('calculated for kf = %6.3f A-1' % kf)
    spurlist = []
    for nA in range(1, 6):
        for nM in range(1, 6):
            dE = (nA**2/float(nM)**2 - 1) * 2.0725 * kf**2
            spurlist.append((dE, nM, nA))
    spurlist.sort()
    for item in spurlist:
        if dEmin <= item[0] <= dEmax:
            printinfo('potential spurion at energy transfer %6.3f meV for '
                      '%d ki = %d kf ' % item)


@usercommand
@helparglist('[ki, phi]')
def alu(ki=None, phi=None):
    """Print powder ray positions of Al."""
    alu_hkl = {'1,1,1': 2.3375,
               '2,0,0': 2.0242,
               '2,2,0': 1.4316,
               '3,1,1': 1.2207,
               '2,2,2': 1.1687,
               '4,0,0': 1.0123}
    powderrays(alu_hkl, ki, phi)


@usercommand
@helparglist('[ki, phi]')
def copper(ki=None, phi=None):
    """Print powder ray positions of Cu."""
    cop_hkl = {'1,1,1': 2.0874,
               '2,0,0': 1.8076,
               '2,2,0': 1.2781,
               '3,1,1': 1.0899,
               '2,2,2': 1.0435,
               '4,0,0': 0.9038}
    powderrays(cop_hkl, ki, phi)


def powderrays(dlist, ki=None, phi=None):
    """Calculate powder ray positions."""
    instr = session.instrument
    if ki is None:
        ki = instr._adevs['mono'].read()
    lines1_list = {}
    lines2_list = {}

    for reflex, dvalue in dlist.items():
        try:
            twotheta = 2 * asin(pi / ki / dvalue) * 180 / pi
            if twotheta < 135:
                lines1_list[reflex] = twotheta
        except ValueError:
            pass
        try:
            twotheta = 2 * asin(pi / ki / 2 / dvalue) * 180 / pi
            if twotheta < 135:
                lines2_list[reflex] = twotheta
        except ValueError:
            pass

    if phi is not None:
        for my_line in lines1_list.keys():
            if abs(lines1_list[my_line] - phi) < 2:
                printinfo('warning: powder line: %s at %6.3f deg' %
                          (my_line, lines1_list[my_line]))
        for my_line in lines2_list.keys():
            if abs(lines2_list[my_line] - phi) < 2:
                printinfo('warning: powder line from 2ki: %s at %6.3f deg' %
                          (my_line, lines2_list[my_line]))

    printinfo('found powder lines for ki = %5.3f A-1:' % ki)
    for my_line, angle in lines1_list.items():
        printinfo(' %s at %7.3f deg' % (my_line, angle))
    printinfo('found powder lines for 2ki = %5.3f A-1:' % (2 * ki))
    for my_line, angle in lines2_list.items():
        printinfo(' %s at %7.3f deg' % (my_line, angle))


def _create_resmat(args, kwds):
    from nicos.tas.rescalc import resmat

    instr = session.instrument
    cell = instr._adevs['cell']

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

    pars = {
        'dm': instr._adevs['mono'].dvalue,
        'da': instr._adevs['ana'].dvalue,
        'sm': instr.scatteringsense[0],
        'ss': instr.scatteringsense[1],
        'sa': instr.scatteringsense[2],
        'etam': instr._adevs['mono'].mosaic * 60,
        'etas': cell.mosaic * 60,
        'etaa': instr._adevs['ana'].mosaic * 60,
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
        'en': pos[3] if instr.energytransferunit == 'meV' else pos[3] * THZ2MEV,
    }

    return resmat(**pars)


@usercommand
@helparglist('[h, k, l[, E]] [, ki|kf=const]')
def rescal(*args, **kwds):
    """Calculate and print resolution at the current or the given Q/E point.

    Example:

    >>> rescal()           # display resolution at current Q/E point
    >>> rescal(1, 1, 0)    # display resolution at the given point
    >>> rescal(1, 1, 0, 5, kf=2.662)  # at the given point with const kf = 2.662

    Obviously, several sample and spectrometer parameters must be set correctly
    for the resolution calculation to work.
    """
    print _create_resmat(args, kwds)


@usercommand
@helparglist('[h, k, l[, E]] [, ki|kf=const]')
def resplot(*args, **kwds):
    """Calculate and plot resolution at the current or the given Q/E point.

    Example:

    >>> resplot()           # plot resolution at current Q/E point
    >>> resplot(1, 1, 0)    # plot resolution at the given point
    >>> resplot(1, 1, 0, 5, kf=2.662) # at the given point with const kf = 2.662

    Obviously, several sample and spectrometer parameters must be set correctly
    for the resolution calculation to work.
    """
    from nicos.tas.plotting import plot_ellipsoid
    resmat = _create_resmat(args, kwds)
    printinfo('plotting resolution in separate window, please wait...')
    plot_ellipsoid(resmat)


@hiddenusercommand
@helparglist('hkle1, hkle2, ...')
def resscan(*hkles, **kwds):
    """Calculate and plot resolution at every given point.

    This is usually used via the `qscan()` and `qcscan()` commands with the
    plot='res' parameter.
    """
    from nicos.tas.plotting import plot_scan
    resmat = _create_resmat(hkles[0], kwds)
    printinfo('plotting scan resolution in separate window, please wait...')
    plot_scan(resmat, hkles)


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
    """
    from nicos.tas.plotting import SpaceMap
    resmat = _create_resmat((), kwds)
    SpaceMap(session.instrument, resmat, **kwds).plot_map()
