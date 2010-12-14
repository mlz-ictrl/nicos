#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   ESS-Lambda power supply class
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Class for MIRA magnet consisting of the ESS-Lambda power supply and polarity
switches attached to digital IOs of a Phytron motor controller.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from time import sleep

from nicm.device import Param
from nicm.taco.analog import Output as AnalogOutput
from nicm.taco.digital import Output as DigitalOutput


class ESSController(AnalogOutput):

    attached_devices = {
        'plusswitch': DigitalOutput,
        'minusswitch': DigitalOutput,
    }

    parameters = {
        'ramprate':  Param('Rate of ramping', type=float, default=5,
                           unit='main/min', settable=True),
        'rampdelay': Param('Time per ramping step', type=float, default=5,
                           unit='s', settable=True),
    }

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
	steps, fraction = divmod(abs(diff), self.stepwidth)
        for i in xrange(int(steps)):
            currentval += direction * self.stepwidth
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
