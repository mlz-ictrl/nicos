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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#
# *****************************************************************************

"""Toni-protocol device classes."""

from __future__ import absolute_import, division, print_function

from nicos.core import ADMIN, Attach, CommunicationError, Moveable, Override, \
    Param, intrange, oneofdict, requires, status
from nicos.devices.tango import StringIO


class ToniBus(StringIO):
    """Communication device that implements the Toni protocol.

    Toni devices communicate via an RS-485 bus, where each device has an
    address assigned.
    """

    parameters = {
        'source':   Param('Source address of host', type=int, default=0),
    }

    parameter_overrides = {
        'comtries': Override(default=5),
    }

    def _crc(self, value):
        crc = ord(value[0])
        for i in value[1:]:
            crc ^= ord(i)
        return '%02X' % crc

    def communicate(self, msg, dest, expect_ok=False, expect_hex=0):
        msg = '%02X%02X%s' % (dest, self.source, msg)
        msg += self._crc(msg)
        ret = self._dev.communicate(msg)
        # check reply for validity
        crc = self._crc(ret[:-2])
        if (len(ret) < 7 or ret[4] != '>' or ret[-2:] != crc or
           ret[:2] != '%02X' % self.source or ret[2:4] != '%02X' % dest):
            raise CommunicationError(self, 'garbled reply: %r' % ret)
        resp = ret[5:-2]
        if expect_ok and resp != 'OK':
            raise CommunicationError(self, 'unexpected reply: %r' % resp)
        if expect_hex:
            if len(resp) != expect_hex:
                raise CommunicationError(self, 'response invalid: %r' % resp)
            try:
                value = int(resp, 16)
            except ValueError:
                raise CommunicationError(self, 'invalid hex number: %r' % resp)
            return value
        return resp


class DelayBox(Moveable):
    """Toni TOFTOF-type programmable delay box."""

    attached_devices = {
        'bus':  Attach('Toni communication bus', ToniBus),
    }

    parameters = {
        'addr':  Param('Bus address of the supply controller',
                       type=intrange(0xF0, 0xFF), mandatory=True),
    }

    parameter_overrides = {
        'fmtstr':  Override(default='%d'),
    }

    valuetype = int

    def doRead(self, maxage=0):
        return self._attached_bus.communicate('D?', self.addr, expect_hex=4)

    def doStart(self, target):
        self._attached_bus.communicate('D=%04X' % target, self.addr,
                                       expect_ok=True)

    def doIsAllowed(self, target):
        if 0 <= target <= 65535:
            return True, ''
        else:
            return False, '%r is not in the allowed range [0, 65535], please '\
                          'check your delay calculation' % (target,)

    def doStatus(self, maxage=0):
        return status.OK, ''


class LVPower(Moveable):
    """Toni TOFTOF-type low-voltage power supplies."""

    attached_devices = {
        'bus':  Attach('Toni communication bus', ToniBus),
    }

    parameters = {
        'addr':  Param('Bus address of the supply controller',
                       type=intrange(0xF0, 0xFF), mandatory=True),
    }

    parameter_overrides = {
        'unit':  Override(mandatory=False, default=''),
    }

    valuetype = oneofdict({1: 'on', 0: 'off'})

    def doRead(self, maxage=0):
        sval = self._attached_bus.communicate('S?', self.addr, expect_hex=2)
        return 'on' if sval >> 7 else 'off'

    def doStatus(self, maxage=0):
        sval = self._attached_bus.communicate('S?', self.addr, expect_hex=2)
        tval = self._attached_bus.communicate('T?', self.addr, expect_hex=2)
        return status.OK, 'status=%d, temperature=%d' % (sval, tval)

    @requires(level=ADMIN)
    def doStart(self, target):
        self._attached_bus.communicate('P%d' % (target == 'on'),
                                       self.addr, expect_ok=True)
