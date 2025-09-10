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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Scan commands for NICOS."""

from numpy import meshgrid, ndarray

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.core import Device, Measurable, Moveable, NicosError, Readable, \
    UsageError
from nicos.core.constants import SUBSCAN
from nicos.core.scan import CONTINUE_EXCEPTIONS, SKIP_EXCEPTIONS, \
    ContinuousScan, ManualScan, Scan, StopScan, SweepScan
from nicos.utils import number_types

__all__ = [
    'scan', 'cscan', 'timescan', 'sweep', 'twodscan', 'contscan',
    'manualscan', 'appendscan', 'gridscan',
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
    preset, detlist, envlist, move, multistep = {}, None, None, [], []
    for arg in args:
        if isinstance(arg, str):
            scaninfo = arg + ' - ' + scaninfo
        elif isinstance(arg, number_types):
            preset['t'] = arg
        elif isinstance(arg, Measurable):
            if detlist is None:
                detlist = []
            detlist.append(arg)
        elif isinstance(arg, Readable):
            if envlist is None:
                envlist = []
            envlist.append(arg)
        else:
            raise UsageError('unsupported scan argument: %r' % arg)
    for key, value in kwargs.items():
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
        elif key == 'info' and isinstance(value, str):
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
    argsrepr = ', '.join(devrepr(a) for a in args if not isinstance(a, str))
    if kwargs:
        kwargsrepr = ', '.join('%s=%r' % kv for kv in kwargs.items())
        return '%s(%s, %s)' % (fn, argsrepr, kwargsrepr)
    return '%s(%s)' % (fn, argsrepr)


@usercommand
@helparglist('dev, [start, step, numpoints | listofpoints], ...')
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
@helparglist('dev-list, start-list, step-list, numpoints-list, ...')
def gridscan(dev, *args, **kwargs):
    """Scans over a grid of device positions and count detector(s).

    The orthogonal grid will spanned by the positions of each device.

    >>> gridscan([dev1, dev2], [-1, -2], [1, 1], [3, 5])

    which generates a measurement over a grid with positions:

    ==== ==== ====
    Step dev1 dev2
    ==== ==== ====
    1    -1.0 -2.0
    2     0.0 -2.0
    3     1.0 -2.0
    4    -1.0 -1.0
    5     0.0 -1.0
    6     1.0 -1.0
    7    -1.0  0.0
    8     0.0  0.0
    9     1.0  0.0
    10   -1.0  1.0
    11    0.0  1.0
    12    1.0  1.0
    13   -1.0  2.0
    14    0.0  2.0
    15    1.0  2.0
    ==== ==== ====
    """
    def mkpos(starts, steps, numpoints):
        if isinstance(numpoints, (list, tuple)):
            if len(starts) != len(numpoints):
                raise UsageError('start, steps, and numpoint arguments must '
                                 'have the same length')
            scanvals = [[start + j * step for j in range(numpoint)]
                        for start, step, numpoint in
                        zip(starts, steps, numpoints)]
            values = [grid.ravel().tolist() for grid in meshgrid(*scanvals)]
            return [tuple(v[i] for v in values) for i in range(len(values[0]))]
        raise UsageError('numpoints must be a list')

    scanstr = _infostr('gridscan', (dev,) + args, kwargs)
    devs, values, restargs = _fixType(dev, args, mkpos)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(restargs, kwargs, scanstr)
    Scan(devs, values, None, move, multistep, detlist, envlist, preset,
         scaninfo).run()


@usercommand
@helparglist('dev, center, step, numperside, ...')
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
def sweep(dev, start, end, *args, **kwargs):
    """Do a sweep of *dev* from *start* to *end*, repeating a count in between.

    Example:

    >>> sweep(T, 10, 100, t=10)

    will move T to 10, then start moving it to 100 and count for 10 seconds as
    long as T is still moving.  *start* can be None to start moving towards the
    *end* immediately without moving to a starting value first.

    Special arguments "delay" (in seconds) and "minstep" (in device units)
    are supported to allow delays between two points. They can be combined
    which will wait for both conditions (minimum time and also step between
    points):

    >>> sweep(T, 10, 20, t=2, delay=5)      # minimum 2 points based on ramp
    >>> sweep(T, 10, 20, t=2, minstep=0.5)  # 21 points
    >>> sweep(T, 10, 20, t=2, delay=5, minstep=0.5)  # 2-21 points
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
gridscan.__doc__ += (
    ADDSCANHELP0 + ADDSCANHELP1 + ADDSCANHELP2).replace(
            'scan(dev,', 'gridscan([dev1, dev2],')


@usercommand
@helparglist('dev, start, end[, speed, timedelta], ...')
# pylint: disable=keyword-arg-before-vararg
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
    if getattr(dev, 'backlash', 0) != 0:
        session.log.warning('device has a nonzero backlash; this will most '
                            'likely not work properly with a continuous scan')
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


