#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import

import math

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.device import maw
from nicos.commands.measure import count
from nicos.commands.scan import manualscan
from nicos.core.errors import UsageError

from nicos_mlz.antares.commands import darkimage, openbeamimage

__all__ = ['grtomo', 'alignsample']


@usercommand
@helparglist('nangles, moveable, imgsperangle=1, img180=True, startpoint=0, '
             '[detectors], [presets]')
# pylint: disable=keyword-arg-before-vararg
def grtomo(nangles, moveable=None, imgsperangle=1, img180=True, startpoint=0,
           *detlist, **preset):
    """Golden Ratio tomography.

    Performs a tomography by scanning over nangles steps in a sequence from
    the Golden ratio and capturing a desired amount of images (imgsperangle)
    per step.

    see: https://en.wikipedia.org/wiki/Golden_angle
    """
    session.log.info('Starting golden ratio tomography scan.')
    if moveable is None:
        # TODO: currently, sry is the common name on nectar and antares for the
        # sample rotation (phi - around y axis).  Is this convenience function
        # ok, or should it be omitted and added to the instrument custom?
        moveable = session.getDevice('sry')

    session.log.info('Performing golden ratio scan.')

    angles = []
    if img180 and startpoint == 0:
        angles += [180.0]
    _x = 180. * (3.0 - math.sqrt(5))
    angles += [(i * _x) % 360 for i in range(startpoint, startpoint + nangles)]
    with manualscan(moveable):
        for angle in angles:
            # Move the given movable to the target angle
            moveable.maw(angle)
            # Capture the desired amount of images
            for _ in range(imgsperangle):
                count(*detlist, **preset)


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
