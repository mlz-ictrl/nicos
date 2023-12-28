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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Magnetic Lock."""

from nicos import session
from nicos.core import Attach, Moveable, NicosError, Param, Readable, listof, \
    oneof, status


class MagLock(Moveable):
    """Puma specific magnetic lock device."""

    attached_devices = {
        'magazine': Attach('The monochromator magazine', Readable),
        'io_open': Attach('readout for the status', Readable),
        'io_closed': Attach('readout for the status', Readable),
        'io_set': Attach('output to set', Moveable),
    }

    valuetype = oneof('open', 'closed')

    parameters = {
        'states': Param('List of state names', type=listof(str),
                        mandatory=True),
    }

    def _bitmask(self, num):
        return 1 << num

    def doStart(self, target):
        if target == self.doRead(0):
            return

        if target == 'closed':
            self._attached_io_set.move(0)
        elif target == 'open':
            self._attached_io_set.move(self._bitmask(self._magpos()))

        session.delay(2)  # XXX!

        pos = self.doRead(0)
        if pos != target:
            raise NicosError(self, f'did not reach target! {pos}')
        self.log.debug('Maglock: %s', pos)

    def _read(self):
        """Return internal string repr. of the right sensing switches."""
        bitmask = self._bitmask(self._magpos())
        val = list(
            map(str,
                [(self._attached_io_open.read(0) & bitmask) // bitmask,
                 (self._attached_io_closed.read(0) & bitmask) // bitmask,
                 ],
                )
            )
        self.log.debug('Sensing switches are in State %s', val)
        return ''.join(val)

    def doRead(self, maxage=0):
        s = self._read()
        if s == '01':
            return 'closed'
        if s == '10':
            return 'open'
        if s == '00':
            return 'UNKNOWN'
        raise NicosError(self, 'Depot magnet switches in undefined status '
                         '{s} check switches')

    def doStatus(self, maxage=0):
        s = self._read()
        if s in ['01', '10']:
            return status.OK, 'idle'
        if s == '00':
            return status.BUSY, 'Moving'  # '? or Error!'
        return status.ERROR, 'maglock is in error state'

    def _magpos(self):
        try:
            return self.states.index(self._attached_magazine.read(0))
        except ValueError as exc:
            raise NicosError(self, 'depot at unknown position') from exc
