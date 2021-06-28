#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

from nicos.core import Attach, PositionError, Readable
from nicos.devices.epics import EpicsMoveable, PVMonitor
from nicos.devices.generic import ManualSwitch


class DlsPositioner(PVMonitor, ManualSwitch, EpicsMoveable):
    """A device for controlling the Diamond Light Source's positioner for the
    EPICS motor.

    The DLS positioner allows the motor to only be moved to set positions which
    are pre-defined in the EPICS IOC.

    This device needs to be configured to have the same number of set positions
    as the IOC does.
    """
    attached_devices = {
        'motor': Attach('the underlying motor', Readable),
    }

    def doStart(self, target):
        self._put_pv('writepv', target)
        if target != self.doRead():
            self._wait_for_start()

    def doStatus(self, maxage=0):
        return self._attached_motor.doStatus(maxage)

    def doRead(self, maxage=0):
        position = EpicsMoveable.doRead(self, maxage)
        if position in self.states:
            return position
        raise PositionError(self, 'device is in an unknown state')

    def _get_pv_parameters(self):
        return {'readpv', 'writepv'}
