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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# ****************************************************************************

"""
Devices to control the sample environment at SPHERES
"""

from __future__ import absolute_import, division, print_function

from time import time as currenttime

from nicos import session
from nicos.core import SIMULATION, oneof
from nicos.core.params import Attach, Param, tangodev
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
        'tubeoffset':  Param('Keep tube this many degrees below the setpoint.',
                             volatile=True, settable=True),
        'samplestick': Param('Sample stick currently in use',
                             type=oneof('lt', 'ht'),
                             volatile=True, settable=True),
        'devtarget':   Param('Target of the underlying tango device',
                             volatile=True)
    }

    def rushTemperature(self, temperature):
        """Move to temperature as fast as possible
        Due to potential delay when going over 310K this will be handled
        in the underlying Tango server."""
        if session.mode == SIMULATION:
            return

        self._dev.RushTemperature(temperature)

    def _combinedStatus(self, maxage=0):
        state = tango.TemperatureController.doStatus(self, maxage)
        # if there is a warning from the controller, display it.
        if state[0] == WARN:
            return state
        else:
            return tango.TemperatureController._combinedStatus(self, maxage)

    def stopPressure(self):
        self._dev.StopPressureRegulation()

    def doReadTubeoffset(self):
        return self._dev.tube_offset

    def doWriteTubeoffset(self, value):
        self._dev.tube_offset = value

    def doReadSamplestick(self):
        return self._dev.sample_stick

    def doWriteSamplestick(self, value):
        self._dev.sample_stick = value

    def doReadDevtarget(self):
        if not self._dev:
            return None
        return self._dev.target

    def isAtTarget(self, val):
        ct = currenttime()
        self._cacheCB('value', val, ct)
        if self.devtarget is None:
            return True

        # check subset of _history which is in window
        # also check if there is at least one value before window
        # to know we have enough datapoints
        hist = self._history[:]
        window_start = ct - self.window
        hist_in_window = [v for (t, v) in hist if t >= window_start]
        stable = all(abs(v - self.devtarget) <= self.precision
                     for v in hist_in_window)
        if 0 < len(hist_in_window) < len(hist) and stable:  # pylint: disable=len-as-condition
            if hasattr(self, 'doIsAtTarget'):
                return self.doIsAtTarget(val)
            return True
        return False

    def doIsAtTarget(self, pos):
        target = self.devtarget
        if target is None:
            return True
        return abs(target - pos) <= self.precision


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
