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

"""Scan commands for NICOS."""

from nicos import session
from nicos.core import Device, Measurable, Moveable, Readable, UsageError, \
    NicosError
from nicos.core.constants import SUBSCAN
from nicos.core.spm import spmsyntax, Dev, Bare
from nicos.core.scan import SweepScan, ContinuousScan, ManualScan, \
    StopScan, CONTINUE_EXCEPTIONS, SKIP_EXCEPTIONS
from nicos.core.scan import Scan
from nicos.commands import usercommand, helparglist
from nicos.pycompat import iteritems, number_types, string_types
from nicos.pycompat import xrange as range  # pylint: disable=W0622


__all__ = [
    'scan', 'cscan', 'timescan', 'sweep', 'twodscan', 'contscan',
    'manualscan', 'appendscan',
]


def _fixType(dev, args, mkpos):
    if not args:
        raise UsageError('at least two arguments are required')
    if isinstance(dev, (list, tuple)):
        if not isinstance(args[0], (list, tuple)):
            raise UsageError('positions must be a list if devices are a list')
        devs = dev
        if isinstance(args[0][0], (list, tuple)):
            for l in args[0]:
                if len(l) != len(args[0][0]):
                    raise UsageError('all position lists must have the same '
                                     'number of entries')
            values = list(zip(*args[0]))
            restargs = args[1:]
        else:
            if len(args) < 3:
                raise UsageError('at least four arguments are required in '
                                 'start-step-numpoints scan command')
            if not (isinstance(args[0], (list, tuple)) and
                    isinstance(args[1], (list, tuple))):
                raise UsageError('start and step must be lists')
            if not len(dev) == len(args[0]) == len(args[1]):
                raise UsageError('start and step lists must be of equal '
                                 'length')
            values = mkpos(args[0], args[1], args[2])
            restargs = args[3:]
    else:
        devs = [dev]
        if isinstance(args[0], (list, tuple)):
            values = list(zip(args[0]))
            restargs = args[1:]
        else:
            if len(args) < 3:
                raise UsageError('at least four arguments are required in '
                                 'start-step-numpoints scan command')
            values = mkpos([args[0]], [args[1]], args[2])
            restargs = args[3:]
    devs = [session.getDevice(d, Moveable) for d in devs]
    return devs, values, restargs


def _handleScanArgs(args, kwargs, scaninfo):
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
            raise UsageError('unsupported scan argument: %r' % arg)
    for key, value in iteritems(kwargs):
        if key in session.devices and isinstance(session.devices[key],
                                                 Moveable):
            # Here, don't replace 'list' by '(list, tuple)'
            # (tuples are reserved for valid device values)
            if isinstance(value, list):
                if multistep and len(value) != len(multistep[-1][1]):
                    raise UsageError('all multi-step arguments must have the '
                                     'same length')
                multistep.append((session.devices[key], value))
            else:
                move.append((session.devices[key], value))
        elif key == 'info' and isinstance(value, string_types):
            scaninfo = value + ' - ' + scaninfo
        else:
            preset[key] = value
    return preset, scaninfo, detlist, envlist, move, multistep


def _infostr(fn, args, kwargs):
    def devrepr(x):
        if isinstance(x, Device):
            return x.name
        elif isinstance(x, (list, tuple)):  # and x and isinstance(x[0], Device):
            return '[' + ', '.join(map(devrepr, x)) + ']'
        elif isinstance(x, float):
            if abs(x) < 0.01:
                return '%.4g' % x
            return '%.4f' % x
        return repr(x)
    argsrepr = ', '.join(devrepr(a) for a in args
                         if not isinstance(a, string_types))
    if kwargs:
        kwargsrepr = ', '.join('%s=%r' % kv for kv in kwargs.items())
        return '%s(%s, %s)' % (fn, argsrepr, kwargsrepr)
    return '%s(%s)' % (fn, argsrepr)


