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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF histogram counter card Taco devices."""

import numpy as np

from SIS3400 import (Timer, MonitorCounter,  # pylint: disable=F0401
                     HistogramCounter)
import TACOStates

from nicos.core import Measurable, Param, Value, intrange, status, tacodev
from nicos.devices.taco.core import TacoDevice
from nicos.core import SIMULATION


class TofCounter(TacoDevice, Measurable):
    """The TOFTOF histogram counter card accessed via TACO."""

    taco_class = HistogramCounter

    parameters = {
        'monitor':        Param('Monitor device',
                                type=tacodev, mandatory=True, preinit=True),
        'timer':          Param('Timer device',
                                type=tacodev, mandatory=True, preinit=True),
        'timechannels':   Param('Number of time channels per detector channel',
                                type=intrange(1, 4096), settable=True,
                                default=1024, volatile=True,),
        'timeinterval':   Param('Time interval between pulses', type=float,
                                settable=True, volatile=True,),
        'delay':          Param('TOF frame delay', type=int,
                                settable=True, volatile=True,),
        'monitorchannel': Param('Channel number of the monitor counter',
                                default=956,
                                type=intrange(1, 1024), settable=True,),
        'channelwidth':   Param('Channel width', volatile=True),
        'numinputs':      Param('Number of detector channels', type=int,
                                volatile=True),
    }

    def valueInfo(self):
        return Value('timer', unit='s', type='timer'), \
            Value('monitor', unit='cts', type='monitor'), \
            Value('total', unit='cts', type='counter')

    def presetInfo(self):
        return ['t', 'm']

    def doPreinit(self, mode):
        TacoDevice.doPreinit(self, mode)
        if mode != SIMULATION:
            self._timer = self._create_client(devname=self.timer,
                                              class_=Timer,
                                              resetok=False,
                                              timeout=None)
            self._monitor = self._create_client(devname=self.monitor,
                                                class_=MonitorCounter,
                                                resetok=False,
                                                timeout=None)

    def doShutdown(self):
        if self._monitor:
            self._monitor.disconnectClient()
            del self._monitor
        if self._timer:
            self._timer.disconnectClient()
            del self._timer
        TacoDevice.doShutdown(self)

    def doSetPreset(self, **preset):
        self.doStop()
        if 't' in preset:
            self._taco_guard(self._monitor.enableMaster, 0)
            self._taco_guard(self._timer.enableMaster, 1)
            self._taco_guard(self._timer.setPreselection, preset['t'])
        elif 'm' in preset:
            self._taco_guard(self._monitor.enableMaster, 1)
            self._taco_guard(self._timer.enableMaster, 0)
            self._taco_guard(self._monitor.setPreselection, int(preset['m']))

    def doStart(self):
        self.doStop()
        # the deviceOn command on the server resets the delay time
        # store the value
        tmp = self.doReadDelay()
        # and reset the value back
        self.doWriteDelay(tmp)
        self._taco_guard(self._dev.start)
        self._taco_guard(self._timer.start)
        self._taco_guard(self._monitor.start)

    def doStop(self):
        self._taco_guard(self._dev.deviceOn)
        self._taco_guard(self._timer.deviceOn)
        self._taco_guard(self._monitor.deviceOn)

    def doStatus(self, maxage=0):
        state = self._taco_guard(self._dev.deviceStatus)
        if state == 'counting':
            return status.BUSY, 'counting'
        elif state in ['init', 'unknown']:
            return status.OK, 'idle'
        else:
            return status.ERROR, state

    def doIsCompleted(self):
        return self._taco_guard(self._dev.deviceState) != TACOStates.COUNTING

    def doRead(self, maxage=0):
        arr = self._taco_guard(self._dev.read)
        return [self._taco_guard(self._timer.read),
                self._taco_guard(self._monitor.read),
                sum(arr[2:])]

    def read_full(self):
        arr = np.array(self._taco_guard(self._dev.read))
        ndata = np.reshape(arr[2:], (arr[1], arr[0]))
        return self._taco_guard(self._timer.read), \
            self._taco_guard(self._monitor.read), ndata

    def doReset(self):
        self._taco_guard(self._dev.deviceOn)
        self._taco_guard(self._timer.deviceOn)
        self._taco_guard(self._monitor.deviceOn)

    def doReadTimechannels(self):
        return self._taco_guard(self._dev.timeChannels)

    def doWriteTimechannels(self, value):
        self._taco_guard(self._dev.setTimeChannels, value)

    def doReadTimeinterval(self):
        return self._taco_guard(self._dev.timeInterval)

    def doWriteTimeinterval(self, value):
        self._taco_guard(self._dev.setTimeInterval, value)

    def doReadDelay(self):
        return self._taco_guard(self._dev.getDelay)

    def doWriteDelay(self, value):
        self._taco_guard(self._dev.setDelay, value)

    def doReadChannelwidth(self):
        return self._taco_guard(self._dev.channelWidth)

    def doReadNuminputs(self):
        return self._taco_guard(self._dev.numInputs)
