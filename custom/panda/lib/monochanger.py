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
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA Monochromator changer hardware classes. FOR TESTING ONLY !"""

from struct import pack, unpack
from time import sleep, time as currenttime
from datetime import datetime

from Modbus import Modbus as TacoModBus

from nicos import session
from nicos.core import Readable, Moveable, status, SIMULATION, usermethod, \
    Device
from nicos.core.utils import multiWait
from nicos.core.params import Param, Override, Attach, intrange, oneof
from nicos.core.errors import ConfigurationError, MoveError, NicosError, \
    UsageError
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqMethod, \
    SequenceItem, SeqCall
from nicos.devices.taco.core import TacoDevice
from nicos.utils import createThread


class Beckhoff(TacoDevice, Device):
    """Modbus based interfacing module for beckhoff PLC's

    compared to the TACO Server for the same purpose it has the
    following improvements:
     - caches reads of registers, speeding up the reading operations
     - cache refresh timeout can be adjusted
     - writes force a refresh of the cache
    """
    taco_class = TacoModBus

    parameters = {
        'cache_refresh':  Param('Refresh timeout for caching reads',
                                type=float, settable=True, default=0.1),
        'cache_baseaddr': Param('Number of registers to cache', type=int,
                                mandatory=True),
        'cache_numregs':  Param('Number of registers to cache', type=int,
                                mandatory=True),
        'baseaddr':       Param('Base-address of %M* area', type=int,
                                mandatory=False, default=0x4000),
    }

    __thread = None
    _keep_running = True
    _cached_registers = []
    _last_update = 0
    __float_conv = ('<f', '<HH')
    _devices = {}  # stores adress:(typcode,[name]) mapping

    def doInit(self, mode):
        if mode != SIMULATION:
            self._sync()
            if self.__thread is None:
                self.__thread = createThread('%s thread' % self, self._thread)
            for conv in (('<f', '<HH'), ('<f', '>HH'), ('>f', '<HH'),
                         ('>f', '>HH')):
                self.__float_conv = conv
                if 2014.07 <= self.ReadFloat(0) <= datetime.now().year+1:
                    break
            else:
                self.__float_conv = None
            # scan the plc for devices and adresses....
            adr = self.ReadWord(2)/2
            devid = 1
            devadr = adr + 2  # first address for devices
            while devid < 255:
                self.WriteWord(adr, devid)
                typecode = self.ReadWord(adr + 1)
                if typecode == 0:
                    break
                devname = []
                for i in range(8, 16):
                    self.WriteWord(adr, i << 8 | devid)
                    chars = self.ReadWord(adr + 1)
                    devname.append(chars & 0xff)
                    devname.append(chars >> 8)
                devname = ''.join(chr(c) for c in devname if c)
                self._devices[devadr] = (typecode, devname)
                self.log.debug('Found Device %r with TypeCode 0x%04x at 0x%04x'
                               % (devname, typecode, devadr))
                devadr += typecode & 0xff
                devid += 1
            if devid == 1:
                self.log.warning('PLC Indexer not working or no devices '
                                 'exported from there!')
            self.WriteWord(adr, 0xffff)  # enable cycle counter

    def _thread(self):
        now = currenttime()
        while self._keep_running:
            while now - self._last_update < self.cache_refresh:
                sleep(max(0, self.cache_refresh - now + self._last_update))
                now = currenttime()
            self._sync()

    def _sync(self):
        regs = []
        remaining = self.cache_numregs
        base = self.cache_baseaddr
        while remaining:
            num = min(remaining, 100)  # transfer at most 100 regs at a time...
            regs.extend(self._taco_guard(self._dev.readHoldingRegisters,
                                         (0, base, num)))
            base += num
            remaining -= num
        self._cached_registers = regs
        self._last_update = currenttime()

    def ReadWord(self, addr):
        addr += self.baseaddr
        if self.cache_baseaddr <= addr <= \
           self.cache_baseaddr + self.cache_numregs:
            return self._cached_registers[addr - self.cache_baseaddr]
        return self._taco_guard(
            self._dev.readHoldingRegisters, (0, addr, 1))[0]

    def WriteWord(self, addr, value):
        self._taco_guard(self._dev.writeSingleRegister,
                         (0, int(addr + self.baseaddr), int(value)))
        self._sync()

    def ReadDWord(self, addr):
        addr += self.baseaddr
        if self.cache_baseaddr <= addr <= \
           self.cache_baseaddr + self.cache_numregs - 1:
            low = self._cached_registers[addr - self.cache_baseaddr]
            high = self._cached_registers[addr - self.cache_baseaddr + 1]
        else:
            low, high = self._taco_guard(self._dev.readHoldingRegisters,
                                         (0, int(addr), 2))
        return unpack('<I', pack('<HH', low, high))

    def WriteDWord(self, addr, value):
        low, high = unpack('<HH', pack('<I', int(value)))
        self._taco_guard(self._dev.writeMultipleRegisters,
                         (0, int(addr + self.baseaddr), low, high))
        self._sync()

    # REAL's are stored differently on different Beckhoffs.
    def ReadFloat(self, addr):
        addr += self.baseaddr
        if self.cache_baseaddr <= addr <= \
           self.cache_baseaddr + self.cache_numregs - 1:
            low = self._cached_registers[addr - self.cache_baseaddr]
            high = self._cached_registers[addr - self.cache_baseaddr + 1]
        else:
            low, high = self._taco_guard(self._dev.readHoldingRegisters,
                                         (0, int(addr), 2))
        return unpack(self.__float_conv[0],
                      pack(self.__float_conv[1], low, high))

    def WriteFloat(self, addr, value):
        low, high = unpack(self.__float_conv[1],
                           pack(self.__float_conv[0], float(value)))
        self._taco_guard(self._dev.writeMultipleRegisters,
                         (0, int(addr + self.baseaddr), low, high))
        self._sync()


STATUS_MAP = [status.UNKNOWN, status.OK, status.BUSY, status.BUSY,
              status.OK, status.NOTREACHED, status.NOTREACHED,
              status.NOTREACHED,
              status.ERROR, status.ERROR, status.ERROR, status.ERROR,
              status.ERROR, status.ERROR, status.ERROR, status.ERROR]


class PLCDevice(Readable):
    hw_access = False
    attached_devices = {
        'bus': Attach('Modbus connector to Beckhoff', Beckhoff)
        }

    parameters = {
        'addr': Param('Base-Address of the Device in the Modbus-Space',
                      type=int, mandatory=True, settable=True)
        }
    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
        }

    @property
    def bus(self):
        return self._adevs['bus']

    def doInit(self, mode):
        if mode != SIMULATION:
            if self.addr not in self.bus._devices:
                raise ConfigurationError(self, 'Configured Address %0x04x not '
                                               'exported from the Beckhoff' %
                                               self.addr)

    def doStatus(self, maxage=0):
        return status.OK, ''


class SimpleDiscreteInput(PLCDevice):
    parameter_overrides = {
        'fmtstr': Override(default='%d'),
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
            raise MoveError(self, 'target value %d not accepted, was reset to '
                                  '%d' % (target, readback))


class JustAWord(SimpleDiscreteInput):
    def doStart(self, target):
        self.wait()
        self.bus.WriteWord(self.addr, target)


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
            raise MoveError(self, 'target value %g not accepted, was reset to '
                                  '%g' % (target, readback))


class FullDiscreteInput(SimpleDiscreteInput):
    def doStatus(self, maxage=0):
        Status = self.bus.ReadWord(self.addr + 1)
        self.log.debug('Statusword = ' + bin(65536 | Status)[3:])
        return STATUS_MAP[Status >> 12], \
            'Status: %s, Aux bits: %s' % (bin(16 | (Status >> 12))[3:],
                                          bin(65536 | Status)[7:])


class FullDiscreteOutput(SimpleDiscreteOutput):
    def doStatus(self, maxage=0):
        Status = self.bus.ReadWord(self.addr + 2)
        self.log.debug('Statusword = ' + bin(65536 | Status)[3:])
        return STATUS_MAP[Status >> 12], \
            'Status: %s, Aux bits: %s' % (bin(16 | (Status >> 12))[3:],
                                          bin(65536 | Status)[7:])


class FullAnalogInput(SimpleAnalogInput):
    def doStatus(self, maxage=0):
        Status = self.bus.ReadWord(self.addr + 2)
        self.log.debug('Statusword = ' + bin(65536 | Status)[3:])
        return STATUS_MAP[Status >> 12], \
            'Status: %s, Aux bits: %s' % (bin(16 | (Status >> 12))[3:],
                                          bin(65536 | Status)[7:])


class FullAnalogOutput(SimpleAnalogOutput):
    def doStatus(self, maxage=0):
        Status = self.bus.ReadWord(self.addr + 4)
        self.log.debug('Statusword = ' + bin(65536 | Status)[3:])
        return STATUS_MAP[Status >> 12], \
            'Status: %s, Aux bits: %s' % (bin(16 | (Status >> 12))[3:],
                                          bin(65536 | Status)[7:])


class HWError(NicosError):
    category = 'Hardware error'  # can't continue!


#
# new SequenceItems
#
class SeqCheckStatus(SequenceItem):
    def __init__(self, dev, status, *args, **kwargs):
        SequenceItem.__init__(dev=dev, status=status, args=args, kwargs=kwargs)

    def run(self):
        if hasattr(self.status, '__iter__'):
            stati = self.status
        else:
            stati = [self.status]
        status = self.dev.status(0)[0]
        if status not in stati:
            raise HWError(self, 'Expected %r to have a Status of %r, but has '
                          '%r' % (self.dev, stati, status))


class SeqCheckPosition(SequenceItem):
    def __init__(self, dev, position, *args, **kwargs):
        SequenceItem.__init__(dev=dev, position=position, args=args,
                              kwargs=kwargs)

    def run(self):
        if hasattr(self.position, '__iter__'):
            positions = self.position
        else:
            positions = [self.position]
        pos = self.dev.read(0)
        if pos not in positions:
            raise HWError(self, 'Expected %r to have a Position of %r, but '
                          'has %r' % (self.dev, positions, pos))


class SeqSetAttr(SequenceItem):
    def __init__(self, obj, key, value):
        SequenceItem.__init__(obj=obj, key=key, value=value)

    def run(self):
        setattr(self.obj, self.key, self.value)


class SeqCheckAttr(SequenceItem):
    def __init__(self, obj, key, value=None, values=None):
        SequenceItem.__init__(obj=obj, key=key, value=value, values=values)

    def run(self):
        if self.value is not None:
            if getattr(self.obj, self.key) != self.value:
                raise HWError(self, '%s.%s should be %r !' %
                              (self.obj, self.key, self.value))
        elif self.values is not None:
            if getattr(self.obj, self.key) not in self.values:
                raise HWError(self, '%s.%s should be one of %s !'
                              % (self.obj, self.key, ', '.join(self.values)))


#
# here comes the real monochanger device: TEST THIS !
#
class Changer(BaseSequencer):
    attached_devices = {
        'lift':          Attach('Lift moving a mono up or down between 4 '
                                'positions', Moveable),
        'magazine':      Attach('Magazine holding the monos and having 4 '
                                'positions', Moveable),
        'liftclamp':     Attach('clamp holding the mono in the lift',
                                Moveable),
        'magazineclamp': Attach('clamp holding the mono in the magazine',
                                Moveable),
        'tableclamp':    Attach('clamp holding the mono on the table',
                                Moveable),
        'inhibitrelay':  Attach('Inhibit to the remaining motor controllers',
                                Moveable),
        'enable':        Attach('to enable operation of the changer',
                                Moveable),
        'magazineocc':   Attach('readout for occupancy of the magazine',
                                Moveable),
    }

    parameters = {
        'mono_on_table': Param('Name of Mono on the Monotable',
                               type=oneof('PG', 'Si', 'Cu', 'Heusler', 'None'),
                               default='None', settable=True, userparam=False),
        'mono_in_lift':  Param('Which mono is in the lift',
                               type=oneof('PG', 'Si', 'Cu', 'Heusler', 'None'),
                               default='None', settable=True, userparam=False),
        'exchangepos':   Param('dict of device names to positional values for '
                               'changing monos',
                               type=dict, settable=False, userparam=False),
    }

    parameter_overrides = {
        'requires': Override(default={'level': 'admin'},),
    }

    positions = ['101', '110', '011', '111']  # CounterClockwise
    monos = ['Heusler', 'PG', 'Si', 'Cu']  # assigned monos
    shields = ['111', '111', '111', '111']  # which magazinslot after changing
    # (e.g. Put a PE dummy to 101 and set this to ('101,'*4).split(',')
    valuetype = oneof(monos + ['None'])

    def PrepareChange(self):
        '''prueft, ob alle Bedingungen fuer einen Wechsel gegeben sind und
        stellt diese ggfs. her'''

        # if not(self.SecShutter_is_closed()):
        #     raise UsageError(self, 'Secondary Shutter needs to be closed, '
        #                      'please close by hand and retry!')
        # if self.NotAus():
        #     raise UsageError(self, 'NotAus (Emergency stop) activated, '
        #                      'please check and retry!')
        # read all inputs and check for problems
        if not(self._adevs['magazine'].read() in self.positions):
            raise HWError(self, 'Unknown Magazine-Position !')
        if self._adevs['lift'].read() != 2:
            raise HWError(self, 'Lift not at parking position!')
        if self._adevs['liftclamp'].read() != 'close':
            raise HWError(self, 'liftclamp should be closed!')
        if self._adevs['tableclamp'].read() != 'close':
            raise HWError(self, 'tableclamp should be closed!')
        if self._adevs['magazineclamp'].read() != 'close':
            raise HWError(self, 'magazineclamp should be closed!')
        if self.mono_in_lift != 'None':
            raise HWError(self, 'There is mono %s in the lift, please change '
                                'manually!' % self.mono_in_lift)

        # TODO: store old values of positions and offsets someplace to
        # recover after changing back

        # go to the place where a change is possible
        devs = []
        for devname, pos in self.exchangepos.items():
            dev = session.getDevice(devname)
            dev.start(pos)
            devs.append(dev)
        multiWait(devs)

        try:
            dev = session.getDevice('focibox')
            self.mono_on_table = dev.read(0)
            dev.comm('XMA', forcechannel=False)
            dev.comm('YMA', forcechannel=False)
            dev.driverenable = False
        except NicosError as err:
            self.log.error('Problem disabling foci', err)

        # switch on inhibit and enable
        self._adevs['enable'].maw(0xef14)
        self._adevs['inhibitrelay'].maw('on')

    def FinishChange(self):
        self._adevs['inhibitrelay'].maw('off')
        self._adevs['enable'].maw(0)
        self.log.warning('Please restart the daemon or reload the setups to '
                         'init the new Mono:')
        self.log.warning('  > NewSetup()')
        self.log.info('  > NewSetup()')

    def CheckMagazinSlotEmpty(self, slot):
        # checks if the given slot in the magazin is empty
        index = self.positions.index(slot)
        if (self._adevs['magazineocc'].read() >> index) & 1:
            raise UsageError(self, 'Position %r is already occupied!' % slot)

    def CheckMagazinSlotUsed(self, slot):
        # checks if the given slot in the magazin is used
        # (contains a monoframe)
        index = self.positions.index(slot) + 4
        if (self._adevs['magazineocc'].read() >> index) & 1:
            raise UsageError(self, 'Position %r is empty!' % slot)

    def _start(self, seq):
        if self._seq_thread is not None:
            raise MoveError(self, 'Can not start sequence, device is still '
                            'busy')
        self._startSequence(seq)

    # here is the party going on!
    def Transfer_Mono_Magazin2Lift(self):
        self._start(self._gen_mag2lift())

    def _gen_mag2lift(self, magpos=None):
        seq = []
        if magpos is None:
            magpos = self._adevs['magazine'].read(0)
        else:
            seq.append(SeqDev(self._adevs['magazine'], magpos))
        # check preconditions
        seq.append(SeqCheckStatus(self._adevs['magazine'], status.OK))
        seq.append(SeqCheckStatus(self._adevs['lift'], status.OK))
        seq.append(SeqCheckPosition(self._adevs['lift'], 2))
        seq.append(SeqCheckPosition(self._adevs['liftclamp'], 'close'))
        seq.append(SeqCheckPosition(self._adevs['magazine'], magpos))
        seq.append(SeqCheckPosition(self._adevs['magazineclamp'], 'close'))
        seq.append(SeqMethod(self, 'CheckMagazinSlotUsed', magpos))
        seq.append(SeqCheckAttr(self, 'mono_in_lift', 'None'))
        # transfer mono to lift
        seq.append(SeqDev(self._adevs['liftclamp'], 'open'))
        seq.append(SeqDev(self._adevs['lift'], 3))  # almost top position
        seq.append(SeqMethod(self._adevs['liftclamp'], 'start', 'close'))
        seq.append(SeqDev(self._adevs['lift'], 4))  # top position
        seq.append(SeqDev(self._adevs['liftclamp'], 'close'))
        seq.append(SeqMethod(self._adevs['magazineclamp'], 'start', 'open'))
        # rattle a little
        seq.append(SeqDev(self._adevs['lift'], 3))  # almost top position
        seq.append(SeqDev(self._adevs['lift'], 4))  # top position
        seq.append(SeqDev(self._adevs['lift'], 3))  # almost top position
        seq.append(SeqDev(self._adevs['lift'], 4))  # top position
        seq.append(SeqDev(self._adevs['magazineclamp'], 'open'))
        # move (with mono) to parking position
        seq.append(SeqSetAttr(self, 'mono_in_lift',
                              self.monos[self.positions.index(magpos)]))
        seq.append(SeqDev(self._adevs['lift'], 2))  # park position
        seq.append(SeqDev(self._adevs['magazineclamp'], 'close'))
        # Magazin should not contain a mono now
        seq.append(SeqMethod(self, 'CheckMagazinSlotEmpty', magpos))
        return seq

    def Transfer_Mono_Lift2Magazin(self):
        self._start(self._gen_lift2mag())

    def _gen_lift2mag(self, magpos=None):
        seq = []
        if magpos is None:
            magpos = self._adevs['magazine'].read(0)
        else:
            seq.append(SeqDev(self._adevs['magazine'], magpos))
        # check preconditions
        seq.append(SeqCheckStatus(self._adevs['magazine'], status.OK))
        seq.append(SeqCheckStatus(self._adevs['lift'], status.OK))
        seq.append(SeqCheckPosition(self._adevs['lift'], 2))
        seq.append(SeqCheckPosition(self._adevs['liftclamp'], 'close'))
        seq.append(SeqCheckPosition(self._adevs['magazine'], magpos))
        seq.append(SeqCheckPosition(self._adevs['magazineclamp'], 'close'))
        seq.append(SeqMethod(self, 'CheckMagazinSlotEmpty', magpos))
        # there needs to be a mono in the lift
        seq.append(SeqCheckAttr(self, 'mono_in_lift',
                                values=[m for m in self.monos if m != 'None']))
        # prepare magazin
        seq.append(SeqDev(self._adev['magazineclamp'], 'open'))
        seq.append(SeqDev(self._adev['magazineclamp'], 'close'))
        seq.append(SeqDev(self._adev['magazineclamp'], 'open'))
        seq.append(SeqDev(self._adev['magazineclamp'], 'close'))
        seq.append(SeqDev(self._adev['magazineclamp'], 'open'))
        # transfer mono to lift
        seq.append(SeqDev(self._adevs['lift'], 4))  # top position
        seq.append(SeqMethod(self._adev['magazineclamp'], 'start', 'close'))
        # rattle a little
        seq.append(SeqDev(self._adevs['lift'], 3))  # almost top position
        seq.append(SeqDev(self._adevs['lift'], 4))  # top position
        seq.append(SeqDev(self._adevs['lift'], 3))  # almost top position
        seq.append(SeqDev(self._adevs['lift'], 4))  # top position
        seq.append(SeqDev(self._adevs['lift'], 3))  # almost top position
        seq.append(SeqDev(self._adev['magazineclamp'], 'close'))
        seq.append(SeqMethod(self._adevs['liftclamp'], 'start', 'open'))
        seq.append(SeqDev(self._adevs['lift'], 4))  # top position
        seq.append(SeqDev(self._adevs['lift'], 3))  # top position
        seq.append(SeqDev(self._adevs['liftclamp'], 'open'))
        seq.append(SeqDev(self._adevs['lift'], 2))  # park position
        seq.append(SeqDev(self._adevs['liftclamp'], 'close'))
        # move (without mono) to parking position
        seq.append(SeqSetAttr(self, 'mono_in_lift', 'None'))
        # Magazin should not contain a mono now
        seq.append(SeqMethod(self, 'CheckMagazinSlotUsed', magpos))
        return seq

    def Transfer_Mono_Lift2Monotisch(self):
        self._start(self._gen_lift2table())

    def _gen_lift2table(self):
        seq = []
        # check preconditions
        seq.append(SeqCheckStatus(self._adevs['tableclamp'], status.OK))
        seq.append(SeqCheckStatus(self._adevs['liftclamp'], status.OK))
        seq.append(SeqCheckStatus(self._adevs['lift'], status.OK))
        seq.append(SeqCheckPosition(self._adevs['lift'], 2))
        seq.append(SeqCheckPosition(self._adevs['liftclamp'], 'close'))
        seq.append(SeqCheckPosition(self._adevs['tableclamp'], 'close'))
        # there shall be a mono in the lift!
        seq.append(SeqCheckAttr(self, 'mono_in_lift',
                                values=[m for m in self.monos if m != 'None'])
                   )
        seq.append(SeqCheckAttr(self, 'mono_on_table', 'None'))
        # transfer mono to table
        seq.append(SeqDev(self._adevs['tableclamp'], 'open'))
        seq.append(SeqDev(self._adevs['lift'], 1))  # bottom position
        seq.append(SeqDev(self._adevs['tableclamp'], 'close'))

        # move (without mono) to parking position
        seq.append(SeqDev(self._adevs['liftclamp'], 'open'))

        def func(self):
            self.mono_on_table, self.mono_in_lift = self.mono_in_lift, 'None'
        seq.append(SeqCall(func, self))
        # seq.append(SeqSetAttr(self, 'mono_on_table', self.mono_in_lift))
        # seq.append(SeqSetAttr(self, 'mono_in_lift', 'None'))
        seq.append(SeqDev(self._adevs['lift'], 2))  # park position
        seq.append(SeqDev(self._adevs['liftclamp'], 'close'))
        # TODO: change foci alias and reactivate foci
        return seq

    def Transfer_Mono_Monotisch2Lift(self):
        self._start(self._gen_table2lift())

    def _gen_table2lift(self):
        # XXX TODO drive all foci to 0 and switch of motors....
        # XXX TODO move mty/mtx to monospecific abholposition
        # hier nur das reine abholen vom Monotisch
        seq = []
        # check preconditions
        seq.append(SeqCheckStatus(self._adevs['tableclamp'], status.OK))
        seq.append(SeqCheckStatus(self._adevs['liftclamp'], status.OK))
        seq.append(SeqCheckStatus(self._adevs['lift'], status.OK))
        seq.append(SeqCheckPosition(self._adevs['lift'], 2))
        seq.append(SeqCheckPosition(self._adevs['liftclamp'], 'close'))
        seq.append(SeqCheckPosition(self._adevs['tableclamp'], 'close'))
        # there shall be no mono in the lift, but one on the table
        seq.append(SeqCheckAttr(self, 'mono_in_lift', 'None'))
        seq.append(SeqCheckAttr(self, 'mono_on_table',
                                values=[m for m in self.monos if m != 'None'])
                   )
        # transfer mono to lift
        seq.append(SeqDev(self._adevs['liftclamp'], 'open'))
        seq.append(SeqDev(self._adevs['lift'], 1))  # bottom position
        seq.append(SeqDev(self._adevs['liftclamp'], 'close'))
        seq.append(SeqDev(self._adevs['tableclamp'], 'open'))

        # move (with mono) to parking position
        def func(self):
            self.mono_on_table, self.mono_in_lift = 'None', self.mono_on_table
        seq.append(SeqCall(func, self))
        # seq.append(SeqSetAttr(self, 'mono_on_table', 'None'))
        # seq.append(SeqSetAttr(self, 'mono_in_lift', self.mono_on_table))
        seq.append(SeqDev(self._adevs['lift'], 2))  # park position
        seq.append(SeqDev(self._adevs['tableclamp'], 'close'))
        return seq

    def doStart(self, target):
        self.change(self.mono_on_table, target)

    def change(self, old, whereto):
        ''' cool kurze Wechselroutine
        Der Knackpunkt ist in den Hilfsroutinen!'''
        if not(old in self.monos + ['None']):
            raise UsageError(self, '\'%s\' is illegal value for Mono, use one '
                             'of ' % old + ', '.join(self.monos + ['None']))
        if not(whereto in self.monos + ['None']):
            raise UsageError(self, '\'%s\' is illegal value for Mono, use one '
                             'of ' % whereto + ', '.join(self.monos + ['None'])
                             )
        self.PrepareChange()
        if self.monos.index(whereto) == self.monos.index(old):
            # Nothing to do, requested Mono is supposed to be on the table
            return
        # Ok, we have a good state, the only thing we do not know is which mono
        # is on the table......
        # for this we use the (cached) parameter mono_on_table

        if self.mono_on_table != old:
            raise UsageError(self, 'Mono %s is not supposed to be on the '
                             'table, %s is!' % (old, self.mono_on_table))

        seq = []
        # 1) move away the old mono, if any
        if old != 'None':
            seq.extend(self._gen_table2lift())
            seq.extend(self._gen_lift2mag(self.positions[
                self.monos.index(old)]))
        # 2) fetch the new mono (if any) from the magazin
        if whereto != 'None':
            seq.extend(self._gen_mag2lift(self.positions[
                self.monos.index(whereto)]))
            seq.extend(self._gen_lift2table())
            seq.append(SeqDev(self._adevs['magazine'],
                              self.shields[self.monos.index(whereto)]))

        seq.append(SeqDev(self._adevs['enable'], 0))
        seq.append(SeqMethod(self, 'FinishChange'))
        self._start(seq)
        self.wait()

    @usermethod
    def printstatusinfo(self):
        self.log.info('PLC is %s' %
                      ('enabled' if self._adevs['enable'].read() == 0xef14 else
                       'disabled'))
        self.log.info('Inhibit_realy is %s' %
                      self._adevs['inhibitrelay'].read())
        liftposnames = {1: 'Absetzposition',
                        2: 'Parkposition',
                        3: 'untere Ablage',
                        4: 'obere Ablage'}
        self.log.info('lift is at %s' %
                      liftposnames[self._adevs['lift'].read()])
        try:
            magpos = self._adevs['magazine']
            self.log.info('magazine is at %r which is assigned to %s' % (
                          magpos, self.monos[self.positions.index(magpos)]))
        except Exception:
            self.log.error('magazine is at an unknown position !!!')
        for n in 'liftclamp magazineclamp tableclamp'.split():
            self.log.info('%s is %s' % (n, self._adevs[n].read()))
        occ = self._adevs['magazineocc'].read()
        for i in range(4):
            self.log.info('magazineslot %r is %s empty and %s occupied' %
                          (self.positions[i],
                           '' if (occ >> i) & 1 else 'not',
                           '' if (occ >> (i+4)) & 1 else 'not'))
