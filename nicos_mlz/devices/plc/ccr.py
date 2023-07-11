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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import Moveable, limits
from nicos.devices.entangle import AnalogInput


# This class is used to access the pressure regulation limits
# on newer CCR-Boxes.
class PLCLimits(AnalogInput, Moveable):
    """Device accessing the limits of pressure controlling PLC device.

    Deriving from AnalogInput as this already handles the unit.
    AnalogOutput has HasLimits mixin is therefore too complex.
    Could also inherit from PyTangoDevice instead of AnalogInput,
    but would need to duplicate unit handling.

    In the future this may use the pressure sensor as attached_device
    and use the tango_device of the sensor directly.
    Also in the future, the limits may be calculated from a Temperature.

    As long as none of the details of 'in the future we may...' is clear,
    we stick with a minimalist implementation allowing setting and
    reading the limits as an additional device (of this class).
    """

    valuetype = limits

    def doStart(self, target):
        self._dev.SetParam([[min(target)], ['UserMin']])
        self._dev.SetParam([[max(target)], ['UserMax']])

    def doRead(self, maxage=0):
        return self._dev.GetParam('UserMin'), self._dev.GetParam('UserMax')
