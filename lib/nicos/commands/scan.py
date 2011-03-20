#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""Scan commands for NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicos import session
from nicos.scan import Scan
from nicos.device import Measurable, Moveable
from nicos.errors import UsageError
from nicos.commands import usercommand


def _handleScanArgs(args, kwargs):
    preset, infostr, detlist, move, multistep = {}, None, [], [], []
    for arg in args:
        if isinstance(arg, str):
            infostr = arg
        elif isinstance(arg, (int, long, float)):
            preset['t'] = arg
        elif isinstance(arg, Measurable):
            detlist.append(arg)
        elif isinstance(arg, list):
            detlist.extend(arg)
        else:
            raise UsageError('unsupported scan argument: %r' % arg)
    for key, value in kwargs.iteritems():
        if key in session.devices and isinstance(session.devices[key], Moveable):
            if isinstance(value, list):
                if multistep and len(value) != len(multistep[-1][1]):
                    raise UsageError('all multi-step arguments must have the '
                                     'same length')
                multistep.append((session.devices[key], value))
            else:
                move.append((session.devices[key], value))
        else:
            preset[key] = value
    return preset, infostr, detlist, move, multistep


def _fixType(dev, start, step):
    if isinstance(dev, list):
        dev = [session.getDevice(d, Moveable) for d in dev]
        l = len(dev)
        if not isinstance(start, list) or not len(start) == l:
            raise UsageError('start/center must be a list of length %d' % l)
        if not isinstance(step, list):
            step = [step] * l
        elif not len(step) == l:
            raise UsageError('step must be a single number or a list of '
                             'length %d' % l)
        return dev, start, step
    else:
        dev = session.getDevice(dev, Moveable)
    return [dev], [start], [step]

def _infostr(fn, args, kwargs):
    if kwargs:
        return '%s(%s, %s)' % (fn,
                               ', '.join(map(repr, args)),
                               ', '.join('%s=%r' % kv for kv in kwargs.items()))
    return '%s%r' % (fn, args)


@usercommand
def scan(dev, start, step, numsteps, *args, **kwargs):
    """Single-sided scan."""
    preset, infostr, detlist, move, multistep  = _handleScanArgs(args, kwargs)
    infostr = infostr or \
              _infostr('scan', (str(dev), start, step, numsteps) + args, kwargs)
    dev, start, step = _fixType(dev, start, step)
    values = [[x + i*y for x, y in zip(start, step)]
              for i in range(numsteps)]
    scan = Scan(dev, values, move, multistep, detlist, preset, infostr)
    scan.run()


@usercommand
def cscan(dev, center, step, numperside, preset=None, infostr=None,
          det=None, **presets):
    """Scan around center."""
    preset, infostr, detlist, move, multistep = _handleScanArgs(args, kwargs)
    infostr = infostr or \
              _infostr('cscan', (str(dev), center, step, numperside) + args, kwargs)
    dev, center, step = _fixType(dev, center, step)
    start = [x - numperside*y for x, y in zip(center, step)]
    values = [[x + i*y for x, y in zip(start, step)]
              for i in range(numperside*2 + 1)]
    scan = Scan(dev, values, move, multistep, detlist, preset, infostr)
    scan.run()


@usercommand
def qcscan(Q, ny, dQ, dny, numsteps, sc, preset=None, infostr=None,
           det=None, **presets):
    """Q scan around center."""
    # XXX write this
