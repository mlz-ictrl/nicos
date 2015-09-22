#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from os.path import relpath

from nicos import session
from nicos.commands import usercommand, helparglist
from nicos.commands.utility import floatrange
from nicos.commands.output import printinfo
from nicos.commands.measure import count
from nicos.commands.device import maw
from nicos.commands.scan import manualscan


__all__ = ['tomo', 'openbeamimage', 'darkimage']


@usercommand
@helparglist('nangles, moveable, imgsperangle=1, [detectors], [presets]')
def tomo(nangles, moveable=None, imgsperangle=1, *detlist, **preset):
    """Performs a tomography by scanning over 360 deg in nangles steps
    and capturing a desired amount of images (imgsperangle) per step."""

    printinfo('Starting tomography scan.')
    if moveable is None:
        # TODO: currently, sry is the common name on nectar and antares for the
        # sample rotation (phi - around y axis).  Is this convenience function
        # ok, or should it be omitted and added to the instrument custom?
        moveable = session.getDevice('sry')

    printinfo('Performing 360 deg scan.')

    angles = [180.0] + floatrange(0.0, 360.0, num=nangles).tolist()
    with manualscan(moveable):
        for angle in angles:
            # Move the given movable to the target angle
            maw(moveable, angle)

            # Capture the desired amount of images
            for _ in range(imgsperangle):
                count(*detlist, **preset)


@usercommand
@helparglist('shutter, [detectors], [presets]')
def openbeamimage(shutter=None, *detlist, **preset):
    """Acquire an open beam image."""
    exp = session.experiment
    det = exp.detectors[0]

    # TODO: better ideas for shutter control
    if shutter:
        # Shutter was given, so open it
        maw(shutter, 'open')
    else:
        # No shutter; try the lima way
        oldmode = det.shuttermode
        det.shuttermode = 'auto'

    try:
        det.subdir = relpath(exp.openbeamdir, exp.datapath)
        return count(*detlist, **preset)
    finally:

        if shutter:
            maw(shutter, 'closed')
        else:
            det.shuttermode = oldmode

        lastImg = det.read(0)
        if lastImg:
            # only show the path relative to the proposalpath
            lastImg = lastImg[0]
        else:
            lastImg = ''

        printinfo('last open beam image is %r' % lastImg)
        exp._setROParam('lastopenbeamimage', lastImg)
        det.subdir = ''


@usercommand
@helparglist('shutter, [detectors], [presets]')
def darkimage(shutter=None, *detlist, **preset):
    """Acquire a dark image."""
    exp = session.experiment
    det = exp.detectors[0]

    # TODO: better ideas for shutter control
    if shutter:
        # Shutter was given, so open it
        maw(shutter, 'closed')
    else:
        # No shutter; try the lima way
        oldmode = det.shuttermode
        det.shuttermode = 'always_closed'

    try:
        det.subdir = relpath(exp.darkimagedir, exp.datapath)
        return count(*detlist, **preset)
    finally:

        if shutter:
            maw(shutter, 'open')
        else:
            det.shuttermode = oldmode

        lastImg = det.read(0)
        if lastImg:
            # only show the path relative to the proposalpath
            lastImg = lastImg[0]
        else:
            lastImg = ''

        printinfo('last dark image is %r' % lastImg)
        exp._setROParam('lastdarkimage', lastImg)
        det.subdir = ''
