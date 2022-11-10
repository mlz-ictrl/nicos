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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos.core import Moveable, Param, pvname
from nicos.core.mixins import CanDisable
from nicos.devices.epics import EpicsMoveable

from nicos_sinq.devices.epics.generic import WindowMoveable


class SLSMagnet(CanDisable, WindowMoveable):

    parameters = {
        'wenable': Param('PV to enable the magnet',
                         type=pvname),
        'renable': Param('PV to read if the magnet is on',
                         type=pvname),
    }

    def _get_pv_parameters(self):
        pvs = EpicsMoveable._get_pv_parameters(self)
        pvs.add('wenable')
        pvs.add('renable')
        return pvs

    def doEnable(self, on):
        self._pvs['wenable'].put(int(on))

    def isAllowed(self, pos):
        if not self._pvs['renable'].get():
            return False, 'Magnet disabled'
        return Moveable.isAllowed(self, pos)
