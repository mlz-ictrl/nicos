#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************

"""Device class for the shutter cylinder device."""

import time

from nicos.core import Moveable, Readable, NicosError, Param, Attach


class SH_Cylinder(Moveable):

    attached_devices = {
        'io_ref': Attach('limit switches', Readable),
        'io_air': Attach('air in the open/close direction', Moveable),
        'io_pos': Attach('position stop, if in closed position, -1', Moveable),
    }

    parameters = {
        'timedelay': Param('Waiting time for the movement',
                           type=float, default=3, settable=True,
                           mandatory=False, unit='s'),
    }

    def doStart(self, position):
        if position == self.read(0):
            return

        if self._checkAir() != 1:
            raise NicosError(self, 'No air! Please open the shutter with the '
                             'button near the door.')

        self._attached_io_air.move(0)
        time.sleep(self.timedelay)

        if self._attached_io_ref.read(0) != 1:
            raise NicosError(self, 'Cannot close the shutter!')

        if position != -1:
            self._attached_io_pos.move(position)
            time.sleep(self.timedelay)
            self._attached_io_air.move(1)
            time.sleep(self.timedelay)

    def doRead(self, maxage=0):
        if self._attached_io_ref.read(0) == 1:
            return -1
        if self._attached_io_air.read(0) == 1:
            return self._attached_io_pos.read(0)

    def _checkAir(self):
        if self._attached_io_ref.read(0) == 1:
            self._attached_io_air.move(1)
            time.sleep(self.timedelay)
            if self._attached_io_ref.read(0) == 1:
                return 0
        return 1
