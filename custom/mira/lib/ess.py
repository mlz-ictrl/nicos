#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Class for MIRA magnet consisting of the ESS-Lambda power supply and polarity
switches attached to digital IOs of a Phytron motor controller.
"""

__version__ = "$Revision$"

from time import sleep

from PowerSupply import CurrentControl

from nicos.io import AnalogOutput, DigitalOutput
from nicos.device import Param


class ESSController(AnalogOutput):

    taco_class = CurrentControl

    attached_devices = {
        'plusswitch':  (DigitalOutput, 'Switch to set for positive polarity'),
        'minusswitch': (DigitalOutput, 'Switch to set for negative polarity'),
    }

    # XXX switch to single "ramp" parameter
    parameters = {
        'ramprate':  Param('Rate of ramping', type=float, default=60,
                           unit='main/min', settable=True),
        'rampdelay': Param('Time per ramping step', type=float, default=5,
                           unit='s', settable=True),
    }

    def doInit(self):
        if self._mode != 'simulation':
            self._dev.setRamp(0)

    # XXX make it parallel moving!

    def doStart(self, value):
        delay = self.rampdelay
        if value != 0:
            minus, plus = self._adevs['minusswitch'], self._adevs['plusswitch']
            # select which switch must be on and which off
            switch = value < 0 and minus or plus
            other  = value < 0 and plus or minus
            # if the switch values are not correct, drive to zero and switch
            if switch.read() & 1 != 1:
                self.doStart(0)
                other.start(0)
                switch.start(1)
            # then, just continue ramping to the absolute value
            value = abs(value)
        currentval = self._taco_guard(self._dev.read)
        diff = value - currentval
        direction = diff > 0 and 1 or -1
        stepwidth = self.ramprate / 60. * delay
        steps, fraction = divmod(abs(diff), stepwidth)
        for i in xrange(int(steps)):
            currentval += direction * stepwidth
            self._taco_guard(self._dev.write, currentval)
            sleep(delay)
        self._taco_guard(self._dev.write, value)
        sleep(delay)

    def _off(self):
        self.start(0)
        self._adevs['minusswitch'].start(0)
        self._adevs['plusswitch'].start(0)

    def doRead(self):
        sign = +1
        if self._adevs['minusswitch'].read() & 1:
            sign = -1
        return sign * self._taco_guard(self._dev.read)

    def doWait(self):
        pass  # all movement happens in doStart()
