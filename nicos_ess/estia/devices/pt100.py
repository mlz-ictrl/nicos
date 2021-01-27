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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
from nicos.core import Param, pvname, status

from nicos_ess.devices.epics.base import EpicsReadableEss

error_bits = {
    'underrange': 0x1,
    'overrange': 0x2,
    'limit1 overshot': 0x4,
    'limit1 undershot': 0x8,
    'limit2 overshot': 0x10,
    'limit2 undershot': 0x20,
    'error': 0x40,
}


def get_pt100_status_message(value):
    """
    Maps the content of the status PV to the internal status of the device
    """

    # The sign bit is used as a flag for the internal status of the device.
    # In case its value is 1 we need to enforce 'value' to be unsigned.
    #
    # Error map
    # |   15   |   14  |  ... |   6   | 5 | 4 | 3 | 2 |     1     |     0      |
    # | Toggle | State | None | Error |  Lim2 |  Lim1 | Overrange | Underrange |

    if value < 0:
        value = (value + 0x100000000) | 0xFF
    if value & error_bits['error']:
        value ^= error_bits['error']
        for text, error in error_bits.items():
            if value == error:
                return status.ERROR, text
        return status.ERROR, 'error'
    return status.OK, ''


class EpicsPT100Temperature(EpicsReadableEss):
    """
    Device that reads one of the PT100 sensors.
    """

    parameters = {
        'statuspv': Param('PV name for status code', type=pvname,
                          mandatory=False),
    }

    def _get_record_fields(self):
        pvs = self.pv_parameters
        if self.statuspv:
            pvs |= {'statuspv'}
        return pvs

    def doStatus(self, maxage=0):
        mapped_status, status_message = EpicsReadableEss.doStatus(self, maxage)
        if mapped_status != status.OK:
            return mapped_status, status_message

        if self.statuspv:
            st = int(self._get_pv('statuspv'))
            return get_pt100_status_message(st)

        return status.UNKNOWN, ''
