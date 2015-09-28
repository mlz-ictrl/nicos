#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""Sans1 spinflipper specific devices."""

import time
from nicos.core import Param, status, tangodev, SIMULATION, HasTimeout
from nicos.devices.tango import AnalogInput, AnalogOutput


class SpinflipperPower(HasTimeout, AnalogOutput):
    """This class provides access to the ag1016 power, forward power
    and reverse power.

    Additionally, it stays BUSY for 'busytime' after setting a new power before
    returning to the idle state. This gives the ag1016 some time to update
    forward and reverse power, which are read after the busytime has passed.

    Due to this additional waiting, the parameter 'maxage' should *never*
    be smaller than 'pollinterval' + 'busytime'.
    Recommended Values are:  busytime = 5, pollinterval = 3, maxage = 15
    """

    parameters = {
        'forwardtangodevice': Param('Forward tango device address',
                                    type=tangodev, mandatory=True, preinit=True,
                                    settable=False),
        'reversetangodevice': Param('Reverse tango device address',
                                    type=tangodev, mandatory=True, preinit=True,
                                    settable=False),
        'forward':            Param('Forward power', unit='W',
                                    settable=False, category='general',
                                    volatile=True),
        'reverse':            Param('Reverse power', unit='W',
                                    settable=False, category='general',
                                    volatile=True),
        'busytime':           Param('Time to stabilize output readings',
                                    type=float, unit='s', default=5,
                                    settable=True),
    }

    valuetype = float
    hardware_access = True

    def doPreinit(self, mode):
        AnalogOutput.doPreinit(self, mode)
        if mode != SIMULATION:
            self._forwardDev = AnalogInput('%s._forwardDev' % self.name,
                                           tangodevice=self.forwardtangodevice,
                                           lowlevel=True)

            self._reverseDev = AnalogInput('%s._reverseDev' % self.name,
                                           tangodevice=self.reversetangodevice,
                                           lowlevel=True)

    def doTime(self, move_from, move_to):
        return self.busytime

    def doStatus(self, maxage=0):
        if self._timesout:
            if time.time() < self._timesout[-1][1]:
                return status.BUSY, 'waiting %.1gs for stabilisation' % self.busytime
        return AnalogOutput.doStatus(self, maxage)

    def doReadForward(self):
        self.wait()
        return self._forwardDev.read(0)

    def doReadReverse(self):
        self.wait()
        return self._reverseDev.read(0)

    def doPoll(self, nr, maxage):
        _ = self.forward
        _ = self.reverse
