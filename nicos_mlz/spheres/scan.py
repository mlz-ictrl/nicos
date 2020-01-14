#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# *****************************************************************************

"""Scan related commands for SPHERES"""

from __future__ import absolute_import, division, print_function

from time import time

from nicos import session
from nicos.commands import parallel_safe, usercommand
from nicos.commands.scan import _handleScanArgs, _infostr
from nicos.core import SIMULATION
from nicos.core.scan import StopScan, SweepScan

from nicos_mlz.spheres.devices.doppler import INELASTIC
from nicos_mlz.spheres.utils import canStartSisScan, getSisDetector, \
    getSisImageDevice, parseDuration

VALIDTARGETS = ['eta', 'acq']

lasttarget = [VALIDTARGETS[0]]


class VariableTimeScan(SweepScan):
    def __init__(self, devices, startend, firstmoves=None,
                 multistep=None, detlist=None, envlist=None, preset=None,
                 scaninfo=None, subscan=False, xindex=None, totaltime=None,
                 target=VALIDTARGETS[0]):
        SweepScan.__init__(self, devices, startend, -1, firstmoves,
                           multistep, detlist, envlist, preset, scaninfo,
                           subscan, xindex)

        self.eta = time() + totaltime
        self.remainingTime = totaltime
        if target in ['eta', 'acq']:
            self.target = target
            global lasttarget
            lasttarget = target
        else:
            session.log.warning('"%s", is not a valid target, must be one of '
                                '%r, defaulting to "%s"', target,  VALIDTARGETS,
                                VALIDTARGETS[0])
            self.target = VALIDTARGETS[0]

    def increaseTime(self, value):
        self.remainingTime += value
        if self.target == 'acq':
            self.eta = time() + self.remainingTime - self.getElapsedTime()
        else:
            self.eta += value

    def decreaseTime(self, value):
        self.remainingTime -= value
        if self.target == 'acq':
            self.eta = time() + self.remainingTime - self.getElapsedTime()
        else:
            self.eta -= value

    def stopScan(self):
        self._startpositions.stop()
        self.eta = time()
        self.remainingTime = 0

    def acquireCompleted(self):
        if self.eta <= time():
            if self.target == 'acq':
                elapsed = self.getElapsedTime()
                if elapsed < self.remainingTime:
                    # push eta a bit further
                    self.eta += max(self.remainingTime - elapsed - 0.5, 0)
                    return False
            self._startpositions.stop()
            return True

        return False

    def preparePoint(self, num, xvalues):
        if session.mode == SIMULATION:
            session.clock.tick(self.remainingTime)
            raise StopScan
        if self.acquireCompleted():
            return
        SweepScan.preparePoint(self, num, xvalues)

    def getElapsedTime(self):
        return round(self._detlist[0]._attached_timers[0].read()[0], 4)

    def finishPoint(self):
        self.remainingTime -= self.getElapsedTime()
        SweepScan.finishPoint(self)


@usercommand
def atscan(time, *args, **kwargs):
    """A timescan that has an adjustable running time."""
    time = parseDuration(time, 'atscan')

    scanstr = _infostr('vartimescan', (time,) + args, kwargs)
    target = kwargs.pop('target', 'eta')

    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(args, kwargs, scanstr)

    scan = VariableTimeScan([], [], move, multistep, detlist, envlist,
                            preset, scaninfo, totaltime=time, target=target)
    scan.run()


@parallel_safe
@usercommand
def extendScan(time):
    time = parseDuration(time, 'extendScan')
    try:
        current = session._currentscan
    except AttributeError:
        current = None

    if not current:
        session.log.warning('No scan running.')
        return
    elif not isinstance(current, VariableTimeScan):
        session.log.warning('Current scan is not a VariableTimeScan and cannot '
                            'be extended.')
    else:
        current.increaseTime(time)


@parallel_safe
@usercommand
def shortenScan(time):
    time = parseDuration(time, 'shortenScan')
    try:
        current = session._currentscan
    except AttributeError:
        session.log.warning('No scan running.')

    if not current:
        session.log.warning('No scan running.')
    elif not isinstance(current, VariableTimeScan):
        session.log.warning('Current scan is not a VariableTimeScan and cannot '
                            'be shortened.')
    else:
        current.decreaseTime(time)


@parallel_safe
@usercommand
def stopScan():
    if(isinstance(session._currentscan, VariableTimeScan)):
        session._currentscan.stopScan()


def startinelasticscan(time, interval, incremental):
    image = getSisImageDevice()
    if not image:
        return

    canStartSisScan(INELASTIC)

    time = parseDuration(time, 'inelastic time')
    interval = parseDuration(interval, 'inelastic interval')

    if not interval:
        interval = image.inelasticinterval
        if interval == 0:
            interval = 1200
    else:
        interval = parseDuration(interval, 'inelastic interval')
        image.inelasticinterval = interval

    image.incremental = incremental

    image.clearAccumulated()
    atscan(time, t=interval)


@usercommand
def acquireInelasticAccu(time, interval=1200):
    """Measure inelastic with count accumulation.
    Will only start if doppler is running.
    Will not start the doppler if it is standing to ensure inelastic
    measurement is explicitly wanted.

    Required:
    ``time``: time frame for the measurement

    Optional:
    ``interval``: count duration for one file. Defaults to 20min.

    Number of files is rounded up, so any leftover time will result in an
    additional file with full duration.
    """
    startinelasticscan(time, interval, incremental=True)


@usercommand
def acquireInelasticTime(time, interval=1200):
    """Measure inelastic without count accumulation.
    Will only start if doppler is running.
    Will not start the doppler if it is standing to ensure inelastic
    measurement is explicitly wanted.

    Required:
    ``time``: time frame for the measurement

    Optional:
    ``interval``: count duration for one file. Defaults to 20min.

    Number of files is rounded up, so any leftover time will result in an
    additional file with full duration.
    """
    startinelasticscan(time, interval, incremental=False)


@parallel_safe
@usercommand
def save():
    """Trigger an intermediate save.
    The file will be overwritten every time this is triggered
    within one datapoint and when the set countduration for
    this file is reached."""

    getSisDetector().saveIntermediate()


@parallel_safe
@usercommand
def showDetectorSettings():
    """Print the current detector settings.
    Prints the currently set measure mode and parameters.
    """
    image = getSisImageDevice()
    if not image:
        return

    mode = image.measuremode

    if mode == INELASTIC:
        print('SIS detector is measuring inelastic.',
              'Counttime per file: %s'
              % parseDuration(image.inelasticinterval, 'detector settings'))
    else:
        params = image.elasticparams
        print('The SIS detector is measuring elastic.',
              'Lines per file: %d' % params[0],
              'Counttime per line: %s' % parseDuration(params[1],
                                                       'detector settings'),
              'Counttime per file: %s' % parseDuration(params[0]*params[1],
                                                       'detector settings'))
