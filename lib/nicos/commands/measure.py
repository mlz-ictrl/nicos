#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

__version__ = "$Revision$"


from nicos import session
from nicos.core import Measurable, UsageError
from nicos.commands import usercommand
from nicos.commands.output import printinfo
from nicos.commands.basic import sleep


def _count(detlist, preset):
    """Low-level counting function.

    The loop delay is configurable in the instrument object, and defaults to
    0.025 seconds.
    """
    # put detectors in a set and discard them when completed
    detset = set(detlist)
    for det in detlist:
        det.start(**preset)
    i = 0
    delay = getattr(session.instrument, 'countloopdelay', 0.025)
    sleep(0.02)
    while True:
        i += 1
        for det in list(detset):
            try:
                det.duringMeasureHook(i)
                # XXX implement pause logic
                if det.isCompleted():
                    detset.discard(det)
            except:  # really ALL exceptions
                for det in detset:
                    det.stop()
                raise
        if not detset:
            # all detectors finished measuring
            break
        sleep(delay)
    for det in detlist:
        try:
            det.save()
        except Exception:
            det.log.exception('error saving measurement data')
    return sum((det.read() for det in detlist), [])


@usercommand
def count(*detlist, **preset):
    """Perform a single counting.

    With preset arguments, this preset is used instead of the default preset.

    With detector devices as arguments, these detectors are used instead of the
    default detectors set with SetDetectors().

    Within a manual scan, perform the count as one step of the manual scan.

    Examples::

        count()             # count once with the default preset and detectors
        count(t=10)         # count once with time preset of 10 seconds
        count(psd, t=10)    # count 10 seconds with the psd detector
    """
    detectors = []
    for det in detlist:
        if isinstance(det, (int, long, float)):
            preset['t'] = det
            continue
        elif isinstance(det, str):
            preset['info'] = det
            continue
        if not isinstance(det, Measurable):
            raise UsageError('device %s is not a measurable device' % det)
        detectors.append(det)
    scan = getattr(session, '_manualscan', None)
    if scan is not None:
        if detectors:
            raise UsageError('cannot specify different detector list '
                             'in manual scan')
        scan.step(**preset)
        return
    if not detectors:
        detectors = session.experiment.detectors
    return _count(detectors, preset)


@usercommand
def preset(**preset):
    """Set a new default preset for the currently selected detectors.

    The arguments that are accepted depend on the detectors.

    Examples::

        preset(t=10)      # sets a time preset of 5 seconds
        preset(m1=5000)   # sets a monitor preset of 5000 counts, for detectors
                          # that support monitor presets
    """
    for detector in session.experiment.detectors:
        detector.setPreset(**preset)
    printinfo('new preset: ' +
              ', '.join('%s=%s' % item for item in preset.iteritems()))


@usercommand
def SetDetectors(*detlist):
    """Select the detector device(s) to read out when calling scan() or count().

    Examples::

        SetDetectors(det)       # to use the "det" detector
        SetDetectors(det, psd)  # to use both the "det" and "psd" detectors
    """
    session.experiment.setDetectors(detlist)
    session.log.info('standard detectors are now: %s' %
                     ', '.join(session.experiment.detlist))


@usercommand
def AddDetector(*detlist):
    """Add the specified detector device(s) to the standard detectors."""
    existing = session.experiment.detlist
    session.experiment.setDetectors(existing + list(detlist))
    session.log.info('standard detectors are now: %s' %
                     ', '.join(session.experiment.detlist))


@usercommand
def ListDetectors():
    """List the standard detectors."""
    session.log.info('standard detectors are %s' %
                     ', '.join(session.experiment.detlist))


@usercommand
def SetEnvironment(*devlist):
    """Select the device(s) to read out as "experiment environment" at every
    step of a scan.

    Examples::

        SetEnvironment(T, B)   # to read out T and B devices
        SetEnvironment()       # to read out no additional devices
    """
    session.experiment.setEnvironment(devlist)
    session.log.info('standard environment is now: %s' %
                     ', '.join(session.experiment.envlist))


@usercommand
def AddEnvironment(*devlist):
    """Add the specified environment device(s) to the standard environment."""
    existing = session.experiment.envlist
    session.experiment.setEnvironment(existing + list(devlist))
    session.log.info('standard environment is now: %s' %
                     ', '.join(session.experiment.envlist))


@usercommand
def ListEnvironment():
    """List the standard environment devices."""
    session.log.info('standard environment is %s' %
                     ', '.join(session.experiment.envlist))
