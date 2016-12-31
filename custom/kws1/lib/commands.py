#  -*- coding: utf-8 -*-
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Custom commands for KWS(-1)."""

from nicos import session
from nicos.core import Moveable, multiWait, UsageError, DeviceAlias
from nicos.commands import usercommand
from nicos.commands.measure import count, SetEnvironment
from nicos.pycompat import listitems


@usercommand
def SetupRealtime(channels, interval, progression, trigger):
    """Set up measurement for real-time mode."""
    detector = session.getDevice('det')
    if trigger == 'external':
        detector.mode = 'realtime_external'
    else:
        detector.mode = 'realtime'
    detector.tofchannels = channels
    detector.tofinterval = interval
    detector.tofprogression = progression
    # let the detector calculate the preset
    detector.prepare()
    detector.setPreset(t=0)
    # switch SPS output that triggers signal routing relays (only KWS1)
    if 'det_ext_rt' in session.configured_devices:
        rtswitch = session.getDevice('det_ext_rt')
        rtswitch.move(1 if trigger == 'external' else 0)
    session.log.info('Detector presets set to realtime mode%s.',
                     ' with external trigger' if trigger == 'external' else '')


@usercommand
def SetupNormal():
    """Set up measurement for normal or TOF mode."""
    detector = session.getDevice('det')
    # just set it to standard mode, TOF mode will be set by the chopper preset
    detector.mode = 'standard'
    rtswitch = session.getDevice('det_ext_rt')
    rtswitch.move(0)
    session.log.info('Detector presets set to standard or TOF mode.')


# The order in which the main instrument components are moved.  This is
# important because for our switchers, the available targets depend on other
# devices' targets.  For example, the detector mapping changes depending on
# the selector target.
DEFAULT = ['selector', 'detector', 'chopper', 'collimation',
           'polarizer', 'lenses']


@usercommand
def kwscount(**arguments):
    """Move sample and devices into place followed by a count.

    This takes KWS-specific circumstances such as sample time factor into
    account.

    Example:

    >>> kwscount(sample=1, selector='6A', detector='2m', collimation='2m', time=3600)

    Keywords for standard instrument components are:

    * sample (sample number or name if unique, defaults to no sample change)
    * selector (must be present)
    * detector (must be present)
    * collimation (must be present)
    * chopper (defaults to off)
    * polarizer (defaults to out)
    * lenses (defaults to all out)

    Keywords for the selector, detector and collimation are required.

    Any other keywords are interpreted as devices names and the target values.
    """
    def sort_key(kv):
        try:
            # main components move first, in selected order
            return (0, DEFAULT.index(kv[0]))
        except ValueError:
            # all other devices move last, sorted by devname
            return (1, kv[0])

    # check that all required components are present, and put defaults for
    # optional components
    if 'selector' not in arguments:
        raise UsageError('kwscount must have a value for the selector')
    if 'detector' not in arguments:
        raise UsageError('kwscount must have a value for the detector')
    if 'collimation' not in arguments:
        raise UsageError('kwscount must have a value for the collimation')
    if 'polarizer' not in arguments:
        arguments['polarizer'] = 'out'
    if 'lenses' not in arguments:
        arguments['lenses'] = 'out-out-out'
    if 'chopper' not in arguments:
        arguments['chopper'] = 'off'
    # leave space between kwscounts
    session.log.info('')
    # measurement time
    meastime = arguments.pop('time', 0)
    # select sample
    sample = arguments.pop('sample', None)
    # move devices
    waiters = []
    # the order is important!
    devs = listitems(arguments)
    devs.sort(key=sort_key)
    # add moved devices to sampleenv
    _fixupSampleenv(devs)
    # start devices
    for devname, value in devs:
        dev = session.getDevice(devname, Moveable)
        dev.start(value)
        if devname == 'selector':
            dev2 = session.getDevice('selector_speed')
            session.log.info('%-12s --> %s (%s)',
                             devname, dev.format(value),
                             dev2.format(dev2.target, unit=True))
        elif devname == 'chopper':
            dev2 = session.getDevice('chopper_params')
            session.log.info('%-12s --> %s (%s)',
                             devname, dev.format(value),
                             dev2.format(dev2.target, unit=True))
        else:
            session.log.info('%-12s --> %s',
                             devname, dev.format(value, unit=True))
        waiters.append(dev)
    # select and wait for sample here
    if sample is not None:
        session.experiment.sample.select(sample)
    # now wait for everyone else
    multiWait(waiters)
    # count
    det = session.getDevice('det')
    if det.mode in ('standard', 'tof'):
        session.log.info('Now counting for %d seconds...', meastime)
    elif det.mode == 'realtime':
        session.log.info('Now counting (real-time)...')
    elif det.mode == 'realtime_external':
        session.log.info('Now waiting for signal to start real-time '
                         'counting...')
    count(t=meastime)


def _fixupSampleenv(devs):
    """Add moved devices to sample env, remove aliases that point to
    devices that are being added.
    """
    envlist = session.experiment.envlist
    aliases = {dev.alias: dev.name for dev in session.experiment.sampleenv
               if isinstance(dev, DeviceAlias)}
    to_add = []
    to_remove = set()
    for devname, _ in devs:
        if devname in DEFAULT:
            continue
        if devname in envlist:
            continue
        to_add.append(devname)
        if devname in aliases:
            to_remove.add(aliases[devname])
    new_envlist = [n for n in envlist if n not in to_remove] + to_add
    if new_envlist != envlist:
        SetEnvironment(*new_envlist)
