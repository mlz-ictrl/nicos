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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from nicos import session
from nicos.commands import usercommand, helparglist
from nicos.commands.utility import floatrange
from nicos.commands.measure import count
from nicos.commands.device import maw
from nicos.commands.scan import manualscan


__all__ = ['tomo']


@usercommand
@helparglist('nangles, moveables, imgsperangle=1, [detectors], [presets]')
def tomo(nangles, moveables=None, imgsperangle=1, *detlist, **preset):
    """Performs a tomography by scanning over 360 deg in nangles steps
    and capturing a desired amount of images (imgsperangle) per step.
    The scanning movement will be done by all given moveables.

    Examples:

    >>> tomo(10, sry) # single moveable
    >>> tomo(10, [sry_multi_1, sry_multi_2, sry_multi_3]) # multiple moveables
    >>> tomo(10, sry, 5) # multiple images per angle
    >>> tomo(10, sry, t=1) # tomography with 1s exposure time
    >>> tomo(10, sry, 1, det_neo, det_ikonl) # tomography by using 2 detectors (neo + ikonl)
    >>> tomo(10, sry, 5, det_neo, det_ikonl, t=1) # full version
    """

    session.log.info('Starting tomography scan.')
    if moveables is None:
        # TODO: currently, sry is the common name on nectar and antares for the
        # sample rotation (phi - around y axis).  Is this convenience function
        # ok, or should it be omitted and added to the instrument custom?
        moveables = [session.getDevice('sry')]

    if not isinstance(moveables, list):
        moveables = [moveables]

    session.log.info('Performing 360 deg scan.')

    angles = [180.0] + floatrange(0.0, 360.0, num=nangles)
    with manualscan(*moveables):
        for angle in angles:
            # Move the given movable to the target angle
            args = sum([[entry, angle] for entry in moveables], [])
            maw(*args)

            # Capture the desired amount of images
            for _ in range(imgsperangle):
                count(*detlist, **preset)
