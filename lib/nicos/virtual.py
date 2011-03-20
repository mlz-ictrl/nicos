#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
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
# *****************************************************************************

"""Virtual devices for testing."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time
import random
import threading

from nicos import status
from nicos.utils import tacodev
from nicos.device import Readable, HasOffset, Param
from nicos.abstract import Motor, Coder
from nicos.detector import FRMTimerChannel, FRMCounterChannel


class VirtualMotor(Motor, HasOffset):
    parameters = {
        'initval': Param('Initial value for the virtual device', mandatory=True),
        'speed':   Param('Virtual speed of the device'),
        'jitter':  Param('Jitter of the read value', default=0),
    }

    def doInit(self):
        self.__val = self.initval
        self.__busy = False

    def doStart(self, pos):
        pos = float(pos) + self.offset
        self.__busy = True
        if self.speed != 0:
            thread = threading.Thread(target=self.__moving, args=(pos,))
            thread.start()
        else:
            self.printdebug('moving to %s' % pos)
            self.__val = pos + self.jitter * (0.5 - random.random())
            self.__busy = False

    def doRead(self):
        return self.__val - self.offset

    def doStatus(self):
        if self.__busy:
            return (status.BUSY, 'moving')
        return (status.OK, 'idle')

    def __moving(self, pos):
        incr = self.speed
        delta = pos - self.doRead()
        steps = int(abs(delta) / incr)
        incr = delta < 0 and -incr or incr
        for i in range(steps):
            time.sleep(0.1)
            self.printdebug('thread moving to %s' % (self.__val + incr))
            self.__val += incr
        self.__val = pos
        self.__busy = False


class VirtualCoder(Coder, HasOffset):
    attached_devices = {
        'motor': Readable,
    }

    def doRead(self):
        val = self._adevs['motor'] and self._adevs['motor'].doRead() or 0
        return val - self.offset

    def doStatus(self):
        return (status.OK, 'idle')


class VirtualTimer(FRMTimerChannel):
    parameters = {
        'tacodevice': Param('(not used)', type=tacodev),
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
        return (status.OK, 'idle')

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
    parameters = {
        'countrate':  Param('The maximum countrate', default=1000),
        'tacodevice': Param('(not used)', type=tacodev),
    }

    def nothing(self):
        pass
    doPreinit = doInit = doStart = doPause = doResume = doStop = doWait = \
                doReset = nothing

    def doStatus(self):
        return (status.OK, 'idle')

    def doRead(self):
        if self.ismaster:
            return self.preselection
        return random.randint(0, self.countrate)

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