@usercommand
@helparglist('dev, [start, step, numpoints | listofpoints], ...')
@spmsyntax(Dev(Moveable), Bare, Bare, Bare)
def scan(dev, *args, **kwargs):
    """Scan over device(s) and count detector(s).

    A scan is used to collect data during the experiment depending on the
    position of one or more devices:

    - Move the devices to a new position, called a **point**, and wait until
      all devices have reached their position.
    - Start the detectors and wait until the requested time and/or monitor
      counts, called a **preset**, are reached.

    The output is a sequence of detector data corresponding to the device
    positions.

    The command has two basic modes:

    - Equidistant steps between the points

      A start value, the step size, and the number of points are given to the
      command:

      >>> scan(dev, 0, 1, 11)   # counts at positions from 0 to 10 in steps of 1

      For scans *around* a center, use the `cscan()` command.

    - A user defined list of points

      Here, the command expects a list of points:

      >>> scan(dev, [0, 1, 2, 3, 7, 8, 9])  # counts at the given positions

    Instead of one device, the command also handles a list of devices that
    should be moved for each step.  In this case, the start and step width
    also have to be lists:

    >>> scan([dev1, dev2], [0, 0], [0.5, 1], 4)

    The list of points will be:

    ==== ==== ====
    Step dev1 dev2
    ==== ==== ====
    1    0.0  0.0
    2    0.5  1.0
    3    1.0  2.0
    4    1.5  3.0
    ==== ==== ====

    This also works for the second operation mode:

    >>> scan([dev1, dev2], [[0, 1, 2, 3], [0, 1, 5, 7]])

    with positions:

    ==== ==== ====
    Step dev1 dev2
    ==== ==== ====
    1    0.0  0.0
    2    1.0  1.0
    3    2.0  5.0
    4    3.0  7.0
    ==== ==== ====
    """
    def mkpos(starts, steps, numpoints):
        return [[start + i*step for (start, step) in zip(starts, steps)]
                for i in range(numpoints)]
    scanstr = _infostr('scan', (dev,) + args, kwargs)
    devs, values, restargs = _fixType(dev, args, mkpos)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(restargs, kwargs, scanstr)
    Scan(devs, values, None, move, multistep, detlist, envlist, preset,
         scaninfo).run()


@usercommand
@helparglist('dev, center, step, numperside, ...')
@spmsyntax(Dev(Moveable), Bare, Bare, Bare)
def cscan(dev, *args, **kwargs):
    """Scan around a center.

    This command is a specialisation of the `scan()` command to scan around a
    center a number of points left from the center and the same number right
    from the center with a certain step size.

    The command takes as parameters the center, a step size, and number of
    points on each side of the center:

    >>> cscan(dev, 0, 1, 5)   # scans around 0 from -5 to 5 in steps of 1.

    The total number of points is (2 * numperside) + 1.  The above commands
    counts at -5, -4, ..., 5.

    The equivalent `scan()` command would be:

    >>> scan(dev, -5, 1, 11)

    The device can also be a list of devices that should be moved for each
    step.  In this case, the center and step width also have to be lists:

    >>> cscan([dev1, dev2], [0, 0], [0.5, 1], 3)

    Resulting positions:

    ==== ==== ====
    Step dev1 dev2
    ==== ==== ====
    1    -1.5 -3.0
    2    -1.0 -2.0
    3    -0.5 -1.0
    4    0.0  0.0
    5    0.5  1.0
    6    1.0  2.0
    7    1.5  3.0
    ==== ==== ====
    """
    def mkpos(centers, steps, numperside):
        return [[center + (i-numperside)*step for (center, step)
                 in zip(centers, steps)] for i in range(2*numperside+1)]
    scanstr = _infostr('cscan', (dev,) + args, kwargs)
    devs, values, restargs = _fixType(dev, args, mkpos)
    subscan = kwargs.pop(SUBSCAN, False)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(restargs, kwargs, scanstr)
    Scan(devs, values, None, move, multistep, detlist, envlist, preset,
         scaninfo, subscan=subscan).run()


