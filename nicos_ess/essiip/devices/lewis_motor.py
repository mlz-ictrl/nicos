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
#   Michael Wedel <michael.wedel@esss.se>
#
# *****************************************************************************

from nicos.devices.epics_ng import EpicsAnalogMoveable, EpicsDigitalMoveable, \
    EpicsReadable
from nicos.core import Attach
from nicos.core import status
from nicos.devices.abstract import Motor


class LewisEpicsMotor(EpicsAnalogMoveable, Motor):
    attached_devices = {
        'status_pv': Attach('Status PV', EpicsReadable),
        'stop_pv': Attach('Stop PV', EpicsDigitalMoveable),
        'speed_pv': Attach('Speed PV', EpicsAnalogMoveable),
    }

    def doStatus(self, maxage=0):
        epics_status = self._attached_status_pv.read(0)

        if epics_status == 'moving':
            return status.BUSY, 'Moving to target.'

        return status.OK, ''

    def doIsCompleted(self):
        return self.read() == self.target

    def doStop(self):
        self._attached_stop_pv.start(1)

    def doReadSpeed(self):
        return self._attached_speed_pv.read()

    def doWriteSpeed(self, new_speed):
        self._attached_speed_pv.start(new_speed)
