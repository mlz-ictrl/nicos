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
from nicos.commands import usercommand
from nicos.commands.scan import timescan
from nicos.core import UsageError
from nicos.core.status import OK
from nicos.utils import parseDuration as pd
from nicos_mlz.spheres.devices.doppler import Doppler, ELASTIC, INELASTIC
from nicos_mlz.spheres.devices.sisdetector import SISDetector


def parseDuration(interval, reason):
    try:
        return pd(interval)
    except TypeError:
        raise UsageError('Can not parse %d from %s. '
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

    session.log.warning('No SIS Detector found/active. Add it to the '
                        'environment after loading the sis setup.')


def getDoppler():
    for device in session.devices.values():
        if isinstance(device, Doppler):
            return device

    session.log.warning('No doppler found.')


def canStartSisScan():
    doppler = getDoppler()
    if getSisImageDevice() and doppler and doppler.status()[0] == OK:
        return True

    return False


def startinelasticscan(time, interval, incremental):
    if not canStartSisScan():
        return
    image = getSisImageDevice()

    if not image:
        return
    elif image.getMode() == ELASTIC:
        session.log.warning('Detector is measuring in elastic mode. '
                            'Start the doppler to change the mode first.')
        return

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
        session.log.warning('Scanduration must be at least one scaninterval '
                            '(currently: %ds).', interval)


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

    if not canStartSisScan():
        return

    image = getSisImageDevice()
    if not image:
        return
    if image.getMode() == INELASTIC:
        session.log.warning('Detector is measuring in inelastic mode. '
                            'Stop the doppler to change the mode first.')
        return

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
        session.log.warning('Scanduration must be at least %ds, %ds was set.',
                            fileduration, seconds)


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
