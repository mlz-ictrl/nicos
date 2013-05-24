#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""PANDA Mcc2 Interface for 7T5 Magnet."""

from time import sleep

from IO import StringIO

from nicos.core import status, intrange, floatrange, oneofdict, oneof, \
     usermethod, Device, Param, CommunicationError, TimeoutError
from nicos.devices.abstract import Motor as NicosMotor, Coder as NicosCoder
from nicos.devices.taco.core import TacoDevice


class TacoSerial(TacoDevice, Device):
    taco_class = StringIO
    def communicate(self, msg):
        return self._taco_guard(self._dev.communicate, msg)
        # return self._taco_multitry('communicate', 3,
        #                            self._dev.communicate, msg)


class MCC2Base(object):
    """Base class for devices communicating using the Phytron protocol."""

    attached_devices = {
        'bus':  (TacoSerial, 'Serial connection to the Phytron controller'),
    }

    parameters = {
        'channel'  : Param('Channel of MCC2 to use (X or Y)',
                           type=oneof('X', 'Y'), default='Y'),
        'addr'     : Param('Address of MCC2 to use (0 to 15)',
                           type=intrange(0, 15), default=0),
    }

    def _comm(self, cmd, forcechannel=True):
        if forcechannel:
            cmd = cmd.replace('X', self.channel).replace('Y', self.channel)
        temp = self._adevs['bus'].communicate('\x02' + hex(self.addr)[-1] +
                                              cmd + '\x03')
        if len(temp) >= 2 and temp[0] == '\x02':   # strip beginning STX
            if temp[-1] == '\x03': # strip optional ending ETX
                temp = temp[:-1]
            if temp[1] == '\x06':
                return temp[2:]
            # no ACK -> raise exception
            raise CommunicationError(self, 'NAK response to %r' % cmd)
        raise CommunicationError(self, 'no response to %r' % cmd)

    def doInit(self, mode):
        if mode != 'simulation':
            if not self._comm('IVR').startswith('MCC'):
                raise CommunicationError(self, 'no response from Phytron, '
                                         'please check')

    @usermethod
    def store(self):
        return self._comm('SA')


class MCC2Coder(MCC2Base, NicosCoder):
    """Class for the readout of a MCC2 coder."""

    codertypes = ('none', 'incremental', 'ssi-binary', 'ssi-gray')
    parameters = {
        'slope'    : Param('Coder units per degree of rotation',
                           settable=True, type=float, default=1),
        'zerosteps': Param('Coder steps at physical zero',
                           settable=True, type=int, default=0),
        'codertype': Param('Type of encoder', settable=True,
                           type=oneof(*codertypes), default='none'),
        'coderbits': Param('Number of bits of SSI encoder',
                           type=intrange(0, 31), default=0, settable=True),
    }

    def doReset(self):
        self._comm('XP39S1')

    def doReadCoderbits(self):
        return int(self._comm('XP35R'))

    def doWriteCoderbits(self, value):
        return self._comm('XP35S%d' % int(value))

    def doReadCodertype(self):
        return self.codertypes[int(self._comm('XP34R'))]

    def doWriteCodertype(self, value):
        return self._comm('XP34S%d' % self.codertypes.index(value))

    def doRead(self, maxage=0):
        return (float(self._comm('XP22R')) - self.zerosteps) / self.slope

    def doStatus(self, maxage=0):
        return status.OK, 'no status readout'

    def doSetPosition(self, pos):
        self._comm('XP22S%d' % int(float(pos)*self.slope + self.zerosteps))


