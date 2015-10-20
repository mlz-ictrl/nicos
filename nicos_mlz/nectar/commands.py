#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""NECTAR special commands."""

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.device import maw
from nicos.core.errors import UsageError

from nicos_mlz.antares.commands import darkimage, openbeamimage

__all__ = ['alignsample']


@usercommand
@helparglist('xpos, ypos, exposuretime=1, number_ob=15, number_di=15')
def alignsample(xpos, ypos, exposuretime=1, number_ob=15, number_di=15):
    """Performs a 'sample alignment'.

    Moves the sample to a safe position and takes first *number_di* dark images
    with *exposuretime* and then *number_ob* open beam images with the same
    *exposuretime*.  Thereafter moves the sample to *xpos*, *ypos*.
    """
    if not (0 < number_ob < 100):
        raise UsageError('Number of open beam images must be in [1..99]')
    if not (0 < number_di < 100):
        raise UsageError('Number of dark images must be in [1..99]')
    stx = session.getDevice('stx')
    sty = session.getDevice('sty')

    session.log.info('Acquire openbeam and dark images')
    maw(sty, 1.0)
    maw(stx, 1.0)

    for _i in range(number_di):
        darkimage(t=exposuretime)
    for _i in range(number_ob):
        openbeamimage(t=exposuretime)

    maw(stx, xpos)
    maw(sty, ypos)
    session.log.info('Sample is aligned')
