#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""Magnetic Lock."""

import time

from nicos.core import Moveable, Readable, status, NicosError, oneof


class MagLock(Moveable):

    attached_devices = {
        'magazin': (Moveable, 'The monochanger magazin'),
        'io_open': (Readable, 'readout for the status'),
        'io_closed': (Readable, 'readout for the status'),
        'io_set': (Moveable, 'output to set'),
    }

    valuetype = oneof('open', 'closed')

#    parameters = {
#        'states':    Param('List of state names.', type=listof(str),
#                           mandatory=True),
#        'values':    Param('List of values to move to', type=listof(anytype),
#                           mandatory=True),
#        'io_values': Param('List of values to move to', type=listof(anytype),
#                           mandatory=True),
#        'precision': Param('Precision for comparison', mandatory=True),
#    }

    def doInit(self, mode):
        return

    def doStart(self, position):
        magpos = self._readMag()
        if magpos not in [0, 1, 2, 3]:
            raise NicosError(self, 'magazin at unknown position')

        if position == self.doRead(0):
            return

        if position == 'closed':
            self._adevs['io_set'].move(0)
        elif position == 'open':
            self._adevs['io_set'].move(1 << magpos)
        else:
            self.log.info('Maglock: illegal input')
            return

        time.sleep(2)
        if self.doRead (0) != position:
            raise NicosError(self, 'maglock returned wrong position!')

    def doRead(self, maxage=0):

        magpos = self._readMag()

#        if magpos == 4:
#            raise NicosError(self, 'magazin at unknown position')
#            return

        try:
            s = (((self._adevs['io_open'].read(0) >> magpos) & 1) << 1) + \
                  ((self._adevs['io_closed'].read (0) >> magpos) & 1)
        except Exception:
            raise NicosError(self, 'cannot read position of maglock!')
        s = s - 1

        if s == 0:
            return 'closed'
        elif s == 1:
            return 'open'
        else:
            raise NicosError(self, 'Magazin magnet switches in undefined status;'
                             ' check switches')

    def doStatus(self, maxage=0):
        s = self.doRead(0)
        if s in ['closed','open']:
            return (status.OK, 'idle')
        else:
            return (status.ERROR, 'maglock is in error state')

    def _readMag(self):
        s = self._adevs['magazin'].doRead(0)
        if s == 'A':
            return 0
        elif s == 'B':
            return 1
        elif s == 'C':
            return 2
        elif s == 'D':
            return 3
        else:
            return 4
