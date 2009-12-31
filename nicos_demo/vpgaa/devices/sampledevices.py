#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Attach, Override, Param, Readable


class PushReader(Readable):
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
    }

    mapping = {
        'up': 0,
        'down': 1,
    }

    fallback = -1

    def doRead(self, maxage=0):
        if self.inverse:
            return not self._readRaw(maxage)
        return self._readRaw(maxage)

    def _readRaw(self, maxage=0):
        val = self._attached_moveable.read(maxage)
        return self.mapping.get(val, self.fallback)
