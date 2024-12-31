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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# **************************************************************************
"""Support Code for REFSANS's NOK's."""

from nicos.core import ConfigurationError, HardwareError
from nicos.core.params import Override, Param, none_or, tupleof
from nicos.devices.abstract import TransformedReadable
from nicos.devices.entangle import Sensor


class NOKMonitoredVoltage(TransformedReadable, Sensor):
    """Return a scaled and monitored analogue value.

    Also checks the value to be within certain limits, if not, complain.
    """

    parameters = {
        'reflimits': Param('None or Limits to check the reference: low, warn, '
                           'high',
                           type=none_or(tupleof(float, float, float)),
                           settable=False, default=None),
        'scale': Param('Scaling factor', type=float, settable=False,
                       default=1.),
    }

    parameter_overrides = {
        'unit': Override(default='V', mandatory=False),
    }

    def doUpdateReflimits(self, limits):
        if limits is not None:
            if not (0 <= limits[0] <= limits[1] <= limits[2]):
                raise ConfigurationError(self, 'reflimits must be in ascending'
                                         ' order!')

    def _readRaw(self, maxage=0):
        return Sensor.doRead(self, maxage)

    def _mapReadValue(self, value):
        value *= self.scale
        if self.reflimits is not None:
            if abs(value) > self.reflimits[2]:
                raise HardwareError(self, 'Reference voltage (%.2f) above '
                                    'maximum (%.2f)' % (value,
                                                        self.reflimits[2]))
            if abs(value) < self.reflimits[0]:
                raise HardwareError(self, 'Reference voltage (%.2f) below '
                                    'minimum (%.2f)' % (value,
                                                        self.reflimits[0]))
            if abs(value) < self.reflimits[1]:
                self.log.warning('Reference voltage (%.2f) seems rather low, '
                                 'should be above %.2f', value,
                                 self.reflimits[1])
        return value
