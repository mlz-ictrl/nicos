# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

from nicos.core import Moveable, Param, pvname, status
from nicos.core.constants import MASTER
from nicos.core.mixins import CanDisable
from nicos.devices.epics.pyepics import EpicsMoveable

from nicos_sinq.devices.epics.generic import WindowMoveable


class SampleMagnet(CanDisable, WindowMoveable):

    parameters = {
        'wenable': Param('PV to enable the magnet',
                         type=pvname),
        'renable': Param('PV to read if the magnet is on',
                         type=pvname),
        'on': Param('Equals the on value from the latest doEnable call',
                    type=bool, internal=True, settable=True),
    }

    def doInit(self, mode):
        WindowMoveable.doInit(self, mode)

        # Set initial target = current status
        if mode == MASTER:
            self.on = self.isEnabled

    def _get_pv_parameters(self):
        pvs = EpicsMoveable._get_pv_parameters(self)
        pvs.add('wenable')
        pvs.add('renable')
        return pvs

    def doEnable(self, on):
        self._pvs['wenable'].put(int(on))

        # Register in the cache that an enable command has been given
        self.on = on

    @property
    def isEnabled(self):
        """Shows if the magnet is enabled or not"""
        if not self._sim_intercept:
            return self._get_pv('renable') != 0
        return True

    def doStatus(self, maxage=0):

        # Check if an enable command has been given
        isEnabled = self.isEnabled
        if self.on:
            # Enable command has been given
            if isEnabled:
                return WindowMoveable.doStatus(self, maxage)
            return status.BUSY, 'Enabling'
        else:
            # Disable command has been given
            if isEnabled:
                return status.BUSY, 'Disabling'
            return status.DISABLED, 'Magnet is disabled'

    def isAllowed(self, pos):
        if not self.isEnabled:
            return False, 'Magnet disabled'
        return Moveable.isAllowed(self, pos)
