#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA Monochromator changer hardware classes. FOR TESTING ONLY !"""

from struct import pack, unpack

from nicos.core import Readable, Moveable, status, Device, SIMULATION
from nicos.core.params import Param, Override, Attach, intrange
from nicos.core.errors import ConfigurationError, MoveError

from pymodbus.client.sync import ModbusTcpClient # pylint: disable=F0401


class ModBusThingy(Device):
    """For testing only. shall be replaced by a working ModBusServer"""
    parameters = {
        'host' : Param('Hostname or IP Adress of the ModBusServer', type=str, mandatory=True),
        }
    _dev = None
    hw_access = True

    def doInit(self, mode):
        if mode != SIMULATION:
            try:
                self._dev = ModbusTcpClient(self.host)
                self._dev.connect()
            except Exception as err:
                raise ConfigurationError(self, err)

    def ReadWord(self, addr):
        return self._dev.read_holding_registers(int(addr), 1).registers[0]

    def WriteWord(self, addr, value):
        return self._dev.write_register(int(addr), int(value))

    def ReadDWord(self, addr):
        low, high = self._dev.read_holding_registers(int(addr), 2).registers
        return unpack('<I', pack('<HH', low, high))

    def WriteDWord(self, addr, value):
        low, high = unpack('<HH', pack('<I', int(value)))
        return self._write_registers(int(addr), [low, high])

    # REAL is stored High word first...
    def ReadFloat(self, addr):
        low, high = self._dev.read_holding_registers(int(addr), 2).registers
        return unpack('<f', pack('<HH', high, low))

    def WriteFloat(self, addr, value):
        low, high = unpack('<HH', pack('<f', float(value)))
        return self._write_registers(int(addr), [high, low])


STATUS_MAP = [ status.UNKNOWN,
               status.OK,
               status.BUSY, status.BUSY,
               status.OK, status.NOTREACHED, status.NOTREACHED, status.NOTREACHED,
               status.ERROR, status.ERROR, status.ERROR, status.ERROR,
               status.ERROR, status.ERROR, status.ERROR, status.ERROR ]


class PLCDevice(Readable):
    hw_access = False
    attached_devices = {
        'bus' : Attach('Modbus connector thingy/Beckhoff dev', ModBusThingy)
        }

    parameters = {
        'addr' : Param('Base-Address of the Device in the Modbus-Space', type=int, mandatory=True, settable=True)
        }
    parameter_overrides = {
        'unit' : Override(mandatory=False, default=''),
        }

    @property
    def bus(self):
        return self._adevs['bus']

    def doStatus(self, maxage=0):
        return status.OK, ''


class SimpleDiscreteInput(PLCDevice):
    parameter_overrides = {
        'fmtstr' : Override(default='%d'),
        }
    valuetype = intrange(0, 65535)
    def doRead(self, maxage=0):
        return self.bus.ReadWord(self.addr)


class SimpleDiscreteOutput(SimpleDiscreteInput, Moveable):
    def doStart(self, target):
        self.wait()
        self.bus.WriteWord(self.addr + 1, target)
        readback = self.bus.ReadWord(self.addr + 1)
        self.log.debug('Wrote %x, read back %x' % (target, readback))
        if readback != target:
            raise MoveError(self, 'target value %d not accepted, was reset to %d' % (target, readback))


class JustAWord(SimpleDiscreteInput):
    def doStart(self, target):
        self.wait()
        self.bus.WriteWord(self.addr, target)
        readback = self.bus.ReadWord(self.addr + 1)
        self.log.debug('Wrote %x, read back %x' % (target, readback))
        if readback != target:
            raise MoveError(self, 'target value %d not accepted, was reset to %d' % (target, readback))


class SimpleAnalogInput(PLCDevice):
    valuetype = float
    def doRead(self, maxage=0):
        return self.bus.ReadFloat(self.addr)


class SimpleAnalogOutput(Moveable, SimpleAnalogInput):
    def doStart(self, target):
        self.wait()
        self.bus.WriteFloat(self.addr + 2, target)
        readback = self.bus.ReadFloat(self.addr + 2)
        self.log.debug('Wrote %g, read back %g' % (target, readback))
        if readback != target:
            raise MoveError(self, 'target value %g not accepted, was reset to %g' % (target, readback))


class FullDiscreteInput(SimpleDiscreteInput):
    def doStatus(self, maxage=0):
        Status = self.bus.ReadWord(self.addr + 1)
        self.log.debug('Statusword = ' + bin(65536 | Status)[3:])
        return STATUS_MAP[Status >> 12], 'Status: %s, Aux bits: %s' % (bin(16|(Status >> 12))[3:], bin(65536 | Status)[7:])


class FullDiscreteOutput(SimpleDiscreteOutput):
    def doStatus(self, maxage=0):
        Status = self.bus.ReadWord(self.addr + 2)
        self.log.debug('Statusword = ' + bin(65536 | Status)[3:])
        return STATUS_MAP[Status >> 12], 'Status: %s, Aux bits: %s' % (bin(16|(Status >> 12))[3:], bin(65536 | Status)[7:])


class FullAnalogInput(SimpleAnalogInput):
    def doStatus(self, maxage=0):
        Status = self.bus.ReadWord(self.addr + 2)
        self.log.debug('Statusword = ' + bin(65536 | Status)[3:])
        return STATUS_MAP[Status >> 12], 'Status: %s, Aux bits: %s' % (bin(16|(Status >> 12))[3:], bin(65536 | Status)[7:])


class FullAnalogOutput(SimpleAnalogOutput):
    def doStatus(self, maxage=0):
        Status = self.bus.ReadWord(self.addr + 4)
        self.log.debug('Statusword = ' + bin(65536 | Status)[3:])
        return STATUS_MAP[Status >> 12], 'Status: %s, Aux bits: %s' % (bin(16|(Status >> 12))[3:], bin(65536 | Status)[7:])


