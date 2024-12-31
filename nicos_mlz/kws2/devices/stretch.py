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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Specialized slit device for the 4-fold stretch apparatus."""

from nicos.core import Param
from nicos.devices.generic.slit import VerticalGap


class StretchGap(VerticalGap):
    """A vertical gap where the speed can be set for both blades."""

    parameters = {
        'speed': Param('Combined speed of the gap opening or closing',
                       type=float, settable=True, volatile=True,
                       unit='main/s'),
    }

    def doReadSpeed(self):
        return self._attached_bottom.speed + self._attached_top.speed

    def doWriteSpeed(self, value):
        self._attached_bottom.speed = value / 2
        self._attached_top.speed = value / 2
