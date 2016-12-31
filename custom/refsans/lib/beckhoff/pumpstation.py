#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""Devices for the Refsans NOK system."""

import struct

from Modbus import Modbus

from nicos import session
from nicos.utils import bitDescription, clamp
from nicos.core import Param, Override, status, SIMULATION, usermethod, \
    requires, TimeoutError, Readable, oneof, limits, floatrange, NicosError, \
    Moveable, Attach
from nicos.devices.taco.core import TacoDevice

# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'


# Box pumpenstand: _Anhang_A_REFSANS_Pumpstand.pdf
# actually 3*2 devices (CB, SR, SFK) * (pressure, pump)
# XXX: provide pumps as own devices
# XXX: disentangle !
# XXX: split into basic support class and concrete Impls.

class PumpstandIO(TacoDevice, Readable):
    """
    Basic IO Device object for devices in refsans' pumping rack
    contains common things for all devices.
    """
    taco_class = Modbus

    hardware_access = True

    parameters = {
        'address':          Param('Starting offset (words) of IO area',
                                  #type=intrange(0x3000, 0x47ff),
                                  type=oneof(16422),
                                  mandatory=True, settable=False,
                                  userparam=False, default=16422),
        'parallel_pumping': Param('Pressure below which all recipients will '
                                  'be pumped parallel, instead of serially',
                                  default=10, type=floatrange(0, 13),
                                  unit='mbar', settable=True, chatty=True,
                                  volatile=True),
        'firmware':         Param('Firmware Version', settable=False,
                                  type=str, mandatory=False, volatile=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))

    #
    # access-helpers for accessing the fields inside the IO area
    #

    def _readU16(self, addr):
        # reads a uint16 from self.address + addr
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address + addr, 1))[0]
        self.log.debug('_readU16(%d): -> %d', addr, value)
        return value

    def _writeU16(self, addr, value):
        # writes a uint16 to self.address+addr
        value = int(value)
        self.log.debug('_writeU16(%d, %d)', addr, value)
        self._taco_guard(self._dev.writeSingleRegister,
                         (0, self.address + addr, value))

    def _readU32(self, addr):
        # reads a uint32 from self.address + addr .. self.address + addr + 1
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address + addr, 2))
        value = struct.unpack('=I', struct.pack('<2H', *value))[0]
        self.log.debug('_readU32(%d): -> %d', addr, value)
        return value

    def _writeU32(self, addr, value):
        # writes a uint32 to self.address + addr
        value = int(value)
        self.log.debug('_writeU32(%d, %d)', addr, value)
        value = struct.unpack('<2H', struct.pack('=I', value))
        self._taco_guard(self._dev.writeMultipleRegisters,
                         (0, self.address + addr) + value)

    #
    # Hardware abstraction: which actions do we want to do...
    #

    def _HW_SFK_current_pressure(self):
        return 1e-6 * self._readU32(0)

    def _HW_SFK_turn_off_pressure(self):
        return 1e-6 * self._readU32(2)

    def _HW_SFK_turn_on_pressure(self):
        return 1e-6 * self._readU32(4)

    def _HW_SFK_timeout(self):
        return 1e-3 * self._readU32(8)

    def _HW_CB_current_pressure(self):
        return 1e-6 * self._readU32(24)

    def _HW_CB_turn_off_pressure(self):
        return 1e-6 * self._readU32(43)

    def _HW_CB_turn_on_pressure(self):
        return 1e-6 * self._readU32(45)

    def _HW_CB_timeout(self):
        return 1e-3 * self._readU32(53)

    def _HW_SR_current_pressure(self):
        return 1e-6 * self._readU32(26)

    def _HW_SR_turn_off_pressure(self):
        return 1e-6 * self._readU32(28)

    def _HW_SR_turn_on_pressure(self):
        return 1e-6 * self._readU32(30)

    def _HW_SR_timeout(self):
        return 1e-3 * self._readU32(51)

    def _HW_read_outputs(self):
        return self._readU16(11)

    def _HW_parallel_pumping_pressure(self):
        return 1e-6 * self._readU32(32)

    _HW_Alarms = (
        #~ (0, 'Ventil 1 Ansteuerung oder Signalkabel defekt'),
        (1, 'Ventil 2 Ansteuerung oder Signalkabel defekt'),
        (2, 'Ventil 3 Ansteuerung oder Signalkabel defekt'),
        (3, 'Ventil 4 Ansteuerung oder Signalkabel defekt'),
        (4, 'Ventil 5 Ansteuerung oder Signalkabel defekt'),
        (5, 'Motorschutzschalter Pumpe 1'),
        (6, 'Motorschutzschalter Pumpe 2'),
        (7, 'Motorschutzschalter Pumpe 3'),
        #~ (8, 'Motorschutzschalter Pumpe 4'),
        (9, 'Leistungsschütz Pumpe 1 schaltet nicht'),
        (10, 'Leistungsschütz Pumpe 2 schaltet nicht'),
        (11, 'Pumpe 3 meldet Fehlerstatus (Kashiyama)'),
        #~ (12, 'Leistungsschütz Pumpe 4 schaltet nicht'),
        (20, 'Ventil 2a Ansteuerung oder Signalkabel defekt'),
        (21, 'Ventil 4a Ansteuerung oder Signalkabel defekt'),
    )
    _HW_Alarms_CB = (
        (13, 'Sensor- oder Kabelfehler Messröhre CB'),
        (17, 'Timeout bei pumpen von CB'),
    )
    _HW_Alarms_SR = (
        (14, 'Sensor- oder Kabelfehler Messröhre SR'),
        (16, 'Timeout bei pumpen von SR'),
    )
    _HW_Alarms_SFK = (
        (15, 'Sensor- oder Kabelfehler Messröhre SFK'),
        (22, 'Timeout bei pumpen von SFK'),
    )
    _HW_Outputs = (
        (0, 'Pumpe 1 aktiviert (Wäkolbenpumpe Ruvac)'),
        (1, 'Pumpe 3 aktiviert (derzeit nicht verbaut)'),
        (2, 'Pumpe 2 aktiviert (Kashiyama)'),
        #~ (3, 'Pumpe 4 aktiviert (Wäkolbenpumpe Feinvakuum)'),
        #~ (4, 'Ventil 1 aktiviert (Belüftung)'),
        (5, 'Ventil 2 aktiviert (CB--Pumpe)'),
        (6, 'Ventil 3 aktiviert (SR--Pumpe)'),
        (7, 'Ventil 4 aktiviert (CB--Belüftung)'),
        (8, 'Ventil 5 aktiviert (SR--Belüftung)'),
        (9, 'Lüfter an Pumpe 1 aktiviert'),
        (10, 'Ventil 2a aktiviert (SFK--Pumpe)'),
        (11, 'Ventil 4a aktiviert (SFK--Belüftung)'),
    )
    _HW_Status = (
        (1, 'CB: may pump'),
        (3, 'CB: may vent'),
        (5, 'CB: pumping'),
        (7, 'CB: venting'),
        (9, 'CB: priming pump'),
        (0, 'SR: may pump'),
        (2, 'SR: may vent'),
        (4, 'SR: pumping'),
        (6, 'SR: venting'),
        (8, 'SR: priming pump'),
        (10, 'SFK: may pump'),
        (11, 'SFK: may vent'),
        (13, 'SFK: pumping'),
        (14, 'SFK: venting'),
        (12, 'SFK: priming pump'),
    )

    _HW_CMDS = dict(
        pump_SR=6,      pump_CB=7,      pump_SFK=30,     # cmd: pump now
        vent_SR=8,      vent_CB=9,      vent_SFK=31,     # cmd: vent now
        stop_SR=10,     stop_CB=11,     stop_SFK=32,     # stop pump/vent
        set_SR_low=12,  set_CB_low=17,  set_SFK_low=33,  # set lower limit
        set_SR_high=13, set_CB_high=18, set_SFK_high=34, # set upper limit
        setTme_SR=23,   setTme_CB=24,   setTme_SFK=26,   # set timeout
        setPar=14,    # set parallel pumping pressure
        ackErr=16,    # cmd: ack errors
        resetAll=255, # reset to default values
    )

    def _HW_rawCommand(self, cmd, par=0):
        if cmd not in self._HW_CMDS:
            raise ValueError('Command code %r not supported, check code and '
                             'docu!' % cmd)
        cmd = int(self._HW_CMDS.get(cmd, cmd))

        pswd = 16082008 + ((int(cmd) + int(par)) % 228)
        self.log.debug('Initiate command %d with par %d and pswd %d',
                       cmd, par, pswd)
        self._writeU32(16, int(par))
        self._writeU32(12, int(pswd))
        self._writeU32(14, int(cmd))

        self.log.debug('checking reaction')
        session.delay(0.1)
        for _ in range(10):
            ack = bool(self._HW_readACK())
            nack = bool(self._HW_readNACK())
            if ack and not nack:
                self.log.debug('Command accepted')
                return
            elif nack and not ack:
                raise NicosError('Command rejected by Beckhoff')
        raise TimeoutError('Command not recognized by Beckhoff within 1s!')

    def _HW_readACK(self):
        return self._readU16(37)

    def _HW_readNACK(self):
        return self._readU16(38)

    def _HW_readVersion(self):
        return 'V%.1f' % (self._readU32(22) *0.1)

    def _HW_readAlarms(self):
        # according to docu this is 16 bits,
        # but a meaning is defined for bits 1..23
        # I guess it is really 32 bits wide
        return self._readU32(34)

    def _HW_readStatusByte(self):
        # docu uses bit 0..14 (more than a byte could hold...)
        return self._readU16(36)

    #
    # Nicos Methods
    #

    def doRead(self, maxage=0):
        return self._HW_parallel_pumping_pressure()

    def doReadParallel_Pumping(self):
        return self._HW_parallel_pumping_pressure()

    def doWriteParallel_Pumping(self, value):
        self._HW_rawCommand('setPar', int(value * 1e6))

    def doReadFirmware(self):
        return self._HW_readVersion()

    def doStatus(self, maxage=0):
        return status.OK, ''

    @usermethod
    def diag(self):
        """displays all available diagnostic information"""
        sb = self._attached_iodev._HW_readStatusByte()
        for idx, msg in sorted(self._HW_Status):
            if sb & (1 << idx):
                self.log.info('Status %d: %s', idx, msg)
        diags = self._attached_iodev._HW_read_outputs()
        for idx, msg in sorted(self._HW_Outputs):
            if diags & (1 << idx):
                self.log.info('Output %d: %s', idx, msg)
        alarms = self._attached_iodev._HW_readAlarms()
        for idx, msg in sorted(self._HW_Alarms + self._HW_Alarms_CB +
                               self._HW_Alarms_SR + self._HW_Alarms_SFK):
            if alarms & (1 << idx):
                self.log.warn('Alarm %d: %s', idx, msg)


