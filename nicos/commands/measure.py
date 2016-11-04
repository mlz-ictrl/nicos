#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""New acquisition commands (scan and count)."""

from nicos.commands import helparglist, usercommand, parallel_safe
from nicos.commands.output import printinfo, printwarning

from nicos import session
from nicos.core.device import Measurable, SubscanMeasurable
from nicos.core.errors import UsageError, NicosError
from nicos.core.acquire import acquire, read_environment, Average, MinMax
from nicos.core.utils import waitForStatus
from nicos.pycompat import number_types, string_types, iteritems

__all__ = [
    'count', 'preset',
    'SetDetectors', 'AddDetector', 'ListDetectors',
    'SetEnvironment', 'AddEnvironment', 'ListEnvironment',
    'avg', 'minmax',
]


class CountResult(list):
    __display__ = None


def inner_count(detectors, preset, temporary=False):
    """Inner counting function for normal counts with single-point dataset.

    If *temporary* is true, use a dataset without data sinks.
    """
    for det in detectors:
        det.prepare()
    for det in detectors:
        waitForStatus(det)
    # start counting
    args = dict(detectors=detectors,
                environment=session.experiment.sampleenv,
                preset=preset)
    if temporary:
        point = session.data.beginTemporaryPoint(**args)
    else:
        point = session.data.beginPoint(**args)
    read_environment(session.experiment.sampleenv)
    try:
        acquire(point, preset)
    finally:
        session.data.finishPoint()
    msg = []
    retval = []
    for det in detectors:
        res = point.results[det.name]
        if res is not None:
            for (info, val) in zip(det.valueInfo(), res[0]):
                msg.append('%s = %s' % (info.name, info.fmtstr % val))
                retval.append(val)
    for filename in point.filenames:
        msg.append('file = %s' % filename)
    printinfo('count: ' + ', '.join(msg))
    return CountResult(retval)


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
    temporary = preset.pop('temporary', False)
    # sanitize detector list; support count(1) and count('info')
    detectors = []
    for det in detlist:
        if isinstance(det, number_types):
            preset['t'] = det
            continue
        elif isinstance(det, string_types):
            preset['info'] = det  # XXX
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
    # counting without detectors is not useful, but does not error out
    if not detectors:
        detectors = session.experiment.detectors
        if not detectors:
            printwarning('counting without detector, use SetDetectors() '
                         'to select which detector(s) you want to use')
    # check preset names for validity
    names = set(preset)
    for det in detectors:
        names.difference_update(det.presetInfo())
    if names:
        printwarning('these preset keys were not recognized by any of '
                     'the detectors: %s -- detectors are %s' %
                     (', '.join(names), ', '.join(map(str, detectors))))
    # check detector types
    has_sub = sum(isinstance(det, SubscanMeasurable) for det in detectors)
    if has_sub > 0:
        # XXX(dataapi): support both types
        if not len(detectors) == has_sub == 1:
            raise NicosError('cannot acquire on normal and subscan detectors')

    return inner_count(detectors, preset, temporary)


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
    return MinMax(dev)
