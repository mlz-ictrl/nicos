#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

"""Custom commands for SPHERES"""

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.commands import usercommand, parallel_safe
from nicos.commands.device import maw
from nicos.commands.scan import timescan
from nicos.core import UsageError, ModeError, SIMULATION
from nicos.core.status import OK, BUSY
from nicos.utils import parseDuration as pd
from nicos_mlz.spheres.devices.doppler import Doppler, ELASTIC, INELASTIC
from nicos_mlz.spheres.devices.sample import SEController, PressureController
from nicos_mlz.spheres.devices.sisdetector import SISDetector


def parseDuration(interval, reason):
    try:
        return pd(interval)
    except TypeError:
        raise UsageError('Can not parse %s from %s. '
                         'Please provide it as a string, int or float. '
                         'When in doubt encapsulate it in quotation marks.'
                         % (reason, type(interval)))
    except ValueError:
        raise UsageError('The format of the provided string for %s can not be '
                         'converted to a duration. Please separate the values '
                         'with spaces and/or ":", sort the durations by size '
                         'and (only) name them with "d", "h", "m", "s". e.g. '
                         '"1d:2h:3m:4s" '
                         % reason)


def getSisImageDevice():
    for detector in session.experiment.detectors:
        if isinstance(detector, SISDetector):
            return detector.getSisImageDevice()

    raise UsageError('No SIS Detector found/active. Add it to the '
                     'environment after loading the sis setup.')


def getTemperatureController():
    for device in session.devices.values():
        if isinstance(device, SEController):
            return device

    raise UsageError('No SEController found. '
                     'Load the sample environment setup.')


def getDoppler():
    for device in session.devices.values():
        if isinstance(device, Doppler):
            return device

    raise UsageError('No doppler found. Load the doppler setup.')


def canStartSisScan(measuremode):
    """Check whether the SIS detector is ready for a measurement of the
    specified type. Wait for up to the doppler's maxacqdelay just in case the
    doppler is still adjusting."""

    if session.mode == SIMULATION:
        return True

    doppler = getDoppler()
    sis = getSisImageDevice()
    if not sis or not doppler:
        return False

    status = doppler.status()[0]
    if status == BUSY:
        print('Doppler not yet ready, waiting a bit.')
        if not waitForAcq():
            raise ModeError('Scan can currently NOT be started. '
                            'Doppler does not leave busy state.')
    elif status != OK:
        raise ModeError('Scan can not be started. '
                        'Doppler is not synchronized.')

    sismode = sis.getMode()
    if measuremode != sismode:
        if sismode == INELASTIC:
            raise ModeError('Detector is measuring in inelastic mode. '
                            'Stop the doppler to change the mode first.')
        if sismode == ELASTIC:
            raise ModeError('Detector is measuring in elastic mode. '
                            'Start the doppler to change the mode first.')

    # doppler is OK, and measure modes match.
    return True


def waitForAcq():
    doppler = getDoppler()
    for i in range(doppler.maxacqdelay):
        if doppler.status()[0] != BUSY:
            return True
        elif i == 0:
            session.log.info('Acq is busy, waiting a bit')
        session.delay(1)

    return False


