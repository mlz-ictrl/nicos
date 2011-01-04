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

from nicos.scan import Scan
from nicos.errors import UsageError
from nicos.commands import usercommand


def _handlePreset(single, keywords):
    if single is not None:
        presets = {'t': single}
        presets.update(keywords)
        return presets
    return keywords


def _fixType(dev, start, step):
    if isinstance(dev, list):
        l = len(dev)
        if not isinstance(start, list) or not len(start) == l:
            raise UsageError('start/center must be a list of length %d' % l)
        if not isinstance(step, list):
            step = [step] * l
        elif not len(step) == l:
            raise UsageError('step must be a single number or a list of '
                             'length %d' % l)
        return dev, start, step
    return [dev], [start], [step]


@usercommand
def sscan(dev, start, step, numsteps, preset=None, infostr=None,
          det=None, **presets):
    """Single-sided scan."""
    preset = _handlePreset(preset, presets)
    infostr = infostr or 'sscan(%s, %s, %s, %s, %s)' % (dev, start, step,
                                                        numsteps, preset)
    dev, start, step = _fixType(dev, start, step)
    values = [[x + i*y for x, y in zip(start, step)]
              for i in range(numsteps)]
    scan = Scan(dev, values, det, preset, infostr)
    scan.run()


@usercommand
def cscan(dev, center, step, numperside, preset=None, infostr=None,
          det=None, **presets):
    """Scan around center."""
    preset = _handlePreset(preset, presets)
    infostr = infostr or 'cscan(%s, %s, %s, %s, %s)' % (dev, center, step,
                                                        numperside, preset)
    dev, center, step = _fixType(dev, center, step)
    start = [x - numperside*y for x, y in zip(center, step)]
    values = [[x + i*y for x, y in zip(start, step)]
              for i in range(numperside*2 + 1)]
    scan = Scan(dev, values, det, preset, infostr)
    scan.run()


@usercommand
def qcscan(Q, ny, dQ, dny, numsteps, sc, preset=None, infostr=None,
           det=None, **presets):
    """Q scan around center."""
    # XXX write this
