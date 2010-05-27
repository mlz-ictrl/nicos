#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Scan commands for NICOS
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Scan commands for NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicm.scan import Scan

__commands__ = ['sscan', 'cscan']


def _handlePreset(single, keywords):
    if single is not None:
        presets = {'t': single}
        presets.update(keywords)
        return presets
    return keywords


def sscan(dev, start, step, numsteps, preset=None, infostr=None,
          det=None, **presets):
    """Single-sided scan."""
    preset = _handlePreset(preset, presets)
    values = [[start + i*step] for i in range(numsteps)]
    infostr = infostr or 'sscan(%s, %s, %s, %s, %s)' % (dev, start, step,
                                                        numsteps, preset)
    scan = Scan([dev], values, det, preset, infostr)
    scan.run()


def cscan(dev, center, step, numperside, preset=None, infostr=None,
          det=None, **presets):
    """Scan around center."""
    preset = _handlePreset(preset, presets)
    start = center - numperside * step
    values = [[start + i*step] for i in range(numperside*2 + 1)]
    infostr = infostr or 'sscan(%s, %s, %s, %s, %s)' % (dev, center, step,
                                                        numperside, preset)
    scan = Scan([dev], values, det, preset, infostr)
    scan.run()
