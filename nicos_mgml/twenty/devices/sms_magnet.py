# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Petr Cermak <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""Allows to read Cryogenics sms power supply"""

from nicos.core import Attach, HasLimits, Moveable, Override, Param
from nicos.core.params import tupleof
from nicos.devices.entangle import RampActuator


class MasterMagnet(HasLimits, Moveable):

    parameters = {
        'mainlimits': Param('Limits of the main powersupply',
                            type=tupleof(float, float), settable=True,
                            default=(0, 0),),
    }

    attached_devices = {
        'maindev': Attach('Cryogenics main Actuator', RampActuator),
        'boosterdev': Attach('Cryogenics booster Actuator', RampActuator),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='T'),
    }

    def doRead(self, maxage=0):
        return sum(self._attached_maindev.read(maxage),
                   self._attached_boosterdev.read(maxage))

    def doStart(self, pos):
        if self.mainlimits[0] <= pos <= self.mainlimits[1]:
            # move only main coil
            self._attached_maindev.move(pos)
            # check second coil on zero
            if self._attached_boosterdev.target > 0:
                self._attached_boosterdev.move(0)
        elif pos < self.mainlimits[0]:
            boosterpos = pos - self.mainlimits[0]
            self._attached_boosterdev.move(boosterpos)
            self._attached_maindev.move(self.mainlimits[0])
        elif pos > self.mainlimits[1]:
            boosterpos = pos - self.mainlimits[1]
            self._attached_boosterdev.move(boosterpos)
            self._attached_maindev.move(self.mainlimits[1])
