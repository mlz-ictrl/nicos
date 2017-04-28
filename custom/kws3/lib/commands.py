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

"""Custom commands for KWS-3."""

from nicos import session
from nicos.core import Moveable, multiWait, UsageError
from nicos.commands import usercommand
from nicos.commands.measure import count
from nicos.pycompat import listitems
from nicos.kws1.commands import _fixupSampleenv


DEFAULT = ['selector', 'resolution', 'sample_pos', 'beamstop', 'detector',
           'polarizer', 'chopper']


@usercommand
def SetupNormal():
    """Currently a no-op."""


@usercommand
def kwscount(**arguments):
    """Move sample and devices into place followed by a count.

    This takes KWS-specific circumstances such as sample time factor into
    account.

    Example:

    >>> kwscount(sample=1, selector='12A', resolution='2m', sample_pos='1.3m', time=3600)

    Keywords for standard instrument components are:

    * sample (sample number or name if unique, defaults to no sample change)
    * selector (must be present)
    * resolution (must be present)
    * sample_pos (must be present)
    * detector (must be present)
    * beamstop (defaults to out)
    * polarizer (defaults to out)
    * chopper (defaults to off)

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
    if 'sample_pos' not in arguments:
        raise UsageError('kwscount must have a value for the sample_pos')
    if 'detector' not in arguments:
        raise UsageError('kwscount must have a value for the detector')
    if 'beamstop' not in arguments:
        arguments['beamstop'] = 'out'
    if 'polarizer' not in arguments:
        arguments['polarizer'] = 'out'
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
        if devname == 'chopper':
            # currently a no-op
            continue
        dev = session.getDevice(devname, Moveable)
        dev.start(value)
        if devname == 'selector':
            dev2 = session.getDevice('sel_speed')
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
    session.log.info('Now counting for %d seconds...', meastime)
    count(t=meastime)
