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

from nicm import nicos
from nicm.scan import Scan

__commands__ = ['sscan', 'cscan']


def sscan(dev, start, step, numsteps, preset=None, det=None):
    if det is None:
        det = nicos.get_device('det')
    values = [[start + i*step] for i in range(numsteps)]
    scan = Scan([dev], values, det, preset)
    scan.run()


def cscan(dev, center, step, numperside, preset=None, det=None):
    if det is None:
        det = nicos.get_device('det')
    start = center - numperside * step
    values = [[start + i*step] for i in range(numperside*2 + 1)]
    scan = Scan([dev], values, det, preset)
    scan.run()
