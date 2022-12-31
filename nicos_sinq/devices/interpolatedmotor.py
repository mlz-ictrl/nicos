#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
from numpy import interp

from nicos.core import Attach, Moveable, Override, Param, listof
from nicos.core.errors import ConfigurationError
from nicos.devices.abstract import TransformedMoveable


class InterpolatedMotor(TransformedMoveable):
    """
    This class implements a logical motor driving a real one
    according to an interpolation table provided.
    """
    parameters = {
        'target_positions': Param('List of positions for this motor',
                                  type=listof(float)),
        'raw_positions': Param('List of matching positions for the attached '
                               'motor',
                               type=listof(float)),
    }

    attached_devices = {
        'raw_motor': Attach('Motor to drive when moving this logical motor',
                            Moveable),
    }

    parameter_overrides = {
        'mapping': Override(mandatory=False),
    }

    valuetype = float
    relax_mapping = True

    def doInit(self, mode):
        if len(self.target_positions) != len(self.raw_positions):
            raise ConfigurationError('Length of target and raw '
                                     'positions must match')

    def _readRaw(self, maxage=0):
        return self._attached_raw_motor.read(maxage)

    def doStatus(self, maxage=0):
        return self._attached_raw_motor.doStatus(maxage)

    def doIsAllowed(self, target):
        low = self.target_positions[0]
        high = self.target_positions[-1]
        if not (low <= target <= high):
            return False, 'Out of limits (%f, %f)' % (low, high)
        return self._attached_raw_motor.isAllowed(
            self._mapTargetValue(target))

    def _startRaw(self, target):
        self._attached_raw_motor.start(target)

    def _mapReadValue(self, value):
        return interp(value, self.raw_positions, self.target_positions)

    def _mapTargetValue(self, target):
        return interp(target, self.target_positions, self.raw_positions)
