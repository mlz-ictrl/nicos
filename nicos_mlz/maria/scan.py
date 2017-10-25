# -*- coding: utf-8 -*-
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from nicos import session
from nicos.core import Moveable, UsageError
from nicos.core.acquire import acquire
from nicos.core.scan import Scan
from nicos.core.spm import spmsyntax, Dev, Bare
from nicos.commands import usercommand, helparglist
from nicos.commands.scan import _handleScanArgs, _infostr, ADDSCANHELP2,\
    _fixType as _fixTypeNPoints


class KScan(Scan):

    def __init__(self, devices, startpositions, endpositions, speed=None,
                 firstmoves=None, multistep=None, detlist=None, envlist=None,
                 scaninfo=None, subscan=False):
        self._speed = speed if speed is not None else devices[0].speed
        preset = {'live': True}
        Scan.__init__(self, devices, startpositions, endpositions, firstmoves,
                      multistep, detlist, envlist, preset, scaninfo, subscan)

    def beginScan(self):
        device = self._devices[0]
        self._original_speed = device.speed
        self._original_accel = device.accel
        self._original_decel = device.decel
        device.speed = self._speed
        device.accel = 1
        device.decel = 1
        Scan.beginScan(self)

    def endScan(self):
        device = self._devices[0]
        device.speed = self._original_speed
        device.accel = self._original_accel
        device.decel = self._original_decel
        Scan.endScan(self)

    def acquire(self, point, preset):
        # take into account live preset which is popped in the base class
        # implementation
        acquire(point, preset, iscompletefunc=self.acquireCompleted)

    def acquireCompleted(self):
        return all(d.isCompleted() for d in self._devices)


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
                                 'start-step-end scan command')
            if not (isinstance(args[0], (list, tuple)) and
                    isinstance(args[1], (list, tuple)) and
                    isinstance(args[2], (list, tuple))):
                raise UsageError('start, step and end must be lists')
            if not len(dev) == len(args[0]) == len(args[1]) == len(args[2]):
                raise UsageError('start, step and end lists must be of ' +
                                 'equal length')
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
                                 'start-step-end scan command')
            values = mkpos([args[0]], [args[1]], [args[2]])
            restargs = args[3:]
    devs = [session.getDevice(d, Moveable) for d in devs]
    return devs, values, restargs


@usercommand
@helparglist('dev, [start, step, end | listofpoints], t=seconds, ...')
@spmsyntax(Dev(Moveable), Bare, Bare, Bare)
def sscan(dev, *args, **kwargs):
    """Scan over device(s) and count detector(s).

    The general syntax is either to give start, step and end:

    >>> sscan(dev, 0, 1, 10)   # scans from 0 to 10 in steps of 1.

    or a list of positions to scan:

    >>> sscan(dev, [0, 1, 2, 3, 7, 8, 9, 10])  # scans at the given positions.

    For floating point arguments, the length of the result is
    ``int(round((end - start) / step + 1)``. Because of floating point
    overflow, this rule may result in the last element being greater than
    ``end``, e.g.

    >>> sscan(dev, 30, .1, 30.19)   # scans from 30 to 30.2 in steps of 0.1.

    """
    def mkpos(starts, steps, ends):
        def mk(starts, steps, numpoints):
            return [[start + i * step for (start, step) in zip(starts, steps)]
                    for i in range(numpoints)]
        # use round to handle floating point overflows
        numpoints = [int(round((end - start) / step + 1))
                     for (start, step, end) in zip(starts, steps, ends)]
        if all(n == numpoints[0] for n in numpoints):
            if numpoints[0] > 0:
                if numpoints[0] > 1:
                    return mk(starts, steps, numpoints[0])
                else:
                    raise UsageError("invalid number of points. At least two "
                                     "points are necessary to define a range "
                                     "scan. Please check parameters.")
            else:
                raise UsageError("negative number of points. Please check "
                                 "parameters. Maybe step parameter has wrong"
                                 "sign.")
        else:
            raise UsageError("all entries must generate the same number of "
                             "points")

    scanstr = _infostr("sscan", (dev,) + args, kwargs)
    devs, values, restargs = _fixType(dev, args, mkpos)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(restargs, kwargs, scanstr)
    Scan(devs, values, None, move, multistep, detlist, envlist, preset,
         scaninfo).run()


@usercommand
@helparglist('dev, start, step, numpoints, ...')
@spmsyntax(Dev(Moveable), Bare, Bare, Bare)
def kscan(dev, start, step, numpoints, speed=None, *args, **kwargs):
    """Kinematic scan over device(s).

    The syntax is to give start, step and number of points:

    >>> kscan(dev, 3, 2, 4)     # kinematic scan starting at 3 oscillate by 2
                                # 4 times with default speed
    >>> kscan(dev, 3, 2, 4, 1)  # same scan as above with speed 1.

    oscillates between 3 and 5 during exposure for each interval of (3, 5)
    respectively (5, 3).

    """
    def mkpos(starts, steps, numpoints):
        startpositions = []
        endpositions = []
        for i in range(numpoints):
            for start, step in zip(starts, steps):
                startpositions.append([start + (i % 2) * step])
                endpositions.append([start + ((i+1) % 2) * step])
        return startpositions, endpositions
    scanargs = (start, step, numpoints) + args
    scanstr = _infostr('kscan', (dev,) + scanargs, kwargs)
    devs, values, restargs = _fixTypeNPoints(dev, scanargs, mkpos)
    _preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(restargs, kwargs, scanstr)
    KScan(devs, values[0], values[1], speed, move, multistep, detlist, envlist,
          scaninfo).run()


sscan.__doc__ += ADDSCANHELP2.replace('scan(dev, ', 'sscan(dev, ')
kscan.__doc__ += ADDSCANHELP2.replace('scan(dev, ', 'kscan(dev, ')
