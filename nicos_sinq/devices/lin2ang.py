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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import math

from nicos.core.device import Moveable
from nicos.core.params import Attach, Override, Param
from nicos.devices.abstract import TransformedMoveable


class Lin2Ang(TransformedMoveable):
    """
    This class translates a rotation angle into the movement
    of a translation table.
    """

    parameters = {
        'length': Param('distance translation motor -- pivot point',
                        type=float),
        'offset': Param('zero offset', settable=True, userparam=True,
                        default=0.0)
    }

    attached_devices = {
        'translation': Attach('Translation motor', Moveable),
    }

    parameter_overrides = {
        'mapping': Override(mandatory=False),
    }

    valuetype = float
    relax_mapping = True

    def _readRaw(self, maxage=0):
        return self._attached_translation.read(maxage)

    def _mapReadValue(self, value):
        dt = value / self.length
        return math.degrees(math.atan(dt)) - self.offset

    def _startRaw(self, target):
        self._attached_translation.start(target)

    def _mapTargetValue(self, target):
        return self.length * math.tan(math.radians(target + self.offset))

    def doStatus(self, maxage=0):
        return self._attached_translation.doStatus(maxage)

    def doIsAllowed(self, target):
        return self._attached_translation.isAllowed(
            self._mapTargetValue(target))