def startinelasticscan(time, interval, incremental):
    image = getSisImageDevice()

    if not image:
        return

    canStartSisScan(INELASTIC)

    if not interval:
        interval = image.inelasticinterval
        if interval == 0:
            interval = 1200
    else:
        interval = parseDuration(interval, 'inelastic interval')
        image.inelasticinterval = interval

    time = parseDuration(time, 'inelastic time')

    image.incremental = incremental

    scans = int(time // interval)

    if scans:
        image.clearAccumulated()
        timescan(scans, t=interval)
    else:
        raise UsageError('Scanduration must be at least one scaninterval '
                         '(currently: %ds). If you want to measure in shorter '
                         'intervals, please specify with "interval="'
                         % interval)


@usercommand
def changeDopplerSpeed(target):
    doppler = getDoppler()

    # for simulation mode only
    if target == 0:
        dummytarget = 0
    else:
        dummytarget = doppler.mapping[target][0]
    getSisImageDevice()._dev.dummy_doppvel = dummytarget
    if waitForAcq():
        maw(doppler, target)
    else:
        raise UsageError('Detector is busy. Therefore the doppler speed can '
                         'not be changed.')


@usercommand
def setStick(value):
    """Adjust the Hardware to use the selected stick"""

    if value not in ('ht', 'lt'):
        raise UsageError('Value must be either "ht" for the high temperature'
                         ' or "lt" for the low temperature stick.')
    getTemperatureController().getSampleController().SetActiveStick(value)


@usercommand
def ramp(target, ramp=None):
    """Move the temperature to target with the given ramp.
    If ramp is omitted and the current ramp is > 0 it is used.
    If the current ramp is 0 the command is not executed.
    """

    controller = getTemperatureController()

    if ramp is not None:
        if ramp > 100:
            raise UsageError('TemperatureController does not support ramps '
                             'higher then 100 K/min. If you want to get to '
                             '%f as fast as possible use rush(%f). '
                             'Ramp will be set to max.' % (target, target))
        controller.ramp = ramp
    elif controller.ramp == 0:
        raise UsageError('Ramp of the TemperatureController is 0. '
                         'Please specify a ramp with this command.\n'
                         'Use "ramp(target, RAMP)", '
                         '"timeramp(target, time)", or "rush(target)"')

    controller.move(target)


@usercommand
def timeramp(target, time):
    """Ramp to the given target in the given timeframe.
    Ramp will be calculated by taking current temperature, given target and
    given time into account. Ramps for tube and sample will be calculated
    separately"""

    time = parseDuration(time, 'timeramp')

    controller = getTemperatureController()

    sample = controller.getSampleController()
    tube = controller.getTubeController()

    controller.ramp = 0

    sample.move(sample.read())
    tube.move(tube.read())

    sample.ramp = abs(target-sample.read())/(time/60)
    tube.ramp = abs(target-tube.read())/(time/60)

    controller.move(target)


@usercommand
def rush(target):
    """Move to the given temperature as fast as possible.
    Previously set ramps will be ignored but preserved.
    """

    getTemperatureController().rushTemperature(target)


@usercommand
def setpressure(target):
    """Adjust pressure to the given value.
    Due to the nature of the underlying hardware the target will have a
    margin of 15 mbar.
    """

    for device in session.devices.values():
        if isinstance(device, PressureController):
            device.move(target)
            return

    raise UsageError('No PressureController found. '
                     'Load the sample environment setup.')


@usercommand
def stoppressure():
    """Stop pressure regulation"""

    getTemperatureController().stopPressure()


@parallel_safe
@usercommand
def showDetectorSettings():
    """Print the current detector settings.
    Prints the currently set measure mode and parameters.
    """
    image = getSisImageDevice()
    if not image:
        return

    mode = image.getMode()

    if mode == INELASTIC:
        print('SIS detector is measuring inelastic.',
              'Counttime per file: %s'
              % pd(image.inelasticinterval))
    else:
        params = image.elasticparams
        print('The SIS detector is measuring elastic.',
              'Lines per file: %d' % params[0],
              'Counttime per line: %s' % pd(params[1]),
              'Counttime per file: %s' % pd(params[0]*params[1]))


@usercommand
def acquireElastic(time, interval=15, count=60):
    """Measure elastic.
    Will only start if the doppler is standing.
    Will not stop the doppler if it is running to ensure that elastic
    measurement is explicitly wanted.

    Required:
        ``time``: time frame of for the measurement

    Optional:
        ``interval``: duration for one line in a datafile
        ``count``:   number of lines per datafile.

        If either is omitted the defaults of 15s and 60 lines are used.

    Number of files is calculated so that ``time`` is the longest possible
    scan duration with files of ``interval``*``count`` duration.
    So with default ``interval`` and ``count`` anything between 15m and 29m59s
    will result in a measurement time of 15 minutes.
    The dryrun and calculated finishing time take this into account.
    """

    image = getSisImageDevice()
    if not image:
        return

    canStartSisScan(ELASTIC)

    elastParams = [interval, count]

    seconds = parseDuration(time, 'elastic time')

    fileduration = elastParams[0]*elastParams[1]

    scans = int(seconds//fileduration)

    if scans:
        # after confirming that there is a measurement possible,
        # write the values to the detector and start the measurement.
        image.elasticparams = elastParams
        timescan(scans, t=fileduration)
    else:
        raise UsageError('Scanduration must be at least %ds, %ds was set. '
                         'If you want to measure for a shorter time, please '
                         'specify with "interval=" and/or "count=".'
                         % (fileduration, seconds))


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

    Number of files is calculated so that ``time`` is the longest possible
    scan duration with files of ``interval`` duration.
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

    Number of files is calculated so that ``time`` is the longest possible
    scan duration with files of ``interval`` duration.
    """
    startinelasticscan(time, interval, incremental=False)
