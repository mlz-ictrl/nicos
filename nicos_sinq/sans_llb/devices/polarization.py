# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2026-present by the NICOS contributors (see AUTHORS)
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
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************
from nicos.core import HasMapping, oneof, status
from nicos.core.device import Attach, Moveable, Param
from nicos_sinq.sans_llb.devices.collimatorcontroller import CollimationChangeble


class PolarizationSwitcher(HasMapping, Moveable):
    """
    A device to switch polarization of SANS-LLB on/off by changing the mapping of the
    collimation selection device (remove longest collimation and change first guide to polarizing).
    """

    parameters = {
        'fallback': Param('The position which is used if no matching collimation exists.',
                          type=str, settable=True, default=''),
    }

    attached_devices = {
        'coll': Attach('Collimation changer device to use',
                        CollimationChangeble),
    }

    def doInit(self, mode):
        self.valuetype = oneof(*self.mapping)

    def doStatus(self, maxage=0):
        cur_map = self._attached_coll.mapping
        if cur_map in self.mapping.values():
            state = self._attached_coll.status()[0]
            return (state, '')
        return (status.UNKNOWN, 'mapping of coll does not match')

    def doRead(self, maxage=0):
        for key, value in self.mapping.items():
            if value == self._attached_coll.mapping:
                return key
        return "Unknown"

    def doStart(self, target):
        cur_map = self._attached_coll.mapping
        if cur_map == self.mapping[target]:
            return
        new_map = self.mapping[target]

        cur_pos = self._attached_coll()
        if cur_pos in new_map:
            # replace the coll mapping and move to the same collimation distance
            self._attached_coll.mapping = new_map
            self._attached_coll.start(cur_pos)
        elif self.fallback in self.mapping:
            # replace the coll mapping and move to the fallback distance
            self._attached_coll.mapping = new_map
            self._attached_coll.start(self.fallback)
        else:
            raise ValueError("current collimation not possible in target mode")
