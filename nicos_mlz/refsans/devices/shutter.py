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
"""Shutter related devices."""


from nicos.core import status
from nicos.core.errors import PositionError
from nicos.devices.generic.switcher import Switcher


class Shutter(Switcher):
    """REFSANS specific shutter.

    The underlying motor may stay in WARN state due to some external conditions
    and this state should be transferred to the 'outer' world via the shutter
    devices itself.
    """
    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        move_status = self._attached_moveable.status(maxage)
        if move_status[0] not in (status.OK, status.WARN):
            return move_status
        # otherwise, we have to check if we are at a known position,
        # and otherwise return an error status
        try:
            r = self.read(maxage)
            if r not in self.mapping:
                if self.fallback:
                    return (status.UNKNOWN, 'unconfigured position of %s, '
                            'using fallback' % self._attached_moveable)
                return (status.NOTREACHED, 'unconfigured position of %s or '
                        'still moving' % self._attached_moveable)
        except PositionError as e:
            return status.NOTREACHED, str(e)
        if move_status[0] == status.WARN:
            return status.DISABLED, move_status[1]
        return move_status
