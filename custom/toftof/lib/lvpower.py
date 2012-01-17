#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF low-voltage power supplies."""

__version__ = "$Revision$"

from nicos.core import Readable, Param, CommunicationError, status, intrange, \
     oneofdict, requires, ADMIN

from nicos.toftof.toni import ModBus


class LVPower(Readable):

    attached_devices = {
        'bus':  (ModBus, 'Toni communication bus'),
    }

    parameters = {
        'addr':     Param('Bus address of the supply controller',
                          type=intrange(0xf0, 0x100), mandatory=True),
    }

    valuetype = oneofdict({1: 'on', 0: 'off'})

    def _comm_hex(self, istr):
        resp = self._adevs['bus'].communicate(istr, self.addr)
        try:
            return int(resp, 16)
        except ValueError:
            raise CommunicationError(self, 'garbled response %r' % resp)

    def doRead(self):
        return 'on' if self._comm_hex('S?') >> 7 else 'off'

    def doStatus(self):
        sval = self._comm_hex('S?')
        tval = self._comm_hex('T?')
        # XXX
        return status.OK, 'status=%d, temperature=%d' % (sval, tval)

    @requires(level=ADMIN)
    def doStart(self, target):
        resp = self._adevs['bus'].communicate('P%d' % (target == 'on'))
        if resp != 'OK':
            raise CommunicationError(self, 'invalid response %r' % resp)
