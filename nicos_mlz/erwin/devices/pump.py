# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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

"""Definition pump class for Kashiyama pump."""

from nicos.core.params import Param, floatrange
from nicos.devices.entangle import NamedDigitalOutput


class Pump(NamedDigitalOutput):

    parameters = {
        'frequency': Param('Rotation frequency of the pump',
                           type=floatrange(125, 190), settable=True, unit='Hz',
                           userparam=True, volatile=True, preinit=True),
        'power': Param('Output power',
                       settable=False, unit='W', userparam=True,
                       volatile=True),
        'temperature': Param('Motor temperature',
                             settable=False, unit='degC', userparam=True,
                             volatile=True),
    }

    def doReadTemperature(self):
        if hasattr(self, '_dev'):
            return self._dev.motor_temperature
        return 0

    def doReadPower(self):
        if hasattr(self, '_dev'):
            return self._dev.power
        return 0

    def doReadFrequency(self):
        if hasattr(self, '_dev'):
            return self._dev.frequency
        return self.parameters['frequency'].type()

    def doWriteFrequency(self, value):
        self._dev.target_frequency = value
