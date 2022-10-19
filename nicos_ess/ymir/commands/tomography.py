#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Kenan Muric <kenan.muric@ess.eu>
#
# *****************************************************************************
from nicos import session
from nicos.commands import usercommand

from nicos_ess.devices.epics.area_detector import DARKFIELD, FLATFIELD, \
    PROJECTION, ImageType


def _find_imagetype_dev():
    for dev in session.devices.values():
        # Should only be one at most.
        if isinstance(dev, ImageType):
            return dev
    raise RuntimeError("Could not find ImageKey device")


@usercommand
def switch_to_dark_field():
    """Switch to dark field state."""
    _find_imagetype_dev().move(DARKFIELD)


@usercommand
def switch_to_flat_field():
    """Switch to flat field state."""
    _find_imagetype_dev().move(FLATFIELD)


@usercommand
def switch_to_projection():
    """Switch to projection state."""
    _find_imagetype_dev().move(PROJECTION)
