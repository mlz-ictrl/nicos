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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA Beryllium filter readout."""

from nicos.core import Param, Override, status, oneof, Readable, Attach
from nicos.devices.taco import AnalogInput

from nicos.panda.wechsler import Beckhoff


class KL320xTemp(Readable):

    attached_devices = {
        'beckhoff': Attach('X', Beckhoff),
    }

    parameters = {
        'addr': Param('Adress of Control/Statusbyte in Beckhoff bus mapping'
                      '(usually even)',
                      type=int, default=0, settable=True),
    }

    parameter_overrides = {
        'unit':   Override(type=oneof('K', '°C', 'Ohm')),
        'fmtstr': Override(default='%4.1f', settable=False),
    }

    # def doReadUnit(self):
    #     return 'K'

    @property
    def bhd(self):  # BeckHoffDevice
        return self._attached_beckhoff

    def _switch_to_K(self):
        self.log.debug('Switching to K')
        # activate writing of the other regs
        self.bhd.WriteReg(self.addr, 31, 0x1235)
        # PT1000, 2wire connection, no overrange cutof, active filter,
        # no watchdog, userscaling
        self.bhd.WriteReg(self.addr, 32, 0x2481)
        # userscaling: offset=273.15*16 to read K instead of °C
        # self.bhd.WriteReg( self.addr, 33, 0x1112 )
        # userscaling: offset=273.15*16 to read K instead of °C
        self.bhd.WriteReg(self.addr, 33, 2732)
        # userscaling: Gain=1  (R34/100)
        self.bhd.WriteReg(self.addr, 34, 0x00A0)
        # Filterconst (50Hz)
        self.bhd.WriteReg(self.addr, 37, 0x00A0)
        # de-activate writing of the other regs
        self.bhd.WriteReg(self.addr, 31, 0x0000)
        # switch to reading of scaled value
        self.bhd.WriteWordOutput(self.addr+0x800, 0)

    def _switch_to_C(self):
        self.log.debug('Switching to °C')
        # activate writing of the other regs
        self.bhd.WriteReg(self.addr, 31, 0x1235)
        # PT1000, 2wire connection, no overrange cutof, active filter,
        # no watchdog, userscaling
        self.bhd.WriteReg(self.addr, 32, 0x2481)
        # userscaling: offset=0 to read °C
        self.bhd.WriteReg(self.addr, 33, 0x0000)
        # userscaling: Gain=1  (R34/100)
        self.bhd.WriteReg(self.addr, 34, 0x00A0)
        # Filterconst (50Hz)
        self.bhd.WriteReg(self.addr, 37, 0x00A0)
        # de-activate writing of the other regs
        self.bhd.WriteReg(self.addr, 31, 0x0000)
        # switch to reading of scaled value
        self.bhd.WriteWordOutput(self.addr+0x800, 0)

    def _switch_to_Ohm(self):
        self.log.debug('Switching to Ohm')
        # activate writing of the other regs
        self.bhd.WriteReg(self.addr, 31, 0x1235)
        # 1KOhm range, 2wire connection, no overrange cutof, active filter,
        # no watchdog, userscaling
        self.bhd.WriteReg(self.addr, 32, 0xF481)
        # userscaling: offset=0
        self.bhd.WriteReg(self.addr, 33, 0x0000)
        # userscaling: Gain=1  (R34/100)
        self.bhd.WriteReg(self.addr, 34, 0x00A0)
        # Filterconst (50Hz)
        self.bhd.WriteReg(self.addr, 37, 0x00A0)
        # de-activate writing of the other regs
        self.bhd.WriteReg(self.addr, 31, 0x0000)
        # switch to reading of scaled value
        self.bhd.WriteWordOutput(self.addr+0x800, 0)

    def doWriteUnit(self, unit):
        self.log.debug('Setting unit from %s to %s' % (self.unit, unit))
        if unit == 'K':
            self._switch_to_K()
        elif unit == '°C':
            self._switch_to_C()
        elif unit == 'Ohm':
            self._switch_to_Ohm()
        else:
            self.log.error('unknown unit! cannot switch!')
            raise Exception('unknown unit! cannot switch!')

    def doInit(self, mode):
        # This code only works for KL3201..4
        if 3201 <= self.bhd.ReadReg(self.addr, 8) <= 3204:
            # update hardware about our unit and set scaling
            self.doWriteUnit(self.unit)
        else:
            raise Exception('Sorry, addr must be wrong, there is no KL320x '
                            'there! please correct')

    def doRead(self, maxage=0):
        v = self.bhd.ReadWordInput(self.addr+1)
        self.log.debug('Raw value is %d (0x%04x)' % (v, v))
        return float(v) * 0.1

    def doStatus(self, maxage=0):
        # why read value during the status detection ???
        self.doRead(maxage)
        v = self.bhd.ReadWordInput(self.addr)
        if v & 0x01:
            return (status.ERROR, 'Underrange bit set!')
        elif v & 0x02:
            return (status.ERROR, 'Overrange bit set!')
        elif v & 0x40:
            return (status.ERROR, 'Error bit set!')
        return (status.OK, 'Idle')


class I7033Temp(AnalogInput):

    parameter_overrides = {
        'unit': Override(type=oneof('K', 'Ohm')),
    }

    def doReadUnit(self):
        return 'K'

    def doRead(self, maxage=0):
        r = self._taco_guard(self._dev.read)
        t = self._temperature(r)
        if self.unit == 'K':
            return t
        return r

    def doStatus(self, maxage=0):
        # why read value during the status detection ???
        self._temperature(self._taco_guard(self._dev.read))
        return (status.OK, '')

    def _temperature(self, r):
        return (r - 1000) / 3.85 + 273.25  # linear approx.
