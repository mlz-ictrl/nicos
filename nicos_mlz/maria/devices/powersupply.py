#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from nicos.core import Param
from nicos.core.constants import SIMULATION
from nicos.devices.tango import AnalogInput


class ReadOnlyPowerSupply(AnalogInput):
    """
    A power supply (voltage and current) device.
    """

    parameters = {
        'voltage': Param('Actual voltage', unit='V',
                         type=float, settable=False, volatile=True),
        'current': Param('Actual current', unit='A',
                         type=float, settable=False, volatile=True),
        'setpoint': Param('Setpoint for value (voltage or current) on '
                          'initialization depending on mode',
                          type=float, settable=False)
    }

    def doInit(self, mode):
        if mode != SIMULATION and self.setpoint is not None:
            self._dev.value = self.setpoint

    def doReadVoltage(self):
        return self._dev.voltage

    def doReadCurrent(self):
        return self._dev.current

    def doPoll(self, n, maxage):
        if n % 5 == 0:
            self._pollParam('voltage', 1)
            self._pollParam('current', 1)
