#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Class for controlling the POLI shutter."""

import time

from nicos.core import HasTimeout, Moveable, Attach, Override, \
    MoveError, status, oneof


class Shutter(HasTimeout, Moveable):
    """Controlling the shutter."""

    valuetype = oneof('closed', 'open')

    attached_devices = {
        'io': Attach('shutter I/Os', Moveable),
    }

    parameter_overrides = {
        'fmtstr':     Override(default='%s'),
        'timeout':    Override(default=10),
        'unit':       Override(mandatory=False, default=''),
    }

    def doStatus(self, maxage=0):
        bits = self._attached_io.read(maxage)
        text = []
        code = status.OK
        if bits & 0b100:
            text.append('remote')
        else:
            text.append('local')
            code = status.WARN
        # bit 3: room free
        # bit 4: keyswitch
        if bits & 0b100000:
            text.append('error')
            code = status.ERROR
        # HasTimeout will check for target reached
        return code, ', '.join(text)

    def doRead(self, maxage=0):
        value = self._attached_io.read(maxage)
        if value & 1:
            return 'open'
        elif value & 2:
            return 'closed'
        return 'unknown'

    def doStart(self, target):
        if target == 'open' and not self._attached_io.read(0) & 0b100:
            raise MoveError(self, 'cannot open shutter: set to local mode')
        # bit 0: data valid, bit 1: open, bit 2: close (inverted)
        self._attached_io.start(0)
        time.sleep(0.1)
        self._attached_io.start(0b111 if target == 'open' else 0b001)
