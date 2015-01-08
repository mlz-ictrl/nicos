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
"""Nicos support module for controlling servos via a micropython board

NOT INTENDED TO BE USED AT THE INSTRUMENT!

servos are too small and inaccurate to be used at the instrument,
but are quite handy for shows
"""

import time
import threading

from nicos import session
from nicos.core import Param, Override, intrange, floatrange, status, \
    HasOffset, Device, Attach, SIMULATION
from nicos.utils import createThread
from nicos.devices.abstract import Motor

import serial


CRLF = '\r\n'

class SerComIO(Device):
    parameters = {
        'devfile'      : Param('name of device file', type=str,
                               default='/dev/ttyACM0'),
        'pollinterval' : Param('pollinterval for registered super devices',
                               type=floatrange(0.01,10), default=1.,
                               settable=True),
    }

    _dev = None
    _lock = None
    _polls = []
    _thread = None

    def _poller(self):
        """mini-poller thread

        polls the devices recorded in self._polls every second.
        may be started by addPollDev and finishes if no more work to be done
        """
        while self._dev:
            time.sleep(self.pollinterval)
            for d in self._polls:
                d.poll()

    def doInit(self, mode):
        if mode != SIMULATION:
            if session.sessiontype != 'poller':
                for d in [self.devfile, '/dev/ttyACM0', '/dev/ttyACM1']:
                    try:
                        self._dev = serial.Serial(d, timeout=0.03)
                        break
                    except Exception:
                        pass
                self._lock = threading.RLock()
                self._dev.write(' ' + CRLF + CRLF) # init sequence
                self._dev.readall()

    def communicate(self, cmd):
        with self._lock:
            self.log.debug('cmd: %r' % cmd)
            self._dev.write(cmd + CRLF)
            res = [l.strip() for l in self._dev.read(10000).splitlines()]
            res = [l for l in res if l if l != ">>>"]
            res = res[-1] if res else ''
            self.log.debug('got: %r' % res)
            return res

    def doShutdown(self):
        while self._polls:
            self.delPollDev(self._polls[0])
        self._dev.close()
        self._dev = None

    def addPollDev(self, device):
        """adds a device to our simplified polling loop

        also starts the polling thread, if necessary
        """
        if self._polls:
            if device not in self._polls:
                self._polls.append(device)
        else:
            self._polls = [device]
            if (self._thread is None) or not(self._thread.isAlive()):
                self._thread = createThread('servo poller', self._poller)

    def delPollDev(self, device):
        """removes a device from our mini-poller

        may also stop the mini-poller
        """
        if device in self._polls:
            self._polls.remove(device)


class MicroPythonServo(HasOffset, Motor):
    attached_devices = {
        'io' : Attach('Comm device', SerComIO),
    }
    parameters = {
        'channel' : Param('Channel (1..4)', type=intrange(1,4), default=1),
    }
    parameter_overrides = {
        'precision' : Override(default=1),
        'fmtstr'    : Override(default='%d'),
    }

    _busytime = 0

    def doInit(self, mode):
        if mode != SIMULATION:
            io = self._adevs['io']
            io.communicate('import pyb')
            io.communicate('s%d=pyb.Servo(%d)' % (self.channel, self.channel))
            io.communicate('s%d.calibration(600,2400,1500,2400,2400)' % self.channel)
            io.communicate('s%d.angle(%f)' %(self.channel, self.target or 0.0))
            io.addPollDev(self)

    def doRead(self, maxage=None):
        return float(self._adevs['io'].communicate('s%d.angle()' % self.channel)) - self.offset

    def doStart(self, target):
        duration = abs(self.read(0) - target) / self.speed
        target = target + self.offset
        cmd = ("s%d.angle(%f,%d)" %
            (self.channel, target, int(duration * 1000)))
        self.log.debug(cmd)
        self._adevs['io'].communicate(cmd)
        self._busytime = time.time() + duration

    def doStatus(self, maxage=None):
        if time.time() < self._busytime:
            return status.BUSY, ''
        return status.OK, ''

    def doShutdown(self):
        self._adevs['io'].delPollDev(self)
