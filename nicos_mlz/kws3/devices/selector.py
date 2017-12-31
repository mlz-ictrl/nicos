#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Class for KWS-3 selector (custom solution using Pfeiffer controller)."""

import time

from nicos.core import Moveable, Readable, HasLimits, HasPrecision, \
    Attach, MoveError, status


class SelectorSpeed(HasLimits, HasPrecision, Moveable):
    """Control selector speed via SPS I/O devices."""

    attached_devices = {
        'valid':     Attach('Output for the "valid" bit', Moveable),
        'speedset':  Attach('Output for speed setpoint', Moveable),
        'speedread': Attach('Input for reading the speed', Readable),
        'status':    Attach('Input for reading the status', Readable),
    }

    def doRead(self, maxage=0):
        return self._attached_speedread.read(maxage)

    def doStatus(self, maxage=0):
        stbits = self._attached_status.read(maxage)
        if not stbits & 1:
            return status.WARN, 'local mode'
        if not stbits & 2:
            if self._attached_speedread.read(maxage) == 0:
                return status.WARN, 'off'
            return status.BUSY, 'moving'
        return status.OK, ''

    def doStart(self, pos):
        stbits = self._attached_status.read(0)
        if not stbits & 1:
            raise MoveError(self, 'selector is in local mode')
        # valid bit needs a rising edge
        self._attached_valid.maw(0)
        self._attached_speedset.maw(pos)
        self._attached_valid.maw(1)
        time.sleep(0.2)
