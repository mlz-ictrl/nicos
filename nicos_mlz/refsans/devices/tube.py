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

"""Refsans specific devices."""

from math import atan2, degrees, radians, tan

from nicos.core import Moveable
from nicos.core.errors import ConfigurationError
from nicos.core.mixins import HasLimits
from nicos.core.params import Attach, Override, Param, floatrange
from nicos.devices.abstract import TransformedMoveable


class TubeAngle(HasLimits, TransformedMoveable):
    """Angle of the tube controlled by the yoke."""

    attached_devices = {
        'yoke': Attach('Yoke device', Moveable),
    }

    parameters = {
        'yokepos': Param('Position of yoke from pivot point',
                         type=floatrange(0, 20000), unit='mm', default=11000),
    }

    parameter_overrides = {
        'abslimits': Override(mandatory=False, volatile=True),
        'unit': Override(mandatory=False, default='deg'),
    }

    hardware_access = False

    def doInit(self, mode):
        self.log.info('%s', self.parameters['yokepos'].unit)
        self.log.info('%s', self._attached_yoke.unit)
        if self.parameters['yokepos'].unit != self._attached_yoke.unit:
            raise ConfigurationError(
                self, "units of attached device 'yoke' and 'yokepos' parameter"
                " are not identical.")

    def _readRaw(self, maxage=0):
        return self._attached_yoke.read(maxage)

    def _mapReadValue(self, value):
        return degrees(atan2(value, self.yokepos))

    def _mapTargetValue(self, target):
        return tan(radians(target)) * self.yokepos

    def _startRaw(self, target):
        self._attached_yoke.move(target)

    def doReadAbslimits(self):
        yokelimits = self._attached_yoke.userlimits
        return (degrees(atan2(yokelimits[0], self.yokepos)),
                degrees(atan2(yokelimits[1], self.yokepos)))