class PumpstandPressure(Readable):
    attached_devices = {
        'iodev' : Attach('IO Device', PumpstandIO),
    }
    parameters = {
        'chamber':          Param('Chamber of pumpenstand',
                                  type=oneof('SFK', 'CB', 'SR'),
                                  mandatory=True, settable=False,
                                  userparam=False, default='SR'),
        'limits':           Param('Pump activation limits',
                                  type=limits, settable=True, volatile=True,
                                  chatty=True, unit='mbar'),
    }

    parameter_overrides = {
        'unit':  Override(default='mbar',mandatory=False),
        'fmtstr': Override(default='%.1g'),
    }
    #
    # Nicos methods
    #

    def doReset(self):
        self._attached_iodev._HW_rawCommand('ackErr')

    def doRead(self, maxage=0):
        return getattr(self._attached_iodev, '_HW_%s_current_pressure' % self.chamber)()

    def doReadLimits(self):
        return (getattr(self._attached_iodev, '_HW_%s_turn_off_pressure' % self.chamber)(),
                getattr(self._attached_iodev, '_HW_%s_turn_on_pressure' % self.chamber)())

    def doWriteLimits(self, limits):
        lower, upper = limits
        upper = clamp(upper, 1e-3, self.parallel_pumping)
        lower = clamp(lower, 1e-3, upper)
        self._attached_iodev._HW_rawCommand('set_%s_low' % self.chamber, int(lower * 1e6))
        self._attached_iodev._HW_rawCommand('set_%s_high' % self.chamber, int(upper * 1e6))
        return (lower, upper)

    _HW_Alarmbit = dict(CB=13, SR=14, SFK=15)
    def doStatus(self, maxage=0):
        alarms = self._attached_iodev._HW_readAlarms()
        alarmbit = self._HW_Alarmbit[self.chamber]
        if alarms & (1 << alarmbit):
            return status.ERROR, 'Sensor- oder Kabelfehler Messröhre'
        return status.OK, ''


