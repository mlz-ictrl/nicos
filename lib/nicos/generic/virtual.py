#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

from nicos.core import status, tacodev, tupleof, nonemptylistof, anytype, \
     Readable, Moveable, HasOffset, Param, Override, PositionError
from nicos.abstract import Motor, Coder
from nicos.taco.detector import FRMTimerChannel, FRMCounterChannel


class VirtualMotor(Motor, HasOffset):
    """A virtual motor that can be set to move in finite time using a thread."""

    parameters = {
        'speed':     Param('Virtual speed of the device', settable=True),
        'jitter':    Param('Jitter of the read value', default=0),
        'curvalue':  Param('Current value', settable=True),
        'curstatus': Param('Current status', type=tupleof(int, str),
                           settable=True, default=(status.OK, 'idle')),
    }

    def doStart(self, pos):
        pos = float(pos) + self.offset
        self.curstatus = (status.BUSY, 'virtual moving')
        if self.speed != 0:
            thread = threading.Thread(target=self.__moving, args=(pos,))
            thread.setDaemon(True)
            thread.start()
        else:
            self.log.debug('moving to %s' % pos)
            self.curvalue = pos + self.jitter * (0.5 - random.random())
            self.curstatus = (status.OK, 'idle')

    def doRead(self):
        return self.curvalue - self.offset

    def doStatus(self):
        return self.curstatus

    def doWait(self):
        while self.curstatus[0] == status.BUSY:
            time.sleep(0.5)

    def doStop(self):
        self._stop = True

    def __moving(self, pos):
        self._stop = False
        incr = 0.2 * self.speed
        delta = pos - self.curvalue + self.offset
        steps = int(abs(delta) / incr)
        incr = delta < 0 and -incr or incr
        for _ in range(steps):
            if self._stop:
                self.log.debug('thread stopped')
                self.curstatus = (status.OK, 'idle')
                self._stop = False
                return
            time.sleep(0.2)
            self.log.debug('thread moving to %s' % (self.curvalue + incr))
            self.curvalue += incr
        self.curvalue = pos
        self.curstatus = (status.OK, 'idle')


class VirtualCoder(Coder, HasOffset):
    """A virtual coder that just returns the value of a motor, with offset."""

    attached_devices = {
        'motor': (Readable, 'Motor to read out to get coder value')
    }

    def doRead(self):
        val = self._adevs['motor'] and self._adevs['motor'].read(0) or 0
        return val - self.offset

    def doStatus(self):
        return status.OK, ''


class VirtualTimer(FRMTimerChannel):
    """A virtual timer channel for use together with `nicos.taco.Detector`."""

    parameters = {
        'tacodevice': Param('(not used)', type=tacodev, default=None),
    }

    def doInit(self):
        self.__finish = False

    def nothing(self):
        pass
    doPreinit = doPause = doResume = doStop = doReset = nothing

    def doStart(self):
        if self.ismaster:
            self.__finish = False
            threading.Thread(target=self.__thread).start()

    def doIsCompleted(self):
        return self.__finish

    def __thread(self):
        time.sleep(self.preselection)
        self.__finish = True

    def doStatus(self):
        return status.OK, ''

    def doRead(self):
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
    """A virtual counter channel for use together with `nicos.taco.Detector`."""

    parameters = {
        'countrate':  Param('The maximum countrate', default=1000),
        'tacodevice': Param('(not used)', type=tacodev, default=None),
    }

    def nothing(self):
        pass
    doPreinit = doInit = doStart = doPause = doResume = doStop = doWait = \
                doReset = nothing

    def doStatus(self):
        return status.OK, ''

    def doRead(self):
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
