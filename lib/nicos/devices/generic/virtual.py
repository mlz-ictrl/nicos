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
from os import path
from math import exp

import numpy as np

from nicos import session
from nicos.core import status, Readable, HasOffset, Param, Override, tacodev, \
     tupleof, floatrange, Measurable, Moveable, Value
from nicos.devices.abstract import Motor, Coder, ImageStorage
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

    def _step(self, start, end, elapsed, speed):
        delta = end - start
        sign = +1 if delta > 0 else -1
        value = start + sign * speed * elapsed
        if (sign == 1 and value >= end) or (sign == -1 and value <= end):
            return end
        return value

    def __moving(self, pos):
        speed = self.speed
        try:
            self._stop = False
            start = self.curvalue
            started = time.time()
            while 1:
                value = self._step(start, pos, time.time() - started, speed)
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

    def _step(self, start, end, elapsed, speed):
        # calculate an exponential approximation to the setpoint with a time
        # constant given by self.speed
        gamma = speed / 10.
        cval = end + (start - end) * exp(-gamma*elapsed)
        if abs(cval - end) < self.jitter:
            return end
        return cval


class Virtual2DDetector(ImageStorage, Measurable):

    attached_devices = {
        'spotsize':   (Moveable, 'determines the virtual spot size'),
    }

    def doInit(self, mode):
        self._lastcounts = 0

    def doStart(self, **preset):
        self._newFile()
        array = self._generate().astype('<I4')
        buf = buffer(array)
        session.updateLiveData('', self.lastfilename, '<I4', 128, 128, 1, 1, buf)
        self._lastcounts = long(array.sum())
        self._writeFile(buf)

    def doStop(self):
        pass

    def doRead(self, maxage=0):
        return [self._lastcounts, path.abspath(self.lastfilename)]

    def valueInfo(self):
        return (Value(self.name + '.sum', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'),
                Value(self.name + '.file', type='info', fmtstr='%s'))

    def doIsCompleted(self):
        return True

    def _generate(self):
        spotsize = self._adevs['spotsize'].read()
        xx, yy = np.meshgrid(np.linspace(-64, 63, 128), np.linspace(-64, 63, 128))
        return 10000 * np.exp(-xx**2 * spotsize**2/1000) * np.exp(-yy**2 * spotsize**2/1000)
