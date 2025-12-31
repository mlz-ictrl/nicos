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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************
"""This module contains specific EPICS devices."""

from nicos.core import Param, pvname, status
from nicos.core.params import Override, none_or
from nicos.devices.epics import EpicsAnalogMoveable


class EpicsControlledAnalogMoveable(EpicsAnalogMoveable):
    """
    Extend `EpicsAnalogMoveable` with additional PV's to check device
    readyness and to stop it.

    This class extends `EpicsAnalogMoveable` with additional functionality
    via two optional PVs. If none of these PVs are given in the setup file, this
    class is equivalent to its parent class EpicsAnalogMoveable.

    - `readypv`: If this parameter is 0, the device is busy and not able to
    receive a new movement command.

    - `stoppv`: Setting this parameter to 1 should stop the device. If this PV
    is not given, the `doStop` implementation of the base class is used, if
    the device is actually busy (target not equal to current position or
    `readypv == 0`)
    """
    parameters = {
        'readypv': Param('Optional PV which should be 0 if the device is not '
                         'ready to move and 1 otherwise.',
                         type=none_or(pvname), mandatory=False, userparam=False),
        'stoppv': Param('Optional PV which is set to 1 when the device is stopped.',
                        type=none_or(pvname), mandatory=False, userparam=False),
    }

    def _get_pv_parameters(self):
        params = EpicsAnalogMoveable._get_pv_parameters(self)
        if self.readypv:
            params.add('readypv')
        if self.stoppv:
            params.add('stoppv')
        return params

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doIsAllowed(self, target):
        if self.doStatus(0)[0] != status.OK:
            return False, 'device not ready to start a movement'
        return True, ''

    def doStatus(self, maxage=0):
        # First read the status of the underlying device. If it is ok, check
        # the readypv
        (stat, msg) = EpicsAnalogMoveable.doStatus(self, maxage)
        if stat != status.OK:
            return (stat, msg)
        if self._get_pv('readypv') == 0:
            return status.BUSY, msg
        return status.OK, msg

    def doStop(self):
        if self.stoppv:
            self._put_pv('stoppv', 1)
        else:
            if self.readypv:
                if self.status()[0] == status.BUSY:
                    self.doStart(self.doRead())
            else:
                # Default behaviour of EpicsAnalogMoveable
                self.doStart(self.doRead())


class EpicsControlledDigitalMoveable(EpicsControlledAnalogMoveable):
    """
    `EpicsControlledAnalogMoveable` for integer values.
    """
    valuetype = int

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
    }
