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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""Imaging commands."""
from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.device import reset
from nicos.commands.measure import count
from nicos.commands.scan import manualscan
from nicos.commands.utility import floatrange
from nicos.core.device import Measurable
from nicos.core.errors import NicosError
from nicos.core.scan import SkipPoint

__all__ = ['tomo']


@usercommand
@helparglist('nangles, moveables, imgsperangle=1, ref_first=True, '
             '[detectors], [presets]')
# pylint: disable=keyword-arg-before-vararg
def tomo(nangles, moveables=None, imgsperangle=1, ref_first=True, *detlist,
         **preset):
    """Performs a tomography.

    This is done by scanning over 360 deg in *nangles* steps and capturing a
    desired amount of images (*imgsperangle*) per step.  The scanning movement
    will be done by all given moveables.
    Additionally to the calculated angles, a fixed acqisition at 180 deg will
    be done (for reference). It can be prepended or inserted in the correct
    order (ref_first).

    Examples:

    >>> tomo(10, sry) # single moveable
    >>> tomo(10, [sry_multi_1, sry_multi_2, sry_multi_3]) # multiple moveables
    >>> tomo(10, sry, 5) # multiple images per angle
    >>> tomo(10, sry, t=1) # tomography with 1s exposure time
    >>> tomo(10, sry, 1, True, det_neo, det_ikonl) # tomography by using 2 detectors (neo + ikonl)
    >>> tomo(10, sry, 5, True, det_neo, det_ikonl, t=1) # full version
    """

    session.log.info('Starting tomography scan.')
    if moveables is None:
        # TODO: currently, sry is the common name on nectar and antares for the
        # sample rotation (phi - around y axis).  Is this convenience function
        # ok, or should it be omitted and added to the instrument custom?
        moveables = [session.getDevice('sry')]
    elif not isinstance(moveables, list):
        moveables = [moveables]

    session.log.info('Performing 360 deg scan.')

    angles = [180.0] + floatrange(0.0, 360.0, num=nangles)

    # This only for compatibility to older scripts
    if isinstance(ref_first, Measurable):
        detlist += (ref_first,)
    elif ref_first is False:  # explicit check for ref_first=False
        angles = sorted(angles)

    session.log.debug('Used angles: %r', angles)

    with manualscan(*moveables) as scan:
        for angle in angles:
            # Move the given movable to the target angle
            try:
                scan.moveDevices(moveables, [angle] * len(moveables))
                # Capture the desired amount of images
                for _ in range(imgsperangle):
                    for i in range(2, -1, -1):
                        try:
                            count(*detlist, **preset)
                        except NicosError:
                            if not i:
                                raise
                            session.log.warning('Count failed, try it again.'
                                                '%d remaining tries', i)
                            if detlist:
                                reset(*detlist)
                            else:
                                reset(*session.experiment.detectors)
                        else:
                            break
            except SkipPoint:
                pass
