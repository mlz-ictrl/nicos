#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
from nicos.commands.device import maw, move, read
from nicos.commands.scan import cscan, contscan
from nicos.commands.analyze import center_of_mass, gauss
from nicos.commands.output import printinfo, printwarning, printerror
from nicos.devices.sxtal.instrument import SXTalBase
from nicos.devices.sxtal.xtal.orientation import orient
from nicos.core import Moveable, UsageError, NicosError, SIMULATION
from nicos.pycompat import number_types
from nicos.core.scan import CONTINUE_EXCEPTIONS, SKIP_EXCEPTIONS
from nicos.utils import printTable

__all__ = [
    'lubricate_liftingctr',
    'centerpeak',
    'calpos',
    'pos',
    'rp',
    'PosListClear',
    'PosListDefine',
    'PosListAdd',
    'PosListShow',
    'PosListRemove',
    'IndexPeaks',
    'AcceptIndexing',
    'GenDataset',
    'ScanDataset',
]


@usercommand
def lubricate_liftingctr(startpos, endpos):
    """Lubricate the lifting counter, while starting from *startpos* and
    moving to *endpos*.
    """
    ldev = session.getDevice('lubrication')
    motor = session.getDevice('liftingctr')
    maw(motor, startpos)
    printinfo('Switching output on for 10 sec...')
    move(ldev, 1)
    session.delay(10)
    move(ldev, 0)
    printinfo('Waiting 15 sec...')
    session.delay(15)
    maw(motor, endpos)
    printinfo('Lubrication is done.')


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
        printinfo('Round %d of %d' % (i + 1, nrounds))
        printinfo('*' * 100)
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
                    printerror('no Gaussian fit found in this scan')
                    return
                fit_center = params[0]
                if not minvalue <= fit_center <= maxvalue:
                    maw(dev, center)
                    printerror('Gaussian fit center outside '
                               'scanning area')
                    return
                thisround[dev] = fit_center
            maw(dev, thisround[dev])
        printinfo('*' * 100)
        again = False
        for dev in devices:
            diff = abs(lastround[dev] - thisround[dev])
            printinfo('%-10s center: %8.6g -> %8.6g (delta %8.6g)' %
                      (dev, lastround[dev], thisround[dev], diff))
            if session.mode == SIMULATION:
                again = i < 1
                if i == 1:
                    printinfo('=> dry run: limiting to 2 rounds')
            elif diff > convergence * stepsizes[dev]:
                if i == nrounds - 1:
                    printinfo('=> would need another round, but command '
                              'limited to %d rounds' % nrounds)
                else:
                    printinfo('=> needs another round')
                again = True
        if not again:
            printinfo('=> found convergence on peak:')
            for dev in devices:
                printinfo('%-10s : %s' % (dev, dev.format(dev())))
            return
        lastround = thisround


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

    The optional arguments are different instrument angles.

    >>> pos2hkl(15.0, 72.4, -4.0)
    """
    instr = session.instrument
    if not isinstance(instr, SXTalBase):
        raise NicosError('your instrument is not a sxtal diffractometer')
    if not gamma:
        read(instr)
    else:
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
        printinfo('Created new position list %r' % listname)
    else:
        printinfo('Cleared position list %r' % listname)
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
        printwarning('Position list %r does not exist' % listname)
        return
    if not lists[listname]:
        printinfo('<empty>')
        return
    items = []
    R2D = math.degrees
    for i, item in enumerate(lists[listname]):
        if item[1] is not None:
            calcpos = instr._calcPos(item[1])
        else:
            calcpos = None
        items.append((
            '%d' % (i + 1),
            '' if item[1] is None else '%d' % item[1][0],
            '' if item[1] is None else '%d' % item[1][1],
            '' if item[1] is None else '%d' % item[1][2],
            '%.3f' % R2D(item[0].gamma),
            '%.3f' % R2D(item[0].omega),
            '%.3f' % R2D(item[0].nu),
            '%.1f' % item[2][0],
            '%.1f' % item[2][1],
            '' if calcpos is None else '%.3f' % R2D(calcpos.gamma),
            '' if calcpos is None else '%.3f' % R2D(calcpos.omega),
            '' if calcpos is None else '%.3f' % R2D(calcpos.nu),
        ))
    printTable(('pos#', 'h', 'k', 'l',
                u'γ', u'ω', u'ν', u'I', u'σ(I)',
                u'γ_calc', u'ω_calc', u'ν_calc'),
               items, printinfo)


def _add_to_pos_list(listname, pos, intensity, sigma, hkl=None):
    if sigma is None:
        sigma = math.sqrt(intensity)
    sample = session.experiment.sample
    lists = dict(sample.poslists)
    if not isinstance(intensity, (int, float)):
        raise UsageError('Intensity must be a number')
    if hkl is not None:
        hkl = list(hkl)
        if len(hkl) != 3:
            raise UsageError('HKL must be a list of 3 indices')
    if listname not in lists:
        printinfo('Created new position list %r' % listname)
        lists[listname] = []
    lists[listname] = lists[listname] + [(pos, hkl, (intensity, sigma))]
    sample.poslists = lists
    printinfo('Position list %r is now:' % listname)
    PosListShow(listname)


@usercommand
@helparglist('gamma, omega, nu, intensity, [sigma], [listname]')
def PosListDefine(gamma, omega, nu, intensity, sigma=None, listname='default'):
    """Add current position to the position list with given intensity.

    The *sigma* parameter can also be given as the intensity error.

    Examples:

    >>> PosListDefine(28.14, 56.7, -4.3, 1000)
    >>> PosListDefine(28.14, 56.7, -4.3, 1000, 100)  # with sigma intensity
    """
    if isinstance(sigma, str):
        sigma = None
        listname = sigma
    pos = session.instrument._createPos(gamma=gamma, omega=omega, nu=nu)
    _add_to_pos_list(listname, pos, intensity, sigma)


@usercommand
@helparglist('intensity, [sigma], [listname]')
def PosListAdd(intensity, sigma=None, listname='default'):
    """Add current position to the position list with given intensity.

    The *sigma* parameter can also be given as the intensity error.

    Examples:

    >>> PosListAdd(1000)           # add current instrument position
    >>> PosListAdd(1000, 10)       # same, with I = 1000 and sigmaI = 10
    >>> PosListAdd(1000, 'other')  # add to named (non default) position list
    """
    if isinstance(sigma, str):
        sigma = None
        listname = sigma
    pos = session.instrument._readPos()
    _add_to_pos_list(listname, pos, intensity, sigma)


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
        printwarning('Position list %r does not exist' % listname)
        return
    if idx < 1 or idx > len(lists[listname]):
        printwarning('Position list does not have %d entries' % idx)
        return
    lists[listname] = [e for (i, e) in enumerate(lists[listname])
                       if i != idx - 1]
    sample.poslists = lists
    printinfo('Position list %r is now:' % listname)
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
    sample = session.experiment.sample
    wavelength = session.getDevice('wavelength').read()
    lists = dict(sample.poslists)
    if listname not in lists:
        printwarning('Position list %r does not exist' % listname)
        return
    posl = lists[listname]
    if len(posl) < 2:
        printwarning('Cannot calculate: need at least two positions in list')
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

    printinfo('Running Indexus...')
    proc = subprocess.Popen(['indexus'], cwd=root, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    output = proc.communicate()[0]
    if 'unable to find solution' in output:
        printwarning('Indexus could not find a solution.')
        IndexPeaks._last_result = None
        return

    # read output from Indexus
    p1, p2 = None, None
    peaks = []
    dgamma = 0.
    dnu = 0.
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
            elif line.startswith(' list:'):
                printinfo('Indexed reflections:')
                for line in lines:
                    printinfo(line.rstrip())
                    if not line.strip():
                        break
                    info = line.strip().strip('*').split()
                    if info[0] == 'H':
                        continue
                    peaks.append([info[0], info[1], info[2]])
                break

    # calculate UB matrix from "best combination" of two peaks
    or_calc = orient(*sample.cell.cellparams())
    pos1 = posl[p1][0]
    pos2 = posl[p2][0]
    hkl1 = [int(round(float(ix))) for ix in peaks[p1]]
    hkl2 = [int(round(float(ix))) for ix in peaks[p2]]
    new_cell = or_calc.Reorient(hkl1, pos1, hkl2, pos2)
    IndexPeaks._last_result = (new_cell.rmat, (dgamma, dnu), listname, peaks)
    printinfo('Using (%d %d %d) and (%d %d %d) to calculate UB matrix:' %
              (tuple(hkl1) + tuple(hkl2)))
    for row in new_cell.rmat.T:
        printinfo('%8.4f %8.4f %8.4f' % tuple(row))
    printinfo('')
    printinfo('Offsets:')
    printinfo('  delta gamma = %8.4f   delta nu = %8.4f' % (dgamma, dnu))
    printinfo('')
    printinfo('Use AcceptIndexing() to use this indexing.')

IndexPeaks._last_result = None


@usercommand
def AcceptIndexing():
    """Accept the last indexing performed by `IndexPeaks()`.

    Calculates the UB matrix for the sample from the peaks and their positions.

    Example:

    >>> AcceptIndexing()
    """
    if IndexPeaks._last_result is None:
        printerror('No indexing performed yet.')
        return

    # apply calculated matrix to sample
    sample = session.experiment.sample
    b, l = sample.bravais, sample.laue
    rmat, _offsets, listname, peaks = IndexPeaks._last_result
    sample.cell = (rmat, b, l)

    # apply indexing to position list (for later refinement)
    lists = dict(sample.poslists)
    if listname not in lists:
        printwarning('Position list %r does not exist anymore' % listname)
        return
    posl = list(lists[listname])
    if len(posl) != len(peaks):
        printwarning('Position list %r changed after indexing' % listname)
        return
    for i in range(len(posl)):
        posl[i] = (posl[i][0],
                   [int(round(float(ix))) for ix in peaks[i]],
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
    printinfo('Generating HKLs...')
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
    printinfo('%d of %d reflections within instrument limits.' %
              (len(all_pos), len(hkls)))

    fullpath = path.join(root, name + '.csv')
    with open(fullpath, 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(['h', 'k', 'l', 'gamma', 'omega', 'nu', 'width'])
        for row in all_pos:
            writer.writerow(row)

    printinfo('Reflection list written to %s.' % fullpath)


@usercommand
@helparglist('name, [speed], [timedelta]')
def ScanDataset(name, speed=None, timedelta=None):
    """Do an omega-scan over all HKL reflections in a given CSV dataset.

    Takes a CSV file created by `GenDataset()` (maybe edited) and does a
    continuous omega scan over all HKLs in the list.
    """
    instr = session.instrument
    root = session.experiment.samplepath
    fullpath = path.join(root, name + '.csv')
    printinfo('Reading reflection list from %s.' % fullpath)

    all_pos = []
    with open(fullpath, 'r') as fp:
        reader = csv.reader(fp)
        for row in reader:
            if row[0] == 'h':
                continue
            h, k, l, _, _, _, width = row[:7]
            all_pos.append(([float(h), float(k), float(l)],
                            float(width.replace(',', '.'))))

    printinfo('%d reflections read.' % len(all_pos))

    for i, (hkl, width) in enumerate(all_pos):
        printinfo('')
        printinfo('*** Scanning: (%4d %4d %4d)' % tuple(hkl))
        session.beginActionScope('HKL %d/%d: (%4d %4d %4d)' % (
            i+1, len(all_pos), hkl[0], hkl[1], hkl[2]
        ))
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
                printwarning('Skipping scan', exc=1)
                continue
            except CONTINUE_EXCEPTIONS:
                printwarning('Positioning problem, continuing', exc=1)
            contscan(instr._attached_omega, om1, om2, speed, timedelta)
        finally:
            session.endActionScope()