@usercommand
@helparglist('numpoints, ...')
@spmsyntax(Bare)
def timescan(numpoints, *args, **kwargs):
    """Count a number of times without moving devices.

    "numpoints" can be -1 to scan for unlimited points (break using Ctrl-C or
    the GUI to quit).

    Example:

    >>> timescan(500, t=10)  # counts 500 times, every count for 10 seconds

    A special "delay" argument is supported to allow time delays between two
    points:

    >>> timescan(500, t=2, delay=5)
    """
    scanstr = _infostr('timescan', (numpoints,) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(args, kwargs, scanstr)
    scan = SweepScan([], [], numpoints, move, multistep, detlist, envlist,
                     preset, scaninfo)
    scan.run()


@usercommand
@helparglist('dev, start, end, ...')
@spmsyntax(Dev(Moveable), Bare, Bare)
def sweep(dev, start, end, *args, **kwargs):
    """Do a sweep of *dev* from *start* to *end*, repeating the count as often
    as possible in between.

    Example:

    >>> sweep(T, 10, 100, t=10)

    will move T to 10, then start moving it to 100 and count for 10 seconds as
    long as T is still moving.  *start* can be None to start moving towards the
    *end* immediately without moving to a starting value first.

    A special "delay" argument is supported to allow time delays between two
    points:

    >>> sweep(T, 10, 100, t=2, delay=5)
    """
    # XXX: the SweepScan supports a) max #points and b) multiple devices, but
    # we don't offer that in this simplified interface until it's actually
    # needed
    scanstr = _infostr('sweep', (dev, start, end,) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(args, kwargs, scanstr)
    scan = SweepScan([dev], [(start, end)], -1, move, multistep, detlist,
                     envlist, preset, scaninfo)
    scan.run()


@usercommand
@helparglist('dev1, start1, step1, numpoints1, dev2, start2, step2, '
             'numpoints2, ...')
@spmsyntax(Dev(Moveable), Bare, Bare, Bare, Dev(Moveable), Bare, Bare, Bare)
def twodscan(dev1, start1, step1, numpoints1,
             dev2, start2, step2, numpoints2,
             *args, **kwargs):
    """Two-dimensional scan of two devices.

    This is a convenience function that runs a number of scans over *dev2*
    with *dev1* at a different position for each.

    Example:

    >>> twodscan(phi, 0, 1, 10, psi, 0, 2, 10, t=1)
    """
    for j in range(numpoints1):
        dev1value = start1 + j*step1
        try:
            dev1.maw(dev1value)
        except NicosError as err:
            if isinstance(err, CONTINUE_EXCEPTIONS):
                session.log.warning('Positioning problem of %s at %s, '
                                    'scanning %s anyway',
                                    dev1, dev1.format(dev1value, unit=True),
                                    dev2, exc=1)
            elif isinstance(err, SKIP_EXCEPTIONS):
                session.log.warning('Skipping scan at %s = %s',
                                    dev1, dev1.format(dev1value, unit=True),
                                    exc=1)
                continue
            else:
                raise
        scan(dev2, start2, step2, numpoints2, dev1, *args, **kwargs)


ADDSCANHELP0 = """
    In addition to the devices and the position parameters the command accepts
    parameters to:

    - specify the preset (time to count, monitor counts to reach and similar)
    - specify the detector(s) to use
    - add some comments to the datafiles
    - select the "scan environment" (devices that are read at every point)
    - move devices before starting the scan
    - perform multiple counts at every scan point
"""

ADDSCANHELP1 = """
    Presets can be given using named arguments:

    >>> scan(dev, ..., t=5)        # at each scan point count for 5 seconds
    >>> scan(dev, ..., mon1=1000)  # at each scan point count unil mon1 is 1000

    An info string describing the scan can be given as a string argument:

    >>> scan(dev, ..., 'peak search', ...)

    or using the named argument 'info':

    >>> scan(dev, ..., <more named args>, info='peak search')
"""

ADDSCANHELP2 = """
    By default, the detectors are those selected by `SetDetectors()`.  They can
    be replaced by a custom set of detectors by giving them as arguments:

    >>> scan(dev, ..., det1, det2)

    Other devices that should be recorded at every point (so-called environment
    devices) are by default those selected by `SetEnvironment()`.  They can
    also be overridden by giving them as arguments:

    >>> scan(dev, ..., T1, T2)

    Any devices can be moved to different positions *before* the scan starts.
    This is done by giving them as keyword arguments:

    >>> scan(dev, ..., ki=1.55)

    A similar syntax can be used to count multiple times per scan point, with
    one or more devices at different positions:

    >>> scan(dev, ..., pol=['up', 'down'])

    will measure twice at every point: once with *pol* moved to 'up', once with
    *pol* moved to 'down'.
"""

scan.__doc__ += ADDSCANHELP0 + ADDSCANHELP1 + ADDSCANHELP2
cscan.__doc__ += (ADDSCANHELP0 + ADDSCANHELP1 + ADDSCANHELP2).replace('scan(',
                                                                      'cscan(')
timescan.__doc__ += (ADDSCANHELP0 + ADDSCANHELP2).replace('scan(dev, ',
                                                          'timescan(5, ')
sweep.__doc__ += (ADDSCANHELP0 + ADDSCANHELP2).replace('scan(dev, ',
                                                       'sweep(dev, ')
twodscan.__doc__ += (ADDSCANHELP0 + ADDSCANHELP2).replace('scan(dev, ',
                                                          'twodscan(dev1, ')


@usercommand
@helparglist('dev, start, end[, speed, timedelta], ...')
@spmsyntax(Dev(Moveable), Bare, Bare, speed=Bare)
def contscan(dev, start, end, speed=None, timedelta=None, *args, **kwargs):
    """Scan a device continuously with low speed.

    If the "speed" is not explicitly given, it is set to 1/5 of the normal
    speed of the device.  This is very useful for peak searches.

    Examples:

    >>> contscan(phi, 0, 10)
    >>> contscan(phi, 0, 10, 1)        # with speed 1
    >>> contscan(phi, 0, 10, None, 2)  # with default speed and timedelta 2s
    >>> contscan(phi, 0, 10, 1, 2)     # with speed 1 and timedelta 2s

    The phi device will move continuously from 0 to 10, with *speed* (the
    default is 1/5th of the current device speed).  In contrast to a `sweep`,
    detectors are read out every *timedelta* seconds (the default is 1 second),
    and each delta between count values is one scan point, so that no counts
    are lost.

    By default, the detectors are those selected by SetDetectors().  They can
    be replaced by a custom set of detectors by giving them as arguments:

    >>> contscan(dev, ..., det1, det2)
    """
    dev = session.getDevice(dev, Moveable)
    if not hasattr(dev, 'speed'):
        raise UsageError('continuous scan device must have a speed parameter')
    # allow skipping speed/timedelta arguments
    if timedelta is not None and not isinstance(timedelta, number_types):
        args = (timedelta,) + args
        timedelta = None
    if speed is not None and not isinstance(speed, number_types):
        args = (speed,) + args
        speed = None
    scanstr = _infostr('contscan',
                       (dev, start, end, speed, timedelta) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(args, kwargs, scanstr)
    if preset:
        raise UsageError('preset not supported in continuous scan')
    if multistep:
        raise UsageError('multi-step not supported in continuous scan')
    scan = ContinuousScan(dev, start, end, speed, timedelta, move,
                          detlist, envlist, scaninfo)
    scan.run()


class _ManualScan(object):
    def __init__(self, args, kwargs):
        scanstr = _infostr('manualscan', args, kwargs)
        preset, scaninfo, detlist, envlist, move, multistep = \
            _handleScanArgs(args, kwargs, scanstr)
        self.scan = ManualScan(move, multistep, detlist, envlist,
                               preset, scaninfo)

    def __enter__(self):
        session._manualscan = self.scan
        try:
            self.scan.manualBegin()
        except:  # yes, all exceptions
            session._manualscan = None
            raise

    def __exit__(self, *exc):
        try:
            # this can raise NicosInteractiveStop!
            self.scan.manualEnd()
        finally:
            session._manualscan = None
        if exc and exc[0] is StopScan:
            return True


@usercommand
@helparglist('...')
def manualscan(*args, **kwargs):
    """"Manual" scan where no devices are moved automatically.

    An example usage::

        with manualscan(device, otherdevice):
            for i in range(10):
                if otherdevice.read() < 15:
                    raise NicosError('cannot continue')
                maw(device, i+1)
                count(t=600)

    This example mimicks a regular `scan()`, with the exception that before
    every point the value of another device is checked for validity.

    The arguments to `manualscan()` can be are:

    * detector devices, to use these for counting
    * other devices, to read them at every scan point
    * presets, in the form accepted by the other scan commands

    Within the ``with manualscan`` block, call `count()` (using the default
    preset) or ``count(presets...)`` whenever you want to measure a point.
    """
    if getattr(session, '_manualscan', None):
        raise NicosError('cannot start manual scan within manual scan')
    return _ManualScan(args, kwargs)


@usercommand
def appendscan(numpoints=5, stepsize=None):
    """Go on *numpoints* steps from the end of the last scan.

    *numpoints* can also be negative to prepend scan points.

    Examples:

    >>> appendscan(5)   # append 5 more points to last scan
    >>> appendscan(-5)  # append 5 more points to beginning of last scan

    The scan data will be plotted into the same live plot, if possible, but
    will be saved into a separate data file.
    """
    if numpoints == 0:
        raise UsageError('number of points must be either positive or '
                         'negative')
    direction = numpoints / abs(numpoints)
    dslist = session.data._last_scans
    if not dslist:
        raise NicosError('no last scan saved')
    contuids = []

    # Find the last scan that wasn't an appendscan.
    i = len(dslist) - 1
    while i >= 0:
        contuids.append(dslist[i].uid)
        if not dslist[i].continuation:
            break
        i -= 1

    # If the last scan was an appendscan in the same direction, append to it,
    # else append to the original scan.  This DWUMs for
    #   scan(...)
    #   appendscan(5)
    #   appendscan(2)
    #   appendscan(-3)
    if dslist[-1].cont_direction == direction:
        scan = dslist[-1]
    else:
        scan = dslist[i]

    if len(scan.devices) != 1:
        raise NicosError('cannot append to scan with more than one device')
    npos = len(scan.subsets)
    if npos < 2:
        raise NicosError('cannot append to scan with no positions')
    pos1 = scan.startpositions[0][0]
    # start at the real end position...
    pos2 = scan.startpositions[len(scan.subsets) - 1][0]
    if isinstance(pos1, tuple):
        stepsizes = tuple((b - a) / (npos - 1) for (a, b) in zip(pos1, pos2))
        if numpoints > 0:
            positions = [[tuple(b + j*s for (b, s) in zip(pos2, stepsizes))]
                         for j in range(1, numpoints+1)]
        else:
            positions = [[tuple(a - j*s for (a, s) in zip(pos1, stepsizes))]
                         for j in range(1, -numpoints+1)]
        numpoints = abs(numpoints)
    elif isinstance(pos1, (int, float)):
        if stepsize is None:
            stepsize = (pos2 - pos1) / (npos - 1)
        if numpoints > 0:
            startpos = pos2 + stepsize
        else:
            stepsize = -stepsize
            startpos = pos1 + stepsize
        numpoints = abs(numpoints)
        positions = [[startpos + j*stepsize] for j in range(numpoints)]
    else:
        raise NicosError('cannot append to this scan')
    s = Scan(scan.devices, positions, [], None, None, scan.detectors,
             scan.environment, scan.preset, '%d more steps of last scan' %
             numpoints)
    s._xindex = scan.xindex
    s._continuation = contuids
    s._cont_direction = direction
    # envlist must be reset since Scan.__init__ messes with the ordering
    s._envlist[:] = scan.environment
    s.run()
