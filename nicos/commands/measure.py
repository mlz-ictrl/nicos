#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""Module for measuring user commands."""

import sys
from time import sleep, time as currenttime

from nicos import session
from nicos.core.device import Measurable
from nicos.core.errors import UsageError
from nicos.core.constants import SIMULATION
from nicos.commands import usercommand, helparglist, parallel_safe
from nicos.commands.output import printinfo, printwarning
from nicos.pycompat import iteritems, number_types, string_types, reraise
from nicos.core.utils import waitForStatus
from nicos.utils import formatDuration


__all__ = [
    'count', 'preset',
    'SetDetectors', 'AddDetector', 'ListDetectors',
    'SetEnvironment', 'AddEnvironment', 'ListEnvironment',
    'avg', 'minmax'
]


def _wait_for_continuation(delay):
    """Wait until the watchdog "pausecount" list is empty."""
    exp = session.experiment
    current_msg = session.should_pause_count or ''
    session.should_pause_count = None
    if current_msg:
        session.log.warning('counting paused: ' + current_msg)
    # allow the daemon to pause here, if we were paused by it
    session.breakpoint(3)
    # but after continue still check for other conditions
    while exp.pausecount:
        if exp.pausecount != current_msg:
            current_msg = exp.pausecount
            session.log.warning('counting paused: ' + current_msg)
        sleep(delay)
    session.log.info('counting resumed')


def _count(detlist, preset, result, dataset=None):
    """Low-level counting function.

    The loop delay is configurable in the instrument object, and defaults to
    0.025 seconds.

    The result is stored in the given argument, which must be an empty list.
    This is so that a result can be returned even when a stop exception is
    propagated upwards.
    """
    # put detectors in a set and discard them when completed
    detset = set(detlist)
    delay = (session.instrument and session.instrument.countloopdelay or 0.025
             if session.mode != SIMULATION else 0.0)

    # set detector presets before the dataset is created
    # (to get the new preset into the new dataset)
    # TODO: move preset handling to a sane place
    for det in detlist:
        det.setPreset(**preset)

    # advance imagecounter
    if not dataset:
        dataset = session.experiment.createDataset()
    session.experiment.advanceImageCounter(detset, dataset)
    session.beginActionScope('Counting')
    if session.should_pause_count:
        _wait_for_continuation(delay)
    starttime = currenttime()
    try:
        for det in detlist:
            det.start(**preset)
    except:
        session.endActionScope()
        raise
    sleep(delay)
    eta_update = 1 if delay else 0  # never update ETA in simulation
    try:
        while True:
            looptime = currenttime()
            for det in list(detset):
                if session.mode != SIMULATION:
                    det.duringMeasureHook(looptime - starttime)
                if det.isCompleted():
                    try:
                        det.finish()
                        det.save()
                    except Exception:
                        det.log.exception('error saving measurement data')
                    detset.discard(det)
            if not detset:
                # all detectors finished measuring
                break
            if session.should_pause_count:
                for det in detset:
                    if not det.pause():
                        session.log.warning(
                            'detector %r could not be paused' % det)
                _wait_for_continuation(delay)
                for det in detset:
                    det.resume()
            if eta_update >= 1:
                # update at most once per 1s
                # note: as delay = 0 in SIMULATION, we are here always in !SIM
                eta_update -= 1
                eta = set()
                for det in detset:
                    eta.add(det.estimateTime(looptime - starttime))
                eta.discard(None)
                if eta:
                    session.action('estimated %s left' %
                                   formatDuration(max(eta)))
                else:
                    session.action('')
            sleep(delay)
            eta_update += delay
    except BaseException:  # really ALL exceptions
        t, v, tb = sys.exc_info()
        if v.__class__.__name__ != 'ControlStop':
            session.log.warning('Exception during count, trying to save data',
                                exc=True)
        for det in detset:
            try:
                if det.stop():
                    det.save()
            except Exception:
                det.log.exception('error saving measurement data', exc=True)
        result.extend(sum((det.read() for det in detlist), []))
        reraise(t, v, tb)
    finally:
        session.endActionScope()
    result.extend(sum((det.read() for det in detlist), []))


class CountResult(list):
    __display__ = None


