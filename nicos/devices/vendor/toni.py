#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#
# *****************************************************************************

"""Toni-protocol device classes."""

from time import sleep, time as currenttime

from IO import StringIO

from nicos.core import status, intrange, listof, oneofdict, requires, ADMIN, \
    Device, Readable, Moveable, Param, Attach, Override, oneof, \
    CommunicationError, ConfigurationError
from nicos.devices.taco.core import TacoDevice
from nicos.core import MASTER


class ModBus(TacoDevice, Device):
    """Communication device that implements the Toni protocol.

    Toni devices communicate via an RS-485 bus, where each device has an address
    assigned.
    """
    taco_class = StringIO

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
        msg = '\x02' + msg + self._crc(msg)
        ret = self._taco_guard(self._dev.communicate, msg)
        # check reply for validity
        crc = self._crc(ret[1:-2])
        if (len(ret) < 8 or ret[0] != '\x02' or ret[5] != '>' or ret[-2:] != crc
              or ret[1:3] != '%02X' % self.source or ret[3:5] != '%02X' % dest):
            raise CommunicationError(self, 'garbled reply: %r' % ret)
        resp = ret[6:-2]
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


class Valve(Moveable):
    """Control element for 8 valves."""

    attached_devices = {
        'bus':  Attach('Toni communication bus', ModBus),
    }

    parameters = {
        'addr':     Param('Bus address of the valve control', type=int,
                          mandatory=True),
        'channel':  Param('Channel of the valve', type=intrange(0, 7),
                          mandatory=True),
        'states':   Param('Names for the closed/open states', type=listof(str),
                          default=['off', 'on']),
        'waittime': Param('Time to wait after switching', type=float, unit='s',
                          default=4),
    }

    parameter_overrides = {
        'unit':     Override(mandatory=False),
    }

    _started = 0

    def doInit(self, mode):
        if len(self.states) != 2:
            raise ConfigurationError(self, 'Valve states must be a list of '
                                     'two strings for closed/open state')
        self.valuetype = oneof(*self.states)

    def doStart(self, value):
        value = self.states.index(value)
        self._hw_wait()
        msg = '%s=%02x' % (value and 'O' or 'C', 1 << self.channel)
        self._attached_bus.communicate(msg, self.addr, expect_ok=True)
        self._started = currenttime()

    def doRead(self, maxage=0):
        ret = self._attached_bus.communicate('R?', self.addr, expect_hex=2)
        return self.states[bool(ret & (1 << self.channel))]

    def doStatus(self, maxage=0):
        ret = self._attached_bus.communicate('I?', self.addr, expect_hex=2)
        if ret != 0:
            return status.BUSY, 'busy'
        if self._started and self._started + self.waittime < currenttime():
            return status.BUSY, 'waiting'
        else:
            return status.OK, 'idle'


class Leckmon(Readable):
    """Water supply leak monitor."""

    attached_devices = {
        'bus': Attach('Toni communication bus', ModBus),
    }

    parameters = {
        'addr': Param('Bus address of monitor', type=int, mandatory=True),
    }

    def doRead(self, maxage=0):
        return self._attached_bus.communicate('S?', self.addr)


class Ratemeter(Readable):
    """Toni ratemeter inside a "crate"."""

    attached_devices = {
        'bus': Attach('Toni communication bus', ModBus),
    }

    parameters = {
        'addr': Param('Bus address of crate', type=intrange(0xF0, 0xFF),
                      mandatory=True),
    }

    def doRead(self, maxage=0):
        bus = self._attached_bus
        self._cachelock_acquire()
        try:
            # ratemeter is on channel 2
            bus.communicate('C2', self.addr, expect_ok=True)
            # send command (T = transmit, X = anything for input buffer update
            bus.communicate('TX', self.addr, expect_ok=True)
            # wait until response is ready
            rlen = -1
            t = 0
            while 1:
                sleep(0.05)
                ret = bus.communicate('R?', self.addr)
                if rlen == -1 or len(ret) == rlen:
                    return ret
                t += 1
                if t == 10:
                    raise CommunicationError('timeout while waiting for response')
        finally:
            self._cachelock_release()


class Vacuum(Readable):
    """Toni vacuum gauge ITR90 read out system."""

    attached_devices = {
        'bus': Attach('Toni communication bus', ModBus),
    }

    parameters = {
        'addr':    Param('Bus address of the valve control',
                         type=intrange(0xF0, 0xFF), mandatory=True),
        'channel': Param('Channel of the vacuum gauge',
                         type=intrange(0, 3), mandatory=True),
        'power':   Param('True if the readout is switched on',
                         type=intrange(0, 1), default=0, settable=True),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%g'),
        'unit':   Override(mandatory=False, default='mbar'),
    }

#   @requires(level=ADMIN)
    def doReset(self):
        self._attached_bus.communicate('P%1d=0' % (self.channel + 1),
                                       self.addr, expect_ok=True)
        sleep(1)
        self._attached_bus.communicate('P%1d=1' % (self.channel + 1),
                                       self.addr, expect_ok=True)
        sleep(0.1)

    def doRead(self, maxage=0):
        resp = self._attached_bus.communicate('R%1d?' % (self.channel + 1),
                                              self.addr, expect_hex=8)
        pressure, config = resp >> 16, (resp >> 8) & 0xFF
        if config & 16:
            ret = 10.0 ** (pressure / 4000.0 - 12.625)
            realunit = 'Torr'
        elif config & 32:
            ret = 10.0 ** (pressure / 4000.0 - 10.5) # Pa
            realunit = 'Pa'
        else:
            ret = 10.0 ** (pressure / 4000.0 - 12.5) # mbar
            realunit = 'mbar'
        if self.unit != realunit:
            if self._mode == MASTER:
                self.unit = 'Torr'
            else:
                self.log.warning('unit should be set to %s' % realunit)
        return ret

    def doReadUnit(self):
        resp = self._attached_bus.communicate('R%1d?' % (self.channel + 1),
                                              self.addr, expect_hex=8)
        config = (resp >> 8) & 0xFF
        if config & 16:
            return 'Torr'
        elif config & 32:
            return 'Pa'
        else:
            return 'mbar'

    def doStatus(self, maxage=0):
        resp = self._attached_bus.communicate('R%1d?' % (self.channel + 1),
                                              self.addr, expect_hex=8)
        state = resp & 0xFF
        if state == 0:
            return status.OK, ''
        else:
            return status.ERROR, 'status value = 0x%X' % state

    def doReadPower(self):
        try:
            self.status()
            return 1
        except CommunicationError:
            return 0

    def doWritePower(self, value):
        self._attached_bus.communicate(
            'P%1d=%d' % (self.channel + 1, value), self.addr, expect_ok=True)


class LVPower(Moveable):
    """Toni TOFTOF-type low-voltage power supplies."""

    attached_devices = {
        'bus':  Attach('Toni communication bus', ModBus),
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


class DelayBox(Moveable):
    """Toni TOFTOF-type programmable delay box."""

    attached_devices = {
        'bus':  Attach('Toni communication bus', ModBus),
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
