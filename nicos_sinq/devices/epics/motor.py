#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <mnichele.brambilla@psi.ch>
#
# *****************************************************************************
from nicos import session
from nicos.core import MAIN, Param, status

from nicos_ess.devices.epics import EpicsMotor
from nicos_ess.devices.epics.extensions import HasDisablePv


class MotorCanDisable(HasDisablePv, EpicsMotor):

    parameters = {
        'auto_enable': Param('Automatically enable the motor when the setup is'
                             ' loaded', type=bool, default=False,
                             settable=False),
    }

    def doInit(self, mode):
        EpicsMotor.doInit(self, mode)
        if session.sessiontype == MAIN and self.auto_enable:
            self.enable()

    def doShutdown(self):
        if session.sessiontype == MAIN:
            self.disable()
        EpicsMotor.doShutdown(self)

    def doStatus(self, maxage=0):
        stat, message = self._get_status_message()
        self._motor_status = stat, message
        if stat == status.ERROR:
            return stat, message or 'Unknown problem in record'
        elif stat == status.WARN:
            return stat, message

        if not self.isEnabled:
            return status.WARN, 'Motor is disabled'

        return EpicsMotor.doStatus(self, maxage)

    def doIsAllowed(self, target):
        if not self.isEnabled:
            return False, 'Motor disabled'
        return EpicsMotor.doIsAllowed(self, target)
