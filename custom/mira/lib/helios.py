#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Class for FRM-II Helios 3He polarizer operation."""

import PowerSupply

from nicos.core import Moveable, Param, Override, usermethod, oneof, UsageError
from nicos.devices.taco.core import TacoDevice


class HePolarizer(TacoDevice, Moveable):
    """
    Class for controlling the polarizing direction of the Helios system.
    """

    taco_class = PowerSupply.VoltageControl

    parameters = {
        'current': Param('Current polarization direction', settable=True,
                         type=oneof('up', 'down')),
    }

    parameter_overrides = {
        'abslimits': Override(mandatory=False, default=('down', 'up')),
    }

    valuetype = oneof('up', 'down')

    def doInit(self, mode):
        # self.current = 'up'
        pass

    @usermethod
    def define(self, value):
        """Define the current polarizing direction as 'up' or 'down'."""
        if value not in ['up', 'down']:
            raise UsageError(self, "value must be 'up' or 'down'")
        self.current = value

    def doRead(self, maxage=0):
        return self.current

    def doReadUnit(self):
        return ''

    def doStart(self, value):
        if value not in ['up', 'down']:
            raise UsageError(self, "value must be 'up' or 'down'")
        if self.current == value:
            return
        curvoltage = self._taco_guard(self._dev.read)
        if curvoltage > 4:
            self._taco_guard(self._dev.write, 0)
        else:
            self._taco_guard(self._dev.write, 5)
        self.current = value
