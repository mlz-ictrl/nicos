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
#
# *****************************************************************************

"""Multi-channel counter card class."""

import TMCS
import TACOStates

from nicos.core import status, tacodev, Measurable, Param
from nicos.devices.taco.core import TacoDevice


class Channel(TacoDevice, Measurable):
    taco_class = TMCS.Channel

    parameters = {
        'admin': Param('The admin taco device', type=tacodev, mandatory=True),
    }

    def doInit(self, mode):
        if mode != 'simulation':
            self._admin = self._create_client(self.admin, TMCS.Admin)

    def doStart(self, **preset):
        self._taco_guard(self._admin.start)

    def doReset(self):
        self._taco_guard(self._admin.stop)
        self._taco_guard(self._dev.clear)

    def doIsCompleted(self):
        return self._taco_guard(self._admin.deviceState) == TACOStates.STOPPED

    def doStop(self):
        self._taco_guard(self._admin.stop)

    def doRead(self, maxage=0):
        return map(int, self._taco_guard(self._dev.read))

    def doStatus(self, maxage=0):
        state = self._taco_guard(self._admin.deviceState)
        if state == TACOStates.STOPPED:
            return status.OK, 'stopped'
        return status.BUSY, TACOStates.stateDescription(state)

    def doReadUnit(self):
        return 'cts'