class PumpstandPump(Moveable):
    """
    abstracts one (of 3) pumps
    values are 1 for venting, 0 for auto, -1 for pumping
    There may be a mapper usefull to map these to strings
    """
    attached_devices = {
        'iodev' : Attach('IO Device', PumpstandIO),
    }
    valuetype = oneof(-1, 0, 1)
    parameters = {
        'chamber':          Param('Chamber of pumpenstand',
                                  type=oneof('SFK', 'CB', 'SR'),
                                  mandatory=True, settable=False,
                                  userparam=False, default='SR'),
        'pumptime':         Param('Max pumping time', settable=True, unit='s',
                                  type=floatrange(0, 4294967), default=10*3600,
                                  volatile=True, chatty=True),
    }

    parameter_overrides = {
        'unit':  Override(default='',mandatory=False),
        'fmtstr': Override(default='%d'),
    }

    #
    # Nicos methods
    #
    _HW_pumping_bit = dict(CB=5, SR=4, SFK=13)
    _HW_venting_bit = dict(CB=7, SR=6, SFK=14)
    _HW_may_pump_bit = dict(CB=1, SR=0, SFK=10)
    _HW_may_vent_bit = dict(CB=3, SR=2, SFK=11)
    _HW_priming_pump = dict(CB=9, SR=8, SFK=12)

    def doIsAllowed(self, target):
        sb = self._attached_iodev._HW_readStatusByte()
        if target == 1:
            if sb & (1 << self._HW_may_vent_bit[self.chamber]):
                return True, ''
            return False, 'venting currently not possible'
        elif target == -1:
            if sb & (1 << self._HW_may_pump_bit[self.chamber]):
                return True, ''
            return False, 'pumping currently not possible'
        elif target == 0:
            mask = (1 << self._HW_pumping_bit[self.chamber]) | \
                   (1 << self._HW_venting_bit[self.chamber]) #| \
                   #(1 << self._HW_priming_pump[self.chamber]) # ??? stop while priming allowed?
            if sb & mask:
                return True, ''
            return False, 'stop currently not possible'

    def doRead(self, maxage=0):
        sb = self._attached_iodev._HW_readStatusByte()
        if sb & (1 << self._HW_pumping_bit[self.chamber]):
            return -1 # pumping
        if sb & (1 << self._HW_priming_pump[self.chamber]):
            return -1 # priming pump
        if sb & (1 << self._HW_venting_bit[self.chamber]):
            return 1 # venting
        return 0

    @usermethod
    @requires(level='admin')
    def doStart(self, target):
        if target == -1:
            self._HW_rawCommand('pump_%s' % self.chamber)
        elif target == 1:
            self._HW_rawCommand('vent_%s' % self.chamber)
        elif target == 0:
            self._HW_rawCommand('stop_%s' % self.chamber)

    def doReset(self):
        self._HW_rawCommand('ackErr')

    def doReadPumptime(self):
        return getattr(self._attached_iodev, '_HW_%s_timeout' % self.chamber)()

    def doWritePumptime(self, value):
        self._HW_rawCommand('setTme_%s' % self.chamber, int(value*1e3))

    def doStatus(self, maxage=0):
        alarms = self._attached_iodev._HW_readAlarms()
        almsg = bitDescription(alarms, *(self._attached_iodev._HW_Alarms +
            getattr(self._attached_iodev, '_HW_Alarms_%s' % self.chamber)))

        if almsg:
            return status.ERROR, almsg

        work = self.doRead(maxage)
        if work in (1,-1):
            # venting, priming or pumping
            return status.BUSY, ['', 'venting', 'priming or pumping'][work]
        return status.OK, ''
