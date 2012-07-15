#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS temperature controller classes."""

__version__ = "$Revision$"

import time

import TANGOStates

from TANGOStates import TANGOState
from AnalogInputClient import AnalogInputClient
from TemperatureControllerClient import TemperatureControllerClient

from nicos.tango.io import AnalogInput,  AnalogOutput

from nicos.core import status, Param, Readable, Moveable, HasOffset, \
     HasLimits, TimeoutError, NicosError

# BaseTemperatureSensorClient has currently no defined TANGO interface
# (represented as AI at the moment)
#class BaseTemperatureSensorClient(BaseInputClient):
#    pass

class TemperatureSensor(AnalogInput, Readable):
    """Temperature sensor device (currently represented by AI)."""
    tango_class = AnalogInputClient


class TemperatureController(AnalogOutput, HasLimits, HasOffset, Moveable):
    """TANGO temperature controller device."""

    parameters =  {
        'p':         Param('The P control parameter', settable=True,
                           type=float, category='general'),
        'i':         Param('The I control parameter', settable=True,
                           type=float, category='general'),
        'd':         Param('The D control parameter', settable=True,
                           type=float, category='general'),
    }

    tango_class = TemperatureControllerClient

    def doRead(self, maxage=0):
        return AnalogOutput.doRead(self, maxage) - self.offset

    def doStart(self, target):
        if self.status()[0] == status.BUSY:
            self.log.debug('stopping running temperature change')
            self.doStop()
        AnalogOutput.doStart(self, target + self.offset)

    def doStop(self):
        self._tango_guard(self._dev.abort)

    def doStatus(self, maxage=0):
        state = self._tango_guard(self._dev.getDeviceState)
        if state == TANGOState.MOVING:
            return (status.BUSY, 'moving')
        elif state == TANGOState.UNKNOWN:
            return (status.NOTREACHED, 'temperature not reached')
        else:
            return (status.ERROR, TANGOStates.toString(state))

    def doWait(self):
        delay = self.loopdelay

        window = self.window
        tolerance = self.tolerance
        setpoint = self.target
        timeout = self.timeout
        firststart = started = time.time()

        while 1:
            value = AnalogOutput.doRead(self)
            self.log.debug('current temperature %7.3f %s' % (value, self.unit))
            now = time.time()
            if abs(value - setpoint) > tolerance:
                # start again
                started = now
            elif now > started + window:
                return value
            if now - firststart > timeout:
                raise TimeoutError(self, 'temperature not reached in %s seconds'
                                   % timeout)
            time.sleep(delay)

    def doReadP(self):
        try:
            return self._tango_guard(self._dev.p)
        except NicosError, err:
            self.log.debug('TANGO call: %s' % str(err))
            return -1

    def doReadI(self):
        try:
            return self._tango_guard(self._dev.i)
        except NicosError, err:
            self.log.debug('TANGO call: %s' % str(err))
            return -1

    def doReadD(self):
        try:
            return self._tango_guard(self._dev.d)
        except NicosError, err:
            self.log.debug('TANGO call: %s' % str(err))
            return -1

    def doWriteP(self, value):
        self._tango_guard(self._dev.setP, value)

    def doWriteI(self, value):
        self._tango_guard(self._dev.setI, value)

    def doWriteD(self, value):
        self._tango_guard(self._dev.setD, value)
