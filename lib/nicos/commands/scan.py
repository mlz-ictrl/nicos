#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

__version__ = "$Revision$"

from nicos import session
from nicos.scan import Scan, TimeScan, ContinuousScan, ManualScan, TwoDimScan
from nicos.device import Device, Measurable, Moveable, Readable
from nicos.errors import UsageError
from nicos.commands import usercommand


def _fixType(dev, args, mkpos):
    if not args:
        raise UsageError('at least two arguments are required')
    if isinstance(dev, list):
        if not isinstance(args[0], list):
            raise UsageError('positions must be a list if devices are a list')
        devs = dev
        if isinstance(args[0][0], list):
            for l in args[0]:
                if len(l) != len(args[0][0]):
                    raise UsageError('all position lists must have the same '
                                     'number of entries')
            values = zip(*args[0])
            restargs = args[1:]
        else:
            if len(args) < 3:
                raise UsageError('at least four arguments are required in '
                                 'start-step-numsteps scan command')
            if not (isinstance(args[0], list) and isinstance(args[1], list)):
                raise UsageError('start and step must be lists')
            if not len(dev) == len(args[0]) == len(args[1]):
                raise UsageError('start and step lists must be of equal length')
            values = mkpos(args[0], args[1], args[2])
            restargs = args[3:]
    else:
        devs = [dev]
        if isinstance(args[0], list):
            values = zip(args[0])
            restargs = args[1:]
        else:
            if len(args) < 3:
                raise UsageError('at least four arguments are required in '
                                 'start-step-numsteps scan command')
            values = mkpos([args[0]], [args[1]], args[2])
            restargs = args[3:]
    devs = [session.getDevice(d, Moveable) for d in devs]
    return devs, values, restargs

def _handleScanArgs(args, kwargs, scaninfo):
    preset, detlist, envlist, move, multistep = {}, [], None, [], []
    for arg in args:
        if isinstance(arg, str):
            scaninfo = arg + ' - ' + scaninfo
        elif isinstance(arg, (int, long, float)):
            preset['t'] = arg
        elif isinstance(arg, Measurable):
            detlist.append(arg)
        elif isinstance(arg, list):
            detlist.extend(arg)
        elif isinstance(arg, Readable):
            if envlist is None:
                envlist = []
            envlist.append(arg)
        else:
            raise UsageError('unsupported scan argument: %r' % arg)
    for key, value in kwargs.iteritems():
        if key in session.devices and isinstance(session.devices[key],
                                                 Moveable):
            if isinstance(value, list):
                if multistep and len(value) != len(multistep[-1][1]):
                    raise UsageError('all multi-step arguments must have the '
                                     'same length')
                multistep.append((session.devices[key], value))
            else:
                move.append((session.devices[key], value))
        else:
            # XXX this silently accepts wrong keys; restrict the possible keys?
            preset[key] = value
    return preset, scaninfo, detlist, envlist, move, multistep

def _infostr(fn, args, kwargs):
    def devrepr(x):
        if isinstance(x, Device):
            return x.name
        elif isinstance(x, list) and x and isinstance(x[0], Device):
            return '[' + ', '.join(map(devrepr, x)) + ']'
        return repr(x)
    argrepr = ', '.join(devrepr(a) for a in args if not isinstance(a, str))
    if kwargs:
        return '%s(%s, %s)' % (fn, argrepr,
                               ', '.join('%s=%r' % kv for kv in kwargs.items()))
    return '%s(%s)' % (fn, argrepr)


@usercommand
def scan(dev, *args, **kwargs):
    """Scan over device(s) and count detector(s).

    The general syntax is either to give start, step and number of steps::

        scan(dev, 0, 1, 11)   # scans from 0 to 10 in steps of 1.

    or a list of positions to scan::

        scan(dev, [0, 1, 2, 3, 7, 8, 9])  # scans at the given positions.

    """
    def mkpos(starts, steps, numsteps):
        return [[start + i*step for (start, step) in zip(starts, steps)]
                for i in range(numsteps)]
    scanstr = _infostr('scan', (dev,) + args, kwargs)
    devs, values, restargs = _fixType(dev, args, mkpos)
    preset, scaninfo, detlist, envlist, move, multistep  = \
        _handleScanArgs(restargs, kwargs, scanstr)
    Scan(devs, values, move, multistep, detlist, envlist, preset, scaninfo).run()

