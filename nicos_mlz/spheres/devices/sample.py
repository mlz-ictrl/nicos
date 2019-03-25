#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# ****************************************************************************

"""
Devices to control the sample environment at SPHERES
"""

from __future__ import absolute_import, division, print_function

from nicos.core import SIMULATION
from nicos.core.params import tangodev, Param, Attach
from nicos.core.status import WARN
from nicos.devices import tango
from nicos.devices.tango import TemperatureController
from nicos.utils import HardwareStub


class SEController(tango.TemperatureController):
    """Controller to set Temperature
    """

    attached_devices = {
        'samplecontroller': Attach('Controller of the sampletemperature',
                                   TemperatureController),
        'tubecontroller':   Attach('Controller of the tubetemperature',
                                   TemperatureController)
    }

    parameters = {
        'tubeoffset': Param('Keep tube this many degrees below the setpoint.',
                            volatile=True, settable=True)
    }

    def rushTemperature(self, temperature):
        """Move to temperature as fast as possible
        Due to potential delay when going over 310K this will be handled
        in the underlying Tango server."""
        self._dev.RushTemperature(temperature)
        self._setROParam('target', temperature)

    def _combinedStatus(self, maxage=0):
        state = tango.TemperatureController.doStatus(self, maxage)
        # if there is a warning from the controller, display it.
        if state[0] == WARN:
            return state
        else:
            return tango.TemperatureController._combinedStatus(self, maxage)

    def getSampleController(self):
        return self._attached_samplecontroller

    def getTubeController(self):
        return self._attached_tubecontroller

    def stopPressure(self):
        self._dev.StopPressureRegulation()

    def doReadTubeoffset(self):
        return self._dev.tube_offset

    def doWriteTubeoffset(self, value):
        self._dev.tube_offset = value


class PressureController(tango.TemperatureController):
    """Device to be able to set the pressure manually.
    Pressure is set via the controller, which is supposed to handle the limits
    within which setting pressure is allowed.
    """

    parameters = {
        'controller': Param('SEController device name', type=tangodev,
                             mandatory=True, preinit=True),
        'pressuretolerance': Param('Tolerance for the adjustment of the '
                                   'pressure',
                                   settable=True, volatile=True)
    }

    def doPreinit(self, mode):
        tango.TemperatureController.doPreinit(self, mode)

        if mode != SIMULATION:
            self._controller = self._createPyTangoDevice(self.controller)
        else:
            self._controller = HardwareStub(self)

    def doStart(self, value):
        self._controller.setPressure(value)

    def doStop(self):
        pass

    def doReadPressuretolerance(self):
        return self._dev.pressure_tolerance

    def doWritePressuretolerance(self, value):
        self._dev.pressure_tolerance = value