class _ManualScan:
    def __init__(self, args, kwargs):
        title = kwargs.pop('_title', 'manualscan')
        scanstr = _infostr(title, args, kwargs)
        preset, scaninfo, detlist, envlist, move, multistep = \
            _handleScanArgs(args, kwargs, scanstr)
        self.scan = ManualScan(move, multistep, detlist, envlist,
                               preset, scaninfo)

    def __enter__(self):
        session._manualscan = self.scan
        try:
            self.scan.manualBegin()
            return self.scan
        except BaseException:
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

    This example mimics a regular `scan()`, with the exception that before
    every point the value of another device is checked for validity.

    The arguments to `manualscan()` can be:

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

    If *stepsize* is given, the step size of the last scan will be overridden.

    Example:

    >>> scan(x, 10, 0.1, 10)  # original scan
    >>> appendscan(10, 0.5)  # continue the scan, but with other step size

    If the previous scan wasn't a scan with fixed step size and *stepsize* is
    not given, the new step size will be calculated as the averaged step size
    from the previous scan:

    >>> scan(x, [0, 0.1, 0.2, 0.5, 1])
    >>> appendscan(5)

    moves x to the following positions:

    ==== ====
    Step x
    ==== ====
    1/5  1.25
    2/5  1.50
    3/5  1.75
    4/5  2.00
    5/5  2.25
    ==== ====

    The scan data will be plotted into the same live plot, if possible, but
    will be saved into a separate data file.

    Scans with multiple devices are supported:

    >>> scan([x, y], [0, 1], [0.1, 0.2], 10)
    >>> appendscan(3, [0.05, 0.1])  # append 5 points with new stepsizes

    If the original scan was made over multiple devices, the *stepsize* must
    be a list with the same number of elements.
    """
    if numpoints == 0:
        raise UsageError('number of points must be either positive or '
                         'negative')
    direction = numpoints / abs(numpoints)
    dslist = session.experiment.data.getLastScans()
    if not dslist:
        raise NicosError('no last scan saved')
    contuids = []

    # Find the last scan that wasn't an appendscan.
    i = len(dslist) - 1
    while i >= 0:
        contuids.insert(0, dslist[i].uid)
        if not dslist[i].chain:
            break
        i -= 1

    # If the last scan was an appendscan in the same direction, append to it,
    # else append to the original scan.  This DWUMs for
    #   scan(...)
    #   appendscan(5)
    #   appendscan(2)
    #   appendscan(-3)
    if dslist[-1].chain_direction == direction:
        scan = dslist[-1]
        # to continue an appendscan in the negative direction, which has
        # the points reversed, we need to reverse the direction again
        if scan.chain_direction == -1:
            numpoints = -numpoints
    else:
        scan = dslist[i]

    n_devs = len(scan.devices)
    n_steps = len(scan.subsets)
    if n_steps < 2:
        raise NicosError('cannot append to scan with no positions')

    if stepsize is not None:
        if isinstance(stepsize, number_types):
            stepsize = [stepsize]
        if n_devs != len(stepsize):
            raise NicosError('the stepsize must have %d elements' % n_devs)
    else:
        stepsize = [None] * n_devs

    # create the new list of positions
    positions = [[None] * n_devs for _ in range(abs(numpoints))]

    # for each device involved in the scan
    for i in range(n_devs):
        # determine step size by first and last position
        pos1 = scan.startpositions[0][i]
        pos2 = scan.startpositions[n_steps - 1][i]

        if isinstance(pos1, (tuple, ndarray)):
            stepsizes = tuple((b - a) / (n_steps - 1)
                              for (a, b) in zip(pos1, pos2))
            if numpoints > 0:
                for j in range(1, numpoints+1):
                    positions[j-1][i] = tuple(b + j*s for (b, s)
                                              in zip(pos2, stepsizes))
            else:
                for j in range(1, -numpoints+1):
                    positions[j-1][i] = tuple(a - j*s for (a, s)
                                              in zip(pos1, stepsizes))

        elif isinstance(pos1, number_types):
            if stepsize[i] is None:
                stepsize[i] = (pos2 - pos1) / (n_steps - 1)
            if numpoints > 0:
                startpos = pos2 + stepsize[i]
            else:
                stepsize[i] = -stepsize[i]
                startpos = pos1 + stepsize[i]
            for j in range(abs(numpoints)):
                positions[j][i] = startpos + j*stepsize[i]

        else:
            # we can't produce new values for this device
            raise NicosError('cannot append to this scan; some devices '
                             'have non-numeric values')

    numpoints = abs(numpoints)
    s = Scan(scan.devices, positions, [], None, None, scan.detectors,
             scan.environment, scan.preset, '%d more steps of last scan' %
             numpoints)
    s._xindex = scan.xindex
    s._chain = contuids
    s._chain_direction = direction
    # envlist must be reset since Scan.__init__ messes with the ordering
    s._envlist[:] = scan.environment
    s.run()
