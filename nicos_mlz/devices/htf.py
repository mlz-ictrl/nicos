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

"""Support classes for the HTF-0x ControlBoxes"""

from nicos.core.params import Attach, Param, floatrange
from nicos.devices.entangle import AnalogOutput, TemperatureController


class HTFTemperatureController(TemperatureController):

    attached_devices = {
        'maxheater': Attach('Maximum heater output device', AnalogOutput),
    }

    parameters = {
        'maxheateroutput': Param('Maximum heater output',
                                 type=floatrange(0, 100), userparam=True,
                                 settable=True, volatile=True, unit='%'),
        'sensortype': Param('Currently used sensor type',
                            type=str, userparam=True, settable=False,
                            volatile=True, mandatory=False),
    }

    def doWriteMaxheateroutput(self, value):
        self._attached_maxheater.move(value)

    def doReadMaxheateroutput(self):
        return self._attached_maxheater.read(0)

    def doReadSensortype(self):
        return self._dev.sensortype
