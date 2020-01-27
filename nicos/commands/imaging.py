#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

import math

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.device import reset
from nicos.commands.measure import count
from nicos.commands.scan import manualscan
from nicos.commands.utility import floatrange
from nicos.core.device import Measurable, Moveable
from nicos.core.errors import NicosError
from nicos.core.scan import SkipPoint
from nicos.pycompat import integer_types

__all__ = ['tomo', 'grtomo']


def _tomo(title, angles, moveables, imgsperangle, *detlist, **preset):

    if moveables is None:
        # TODO: currently, sry is the common name on nectar and antares for the
        # sample rotation (phi - around y axis).  Is this convenience function
        # ok, or should it be omitted and added to the instrument custom?
        moveables = (session.getDevice('sry'),)
    elif isinstance(moveables, Moveable):
        moveables = (moveables,)
    moveables = tuple(moveables)

    session.log.debug('used angles: %r', angles)

    with manualscan(*(moveables + detlist), _title=title) as scan:
        for angle in angles:
            # Move the given movable to the target angle
            try:
                scan.moveDevices(moveables, [angle] * len(moveables))
                # Capture the desired amount of images
                for _ in range(imgsperangle):
                    for i in range(2, -1, -1):
                        try:
                            count(**preset)
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


@usercommand
@helparglist('nangles, moveables, imgsperangle=1, ref_first=True, start=0, '
             '[detectors], [presets]')
# pylint: disable=keyword-arg-before-vararg
def tomo(nangles, moveables=None, imgsperangle=1, ref_first=True, start=0,
         *detlist, **preset):
    """Performs a tomography.

    This is done by scanning over 360 deg in *nangles* steps and capturing a
    desired amount of images (*imgsperangle*) per step.  The scanning movement
    will be done by all given moveables.
    Additionally to the calculated angles, a fixed acqisition at 180 deg will
    be done (for reference). It can be prepended or inserted in the correct
    order (ref_first).

    If you give a starting angle, the tomo command performs a continuation of
    a stopped tomography at the closest point to the given start point.

    Examples:

    >>> tomo(10, sry) # single moveable
    >>> tomo(10, [sry_multi_1, sry_multi_2, sry_multi_3]) # multiple moveables
    >>> tomo(10, sry, 5) # multiple images per angle
    >>> tomo(10, sry, t=1) # tomography with 1s exposure time
    >>> tomo(10, sry, 1, True, det_neo, det_ikonl) # tomography by using 2 detectors (neo + ikonl)
    >>> tomo(10, sry, 5, True, det_neo, det_ikonl, t=1) # full version
    >>>
    >>> # continue a tomography at 40 deg with stepsize of 40 to 360 deg
    >>> tomo(10, sry, 5, start=60)
    >>> # continue a tomography at 80 deg with stepsize of 40 to 360 deg
    >>> tomo(10, sry, 5, start=70)
    """

    angles = floatrange(0.0, 360.0, num=nangles)
    if isinstance(start, (float, integer_types)) and start != 0:
        if ref_first is False:  # explicit check for ref_first=False
            angles = sorted([180.] + angles)
        # remove unnecessary angles for continued tomography
        startidx = min(range(len(angles)),
                       key=lambda i: abs(angles[i] - start))
        angles = angles[startidx:]

        title = 'append tomo: %.3f deg scan with %d scan points' % (
            angles[-1] - angles[0], len(angles))
        session.log.info('%s', title)
        session.log.debug('remaining angles: %r', angles)
    else:
        title = '360 deg tomography'
        angles = [180.0] + angles
        # This only for compatibility to older scripts
        if isinstance(ref_first, Measurable):
            detlist += (ref_first,)
        elif ref_first is False:  # explicit check for ref_first=False
            angles = sorted(angles)
        session.log.debug('angles: %r', angles)

    session.log.info('Performing %s scan.', title)

    _tomo('tomo', angles, moveables, imgsperangle, *detlist, **preset)


@usercommand
@helparglist('nangles, moveables, imgsperangle=1, img180=True, startpoint=0, '
             '[detectors], [presets]')
# pylint: disable=keyword-arg-before-vararg
def grtomo(nangles, moveables=None, imgsperangle=1, img180=True, startpoint=0,
           *detlist, **preset):
    """Golden Ratio tomography.

    Performs a tomography by scanning over nangles steps in a sequence from
    the Golden ratio and capturing a desired amount of images (imgsperangle)
    per step.

    see: https://en.wikipedia.org/wiki/Golden_angle

    Examples:

    >>> grtomo(10, sry) # single moveable
    >>> grtomo(10, [sry_multi_1, sry_multi_2, sry_multi_3]) # multiple moveables
    >>> grtomo(10, sry, 5) # multiple images per angle
    >>> grtomo(10, sry, t=1) # tomography with 1s exposure time
    >>> grtomo(10, sry, 1, True, 10)  # tomography with starting angle 10 deg
    >>> grtomo(10, sry, 1, True, det_neo, det_ikonl) # tomography by using 2 detectors (neo + ikonl)
    >>> grtomo(10, sry, 5, True, det_neo, det_ikonl, t=1) # full version

    """

    title = 'golden ratio tomography'

    angles = []
    if img180 and startpoint == 0:
        angles += [180.0]
    angles += [math.degrees((i * (1 + math.sqrt(5) / 2.0) * 2 * math.pi) %
                            (2 * math.pi)) for i in range(startpoint, nangles)]

    # This only for compatibility to older scripts
    if isinstance(img180, Measurable):
        detlist += (img180,)
    if isinstance(startpoint, Measurable):
        detlist += (startpoint,)

    session.log.info('Performing %s scan.', title)

    if moveables is None:
        # TODO: currently, sry is the common name on nectar and antares for the
        # sample rotation (phi - around y axis).  Is this convenience function
        # ok, or should it be omitted and added to the instrument custom?
        moveables = (session.getDevice('sry'),)
    elif isinstance(moveables, Moveable):
        moveables = (moveables,)
    moveables = tuple(moveables)

    _tomo('grtomo', angles, moveables, imgsperangle, *detlist, **preset)
