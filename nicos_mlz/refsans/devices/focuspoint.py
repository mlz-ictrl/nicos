# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <matthias.pomm@hereon.de>
#
# *****************************************************************************

from nicos.core import Moveable, Readable, status
from nicos.core.mixins import HasLimits, HasPrecision
from nicos.core.params import Attach, Override, Param, floatrange


class FocusPoint(HasPrecision, HasLimits, Moveable):

    attached_devices = {
        'table': Attach('table', Moveable),
        'pivot': Attach('pivot', Readable),
    }

    parameters = {
        'gisansdistance': Param('GISANS distance',
                                type=floatrange(0), default=10700),
    }

    parameter_overrides = {
        'precision': Override(default=100),
        'abslimits': Override(mandatory=True, volatile=False),
    }

    hardware_access = False

    def moveToFocus(self):
        self._attached_table.move(self._calculation())

    def doRead(self, maxage=0):
        return self._attached_table.read(maxage)

    def doStart(self, target):
        # self.moveToFocus() or move table
        self._attached_table.move(target)

    def _calculation(self, pivot=None):
        if pivot is None:
            pivot = self._attached_pivot.read(0)
        focus = self.gisansdistance - pivot * self._attached_pivot.grid
        self.log.debug('FocusPoint _calculation focus %f pivot %d', focus,
                       pivot)
        return focus

    def doStatus(self, maxage=0):
        st = self._attached_table.status(maxage)
        if st[0] != status.OK:
            return st
        table = self._attached_table.read(maxage)
        focus = self._calculation()
        return status.OK, 'focus' if self.isAtTarget(table, focus) else st[1]
