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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA Mcc2 Interface for 7T5 Magnet."""

__version__ = "$Revision$"

from time import sleep

from IO import StringIO

from nicos.core import status, intrange, floatrange, oneofdict, oneof, \
     usermethod, Device, Param, CommunicationError, TimeoutError
from nicos.utils import lazy_property
from nicos.devices.abstract import Motor as NicosMotor, Coder as NicosCoder
from nicos.devices.taco import TacoDevice

class TacoSerial(TacoDevice, Device):
    taco_class = StringIO
    def communicate(self, what):
        return self._taco_guard(self._dev.communicate, what)
        #~ return self._taco_multitry( 'Communicate', 3, self._dev.communicate, what )

class MCC2Coder(NicosCoder):
    """Class for the readout of a Mcc2-coder"""
    attached_devices = dict(
        bus=(TacoSerial, 'The Serial connection to the phytron Box'),
    )
    parameters = {
        'fmtstr'        : Param('Format string for the device value',
                            type=str, default='%.3f', settable=False),
        'channel'       : Param(' Channel of MCC2 to use (X or Y)',
                            type=oneof('X', 'Y'), default='Y'),
        'addr'          : Param(' address of MCC2 to use (0 to 15)',
                            type=intrange(0, 15), default=0),
        'slope'         : Param('coder units per degree of rotation',
                            type=float, default=1,settable=True),
        'zerosteps'     : Param('coder steps at physical zero',
                            type=int, default=0,settable=True),
        'codertype'     : Param('type of encoder',
                            type=oneof('none', 'incremental', 'ssi-binary', 'ssi-gray'), default='none',settable=True),
        'coderbits'     : Param('number of bits of ssi-encoder',
                            type=intrange(0, 31), default=0,settable=True),
    }
    codertypes = ('none', 'incremental', 'ssi-binary', 'ssi-gray')
    @property   # XXX maybe lazy_property ???
    def bus(self):
        return self._adevs['bus']
    def comm(self, cmd, forcechannel=True):
        if forcechannel:
            cmd = cmd.replace('X', self.channel).replace('Y', self.channel)
        temp = self.bus.communicate('\002' + hex(self.addr)[-1] + cmd + '\003')
        if len(temp) >= 2 and temp[0] == '\002':   #strip beginning STX
            temp = temp[1:]
            if temp[-1] == '\003': #strip optional ending stx
                temp = temp[:-1]
            if temp[0] == '\006':
                return temp[1:]
            else:
                return None     # no ACK means nothing good!
        raise CommunicationError(self, 'Response timed out')


    def doInit(self, mode):
        if mode != 'simulation':
            if not self.comm('IVR').startswith('MCC'):
                raise CommunicationError(self, 'No Response from Phytron, please check!')
    def doReset( self ):
        self.comm('XP39S1')
    def doReadCoderbits(self):
        return int(self.comm('XP35R'))
    def doWriteCoderbits(self, value):
        return self.comm('XP35S%d' % int(value))
    def doReadCodertype(self):
        return self.codertypes[int(self.comm('XP34R'))]
    def doWriteCodertype(self, value):
        return self.comm('XP34S%d' % self.codertypes.index(value))
    def doRead(self, maxage=0):
        return (float(self.comm('XP22R')) - self.zerosteps) / self.slope
    def doSetPosition(self,pos):
        self.comm('XP22S%d'%int(float(pos)*self.slope+self.zerosteps))
        return self.doRead()#NicosCoder.doSetPosition(self, pos) # will raise NotImplementedError
    @usermethod
    def store(self):
        return self.comm('SA')


class MCC2Motor(NicosMotor):
    """Class for the control of the Mcc2-Motor"""
    attached_devices = dict(
        bus=(TacoSerial, 'The Serial connection to the phytron Box'),
    )
    parameters = {
        'precision'     : Param('Precision of the device value',
                            type=float, unit='main', settable=False,
                            category='precisions', default=0.001),
        'fmtstr'        : Param('Format string for the device value',
                            type=str, default='%.3f', settable=False),
        'channel'       : Param(' Channel of MCC2 to use (X or Y)',
                            type=oneof('X', 'Y'), default='Y'),
        'addr'          : Param(' address of MCC2 to use (0 to 15)',
                            type=intrange(0, 15), default=0),
        'slope'         : Param('Full motor steps per physical unit',
                            type=float, default=1),
        'power'         : Param('Internal power stage switch', default='on',
                            type=oneofdict({0: 'off', 1: 'on'}), settable=True,
                            volatile=True),
        'steps'         : Param('Last position in steps', settable=True,
                            type=int, prefercache=False),
        'speed'         : Param('Motor speed in physical units', settable=True,
                            type=float),
        'accel'         : Param('Motor acceleration in physical units', settable=True,
                            type=float),
        'microstep'     : Param('Microstepping mode', unit='steps', settable=True,
                            type=intrange(1, 255)),
        'idlecurrent'   : Param('Current whenever Motor is Idle', unit='A', settable=True,
                            type=floatrange(0, 2.5)),
        'rampcurrent'   : Param('Current whenever Motor is Ramping', unit='A', settable=True,
                            type=floatrange(0, 2.5)),
        'movecurrent'   : Param('Current whenever Motor is moving at speed', unit='A', settable=True,
                            type=floatrange(0, 2.5)),
        'linear'        : Param('linear stage (as opposed to choppered stage)', default=False,
                            type=oneof(True, False), settable=False, prefercache=False),
    }

    @property   # XXX maybe lazy_property ???
    def bus(self):
        return self._adevs['bus']
    def comm(self, cmd, forcechannel=True):
        if forcechannel:
            cmd = cmd.replace('X', self.channel).replace('Y', self.channel)
        self.log.debug('CMD is %r' % cmd)
        temp = self.bus.communicate('\002' + hex(self.addr)[-1] + cmd + '\003')
        self.log.debug('Communicate yielded %r' % temp)
        if len(temp) >= 2 and temp[0] == '\002':   #strip beginning STX
            temp = temp[1:]
            if temp[-1] == '\003': #strip optional ending stx
                temp = temp[:-1]
            if temp[0] == '\006':
                return temp[1:]
            else:
                return None     # no ACK means nothing good!
        raise CommunicationError(self, 'Response timed out')


    def doInit(self, mode):
        if mode != 'simulation':
            if not self.comm('IVR').startswith('MCC'):
                raise CommunicationError(self, 'No Response from Phytron, please check!')
    def doReset( self ):
        self.comm('XP1S1')  # linear mode
        self.comm('XP2S1')  # steps
        self.comm('XP3S1')  # unity slope
        self.comm('XP4S20') # lowest frequency which is Ok whithout ramp
        self.comm('XP17S2') # ramping uses boostcurrent
        self.comm('XP25S0') # no backlash correction, this is done in the axis code
        self.comm('XP27S0') # Limit switches are openers (normally closed=n.c.)
    @lazy_property
    def doReadLinear(self):
        return int(self.comm('XP48R')) == 1
    def doReadIdlecurrent(self):
        if self.linear:
            return 0.05 * float(self.comm('XP40R'))
        else:
            return 0.1 * float(self.comm('XP40R'))
    def doWriteIdlecurrent(self, value):
        if self.linear:
            self.comm('XP40S%d' % max(0, min(25, round(value / 0.05))))
        else:
            self.comm('XP40S%d' % max(0, min(25, round(value / 0.1))))
        return self.doReadIdlecurrent()
    def doReadMovecurrent(self):
        if self.linear:
            return 0.05 * float(self.comm('XP41R'))
        else:
            return 0.1 * float(self.comm('XP41R'))
    def doWriteMovecurrent(self, value):
        if self.linear:
            self.comm('XP41S%d' % max(0, min(25, round(value / 0.05))))
        else:
            self.comm('XP41S%d' % max(0, min(25, round(value / 0.1))))
        return self.doReadMovecurrent()
    def doReadRampcurrent(self):
        if self.linear:
            return 0.05 * float(self.comm('XP42R'))
        else:
            return 0.1 * float(self.comm('XP42R'))
    def doWriteRampcurrent(self, value):
        if self.linear:
            self.comm('XP42S%d' % max(0, min(25, round(value / 0.05))))
        else:
            self.comm('XP42S%d' % max(0, min(25, round(value / 0.1))))
        return self.doReadRampcurrent()

    def doRead(self, maxage=0):
        return float(self.comm('XP21R')) / (self.slope * self.microstep)
    @usermethod
    def store(self):
        return self.comm('SA')

    def _readSE(self):
        temp = self.comm('SE')
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
            self.comm('XMA')
        else:
            self.comm('XMD')
        return self.doReadPower()

    def doReadMicrostep(self):
        return int(self.comm('XP45R'))
    def doWriteMicrostep(self, value):
        self.comm('XP45S%d' % int(value))
        return self.doReadMicrostep()
    def doReadSpeed(self):
        return float(self.comm('XP14R')) / float(self.microstep * abs( self.slope ))
    def doWriteSpeed(self, value):
        f = max(0, min(40000, value * abs( self.slope ) * self.microstep))
        self.comm('XP14S%d' % int(f))
        return self.doReadSpeed()
    def doReadAccel(self):
        return float(self.comm('XP15R')) / float(self.microstep * abs( self.slope )) ** 2
    def doWriteAccel(self, value):
        f = max(4000, min(500000, 4000 * round((value * (abs(self.slope) * self.microstep) ** 2) / 4000)))
        self.comm('XP15S%d' % int(f))
        return self.doReadAccel()

    def doStart(self, pos):
        ''' go to a absolute stepperpostition'''
        pos = int(pos * self.slope * self.microstep) # use microsteps as well ???
        self.comm('XE%d' % pos)

    def doStop(self):
        ''' send the stop command '''
        for _i in range(5):
            if self.comm('XS') == '':
                return
        self.log.error(self, 'Stopping failed! no ACK!')

    def doSetPosition(self, newpos):
        ''' set current position to given value'''
        d = int(newpos * self.slope * self.microstep)
        self.comm('XP20S%d XP21S%d XP19S%d' % (d, d, d)) # set all counters

    def doStatus(self, maxage=0): #XXX
        sui = self.comm('SUI')[ ['X', 'Y', 'Z', 'W'].index(self.channel) ]
        t = self._readSE()
        sl = ['Overcurrent', 'Undervoltage', 'Overtemperature', 'Driver enabled',
            'Limit switch - active', 'Limit switch + active', 'stepping error',
            'Encoder error', 'Motor halted', 'referenced']
        s = ''

        if sui in ['+', '2']:
            s = s + 'Limit switch + active, '
        if sui in ['-', '2']:
            s = s + 'Limit switch - active, '

        for i in range(len(sl)):
            if (t & (1 << i)) >> i == 1:
                s = s + sl[i] + ', '
        if (t & 0x100) == 0:
            s = s + 'Motor moving, '
        if s:
            s = s[:-2]
        if (t & 0x100) == 0:
            return status.BUSY, s
        if (t & 0b1000111) != 0:
            return status.ERROR, s
        return status.OK, s




    def doWait(self):
        timeleft = 900
        while self.doStatus()[0] == status.BUSY:
            sleep(0.1)
            timeleft -= 0.1
            if timeleft <= 0:
                self.doStop()
                raise TimeoutError(self, " didn't stop within 900s, something is wrong!")
