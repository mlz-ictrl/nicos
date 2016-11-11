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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Magnetic Lock."""

from nicos import session
from nicos.core import Moveable, Readable, status, NicosError, oneof, Param, \
    Attach, listof


class MagLock(Moveable):

    attached_devices = {
        'magazin': Attach('The monochromator magazin', Moveable),
        'io_open': Attach('readout for the status', Readable),
        'io_closed': Attach('readout for the status', Readable),
        'io_set': Attach('output to set', Moveable),
    }

    valuetype = oneof('open', 'closed')

    parameters = {
        'states':    Param('List of state names', type=listof(str),
                           mandatory=True),
    }
#    parameters = {
#        'values':    Param('List of values to move to', type=listof(anytype),
#                           mandatory=True),
#        'io_values': Param('List of values to move to', type=listof(anytype),
#                           mandatory=True),
#        'precision': Param('Precision for comparison', mandatory=True),
#    }

    def _bitmask(self, num):
        return 1 << num

    def doStart(self, position):
        magpos = self._magpos
        if magpos not in [0, 1, 2, 3]:
            raise NicosError(self, 'depot at unknown position')

        if position == self.read(0):
            return

        if position == 'closed':
            self._attached_io_set.move(0)
        elif position == 'open':
            self._attached_io_set.move(self._bitmask(magpos))
        else:
            self.log.info('Maglock: illegal input')
            return

        session.delay(2)  # XXX!

        if self.read(0) != position:
            raise NicosError(self, 'maglock returned wrong position!')
        else:
            self.log.info('Maglock: %s', self.read(0))

    def _read(self):
        '''return an internal string representation of the right sensing
        switches
        '''
        magpos = self._magpos

#        if magpos == 4:
#            raise NicosError(self, 'depot at unknown position')
#            return
        bitmask = self._bitmask(magpos)
        val = list(map(str,
                       [(self._attached_io_open.read(0) & bitmask) / bitmask,
                        (self._attached_io_closed.read(0) & bitmask) / bitmask]
                       ))
        self.log.debug('Sensing switches are in State %s', val)
        return ''.join(val)

    def doRead(self, maxage=0):
        s = self._read()
        if s == '01':
            return 'closed'
        elif s == '10':
            return 'open'
        elif s == '00':
            return 'UNKNOWN'
        else:
            raise NicosError(self, 'Depot magnet switches in undefined status '
                             '%s check switches' % s)

    def doStatus(self, maxage=0):
        s = self._read()
        if s == '01':
            return status.OK, 'idle'
        elif s == '10':
            return status.OK, 'idle'
        elif s == '00':
            return status.BUSY, 'Moving'  # '? or Error!'
        else:
            return status.ERROR, 'maglock is in error state'

    @property
    def _magpos(self):
        s = self._attached_magazin.read(0)
        for i, k in enumerate(self.states):
            if s == k:
                return i
        return 4
