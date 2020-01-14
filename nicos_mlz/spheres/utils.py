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

"""NICOS utility functions for SPHERES"""

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.core import SIMULATION, ModeError, UsageError
from nicos.core.status import BUSY, OK
from nicos.utils import parseDuration as pd

from nicos_mlz.spheres.devices.doppler import ELASTIC, INELASTIC, Doppler
from nicos_mlz.spheres.devices.sample import SEController
from nicos_mlz.spheres.devices.sisdetector import SISDetector


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
        session.log.info('Doppler not yet ready, waiting a bit.')
        if not waitForAcq():
            raise ModeError('Scan can currently NOT be started. '
                            'Doppler does not leave busy state.')
    elif status != OK:
        raise ModeError('Scan can not be started. '
                        'Doppler is not synchronized.')

    sismode = sis.measuremode
    if measuremode != sismode:
        if sismode == INELASTIC:
            raise ModeError('Detector is measuring in inelastic mode. '
                            'Stop the doppler to change the mode first.')
        if sismode == ELASTIC:
            raise ModeError('Detector is measuring in elastic mode. '
                            'Start the doppler to change the mode first.')

    # doppler is OK, and measure modes match.
    return True


def notifyOverhang(time, interval):
    """Warn about additional measurement time"""
    overhang = time % interval

    if overhang:
        session.log.warning('Measurement will take an additional %ds '
                            'because the total measurement time has to be a'
                            'multiple of %ds.', interval - overhang, interval)


def waitForAcq():
    doppler = getDoppler()
    for i in range(doppler.maxacqdelay):
        if doppler.status()[0] != BUSY:
            return True
        elif i == 0:
            session.log.info('Acq is busy, waiting a bit')
        session.delay(1)

    return False


def getClosestApproximation(total, interval, subcount=1):
    if interval == 0:
        return total, 1

    try:
        fileinterval = interval*subcount

        filecount = int(total/fileinterval)
        newinterval = int(total/filecount)
    except ZeroDivisionError:
        return getClosestApproximation(total, interval-1, subcount)

    if total-newinterval*filecount > filecount/2:
        filecount += 1

    newinterval = int(newinterval/subcount)

    return newinterval*filecount*subcount, newinterval


def getDoppler():
    for device in session.devices.values():
        if isinstance(device, Doppler):
            return device

    raise UsageError('No doppler found. Load the doppler setup.')


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
                         '"1d:2h:3m:4s" or "2h:4s"'
                         % reason)


def getSisDetector():
    for detector in session.experiment.detectors:
        if isinstance(detector, SISDetector):
            return detector

    raise UsageError('No SIS Detector found/active. Add it to the '
                     'environment after loading the sis setup.')


def getSisImageDevice():
    return getSisDetector().getSisImageDevice()


def getTemperatureController():
    for device in session.devices.values():
        if isinstance(device, SEController):
            return device

    raise UsageError('No SEController found. '
                     'Load the sample environment setup.')
