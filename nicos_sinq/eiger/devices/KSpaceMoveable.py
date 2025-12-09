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
#   Edward Wall <edward.wall@psi.ch>
#
# *****************************************************************************

from nicos.core import Attach, Moveable
from nicos.core.mixins import HasLimits
from nicos.core.params import Override
from nicos.devices.abstract import TransformedMoveable
from nicos.devices.generic.mono import from_k, to_k


class KSpaceMoveable(HasLimits, TransformedMoveable):
    """
    A logical Moveable mapping to K Space.
    """

    parameter_overrides = {
        'unit': Override(settable=False, mandatory=False, volatile=True),
        'abslimits': Override(settable=False, mandatory=False, internal=True),
    }

    hardware_access = False
    valuetype = float

    attached_devices = {
        'raw_motor': Attach('Motor to drive when moving this logical motor',
                            Moveable),
    }

    def _mapReadValue(self, value):
        return to_k(value, self._attached_raw_motor.unit)

    def _readRaw(self, maxage=0):
        return self._attached_raw_motor.read(maxage)

    def _mapTargetValue(self, target):
        return from_k(target, self._attached_raw_motor.unit)

    def _startRaw(self, target):
        self._attached_raw_motor.start(target)

    def doReadAbslimits(self):
        (min_val, max_val) = self._attached_raw_motor.abslimits
        return (self._mapReadValue(min_val), self._mapReadValue(max_val))

    def doStatus(self, maxage=0):
        return self._attached_raw_motor.status()

    def doReadUnit(self):
        return 'A-1'
