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

"""Module for data analyzing user commands."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from math import sqrt

import numpy as np

from nicos import session
from nicos.errors import UsageError
from nicos.commands import usercommand
from nicos.commands.output import printinfo


def _getData(xcol=None, ycol=None):
    dataset = session.experiment._last_dataset
    if dataset is None:
        raise UsageError('no latest dataset has been stored')
    xs = ys = None
    if xcol is not None:
        if isinstance(xcol, str):
            try:
                xcol = dataset.xnames.index(xcol)
            except ValueError:
                raise UsageError('no such x column: %r' % xcol)
        try:
            xs = np.array([p[xcol] for p in dataset.positions])
        except IndexError:
            raise UsageError('no such x column: %r' % xcol)
    if ycol is not None:
        if isinstance(ycol, str):
            try:
                ycol = dataset.ynames.index(ycol)
            except ValueError:
                raise UsageError('no such y column: %r' % ycol)
        try:
            ys = np.array([p[ycol] for p in dataset.results])
        except IndexError:
            raise UsageError('no such y column: %r' % ycol)
    return xs, ys


@usercommand
def center_of_mass(xcol, ycol):
    """
    Calculate the center of mass x-coordinate of the last scan.
    """
    xs, ys = _getData(xcol, ycol)
    cm = (xs*ys).sum() / float(ys.sum())
    return float(cm)


@usercommand
def root_mean_square(ycol):
    """
    Calculate the root-mean-square of the last scan.
    """
    ys = _getData(None, ycol)
    return sqrt((ys**2).sum() / len(ys))