@usercommand
def cscan(dev, *args, **kwargs):
    """Scan around center.

    The general syntax is to give center, step and number of steps per side::

        cscan(dev, 0, 1, 5)   # scans from -5 to 5 in steps of 1.

    The total number of steps is (2 * numperside) + 1.
    """
    def mkpos(centers, steps, numperside):
        return [[center + (i-numperside)*step for (center, step)
                 in zip(centers, steps)] for i in range(2*numperside+1)]
    scanstr = _infostr('cscan', (dev,) + args, kwargs)
    devs, values, restargs = _fixType(dev, args, mkpos)
    preset, scaninfo, detlist, envlist, move, multistep  = \
        _handleScanArgs(restargs, kwargs, scanstr)
    Scan(devs, values, move, multistep, detlist, envlist, preset, scaninfo).run()


@usercommand
def timescan(numsteps, *args, **kwargs):
    """Count a number of times without moving devices.

    "numsteps" can be -1 to scan for unlimited steps (break to quit).
    """
    scanstr = _infostr('timescan', (numsteps,) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(args, kwargs, scanstr)
    if session.mode == 'simulation':
        numsteps = 1
    scan = TimeScan(numsteps, move, multistep, detlist, envlist, preset, scaninfo)
    scan.run()


@usercommand
def twodscan(dev1, start1, step1, numsteps1,
             dev2, start2, step2, numsteps2,
             *args, **kwargs):
    """Two-dimensional scan of two devices.
    """
    scanstr = _infostr('twodscan',
                       (dev1, start1, step1, numsteps1,
                        dev2, start2, step2, numsteps2) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(args, kwargs, scanstr)
    scan = TwoDimScan(dev1, start1, step1, numsteps1,
                      dev2, start2, step2, numsteps2,
                      move, multistep, detlist, envlist, preset, scaninfo)
    scan.run()


ADDSCANHELP1 = """
    The device can also be a list of devices that should be moved for each step.
    In this case, the start and stepwidth also have to be lists::

        scan([dev1, dev2], [0, 0], [0.5, 1], 10)

    This also works for the second basic syntax::

        scan([dev1, dev2], [[0, 1, 2, 3], [0, 2, 4, 6]])

    Presets can be given using keyword arguments::

        scan(dev, ..., t=5)
        scan(dev, ..., m1=1000)

    An info string describing the scan can be given as a string argument::

        scan(dev, ..., 'peak search', ...)
"""


# XXX multistep
ADDSCANHELP2 = """
    By default, the detectors are those selected by `SetDetectors()`.  They can
    be replaced by a custom set of detectors by giving them as arguments::

        scan(dev, ..., det1, det2)

    Other devices that should be recorded at every point (so-called environment
    devices) are by default those selected by `SetEnvironment()`.  They can also
    be overridden by giving them as arguments::

        scan(dev, ..., T1, T2)

    Any devices can be moved to different positions *before* the scan starts.
    This is done by giving them as keyword arguments::

        scan(dev, ..., ki=1.55)

"""

scan.__doc__     += ADDSCANHELP1 + ADDSCANHELP2
cscan.__doc__    += (ADDSCANHELP1 + ADDSCANHELP2).replace('scan(', 'cscan(')
timescan.__doc__ += ADDSCANHELP2.replace('scan(dev, ', 'timescan(5, ')
twodscan.__doc__ += ADDSCANHELP2.replace('scan(dev, ', 'twodscan(dev1, ')


@usercommand
def contscan(dev, start, end, speed=None, *args, **kwargs):
    """Scan a device continuously with low speed.

    If the "speed" is not explicitly given, it is set to 1/5 of the normal speed
    of the device.

    By default, the detectors are those selected by SetDetectors().  They can be
    replaced by a custom set of detectors by giving them as arguments::

        contscan(dev, ..., det1, det2)
    """
    dev = session.getDevice(dev, Moveable)
    if 'speed' not in dev.parameters:
        raise UsageError('continuous scan device must have a speed parameter')
    scanstr = _infostr('contscan', (dev, start, end, speed) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep = \
            _handleScanArgs(args, kwargs, scanstr)
    if preset:
        raise UsageError('preset not supported in continuous scan')
    if envlist:
        raise UsageError('environment devices not supported in continuous scan')
    if multistep:
        raise UsageError('multi-step not supported in continuous scan')
    scan = ContinuousScan(dev, start, end, speed, move, detlist, scaninfo)
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
        self.scan.manualEnd()
        session._manualscan = None

@usercommand
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
        raise UsageError('cannot start manual scan within manual scan')
    return _ManualScan(args, kwargs)
