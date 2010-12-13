#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   IPC hardware classes
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""IPC (Institut für Physikalische Chemie, Göttingen) hardware classes."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from time import sleep

from TACOClient import TACOError
from RS485Client import RS485Client

from nicm import status
from nicm.taco import TacoDevice
from nicm.coder import Coder as NicmCoder
from nicm.motor import Motor as NicmMotor
from nicm.utils import intrange, floatrange
from nicm.device import Device, Param
from nicm.errors import NicmError, CommunicationError


class ModBus(TacoDevice, Device):
    """IPC protocol communication bus over RS-485."""

    taco_class = RS485Client

    parameters = {
        'maxtries': Param('Number of tries for sending and receiving',
                          type=int, default=5, settable=True),
    }

    def send(self, addr, cmd, param=0, len=0):
        return self._taco_multitry('send', self.maxtries, self._dev.genSDA,
                                   addr, cmd-31, len, param)

    def get(self, addr, cmd, param=0, len=0):
        return self._taco_multitry('get', self.maxtries, self._dev.genSRD,
                                   addr, cmd-98, len, param)

    def ping(self, addr):
        return self._taco_multitry('ping', self.maxtries, self._dev.Ping, addr)


class Coder(NicmCoder):

    parameters = {
        'addr': Param('Bus address of the coder', type=int, mandatory=True),
        'confbyte': Param('Configuration byte of the coder', type=int),
    }

    attached_devices = {
        'bus': ModBus,
    }

    def doInit(self):
        bus = self._adevs['bus']
        self._adevs['bus'].ping(self.addr)
        confbyte = self.confbyte
        self._type = self._getcodertype(confbyte)
        self._resolution = confbyte & 31

    def doReadConfbyte(self):
        return self._adevs['bus'].get(self.addr, 152)

    def _getcodertype(self, byte):
        """Extract coder type from configuration byte."""
        if byte & 32 and byte & 64:
            return 'ssi-nopar'
        if byte & 32:
            return 'potentiometer'
        if byte & 64:
            outstring1 = 'gray'
        else:
            outstring1 = 'binary'
        if byte & 128:
            outstring2 = 'endat'
        else:
            outstring2 = 'ssi'
        return outstring1 + '-' + outstring2

    def doReset(self):
        self._adevs['bus'].send(self.addr, 153)
        sleep(0.5)

    def doRead(self):
        bus = self._adevs['bus']
        try:
            return bus.get(self.addr, 150)
        except Exception:
            if self._type == 'binary-endat':
                self._endatclearalarm()
            sleep(1)
        # try again
        return bus.get(self.addr, 150)

    def doSetPosition(self, target):
        raise NicmError('setPosition not implemented for IPC coders')

    def _endatclearalarm(self):
        """Clear alarm for a binary-endat encoder."""
        if self._type != 'binary-endat':
            return
        bus = self._adevs['bus']
        try:
            bus.send(self.addr, 155, 185, 3)
            sleep(0.5)
            bus.send(self.addr, 157, 0, 3)
            sleep(0.5)
            self.doReset()
        except Exception:
            # XXX pass-through exception point
            raise CommunicationError(self, 'cannot clear alarm for encoder')


class Motor(NicmMotor):

    parameters = {
        'addr': Param('Bus address of the motor', type=int, mandatory=True),
        'timeout': Param('Waiting timeout', type=int, unit='s', default=360),
        'unit': Param('Motor unit', type=str, default='steps'),
        # XXX those come from the card, make them settable
        'speed': Param('Motor speed (0..255)', type=intrange(0, 256)),
        'accel': Param('Motor acceleration (0..255)', type=intrange(0, 256)),
        'confbyte': Param('Configuration byte', type=int),
        'ramptype': Param('Ramp type', type=intrange(1, 5)),
        'halfstep': Param('Halfstep mode', type=bool),
        'min': Param('Lower motorlimit', type=intrange(0, 1000000), unit='main'),
        'max': Param('Upper motorlimit', type=intrange(0, 1000000), unit='main'),
        'firmware': Param('Firmware version', type=int),
        'startdelay': Param('Start delay', type=floatrange(0, 25), unit='s'),
        'stopdelay': Param('Stop delay', type=floatrange(0, 25), unit='s'),
    }

    attached_devices = {
        'bus': ModBus,
    }

    def doInit(self):
        pass

    def _setMode(self, mode):
        NicmMotor._setMode(self, mode)
        if mode == 'master':
            self.usermin = self.min
            self.usermax = self.max

    def doReadSpeed(self):
        return self._adevs['bus'].get(self.addr, 128)

    def doReadAccel(self):
        return self._adevs['bus'].get(self.addr, 129)

    def doReadMax(self):
        return self._adevs['bus'].get(self.addr, 131)

    def doReadMin(self):
        return self._adevs['bus'].get(self.addr, 132)

    def doReadStepsize(self):
        return bool(self._adevs['bus'].get(self.addr, 134) & 4)

    def doReadConfbyte(self):
        return self._adevs['bus'].get(self.addr, 135)

    def doReadRamptype(self):
        return self._adevs['bus'].get(self.addr, 136)

    def doReadFirmware(self):
        return self._adevs['bus'].get(self.addr, 137)

    def doReadStartdelay(self):
        if self.firmware > 40:
            return self._adevs['bus'].get(self.addr, 139) / 10.0
        else:
            return 0

    def doReadStopdelay(self):
        if self.firmware > 44:
            return self._adevs['bus'].get(self.addr, 143) / 10.0
        else:
            return 0

    def doStart(self, target):
        bus = self._adevs['bus']
        self.doWait()
        pos = self.doRead()
        diff = target - pos
        if diff == 0:
            return
        elif diff < 0:
            bus.send(self.addr, 35)
        else:
            bus.send(self.addr, 34)
        bus.send(self.addr, 46, abs(diff), 6)

    def doReset(self):
        bus = self._adevs['bus']
        bus.send(self.addr, 33)  # stop
        # remember current state
        actpos = bus.get(self.addr, 130)
        speed = bus.get(self.addr, 128)
        accel = bus.get(self.addr, 129)
        min = bus.get(self.addr, 132)
        max = bus.get(self.addr, 131)
        bus.send(self.addr, 31)  # reset card
        sleep(0.2)
        # update state
        bus.send(self.addr, 41, speed, 3)
        bus.send(self.addr, 42, accel, 3)
        bus.send(self.addr, 45, min, 6)
        bus.send(self.addr, 44, max, 6)
        bus.send(self.addr, 43, actpos, 6)

    def doWait(self):
        timeleft = self.timeout
        sleep(0.5)
        while self.doStatus() in [1, 3]:
            sleep(0.5)
            timeleft -= 0.5
            if timeleft <= 0:
                self.doStop()

    def doStop(self):
        self._adevs['bus'].send(self.addr, 52)
        sleep(0.5)

    def doRead(self):
        return self._adevs['bus'].get(self.addr, 130)

    def doStatus(self):
        bus = self._adevs['bus']
        state = bus.get(self.addr, 134)

        if state & 15360:
            msg = ''
            if state & 4096:
                msg += ', overheat SMS device'
            if state & 2048:
                msg += ', motor power below 20V'
            if state & 1024:
                msg += ', motor not connected or leads broken'
            if state & 8192:
                msg += ', hardware failure or device not reset after power-on'
            return status.ERROR, msg[2:]

        if state & 32 and state & 64:
            return status.ERROR, 'both limit switches active, check connections'

        if state & 1:
            return status.BUSY, 'moving'
        if state & 32768:
            return status.NOTREACHED, 'waiting for start/stopdelay'

        return status.OK, 'idle'

    def do
