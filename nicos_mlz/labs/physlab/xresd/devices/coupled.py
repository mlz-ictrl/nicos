#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Alexander Book <alexander.book@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import Attach
from nicos.core.params import Param
from nicos.devices.abstract import Moveable


class CoupledMotor(Moveable):

    attached_devices = {
        'maxis': Attach('Main axis to move', Moveable),
        'caxis': Attach('Coupled axis (to main axis) by the relation '
                        'caxis = maxis / 2 + offset', Moveable)
    }

    parameters = {
        'offset': Param('Offset between mainAxis and slaveAxis',
                        type=float, default=.0, settable=True)
    }

    def doStart(self, value):
        self._attached_maxis.start(value)
        self._attached_caxis.start(value / 2 + self.offset)

    def doIsAtTarget(self, pos, target):
        axis = self._attached_maxis.isAtTarget(pos, target)
        coupled = self._attached_caxis.isAtTarget(
            target=target / 2 + self.offset)

        return axis and coupled

    def doRead(self, maxage=None):
        return self._attached_maxis.read(maxage)
