#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Toni-protocol device classes."""

__version__ = "$Revision$"

from time import sleep, time

from IO import StringIO

from nicos.core import status, intrange, listof, Device, Readable, Moveable, \
     Param, Override, NicosError, CommunicationError, InvalidValueError, \
     ConfigurationError
from nicos.taco.core import TacoDevice


class ModBus(TacoDevice, Device):
    taco_class = StringIO

    parameters = {
        'maxtries': Param('Maximum tries before raising', type=int, default=5),
        'source':   Param('Source address of host', type=int, default=0),
    }

    def _crc(self, str):
        crc = ord(str[0])
        for i in str[1:]:
            crc ^= ord(i)
        return '%02X' % crc

    def communicate(self, msg, dest):
        msg = '%02X%02X%s' % (dest, self.source, msg)
        msg = '\x02' + msg + self._crc(msg)
        tries = self.maxtries
        while True:
            tries -= 1
            try:
                ret = self._taco_guard(self._dev.communicate, msg)
            except NicosError:
                if tries == 0:
                    raise
                sleep(0.1)
            else:
                break
        # check reply for validity
        crc = self._crc(ret[1:-2])
        if (len(ret) < 8 or ret[0] != '\x02' or ret[5] != '>' or ret[-2:] != crc
              or ret[1:3] != '%02X' % self.source or ret[3:5] != '%02X' % dest):
            raise CommunicationError(self, 'ModBus reply garbled: %r' % ret)
        return ret[6:-2]


class Valve(Moveable):

    attached_devices = {
        'bus':  (ModBus, 'Toni communication bus'),
    }

    parameters = {
        'addr':     Param('Bus address of the valve control', type=int,
                          mandatory=True),
        'channel':  Param('Channel of the valve', type=intrange(0, 8),
                          mandatory=True),
        'states':   Param('Names for the closed/open states', type=listof(str),
                          default=['off', 'on']),
        'waittime': Param('Time to wait after switching', type=float, unit='s',
                          default=4),
    }

    parameter_overrides = {
        'unit':     Override(mandatory=False),
    }

    def doInit(self):
        if len(self.states) != 2:
            raise ConfigurationError(self, 'Valve states must be a list of '
                                     'two strings for closed/open state')
        self._timer = 0

    def doStart(self, value):
        if value not in self.states:
            raise InvalidValueError(self, 'value must be one of %s' %
                                    ', '.join(repr(s) for s in self.states))
        value = self.states.index(value)
        self.doWait()
        self._timer = time()
        msg = '%s=%02x' % (value and 'O' or 'C', 1 << self.channel)
        ret = self._adevs['bus'].communicate(msg, self.addr)
        if ret != 'OK':
            raise CommunicationError(self, 'ModBus read error: %r' % ret)

    def doRead(self):
        self.doWait()
        ret = self._adevs['bus'].communicate('R?', self.addr)
        if not ret:
            raise CommunicationError(self, 'ModBus read error: %r' % ret)
        return self.states[bool(int(ret, 16) & (1 << self.channel))]

    def doStatus(self):
        self.doWait()
        ret = self._adevs['bus'].communicate('I?', self.addr)
        if not ret:
            raise CommunicationError(self, 'ModBus read error: %r' % ret)
        if int(ret) == 0:
            return status.OK, 'idle'
        else:
            return status.BUSY, 'busy'

    def doWait(self):
        if self._timer:
            # wait given time after last write action
            while time() - self._timer < self.waittime:
                sleep(0.1)
            self._timer = 0


class Leckmon(Readable):
    attached_devices = {
        'bus': (ModBus, 'Toni communication bus'),
    }

    parameters = {
        'addr': Param('Bus address of monitor', type=int, mandatory=True),
    }

    def doRead(self):
        return self._adevs['bus'].communicate('S?', self.addr)


class Ratemeter(Readable):
    """
    Toni ratemeter inside a "crate".
    """

    attached_devices = {
        'bus': (ModBus, 'Toni communication bus'),
    }

    parameters = {
        'addr': Param('Bus address of crate', type=intrange(0xf0, 0x100),
                      mandatory=True),
    }

    def doRead(self):
        bus = self._adevs['bus']
        self._cachelock_acquire()
        try:
            # ratemeter is on channel 2
            ret = bus.communicate('C2', self.addr)
            if ret != 'OK':
                raise CommunicationError('could not select crate channel')
            # send command (T = transmit, X = anything for input buffer update
            ret = bus.communicate('TX', self.addr)
            if ret != 'OK':
                raise CommunicationError('update command failed')
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

class Vacuum(Readable) :
    """
    Toni vacuum gauge ITR90 read out system
    """
    attached_devices = {
        'bus': (ModBus, 'Toni communication bus'),
    }

    parameters = {
        'addr':     Param('Bus address of the valve control', 
                          type = intrange(0xf0, 0xff), mandatory=True, default=0xf0),
        'channel':  Param('Channel of the vacuum gauge', 
                          type = intrange(0, 4), mandatory=True, default=0),
        'power' : Param('',
                          type = intrange(0, 2), default=0, settable=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='mbar'),
    }

    def doInit(self):
        if self._mode == 'simulation' :
            return
#       if nicd_getLogin()[1] >= 2:
#           raise NicosError("only users with priorities < 2 are allowed to reload TOFTOF_HV devices")

#   @requires(level=ADMIN)
    def doReset (self):
        ret = self._adevs['bus'].communicate('P%1d=0' % (self.channel + 1,), self.addr)
        if ret != "OK":
            raise CommunicationError ("ITR90: read error")
        sleep(1)
        ret = self._adevs['bus'].communicate('P%1d=1' % (self.channel + 1,), self.addr)
        if ret != "OK":
            raise CommunicationError ("ITR90: read error")
        sleep(0.1)

    def doRead (self):
        a = self._t('R%1d?' % (self.channel+1,))
        try:
            ret1 = int(a[0:4], 16)
            ret3 = int(a[4:6], 16)
        except ValueError:
            raise CommunicationError ("ITR90: read error")

        if ret3 & 16:
            ret = 10.0 ** (ret1 / 4000.0 - 12.625) # Torr
            self.unit = "Torr"
        elif ret3 & 32:
            ret = 10.0 ** (ret1 / 4000.0 - 10.5) # Pa
            self.unit = "Pa"
        else:
            ret = 10.0 ** (ret1 / 4000.0 - 12.5) # mbar
            self.unit = "mbar"
        return ret

    def doStatus (self):
        a = self._t('R%1d?' % (self.channel + 1))
        try:
            ret1 = int(a[6:8], 16)
        except ValueError:
            raise CommunicationError ("ITR90: read error")
        return status.OK if ret1 == 0 else status.ERROR, ""

    def doReadPower(self):
        try:
            self.status()
            return 1
        except:
            return 0

    def doWritePower(self, value):
        ret = self._adevs['bus'].communicate("P%1d=%d" % (self.channel + 1, value), self.addr)
        if ret != "OK":
            raise CommunicationError ("ITR90: read error")

    def _t (self, istr):
        ret = self._adevs['bus'].communicate(istr, self.addr)
        if len (ret) != 8:
            raise CommunicationError ("ITR90: read error : string to short, not 8 chars %s" % (ret))
        return ret
