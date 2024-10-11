# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Devices for the SANS-1 collimation system."""

from nicos.core import Attach, Moveable, Override, Param
from nicos.core.utils import multiStatus
from nicos.devices.generic import Switcher


class Slit(Switcher):
    """class for slit mounted onto something moving

    and thus beeing only effective if the underlying
    device is in a certain position.
    """
    attached_devices = {
        'table': Attach('Guide table this slit is mounted on', Moveable),
    }

    parameters = {
        'activeposition': Param('Position of the table where this slit is '
                                'active', type=str),
    }
    parameter_overrides = {
        'precision':    Override(default=0.1, mandatory=False, type=float),
        'fallback':     Override(default='N.A.', mandatory=False, type=str),
        'blockingmove': Override(default=False, mandatory=False),
    }

    def _mapReadValue(self, value):
        if self._attached_table.read() != self.activeposition:
            return 'N.A.'
        return Switcher._mapReadValue(self, value)

    def doStatus(self, maxage=0):
        if self._attached_table.read() != self.activeposition:
            return multiStatus(self._adevs, maxage)
        return Switcher.doStatus(self, maxage)
