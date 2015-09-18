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

"""Device class for PUMA PG filter."""

import time

from nicos.core import Moveable, Readable, status, NicosError, oneof, Attach


class PGFilter(Moveable):

    attached_devices = {
        'io_status': Attach('status of the limit switches', Readable),
        'io_set':    Attach('output to set', Moveable),
    }

    valuetype = oneof('in', 'out')

    def doStart(self, position):
        try:

            if self.doStatus()[0] != status.OK:
                raise NicosError(self, 'filter returned wrong position')

            if position == self.read(0):
                return

            if position == 'in':
                self._adevs['io_set'].move(1)
            elif position == 'out':
                self._adevs['io_set'].move(0)
            else:
                # shouldn't happen...
                self.log.info('PG filter: illegal input')
                return

            time.sleep(2)

            if self.doStatus()[0] == status.ERROR:
                raise NicosError(self, 'PG filter is not readable, please '
                                 'check device!')
        finally:
            self.log.info('PG filter: ', self.read(0))

    def doRead(self, maxage=0):
        result = self._adevs['io_status'].doRead(0)
        if result == 2:
            return 'in'
        elif result == 1:
            return 'out'
        else:
            raise NicosError(self, 'PG filter is not readable, check device!')

    def doStatus(self, maxage=0):
        s = self._adevs['io_status'].doRead(0)
        if s in [1, 2]:
            return (status.OK, 'idle')
        else:
            return (status.ERROR, 'filter is in error state')
