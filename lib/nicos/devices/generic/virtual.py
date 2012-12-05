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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Virtual devices for testing."""

__version__ = "$Revision$"

import time
import random
import threading
from math import exp

from nicos.core import status, Readable, HasOffset, Param, Override, tacodev, \
     tupleof, floatrange
from nicos.devices.abstract import Motor, Coder
from nicos.devices.taco.detector import FRMTimerChannel, FRMCounterChannel


class VirtualMotor(Motor, HasOffset):
    """A virtual motor that can be set to move in finite time using a thread."""

    parameters = {
        'speed':     Param('Virtual speed of the device', settable=True,
                           type=floatrange(0, 1e6)),
        'jitter':    Param('Jitter of the read value', default=0),
        'curvalue':  Param('Current value', settable=True),
        'curstatus': Param('Current status', type=tupleof(int, str),
                           settable=True, default=(status.OK, 'idle')),
    }

    _thread = None

    def doStart(self, pos):
        pos = float(pos) + self.offset
        if self.speed != 0:
            if self._thread:
                self.stop()
                self._thread.join()
            self.curstatus = (status.BUSY, 'virtual moving')
            self._thread = threading.Thread(target=self.__moving, args=(pos,),
                                            name='virtual motor %s' % self)
            self._thread.setDaemon(True)
            self._thread.start()
        else:
            self.curstatus = (status.BUSY, 'virtual moving')
            self.log.debug('moving to %s' % pos)
            self.curvalue = pos
            self.curstatus = (status.OK, 'idle')

    def doRead(self, maxage=0):
        return (self.curvalue - self.offset) + \
            self.jitter * (0.5 - random.random())

    def doStatus(self, maxage=0):
        return self.curstatus

    def doWait(self):
        while self.curstatus[0] == status.BUSY:
            time.sleep(0.1)

    def doStop(self):
        if self.speed != 0 and \
           self._thread is not None and self._thread.isAlive():
            self._stop = True
        else:
            self.curstatus = (status.OK, 'idle')

    def doSetPosition(self, pos):
        self.curvalue = pos + self.offset

    def _step(self, start, end, elapsed):
        delta = end - start
        sign = +1 if delta > 0 else -1
        value = start + sign * self.speed * elapsed
        vdelta = value - start
        if abs(vdelta) > abs(delta):
            return end
        return value

    def __moving(self, pos):
        try:
            self._stop = False
            start = self.curvalue
            started = time.time()
            while 1:
                value = self._step(start, pos, time.time() - started)
                if self._stop:
                    self.log.debug('thread stopped')
                    return
                time.sleep(0.2)
                self.log.debug('thread moving to %s' % value)
                self.curvalue = value
                if value == pos:
                    return
        finally:
            self._stop = False
            self.curstatus = (status.OK, 'idle')
            self._thread = None


class VirtualCoder(Coder, HasOffset):
    """A virtual coder that just returns the value of a motor, with offset."""

    attached_devices = {
        'motor': (Readable, 'Motor to read out to get coder value')
    }

    def doRead(self, maxage=0):
        val = self._adevs['motor'] and self._adevs['motor'].read(maxage) or 0
        return val - self.offset

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doSetPosition(self, _pos):
        pass


class VirtualTimer(FRMTimerChannel):
    """A virtual timer channel for use together with `nicos.devices.taco.Detector`."""

    parameters = {
        'tacodevice': Param('(not used)', type=tacodev, default=None),
    }

    def doInit(self, mode):
        self.__finish = False

    def nothing(self, *args):
        pass
    doPreinit = doPause = doResume = doReset = nothing

    def doStart(self):
        if self.ismaster:
            self.__finish = False
            thr = threading.Thread(target=self.__thread,
                                   name='virtual timer %s' % self)
            thr.setDaemon(True)
            thr.start()

    def doIsCompleted(self):
        return self.__finish

    def __thread(self):
        finish_at = time.time() + self.preselection
        while time.time() < finish_at and not self.__finish:
            time.sleep(0.1)
        self.__finish = True

    def doStop(self):
        self.__finish = True

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doRead(self, maxage=0):
        if self.ismaster:
            return self.preselection
        return random.randint(0, 1000)

    def doReadPreselection(self):
        return 0

    def doReadIsmaster(self):
        return False

    def doReadMode(self):
        return 0

    def doWritePreselection(self, value):
        pass

    def doWriteIsmaster(self, value):
        pass

    def doWriteMode(self, value):
        pass

    def doReadUnit(self):
        return 'sec'


class VirtualCounter(FRMCounterChannel):
    """A virtual counter channel for use together with `nicos.devices.taco.Detector`."""

    parameters = {
        'countrate':  Param('The maximum countrate', default=1000),
        'tacodevice': Param('(not used)', type=tacodev, default=None),
    }

    def nothing(self, *args):
        pass
    doPreinit = doInit = doStart = doPause = doResume = doStop = doWait = \
                doReset = nothing

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doRead(self, maxage=0):
        if self.ismaster:
            return self.preselection
        return random.randint(0, self.countrate)

    def doIsCompleted(self):
        return True

    def doReadPreselection(self):
        return 0

    def doReadIsmaster(self):
        return False

    def doReadMode(self):
        return 0

    def doWritePreselection(self, value):
        pass

    def doWriteIsmaster(self, value):
        pass

    def doWriteMode(self, value):
        pass

    def doReadUnit(self):
        return 'counts'


class VirtualTemperature(VirtualMotor):
    """A virtual temperature regulation device."""

    parameters = {
        'tolerance': Param('Tolerance for wait()', default=1, settable=True,
                           unit='main', category='general'),
        'setpoint':  Param('Last setpoint', settable=True, unit='main',
                           category='general'),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False, default='K'),
        'jitter':    Override(default=0.1),
    }

    def doStart(self, pos):
        self.setpoint = pos
        VirtualMotor.doStart(self, pos)

    def doWait(self):
        while self.curstatus[0] == status.BUSY:
            if abs(self.read(0) - self.setpoint) < self.tolerance:
                break
            time.sleep(0.1)

    def _step(self, start, end, elapsed):
        # calculate an exponential approximation to the setpoint with a time
        # constant given by self.speed
        gamma = self.speed/10
        cval = end + (start - end) * exp(-gamma*elapsed)
        if abs(cval - end) < self.jitter:
            return end
        return cval