@usercommand
@helparglist('[detectors], [presets]')
def count(*detlist, **preset):
    """Perform a single counting.

    With preset arguments, this preset is used instead of the default preset.

    With detector devices as arguments, these detectors are used instead of the
    default detectors set with `SetDetectors()`.

    Examples:

    >>> count()             # count once with the default preset and detectors
    >>> count(t=10)         # count once with time preset of 10 seconds
    >>> count(psd, t=10)    # count 10 seconds with the psd detector

    Within a manual scan, this command is also used to perform the count as one
    point of the manual scan.
    """
    detectors = []
    for det in detlist:
        if isinstance(det, number_types):
            preset['t'] = det
            continue
        elif isinstance(det, string_types):
            preset['info'] = det
            continue
        if not isinstance(det, Measurable):
            raise UsageError('device %s is not a measurable device' % det)
        detectors.append(det)
    # check if manual scan is active
    scan = getattr(session, '_manualscan', None)
    if scan is not None:
        if detectors:
            raise UsageError('cannot specify different detector list '
                             'in manual scan')
        return scan.step(**preset)
    if not detectors:
        detectors = session.experiment.detectors
        if not detectors:
            printwarning('counting without detector, use SetDetectors() '
                         'to select which detector(s) you want to use')
    names = set(preset)
    for det in detectors:
        names.difference_update(det.presetInfo())
    if names:
        printwarning('these preset keys were not recognized by any of '
                     'the detectors: %s -- detectors are %s' %
                     (', '.join(names), ', '.join(map(str, detectors))))
    # preparation before count command
    for det in detectors:
        det.prepare()
    # wait for preparation has been finished.
    for det in detectors:
        waitForStatus(det)
    # start counting
    result = []
    _count(detectors, preset, result)
    i = 0
    msg = []
    for det in detectors:
        for v in det.valueInfo():
            msg.append('%s = %s' % (v.name, result[i]))
            i += 1
    printinfo('count: ' + ', '.join(msg))
    return CountResult(result)


@usercommand
@helparglist('presets...')
def preset(**preset):
    """Set a new default preset for the currently selected detectors.

    The arguments that are accepted depend on the detectors.  The current
    detectors are selected using `SetDetectors()`.

    Examples:

    >>> preset(t=10)      # sets a time preset of 5 seconds
    >>> preset(m1=5000)   # sets a monitor preset of 5000 counts, for detectors
                          # that support monitor presets
    """
    names = set(preset)
    for det in session.experiment.detectors:
        names.difference_update(det.presetInfo())
        det.setPreset(**preset)
    printinfo('new preset: ' +
              ', '.join('%s=%s' % item for item in iteritems(preset)))
    if names:
        printwarning('these preset keys were not recognized by any of '
                     'the detectors: %s -- detectors are %s' %
                     (', '.join(names),
                      ', '.join(map(str, session.experiment.detectors))))


@usercommand
@helparglist('det, ...')
def SetDetectors(*detlist):
    """Select the detector device(s) to read out when calling scan() or count().

    Examples:

    >>> SetDetectors(det)       # to use the "det" detector
    >>> SetDetectors(det, psd)  # to use both the "det" and "psd" detectors
    """
    session.experiment.setDetectors(detlist)
    session.log.info('standard detectors are now: %s' %
                     ', '.join(session.experiment.detlist))


@usercommand
@helparglist('det, ...')
def AddDetector(*detlist):
    """Add the specified detector device(s) to the standard detectors.

    Example:

    >>> AddDetector(psd)    # count also with the "psd" detector
    """
    existing = session.experiment.detlist
    session.experiment.setDetectors(existing + list(detlist))
    session.log.info('standard detectors are now: %s' %
                     ', '.join(session.experiment.detlist))


@usercommand
@parallel_safe
def ListDetectors():
    """List the standard detectors."""
    session.log.info('standard detectors are %s' %
                     ', '.join(session.experiment.detlist))


@usercommand
@helparglist('[dev, ...]')
def SetEnvironment(*devlist):
    """Select the device(s) to read during scans as "experiment environment".

    Experiment environment devices are read out at every point of a scan.

    Examples:

    >>> SetEnvironment(T, B)   # to read out T and B devices
    >>> SetEnvironment()       # to read out no additional devices
    """
    session.experiment.setEnvironment(devlist)
    session.log.info('standard environment is now: %s' %
                     ', '.join(session.experiment.envlist))


@usercommand
@helparglist('dev, ...')
def AddEnvironment(*devlist):
    """Add the specified environment device(s) to the standard environment.

    Example:

    >>> AddEnvironment(T)   # also read out T device
    """
    existing = session.experiment.envlist
    session.experiment.setEnvironment(existing + list(devlist))
    session.log.info('standard environment is now: %s' %
                     ', '.join(session.experiment.envlist))


@usercommand
@parallel_safe
def ListEnvironment():
    """List the standard environment devices."""
    session.log.info('standard environment is %s' %
                     ', '.join(session.experiment.envlist))


@usercommand
def avg(dev):
    """Create a "statistics device" that calculates the scan-point average.

    This pseudo-device can be used in the sample environment in order to
    calculate the average of a device over the whole scan point, as opposed to
    the value at the end of the scan point.

    For example:

    >>> SetEnvironment(avg(T), minmax(T))

    would record for every point in a scan the average and the minimum and
    maximum of the device "T" over the counting period.
    """
    from nicos.core.scan import Average
    return Average(dev)


@usercommand
def minmax(dev):
    """Create a "statistics device" that calculates the scan-point min/maximum.

    This pseudo-device can be used in the sample environment in order to
    calculate the minimum and maximum of a device over the whole scan point.

    For example:

    >>> SetEnvironment(avg(T), minmax(T))

    would record for every point in a scan the average and the minimum and
    maximum of the device "T" over the counting period.
    """
    from nicos.core.scan import MinMax
    return MinMax(dev)
