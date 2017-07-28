#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Michael Wedel <michael.wedel@esss.se>
#
# *****************************************************************************

"""
This module provides control for Julabo devices via EPICS.
"""

from nicos.core import Param, pvname, status, ConfigurationError
from nicos.devices.epics import EpicsWindowTimeoutDevice
from .epics_extensions import HasSwitchPv


class EpicsJulaboController(HasSwitchPv, EpicsWindowTimeoutDevice):
    """
    Julabo devices with status and power switch.

    The device status is obtained via two EPICS PVs, one with an
    integer status code and one with an actual message string.
    Both map directly to the values specified in the device manual
    (for example Julabo F25).

    In addition, the status is WARN when the actuators of the device
    are switched off.
    """

    parameters = {
        'statuscodepv': Param('PV name for integer status code', type=pvname),
        'statusmsgpv': Param('PV name for status message', type=pvname),
    }

    def _get_pv_parameters(self):
        if len(set(map(bool, (self.statuscodepv, self.statusmsgpv)))) > 1:
            raise ConfigurationError(
                'Provide either both statuscodepv and statusmsgpv or neither. It is '
                'not supported to specify only one of them.')

        pvs = set()
        if self.statuscodepv and self.statusmsgpv:
            pvs.add('statuscodepv')
            pvs.add('statusmsgpv')

        return pvs | super(EpicsJulaboController, self)._get_pv_parameters()

    def doStatus(self, maxage=0):
        if self.statuscodepv and self.statusmsgpv:
            status_code = self._get_pv('statuscodepv')
            if status_code < 0:
                status_msg = self._get_pv('statusmsgpv')
                return status.ERROR, '%d: %s' % (status_code, status_msg)

        if not self.isSwitchedOn:
            return status.WARN, 'Device is switched off'

        return super(EpicsJulaboController, self).doStatus(maxage)
