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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Module with specific commands for POLI."""

import csv
import math
import subprocess
from os import path

from nicos import session
from nicos.commands import usercommand, helparglist, parallel_safe
from nicos.commands.basic import Remark
from nicos.commands.device import maw, move, read
from nicos.commands.scan import cscan, contscan, _infostr
from nicos.commands.analyze import center_of_mass, gauss
from nicos.devices.sxtal.instrument import SXTalBase
from nicos.devices.sxtal.xtal.orientation import orient
from nicos.core import Readable, Measurable, Moveable, UsageError, NicosError
from nicos.core.constants import SIMULATION
from nicos.core.spm import spmsyntax, Bare
from nicos.core.scan import Scan, CONTINUE_EXCEPTIONS, SKIP_EXCEPTIONS
from nicos.pycompat import number_types, iteritems, string_types
from nicos.utils import printTable, createSubprocess

__all__ = [
    'lubricate_liftingctr',
    'centerpeak',
    'NewHeCell',
    'calpos',
    'pos',
    'rp',
    'qscan',
    'qcscan',
    'omscan',
    'PosListClear',
    'PosListDefine',
    'PosListAdd',
    'PosListShow',
    'PosListRemove',
    'IndexPeaks',
    'AcceptIndexing',
    'RefineMatrix',
    'AcceptRefinement',
    'GenDataset',
    'ScanDataset',
]


@usercommand
def lubricate_liftingctr(startpos, endpos):
    """Lubricate the lifting counter, while starting from *startpos* and
    moving to *endpos*.

    Example:

    >>> lubricate_liftingctr(0, 20)
    """
    ldev = session.getDevice('lubrication')
    motor = session.getDevice('liftingctr')
    maw(motor, startpos)
    session.log.info('Switching output on for 10 sec...')
    move(ldev, 1)
    session.delay(10)
    move(ldev, 0)
    session.log.info('Waiting 15 sec...')
    session.delay(15)
    maw(motor, endpos)
    session.log.info('Lubrication is done.')


@usercommand
@helparglist('device1, device2, ..., [rounds=N], [steps=N], [steps_device1=N],'
             ' [step=stepsize], [step_device1=stepsize], [fit="func"], '
             '[cont=True], [convergence=C], [preset]')
def centerpeak(*args, **kwargs):
    """Center a peak with multiple scans over multiple devices.

    This does repeated scans of all devices to iteratively center a peak until
    the peak center does not shift anymore.  Starting position is the current
    position of all devices.

    Non-keyword arguments are devices to scan over. At least one is required.

    Supported keyword arguments are:

    * ``rounds`` - maximum number of rounds (a round is one scan per device).
      The default is 5.
    * ``steps`` - number of steps per side for each scan. The default is 15.
    * ``steps_devname`` - special number of steps per side for this device.
    * ``step`` - step size for each scan. The default is 0.1.
    * ``step_devname`` - special step size for this device.
    * ``convergence`` - maximum delta of peak center between two scans of a
      device, in units of the scan step size. The default is 0.5.
    * ``fit`` - fit function to use for determining peak center, see below.
    * ``cont`` - True/False whether to use continuous scans. Default is false.
    * all further keyword arguments (like ``t=1``) are used as detector
      presets.

    Examples::

       # default scan without special options, count 2 seconds
       >>> centerpeak(omega, gamma, 2)
       # scan with device-specific step size and number of steps
       >>> centerpeak(omega, gamma, step_omega=0.05, steps_omega=20, t=1)
       # allow a large number of rounds with very small convergence window
       # (1/5 of step size)
       >>> centerpeak(omega, gamma, rounds=10, convergence=0.2, t=1)
       # center using Gaussian peak fits
       >>> centerpeak(omega, gamma, fit='gauss', t=1)

    Fit functions:

    * ``'center_of_mass'``: default, works for any peak shape
    * ``'gauss'``: symmetric Gaussian
    """
    nrounds = 5
    devices = []
    defsteps = 15
    nsteps = {}
    defstepsize = 0.1
    stepsizes = {}
    preset = {}
    fit = 'center_of_mass'
    allowed_fit = set(['center_of_mass', 'gauss'])
    continuous = False
    convergence = 0.5
    for devname in args:
        if isinstance(devname, number_types):
            preset['t'] = devname
        else:
            devices.append(session.getDevice(devname, Moveable))
    if not devices:
        raise UsageError('need at least one device to scan over')
    for kw, value in kwargs.items():
        if kw == 'rounds':
            nrounds = value
        elif kw == 'fit':
            if value not in allowed_fit:
                raise UsageError('fit function %s is not allowed' % value)
            fit = value
        elif kw == 'convergence':
            convergence = value
        elif kw == 'steps':
            defsteps = value
        elif kw == 'step':
            defstepsize = value
        elif kw == 'cont':
            continuous = bool(value)
        elif kw.startswith('step_'):
            dev = session.getDevice(kw[5:], Moveable)
            if dev not in devices:
                raise UsageError('device %s not in list of devices to scan' %
                                 dev)
            stepsizes[dev] = value
        elif kw.startswith('steps_'):
            dev = session.getDevice(kw[6:], Moveable)
            if dev not in devices:
                raise UsageError('device %s not in list of devices to scan' %
                                 dev)
            nsteps[dev] = value
        else:
            preset[kw] = value
    for dev in devices:
        if dev not in stepsizes:
            stepsizes[dev] = defstepsize
        if dev not in nsteps:
            nsteps[dev] = defsteps

    # main loop
    lastround = dict((dev, dev.read()) for dev in devices)
    for i in range(nrounds):
        session.log.info('Round %d of %d', i + 1, nrounds)
        session.log.info('*' * 100)
        # results of last round
        thisround = {}
        for dev in devices:
            center = lastround[dev]
            if continuous:
                contscan(dev, center - nsteps[dev] * stepsizes[dev],
                         center + nsteps[dev] * stepsizes[dev],
                         speed=stepsizes[dev] / preset.get('t', 1),
                         timedelta=preset.get('t', 1))
            else:
                cscan(dev, center, stepsizes[dev], nsteps[dev], *devices,
                      **preset)
            if session.mode == SIMULATION:
                thisround[dev] = center
            elif fit == 'center_of_mass':
                thisround[dev] = center_of_mass()
            elif fit == 'gauss':
                params, _ = gauss()
                minvalue = center - abs(stepsizes[dev] * nsteps[dev])
                maxvalue = center + abs(stepsizes[dev] * nsteps[dev])
                if params is None:
                    maw(dev, center)
                    session.log.error('no Gaussian fit found in this scan')
                    return
                fit_center = params[0]
                if math.isnan(fit_center) or \
                   not minvalue <= fit_center <= maxvalue:
                    maw(dev, center)
                    session.log.error('Gaussian fit center outside '
                                      'scanning area')
                    return
                thisround[dev] = fit_center
            maw(dev, thisround[dev])
        session.log.info('*' * 100)
        again = False
        for dev in devices:
            diff = abs(lastround[dev] - thisround[dev])
            session.log.info('%-10s center: %8.6g -> %8.6g (delta %8.6g)',
                             dev, lastround[dev], thisround[dev], diff)
            if session.mode == SIMULATION:
                again = i < 1
                if i == 1:
                    session.log.info('=> dry run: limiting to 2 rounds')
            elif diff > convergence * stepsizes[dev]:
                if i == nrounds - 1:
                    session.log.info('=> would need another round, but command'
                                     ' limited to %d rounds', nrounds)
                else:
                    session.log.info('=> needs another round')
                again = True
        if not again:
            session.log.info('=> found convergence on peak:')
            for dev in devices:
                session.log.info('%-10s : %s', dev, dev.format(dev()))
            return
        lastround = thisround


@usercommand
def NewHeCell(m1, m2, pressure, length=13.0, T0=0.88):
    """Notify NICOS of a newly installed Helium-3 polarizer cell.

    - *m1* and *m2* should be monitor counts of the *before* and *after*
      monitors taken without the cell installed.
    - *pressure* is the He pressure in the cell, in bar.
    - *length* is the length of the cell, in cm.
    - *T0* is the transmission of the empty cell.

    Example:

    >>> NewHeCell(12000, 8000, 2.4)
    """
    session.getDevice('beam_pol').newCell(m1, m2, pressure, length, T0)


def _convert_q_arg(args, funcname):
    nargs = len(args)
    try:
        # is first arg a sequence?
        narg1 = len(args[0])
    except TypeError:
        # no: expect 3 single number arguments
        if nargs == 3:
            return args
    else:
        # yes: sequence with 3 items
        if narg1 == 3:
            return tuple(args[0])
    # fallthrough for any invalid combination
    raise UsageError('invalid arguments for %s()' % funcname)


@usercommand
@helparglist('h, k, l')
@parallel_safe
def calpos(*args):
    """Calculate instrument position for a given Q position.

    Can be called with 3 arguments:

    >>> calpos(1, 0, 0)           # H, K, L

    or with a Q vector:

    >>> calpos([1, 0, 0])         # Q-E vector
    """
    instr = session.instrument
    if not isinstance(instr, SXTalBase):
        raise NicosError('your instrument is not a sxtal diffractometer')
    if not args:
        raise UsageError('calpos() takes at least one argument')
    pos = _convert_q_arg(args, 'calpos')
    instr._calpos(pos)


@usercommand
@helparglist('[gamma, omega, nu]')
@parallel_safe
def pos2hkl(gamma=None, omega=None, nu=None):
    """Calculate Q for a given instrument position.

    Without arguments, prints the current Q.  ``rp()`` is an alias.

    >>> pos2hkl()
    >>> rp()

    The optional arguments are different instrument angles:

    >>> pos2hkl(15.0, 72.4, -4.0)

    calculates not for the current position, but for the given gamma, omega, nu
    angles.
    """
    instr = session.instrument
    if not isinstance(instr, SXTalBase):
        raise NicosError('your instrument is not a sxtal diffractometer')
    if not gamma:
        read(instr)
    else:
        if omega is None or nu is None:
            raise UsageError('must give either no angles or all angles')
        instr._reverse_calpos(gamma=gamma, omega=omega, nu=nu)

rp = pos2hkl


@usercommand
@helparglist('[h, k, l]')
def pos(*args, **kwds):
    """Move the instrument to a given Q, or the last `calpos()` position.

    Without arguments, moves to the last position sucessfully calculated with
    `calpos()`.  Examples:

    >>> pos()                       # last calpos() position
    >>> pos(1, 0, 0)                # H, K, L
    """
    instr = session.instrument
    if not isinstance(instr, SXTalBase):
        raise NicosError('your instrument is not a sxtal diffractometer')
    if not args:
        pos = instr._last_calpos
        if pos is None:
            raise NicosError('pos() with no arguments moves to the last '
                             'position calculated by calpos(), but no such '
                             'position has been stored')
    else:
        pos = _convert_q_arg(args, 'pos')
        instr._calpos(pos, checkonly=False)
    maw(instr, pos[:4])


def _getQ(v, name):
    try:
        if len(v) == 3:
            return list(v)
        else:
            raise TypeError
    except TypeError:
        raise UsageError('%s must be a sequence of (h, k, l)' % name)


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
        elif key == 'dh' or key == 'dH':
            dQ[0] = value
        elif key == 'dk' or key == 'dK':
            dQ[1] = value
        elif key == 'dl' or key == 'dL':
            dQ[2] = value
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


class QScan(Scan):
    """
    Special scan class for scans with a sxtal instrument in Q space.
    """

    def __init__(self, positions, firstmoves=None, multistep=None,
                 detlist=None, envlist=None, preset=None, scaninfo=None,
                 subscan=False):
        inst = session.instrument
        if not isinstance(inst, SXTalBase):
            raise NicosError('cannot do a Q scan, your instrument device '
                             'is not a sxtal device')
        Scan.__init__(self, [inst], positions, [],
                      firstmoves, multistep, detlist, envlist, preset,
                      scaninfo, subscan)
        self._envlist[0:0] = [inst._attached_gamma,
                              inst._attached_omega, inst._attached_nu]
        if inst in self._envlist:
            self._envlist.remove(inst)

    def shortDesc(self):
        comps = []
        if len(self._startpositions) > 1:
            for i in range(3):
                if self._startpositions[0][0][i] != \
                   self._startpositions[1][0][i]:
                    comps.append('HKL'[i])
        if self.dataset and self.dataset.counter > 0:
            return 'Scan %s #%s' % (','.join(comps) or 'Q',
                                    self.dataset.counter)
        return 'Scan %s' % (','.join(comps) or 'Q')

    def beginScan(self):
        if len(self._startpositions) > 1:
            # determine first varying index as the plotting index
            for i in range(3):
                if self._startpositions[0][0][i] != \
                   self._startpositions[1][0][i]:
                    self._xindex = i
                    break
        Scan.beginScan(self)


@usercommand
@helparglist('Q, dQ, numpoints, ...')
@spmsyntax(Bare, Bare, Bare)
def qscan(Q, dQ, numpoints, *args, **kwargs):
    """Perform a single-sided Q step scan.

    The *Q* and *dQ* arguments should be lists of 3 components.

    Example:

    >>> qscan((1, 0, 0), (0, 0, 0.1), 11, mon1=100000)

    will perform an L scan at (100) with the given monitor counts per point.
    """
    Q, dQ = _getQ(Q, 'Q'), _getQ(dQ, 'dQ')
    scanstr = _infostr('qscan', (Q, dQ, numpoints) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep, Q, dQ = \
        _handleQScanArgs(args, kwargs, Q, dQ, scanstr)
    if all(v == 0 for v in dQ) and numpoints > 1:
        raise UsageError('scanning with zero step width')
    values = [[(Q[0]+i*dQ[0], Q[1]+i*dQ[1], Q[2]+i*dQ[2])]
              for i in range(numpoints)]
    scan = QScan(values, move, multistep, detlist, envlist, preset, scaninfo)
    scan.run()


@usercommand
@helparglist('Q, dQ, numperside, ...')
@spmsyntax(Bare, Bare, Bare)
def qcscan(Q, dQ, numperside, *args, **kwargs):
    """Perform a centered Q step scan.

    The *Q* and *dQ* arguments should be lists of 3 components.

    Example:

    >>> qcscan((1, 0, 0), (0.001, 0, 0), 20, mon1=1000)

    will perform a longitudinal scan around (100) with the given monitor counts
    per point.
    """
    Q, dQ = _getQ(Q, 'Q'), _getQ(dQ, 'dQ')
    scanstr = _infostr('qcscan', (Q, dQ, numperside) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep, Q, dQ = \
        _handleQScanArgs(args, kwargs, Q, dQ, scanstr)
    if all(v == 0 for v in dQ) and numperside > 0:
        raise UsageError('scanning with zero step width')
    values = [[(Q[0]+i*dQ[0], Q[1]+i*dQ[1], Q[2]+i*dQ[2])]
              for i in range(-numperside, numperside+1)]
    scan = QScan(values, move, multistep, detlist, envlist, preset,
                 scaninfo)
    scan.run()


@usercommand
@helparglist('hkl, [width], [speed], [timedelta]')
def omscan(hkl, width=None, speed=None, timedelta=None, **kwds):
    """Perform a continuous omega scan at the specified Q point.

    The default scan width is calculated from the instrumental resolution.

    Examples:

    >>> omscan((1, 0, 0))     # with default with, speed and timedelta
    >>> omscan((1, 0, 0), 5)  # with a width of 5 degrees
    >>> omscan((1, 0, 0), 5, 0.1, 1)   # with width, speed and timedelta
    """
    instr = session.instrument
    if not isinstance(instr, SXTalBase):
        raise NicosError('your instrument is not a sxtal diffractometer')
    if width is None:
        width = instr.getScanWidthFor(hkl)
    calc = dict(instr._extractPos(instr._calcPos(hkl)))
    om1 = calc['omega'] - width / 2.
    om2 = calc['omega'] + width / 2.
    cur_om = instr._attached_omega.read()
    if abs(cur_om - om1) > abs(cur_om - om2):
        om1, om2 = om2, om1
    maw(instr._attached_gamma, calc['gamma'],
        instr._attached_nu, calc['nu'],
        instr._attached_omega, om1)
    contscan(instr._attached_omega, om1, om2, speed, timedelta)


@usercommand
@helparglist('[listname]')
def PosListClear(listname='default'):
    """Clear the position list with given name.

    Examples:

    >>> PosListClear()         # clear default position list
    >>> PosListClear('other')  # clear named position list
    """
    sample = session.experiment.sample
    lists = dict(sample.poslists)
    if listname not in lists:
        session.log.info('Created new position list %r', listname)
    else:
        session.log.info('Cleared position list %r', listname)
    lists[listname] = []
    sample.poslists = lists


@usercommand
@helparglist('[listname]')
def PosListShow(listname='default'):
    """Show the positions in the given position list.

    Examples:

    >>> PosListShow()         # show default position list
    >>> PosListShow('other')  # show named position list
    """
    sample = session.experiment.sample
    instr = session.instrument
    lists = dict(sample.poslists)
    if listname not in lists:
        session.log.warning('Position list %r does not exist', listname)
        return
    if not lists[listname]:
        session.log.info('<empty>')
        return
    items = []
    R2D = math.degrees
    for i, item in enumerate(lists[listname]):
        calcpos = instr._calcPos(item[1]) if item[1] is not None else None
        items.append((
            '%d' % (i + 1),
            '%.3f' % R2D(item[0].gamma),
            '%.3f' % R2D(item[0].omega),
            '%.3f' % R2D(item[0].nu),
            '%.1f' % item[2][0],
            '%.1f' % item[2][1],
            '' if item[1] is None else '%.4g' % item[1][0],
            '' if item[1] is None else '%.4g' % item[1][1],
            '' if item[1] is None else '%.4g' % item[1][2],
            '' if calcpos is None else '%.3f' % R2D(calcpos.gamma),
            '' if calcpos is None else '%.3f' % R2D(calcpos.omega),
            '' if calcpos is None else '%.3f' % R2D(calcpos.nu),
        ))
    printTable(('pos#',
                u'γ', u'ω', u'ν', u'I', u'σ(I)',
                'h', 'k', 'l',
                u'γ_calc', u'ω_calc', u'ν_calc'),
               items, session.log.info, rjust=True)


def _add_to_pos_list(pos, intensity, args):
    listname = 'default'
    sigma = hkl = None
    for arg in args:
        if isinstance(arg, string_types):
            listname = arg
        elif isinstance(arg, number_types):
            sigma = arg
        else:
            hkl = arg
    if sigma is None:
        sigma = math.sqrt(intensity)
    if not isinstance(intensity, (int, float)):
        raise UsageError('Intensity must be a number')
    if hkl is not None:
        hkl = list(hkl)
        if len(hkl) != 3:
            raise UsageError('HKL must be a list of 3 indices')
    sample = session.experiment.sample
    lists = dict(sample.poslists)
    if listname not in lists:
        session.log.info('Created new position list %r', listname)
        lists[listname] = []
    lists[listname] = lists[listname] + [(pos, hkl, (intensity, sigma))]
    sample.poslists = lists
    session.log.info('Position list %r is now:', listname)
    PosListShow(listname)


@usercommand
@helparglist('gamma, omega, nu, intensity, [hkl], [sigma], [listname]')
def PosListDefine(gamma, omega, nu, intensity, *args):
    """Add current position to the position list with given intensity.

    With an argument like ``(h, k, l)``, the peak will be identified with the
    given indices.

    The *sigma* parameter can also be given as the intensity error.

    Examples:

    >>> PosListDefine(28.14, 56.7, -4.3, 1000)
    >>> PosListDefine(28.14, 56.7, -4.3, 1000, 100)  # with sigma intensity
    >>> PosListDefine(28.14, 56.7, -4.3, 1000, 'list')  # with peak list
    >>> PosListDefine(28.14, 56.7, -4.3, 1000, (1, 0, 0))  # with HKL
    """
    pos = session.instrument._createPos(gamma=gamma, omega=omega, nu=nu)
    _add_to_pos_list(pos, intensity, args)


@usercommand
@helparglist('intensity, [hkl], [sigma], [listname]')
def PosListAdd(intensity, *args):
    """Add current position to the position list with given intensity.

    With an argument like ``(h, k, l)``, the peak will be identified with the
    given indices.

    The *sigma* parameter can also be given as the intensity error.

    Examples:

    >>> PosListAdd(1000)           # add current instrument position
    >>> PosListAdd(1000, 10)       # same, with I = 1000 and sigmaI = 10
    >>> PosListAdd(1000, 'other')  # add to named (non default) position list
    >>> PosListAdd(1000, 'other', (1, 0, 0))  # with given HKL and list name
    """
    pos = session.instrument._readPos()
    _add_to_pos_list(pos, intensity, args)


@usercommand
@helparglist('index, [listname]')
def PosListRemove(idx, listname='default'):
    """Remove position from a position list.

    Examples:

    >>> PosListRemove(1)           # remove first position from default list
    >>> PosListRemove(2, 'other')  # remove second pos from named position list
    """
    sample = session.experiment.sample
    lists = dict(sample.poslists)
    if listname not in lists:
        session.log.warning('Position list %r does not exist', listname)
        return
    if idx < 1 or idx > len(lists[listname]):
        session.log.warning('Position list does not have %d entries', idx)
        return
    lists[listname] = [e for (i, e) in enumerate(lists[listname])
                       if i != idx - 1]
    sample.poslists = lists
    session.log.info('Position list %r is now:', listname)
    PosListShow(listname)


@usercommand
@helparglist('[max_deviation], [listname]')
def IndexPeaks(max_deviation=0.2, listname='default'):
    """Index crystal reflections using Indexus.

    Uses the positions and intensities either the default position list, or the
    given name.

    You can also select the maximum deviation of HKL indices from integers
    using the *max_deviation* parameter (default is 0.2).

    After indexing is complete, the calculated HKLs and matrix are shown.
    You can accept the indexing with the `AcceptIndexing()` command.

    Examples:

    >>> IndexPeaks()            # use default position list
    >>> IndexPeaks(0.1)         # use different maximum deviation
    >>> IndexPeaks('other')     # use other position list

    This command will generate input files for Indexus (indexus.txt and
    angles.txt) in the experiment data directory and run Indexus.  Then it will
    read the output files and show the calculated matrix and positions, as well
    as the gamma/nu offsets.

    If you want to manually run Indexus, you can use the generated input files
    as a template.
    """
    if isinstance(max_deviation, string_types):
        listname = max_deviation
        max_deviation = 0.2
    sample = session.experiment.sample
    wavelength = session.getDevice('wavelength').read()
    lists = dict(sample.poslists)
    if listname not in lists:
        session.log.warning('Position list %r does not exist', listname)
        return
    posl = lists[listname]
    if len(posl) < 2:
        session.log.warning('Cannot calculate: need at least two positions in list')
        return
    params = (
        len(posl),
        1.0, 1.0,
        max_deviation,
        wavelength,
        sample.bravais,
        sample.a, sample.b, sample.c, sample.alpha, sample.beta, sample.gamma,
    )

    # write input file for Indexus
    root = session.experiment.samplepath
    with open(path.join(root, 'indexus.txt'), 'w') as fp:
        fp.write('''\
poli                             ! instrument
n                                ! extended output
%d                               ! num of spots
%f %f                            ! delta theta, delta angle
%f                               ! max deviation
%f                               ! wavelength
%s                               ! lattice type
%.4f %.4f %.4f  %.3f %.3f %.3f   ! lattice parameters
.0 .1 -1.0 1.0                   ! offset gamma, step, low and high limits
.0 .1 -1.0 1.0                   ! offset nu, step, low and high limits
''' % params)
    R2D = math.degrees
    with open(path.join(root, 'angles.txt'), 'w') as fp:
        fp.write('   gamma    omega       nu        I     sigI\n')
        for pos, _hkl, (intensity, sigma) in posl:
            fp.write('%8.3f %8.3f %8.3f %8.2f %8.2f\n' % (
                R2D(pos.gamma), R2D(pos.omega), R2D(pos.nu), intensity, sigma))

    session.log.info('Running Indexus...')
    proc = createSubprocess(['indexus'], cwd=root, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    output = proc.communicate()[0]
    if 'unable to find solution' in output:
        session.log.warning('Indexus could not find a solution.')
        IndexPeaks._last_result = None
        return

    # read output from Indexus
    p1, p2 = None, None
    table = []
    peaks = []
    dgamma = 0.
    dnu = 0.
    chi2 = 0.
    with open(path.join(root, 'indexus.lis'), 'r') as fp:
        lines = iter(fp)
        for line in lines:
            if line.startswith(' best combination:'):
                parts = line.split()
                p1, p2 = int(parts[2]) - 1, int(parts[4]) - 1
            elif line.startswith(' offset gamma:'):
                dgamma = float(line.split()[2])
            elif line.startswith(' offset nu:'):
                dnu = float(line.split()[2])
            elif line.startswith(' chi2:'):
                chi2 = float(line.split()[1])
            elif line.startswith(' list:'):
                session.log.info('Indexed reflections:')
                for i, line in enumerate(lines):
                    if not line.strip():  # empty line after table
                        break
                    cols = line.strip().strip('*').split()
                    if cols[0] == 'H':   # header
                        continue
                    peaks.append([float(ix) for ix in cols[:3]])
                    table.append([str(i)] + cols)
                break
    printTable(('pos#', 'h', 'k', 'l', u'γ', u'ω', u'ν', u'I', u'σ(I)'),
               table, session.log.info, rjust=True)

    # calculate UB matrix from "best combination" of two peaks
    or_calc = orient(*sample.cell.cellparams())
    pos1 = posl[p1][0]
    pos2 = posl[p2][0]
    hkl1 = [int(round(ix)) for ix in peaks[p1]]
    hkl2 = [int(round(ix)) for ix in peaks[p2]]
    new_cell = or_calc.Reorient(hkl1, pos1, hkl2, pos2)
    IndexPeaks._last_result = (new_cell.rmat.T, (dgamma, dnu), listname, peaks)
    session.log.info('Using (%.4g %.4g %.4g) and (%.4g %.4g %.4g) to calculate'
                     ' UB matrix:', *(tuple(hkl1) + tuple(hkl2)))
    for row in new_cell.rmat.T:
        session.log.info(' %8.4f %8.4f %8.4f', *row)
    session.log.info('')
    session.log.info('Fit quality χ²: %8.4f', chi2)
    session.log.info('')
    session.log.info('Offsets:')
    session.log.info('  delta gamma = %8.4f   delta nu = %8.4f', dgamma, dnu)
    session.log.info('')
    session.log.info('Use AcceptIndexing() to use this indexing.')

IndexPeaks._last_result = None


@usercommand
def AcceptIndexing():
    """Accept the last indexing performed by `IndexPeaks()`.

    Calculates the UB matrix for the sample from the peaks and their positions.

    Example:

    >>> AcceptIndexing()
    """
    if IndexPeaks._last_result is None:
        session.log.error('No indexing performed yet.')
        return

    # apply calculated matrix to sample
    sample = session.experiment.sample
    b, l = sample.bravais, sample.laue
    ubmat, _offsets, listname, peaks = IndexPeaks._last_result
    sample.cell = (ubmat, b, l)

    # apply indexing to position list (for later refinement)
    lists = dict(sample.poslists)
    if listname not in lists:
        session.log.warning('Position list %r does not exist anymore',
                            listname)
        return
    posl = list(lists[listname])
    if len(posl) != len(peaks):
        session.log.warning('Position list %r changed after indexing',
                            listname)
        return
    for i in range(len(posl)):
        posl[i] = (posl[i][0],
                   [int(round(ix)) for ix in peaks[i]],
                   posl[i][2])
    lists[listname] = posl
    sample.poslists = lists


@usercommand
def GenDataset(name, hmax, kmax, lmax, uniq=False):
    """Generate a dataset of HKL indices to measure, as a CSV file.

    This will generate a ``.csv`` file with the given *name* in the experiment
    data directory and populate it with all HKL reflections reachable for the
    current sample orientation in the current instrument setup (including
    limits of the axes).  The maximum H, K, and L indices are given by
    *hmax*, *kmax* and *lmax*.

    If *uniq* is true, does not include symmetry equivalent reflections.

    You can view/edit the CSV file afterwards, and finally do a scan over the
    HKL list using the `ScanDataset()` command.

    Example:

    >>> GenDataset('all', 10, 10, 10)
    >>> GenDataset('unique', 10, 10, 10, True)
    """
    instr = session.instrument
    sample = session.experiment.sample
    root = session.experiment.samplepath
    session.log.info('Generating HKLs...')
    hkls = sample.cell.dataset(0, 100, uhmin=-hmax, uhmax=hmax,
                               ukmin=-kmax, ukmax=kmax,
                               ulmin=-lmax, ulmax=lmax,
                               uniq=uniq)
    all_pos = []
    for hkl in hkls:
        hkl = hkl.tolist()
        try:
            poslist = instr._extractPos(instr._calcPos(hkl))
        except Exception:
            continue
        ok = True
        posdict = {}
        for (devname, devvalue) in poslist:
            posdict[devname] = devvalue
            dev = instr._adevs[devname]
            if dev is None:
                continue
            else:
                ok &= dev.isAllowed(devvalue)[0]
        if ok:
            scanwidth = instr.getScanWidthFor(hkl)
            all_pos.append(hkl + ['%.3f' % posdict['gamma'],
                                  '%.3f' % posdict['omega'],
                                  '%.3f' % posdict['nu'],
                                  '%.1f' % scanwidth])
    session.log.info('%d of %d reflections within instrument limits.',
                     len(all_pos), len(hkls))

    fullpath = path.join(root, name + '.csv')
    with open(fullpath, 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(['h', 'k', 'l', 'gamma', 'omega', 'nu', 'width'])
        for row in all_pos:
            writer.writerow(row)

    session.log.info('Reflection list written to %s.', fullpath)


@usercommand
@helparglist('name, [speed], [timedelta]')
def ScanDataset(name, speed=None, timedelta=None, start=1):
    """Do an omega-scan over all HKL reflections in a given CSV dataset.

    Takes a CSV file created by `GenDataset()` (maybe edited) and does a
    continuous omega scan over all HKLs in the list.

    Use ``start=N`` to start at a different line than the first.

    Examples::

       # omega scan of  all peaks in "low_t" with default settings
       >>> ScanDataset('low_t')
       # same, but with speed 0.1 and timedelta 1 second
       >>> ScanDataset('low_t', 0.1, 1)
       # start at row 100
       >>> ScanDataset('low_t', start=100)
    """
    instr = session.instrument
    root = session.experiment.samplepath
    fullpath = path.join(root, name + '.csv')
    session.log.info('Reading reflection list from %s.', fullpath)

    all_pos = []
    with open(fullpath, 'r') as fp:
        reader = csv.reader(fp)
        for row in reader:
            if row[0] == 'h':
                continue
            h, k, l, _, _, _, width = row[:7]
            all_pos.append(([float(h), float(k), float(l)],
                            float(width.replace(',', '.'))))

    session.log.info('%d reflections read.', len(all_pos))

    if start != 1:
        if len(all_pos) < start:
            session.log.info('Nothing to do.')
            return
        else:
            session.log.info('Starting at reflection number %d.', start)
            all_pos = all_pos[start - 1:]

    Remark('Scan dataset %s (%d reflections)' % (name, len(all_pos)))

    skipped = 0
    for i, (hkl, width) in enumerate(all_pos, start=start):
        session.log.info('')
        info = (i, len(all_pos) + start - 1, hkl[0], hkl[1], hkl[2])
        text = '*** Scanning %d/%d: (%4.4g %4.4g %4.4g)' % info
        scope = 'HKL %d/%d: (%4.4g %4.4g %4.4g)' % info
        if skipped:
            text += ' [%d skipped]' % skipped
            scope += ' [%d skipped]' % skipped
        session.log.info(text)
        session.beginActionScope(scope)
        try:
            calc = dict(instr._extractPos(instr._calcPos(hkl)))
            om1 = calc['omega'] - width / 2.
            om2 = calc['omega'] + width / 2.
            cur_om = instr._attached_omega.read()
            if abs(cur_om - om1) > abs(cur_om - om2):
                om1, om2 = om2, om1
            umin, umax = instr._attached_omega.userlimits
            if om1 < umin:
                om1 = umin
            if om1 > umax:
                om1 = umax
            try:
                maw(instr._attached_gamma, calc['gamma'],
                    instr._attached_nu, calc['nu'],
                    instr._attached_omega, om1)
            except SKIP_EXCEPTIONS:
                session.log.warning('Skipping scan', exc=1)
                skipped += 1
                continue
            except CONTINUE_EXCEPTIONS:
                session.log.warning('Positioning problem, continuing', exc=1)
            contscan(instr._attached_omega, om1, om2, speed, timedelta,
                     '(%4.4g %4.4g %4.4g)' % info[2:])
        finally:
            session.endActionScope()


@usercommand
@helparglist('param=value, ...')
def RefineMatrix(listname='default', **kwds):
    """Refine the UB matrix with the given parameters.

    All given parameters are constant, all others are free.

    Possible parameters:

    * ``a``: first lattice parameter
    * ``b``: second lattice parameter, can also be ``'a'``
    * ``c``: third lattice parameter, can also be ``'a'``
    * ``alpha``: first angle
    * ``beta``: second angle, can also be ``'alpha'``
    * ``gamma``: third angle, can also be ``'alpha'``
    * ``wavelength``
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

    lists = dict(sample.poslists)
    if listname not in lists:
        session.log.warning('Position list %r does not exist', listname)
        return
    posl = lists[listname]
    init_lambda = instr.wavelength
    init_offsets = [instr._attached_gamma.offset, instr._attached_nu.offset]

    RefineMatrix._last_result = None
    session.log.info('Refining matrix with %d reflections from position '
                     'list...', len(posl))

    o = orient(sample.cell)
    new_cell, p = o.RefineOrientation(posl, kwds, init_lambda, ['gamma', 'nu'],
                                      init_offsets)

    session.log.info('')
    session.log.info('Cell parameters:')
    session.log.info(u'Initial:    a = %8.4f   b = %8.4f   c = %8.4f   '
                     u'α = %7.3f   β = %7.3f   γ = %7.3f',
                     *sample.cell.cellparams())
    session.log.info(u'Final:      a = %8.4f   b = %8.4f   c = %8.4f   '
                     u'α = %7.3f   β = %7.3f   γ = %7.3f',
                     p.a, p.b, p.c, p.alpha, p.beta, p.gamma)
    session.log.info(u'Errors: +/-     %8.4f       %8.4f       %8.4f   '
                     u'    %7.3f       %7.3f       %7.3f',
                     p.errors['a'], p.errors['b'], p.errors['c'],
                     p.errors['alpha'], p.errors['beta'], p.errors['gamma'])

    session.log.info('')
    session.log.info(u'Initial:    λ = %8.4f   Δγ = %7.3f   Δν = %7.3f',
                     init_lambda, *init_offsets)
    session.log.info(u'Final:      λ = %8.4f   Δγ = %7.3f   Δν = %7.3f',
                     p.wavelength, p.delta_gamma, p.delta_nu)
    session.log.info(u'Errors: +/-     %8.4f        %7.3f        %7.3f',
                     p.errors['wavelength'], p.errors['delta_gamma'],
                     p.errors['delta_nu'])

    session.log.info('')
    session.log.info(u'Reduced χ² (χ²/NDF): %8.4f', p.chi2)

    session.log.info('')
    session.log.info('New UB matrix:')
    for row in new_cell.rmat.T:
        session.log.info(' %8.4f %8.4f %8.4f', *row)

    session.log.info('')
    session.log.info('Use AcceptRefinement() to use this refined data.')

    RefineMatrix._last_result = (new_cell, p.wavelength,
                                 p.delta_gamma, p.delta_nu)

RefineMatrix._last_result = None


@usercommand
def AcceptRefinement():
    """Accept the last refinement performed by `RefineMatrix()`.

    Example:

    >>> AcceptRefinement()
    """
    sample = session.experiment.sample
    instr = session.instrument

    if RefineMatrix._last_result is None:
        session.log.error('No refinement performed yet.')
        return

    new_cell, new_wl, delta_gamma, delta_nu = RefineMatrix._last_result

    sample.cell = new_cell

    instr._attached_mono._adjust(new_wl, 'A')
    instr._attached_gamma.offset = delta_gamma
    instr._attached_nu.offset = delta_nu
