# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Philipp Schmakat <philipp.schmakat@frm2.tum.de>
#
# *****************************************************************************

import os
from os import path

from nicos import session
from nicos.commands import helparglist, hiddenusercommand, usercommand
from nicos.commands.device import maw
from nicos.commands.scan import scan

from nicos_mlz.frm2.commands.imaging import darkimage as _darkimage, grtomo, \
    openbeamimage as _openbeamimage, tomo

__all__ = ['tomo', 'openbeamimage', 'darkimage', 'grtomo']


@usercommand
@helparglist('shutter, [nimages], [detectors], [presets]')
# pylint: disable=keyword-arg-before-vararg
def openbeamimage(shutter=None, nimages=1, *detlist, **preset):
    """ANTARES specific openbeam image acquisition.

    Acquires one or more openbeam images and creates link to the last taken
    image.
    """
    exp = session.experiment
    _openbeamimage(shutter, nimages, *detlist, **preset)

    src = path.join(exp.proposalpath, exp.lastopenbeamimage)
    dst = path.join(exp.proposalpath, 'currentopenbeamimage.fits')

    try:
        if path.islink(dst):
            os.remove(dst)
    except OSError as e:
        session.log.warning('Could not remove symlink: %s', e)

    try:
        os.symlink(src, dst)
    except OSError as e:
        session.log.warning('Could not create symlink: %s', e)


@usercommand
@helparglist('shutter, [nimages], [detectors], [presets]')
# pylint: disable=keyword-arg-before-vararg
def darkimage(shutter=None, nimages=1, *detlist, **preset):
    """ANTARES specific dark image acquisition.

    Acquires one or more dark images and creates a link to the last taken
    image.
    """
    exp = session.experiment
    _darkimage(shutter, nimages, *detlist, **preset)
    src = path.join(exp.proposalpath, exp.lastdarkimage)
    dst = path.join(exp.proposalpath, 'currentdarkimage.fits')

    try:
        if path.islink(dst):
            os.remove(dst)
    except OSError as e:
        session.log.warning('Could not remove symlink: %s', e)

    try:
        os.symlink(src, dst)
    except OSError as e:
        session.log.warning('Could not create symlink: %s', e)


@usercommand
@helparglist('n_points, n_periods, img_per_step, [detectors], [presets]')
# pylint: disable=keyword-arg-before-vararg
def nGI_stepping(n_points, n_periods=1, img_per_step=1, start_pos=0, *detlist,
                 **preset):
    """Perform an nGI step scan of G1tx over n_periods over n_points,
    taking img_per_step images for each position.

    n_periods: number of periods the grating will be moved

    start_pos: starting position of G1tx.

    The period of the G1 grating is fixed to 12.2 um.

    Example:

    >>> nGI_stepping(11, 1, t=30) # steps G1 over one period from 0 to 12.2 um
    >>>                           # in 1.22 um steps and counts for 30 s at each position

    >>> nGI_stepping(21, 2, 2, 500, t=30) # steps G1 over two periods from 500 to 524.4 um
    >>>                                   # in 1.22 um steps and acquires 2 images with 30 s
    >>>                                   # at each position
    """

    # period of G1 grating is 12.2 um
    n_points = max(n_points, 2)
    stepwidth = 12.2 * n_periods / (n_points - 1)

    zero_pos = max(start_pos - 500, -12000)
    scan('G1tx', start_pos, stepwidth, n_points, G1tx=zero_pos,
         fastshutter=img_per_step * ['open'], *detlist, **preset)
    session.getDevice('fastshutter').maw('closed')
    session.log.info('fastshutter closed')


@hiddenusercommand
def reset_grating():
    maw('G1tx', -500)
    maw('G1tx', 0)
