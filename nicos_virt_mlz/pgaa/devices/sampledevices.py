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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""Some devices to simulate the PGAA hardware devices."""

from nicos.core import Attach, Override, Param, Readable, dictof
from nicos.devices.abstract import MappedReadable


class PushReader(MappedReadable):
    """Read back device for the sample pusher sensors.

    Since one of the sensors must give the inverse of the `moveable` value this
    will be achieved by setting the parameter `inverse` at the corresponding
    device in configuration.
    """

    hardware_access = False

    attached_devices = {
        'moveable': Attach('Active device', Readable),
    }

    parameters = {
        'inverse': Param('Invert read value',
                         type=bool, default=False),
    }

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
        'fmtstr': Override(default='%d'),
        'mapping': Override(type=dictof(int, str), mandatory=False,
                            default={
                                0: 'up',
                                1: 'down',
                            }),
        'fallback': Override(default='unknown'),
    }

    def _readRaw(self, maxage=0):
        val = self._inverse_mapping.get(
            self._attached_moveable.read(maxage), self.fallback)
        if self.inverse:
            val = int(not val)
        return self.mapping.get(val, self.fallback)