class MCC2Motor(MCC2Base, NicosMotor):
    """Class for the control of a MCC2 motor."""

    parameters = {
        'slope'      : Param('Full motor steps per physical unit',
                             type=float, default=1, settable=True),
        'power'      : Param('Internal power stage switch', default='on',
                             type=oneofdict({0: 'off', 1: 'on'}), settable=True,
                             volatile=True),
        'steps'      : Param('Last position in steps', settable=True,
                             type=int, prefercache=False),
        'speed'      : Param('Motor speed in physical units', settable=True,
                             type=float),
        'accel'      : Param('Motor acceleration in physical units', settable=True,
                             type=float),
        'microstep'  : Param('Microstepping mode', unit='steps', settable=True,
                             type=intrange(1, 255)),
        'idlecurrent': Param('Current whenever motor is idle', unit='A',
                             settable=True, type=floatrange(0, 2.5)),
        'rampcurrent': Param('Current whenever motor is ramping', unit='A',
                             settable=True, type=floatrange(0, 2.5)),
        'movecurrent': Param('Current whenever motor is moving at speed',
                             unit='A', settable=True, type=floatrange(0, 2.5)),
        'linear'     : Param('Linear stage (as opposed to choppered stage)',
                             default=False, type=oneof(True, False),
                             settable=False, prefercache=False),
    }

    def doReset(self):
        self._comm('XP1S1')  # linear mode
        self._comm('XP2S1')  # steps
        self._comm('XP3S1')  # unity slope
        self._comm('XP4S20') # lowest frequency which is Ok whithout ramp
        self._comm('XP17S2') # ramping uses boostcurrent
        self._comm('XP25S0') # no backlash correction, this is done in the axis code
        self._comm('XP27S0') # limit switches are openers (normally closed=n.c.)

    def doReadLinear(self):
        return int(self._comm('XP48R')) == 1

    def doReadIdlecurrent(self):
        if self.linear:
            return 0.05 * float(self._comm('XP40R'))
        else:
            return 0.1 * float(self._comm('XP40R'))

    def doWriteIdlecurrent(self, value):
        if self.linear:
            self._comm('XP40S%d' % max(0, min(25, round(value / 0.05))))
        else:
            self._comm('XP40S%d' % max(0, min(25, round(value / 0.1))))
        return self.doReadIdlecurrent()

    def doReadMovecurrent(self):
        if self.linear:
            return 0.05 * float(self._comm('XP41R'))
        else:
            return 0.1 * float(self._comm('XP41R'))

    def doWriteMovecurrent(self, value):
        if self.linear:
            self._comm('XP41S%d' % max(0, min(25, round(value / 0.05))))
        else:
            self._comm('XP41S%d' % max(0, min(25, round(value / 0.1))))
        return self.doReadMovecurrent()

    def doReadRampcurrent(self):
        if self.linear:
            return 0.05 * float(self._comm('XP42R'))
        else:
            return 0.1 * float(self._comm('XP42R'))

    def doWriteRampcurrent(self, value):
        if self.linear:
            self._comm('XP42S%d' % max(0, min(25, round(value / 0.05))))
        else:
            self._comm('XP42S%d' % max(0, min(25, round(value / 0.1))))
        return self.doReadRampcurrent()

    def doRead(self, maxage=0):
        return float(self._comm('XP21R')) / (self.slope * self.microstep)

    def _readSE(self):
        temp = self._comm('SE')
        i = ['X', 'Y', 'Z', 'W'].index(self.channel.upper())
        temp = temp[4 * i:4 * i + 4]
        return int(temp, 16)

    def doReadPower(self):
        if self._readSE() & (1 << 3):
            return 'on'
        else:
            return 'off'

    def doWritePower(self, value):
        if value in ['on', 1, True]:
            self._comm('XMA')
        else:
            self._comm('XMD')
        return self.doReadPower()

    def doReadMicrostep(self):
        return int(self._comm('XP45R'))

    def doWriteMicrostep(self, value):
        self._comm('XP45S%d' % int(value))
        return self.doReadMicrostep()

    def doReadSpeed(self):
        return float(self._comm('XP14R')) / float(self.microstep * abs(self.slope))

    def doWriteSpeed(self, value):
        f = max(0, min(40000, value * abs(self.slope) * self.microstep))
        self._comm('XP14S%d' % int(f))
        return self.doReadSpeed()

    def doReadAccel(self):
        return float(self._comm('XP15R')) / float(self.microstep * abs(self.slope)) ** 2

    def doWriteAccel(self, value):
        f = max(4000, min(500000, 4000 * round((value *
            (abs(self.slope) * self.microstep) ** 2) / 4000)))
        self._comm('XP15S%d' % int(f))
        return self.doReadAccel()

    def doStart(self, pos):
        """Go to an absolute stepper postition."""
        pos = int(pos * self.slope * self.microstep) # use microsteps as well???
        self._comm('XE%d' % pos)

    def doStop(self):
        """Send the stop command."""
        for _i in range(5):
            try:
                self._comm('XS')
            except CommunicationError:
                continue
            break
        else:
            self.log.error(self, 'Stopping failed: no ACK')

    def doSetPosition(self, newpos):
        """Set current position to given value."""
        d = int(newpos * self.slope * self.microstep)
        self._comm('XP20S%d XP21S%d XP19S%d' % (d, d, d)) # set all counters

    def doStatus(self, maxage=0): # XXX
        sui = self._comm('SUI')[['X', 'Y', 'Z', 'W'].index(self.channel)]
        t = self._readSE()
        sl = ['overcurrent', 'undervoltage', 'overtemperature', 'driver enabled',
              'limit switch - active', 'limit switch + active', 'stepping error',
              'encoder error', 'motor halted', 'referenced']
        s = ''

        if sui == '2':
            s += 'both limit switches active, '
        elif sui == '+':
            s += 'limit switch + active, '
        elif sui == '-':
            s += 'limit switch - active, '

        for i in range(len(sl)):
            if (t & (1 << i)) >> i == 1:
                s += sl[i] + ', '
        if (t & 0x100) == 0:
            s += 'motor moving, '

        if (t & 0x100) == 0:
            return status.BUSY, s[:-2]
        if (t & 0b1000111) != 0 or sui == '2':
            return status.ERROR, s[:-2]
        return status.OK, s[:-2]

    def doWait(self):
        timeleft = 900
        while self.doStatus()[0] == status.BUSY:
            sleep(0.1)
            timeleft -= 0.1
            if timeleft <= 0:
                self.doStop()
                raise TimeoutError(self, 'Didn\'t stop within 900s, something '
                                   'is wrong!')
