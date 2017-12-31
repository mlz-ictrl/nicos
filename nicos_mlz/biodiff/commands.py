# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

from __future__ import print_function

import math

from nicos import session
from nicos.core import Moveable, UsageError
from nicos.core.scan import Scan
from nicos.core.spm import spmsyntax, Dev, Bare
from nicos.core.utils import waitForCompletion
from nicos.commands import usercommand, helparglist
from nicos.commands.scan import _handleScanArgs, _infostr
from nicos.devices.abstract import Motor as NicosMotor
from nicos_mlz.biodiff.devices.motor import MicrostepMotor
from nicos_mlz.biodiff.devices.detector import BiodiffDetector
from nicos_mlz.jcns.devices.shutter import OPEN


def underlying_motor(devices):
    return [dev._attached_motor if isinstance(dev, MicrostepMotor) else dev
            for dev in devices]


class RScan(Scan):

    def moveDevices(self, devices, positions, wait=True):
        if wait:
            # stop running microstep sequence if wait is true because
            # in the following code the attached motor will be used which will
            # interference with the microstepping device.
            # (If there is a running sequence the microstepping device will be
            #  busy but the attached motor is just busy when it gets a move
            #  command from the sequence)
            # A general stop for microstepping motors avoids this interference.
            for dev in devices:
                if isinstance(dev, MicrostepMotor):
                    dev.stop()
                    waitForCompletion(dev, ignore_errors=True)
            # movement and counting separate
            # do not use software based micro stepping
            devices = underlying_motor(devices)
        return Scan.moveDevices(self, devices, positions, wait)

    def preparePoint(self, num, xvalues):
        if num > 0:  # skip starting point, because of range scan (0..1, ...)
            Scan.preparePoint(self, num, xvalues)
            # Open Shutters before movement of scan devices (e.g. motor).
            # Just for RScan because movement and counting should be done
            # simultaneous.
            where = []
            for det in self._detlist:
                if isinstance(det, BiodiffDetector):
                    if det.ctrl_gammashutter:
                        where.append((det._attached_gammashutter, OPEN))
                    if det.ctrl_photoshutter:
                        where.append((det._attached_photoshutter, OPEN))
            if where:
                where = zip(*where)
                self.moveDevices(where[0], where[1])

    def handleError(self, what, err):
        # consider all movement errors fatal
        if what in ('move', 'wait'):
            session.log.warning('Positioning problem, stopping all moving '
                                'motors and detectors', exc=1)
            try:
                for dev in self._devices:
                    if isinstance(dev, NicosMotor):
                        dev.stop()
                for det in self._detlist:
                    det.stop()
            finally:
                raise  # pylint: disable=misplaced-bare-raise
        return Scan.handleError(self, what, err)

    def beginScan(self):
        # since for every scan interval the underlying motor will be driven
        # to the starting point as described in `moveDevices` instead of the
        # originating motor it is necessary to replace the motor with the
        # underlying one in the dataset. Otherwise datasets will contain
        # ``None`` values because ``resdict`` in `PointDataset._reslist` will
        # contain just values for the underlying motor although values for
        # the originating/microstepping motor are requested.
        copydevices = list(self._devices)
        self._devices = underlying_motor(self._devices)
        ret = Scan.beginScan(self)
        self._devices = copydevices
        return ret


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
def rscan(dev, *args, **kwargs):
    """Scan ranges over device(s) and count detector(s).

    The general syntax is either to give start, step and end:

    >>> rscan(dev, 0, 1, 10)   # scans from 0 to 10 in steps of 1.

    or a list of positions to scan:

    >>> rscan(dev, [0, 1, 2, 3, 7, 8, 9, 10])  # scans at the given positions.

    For floating point arguments, the length of the result is
    ``int(round((end - start) / step + 1)``. Because of floating point
    overflow, this rule may result in the last element being greater than
    ``end``, e.g.

    >>> rscan(dev, 30, .1, 30.19)   # scans from 30 to 30.2 in steps of 0.1.

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

    scanstr = _infostr('rscan', (dev,) + args, kwargs)
    devs, values, restargs = _fixType(dev, args, mkpos)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(restargs, kwargs, scanstr)
    oldspeed = dev.speed
    try:
        if len(values) > 1:
            step = values[1][0] - values[0][0]
        if 't' in preset:
            speed = math.fabs(step / float(preset['t']))
            dev.speed = speed
        else:
            raise UsageError("missing preset parameter t.")
        RScan(devs, values[:-1], values[1:], move, multistep, detlist,
              envlist, preset, scaninfo).run()
    finally:
        dev.speed = oldspeed
