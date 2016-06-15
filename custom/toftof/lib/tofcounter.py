#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF histogram counter card Taco devices."""

try:
    from SIS3400 import (Timer as SIS3400Timer,
                         MonitorCounter,  # pylint: disable=F0401
                         HistogramCounter)
except ImportError:
    SIS3400Timer = None
    MonitorCounter = None
    HistogramCounter = None

from nicos.core import ArrayDesc, Override, Param, Value, intrange, status
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel
from nicos.devices.taco.core import TacoDevice
from nicos.devices.taco.detector import FRMCounterChannel, FRMTimerChannel

import numpy as np


class Monitor(FRMCounterChannel):

    taco_class = MonitorCounter

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
    }

    parameters = {
        'monitorchannel': Param('Channel number of the monitor counter',
                                default=956,
                                type=intrange(1, 1024), settable=True,
                                ),
    }

    def doWriteMonitorchannel(self, chan):
        self._taco_guard(self._dev.setMonitorInput, chan)

    def doReadMonitorchannel(self):
        return self._taco_guard(self._dev.monitorInput)

    def doReset(self):
        self._taco_guard(self._dev.deviceOn)

#   def doClear(self):
#       self.doFinish()

    def doStop(self):
        if self.doStatus()[0] == status.BUSY:
            FRMCounterChannel.doStop(self)

    def doStatus(self, maxage=0):
        state = self._taco_guard(self._dev.deviceStatus)
        if state == 'counting':
            return status.BUSY, 'counting'
        elif state in ['init', 'unknown']:
            return status.OK, 'idle'
        else:
            return status.ERROR, state

    def doIsCompleted(self):
        return self.doRead(0)[0] >= self.preselection

    def doPrepare(self):
        self.doFinish()
        FRMCounterChannel.doPrepare(self)

    def valueInfo(self):
        return Value(self.name, unit=self.unit, type='monitor', fmtstr=self.fmtstr),


class Timer(FRMTimerChannel):

    taco_class = SIS3400Timer

    parameter_overrides = {
        'fmtstr': Override(default='%.1f'),
    }

    def doReset(self):
        if self._taco_guard(self._dev.deviceStatus) != 'init':
            self._taco_guard(self._dev.deviceOn)

    def doStop(self):
        if self.doStatus()[0] == status.BUSY:
            FRMTimerChannel.doStop(self)

    def doStatus(self, maxage=0):
        state = self._taco_guard(self._dev.deviceStatus)
        if state == 'counting':
            if self._taco_guard(self._dev.read) > 0:
                return status.BUSY, 'counting'  # counts down to zero
            return status.OK, 'idle'
        elif state in ['init', 'unknown']:
            return status.OK, 'idle'
        else:
            return status.ERROR, state

    def doRead(self, maxage=0):
        return self.preselection - FRMTimerChannel.doRead(self, maxage)[0]

    def doIsCompleted(self):
        return self.doRead(0) >= self.preselection

    def doPrepare(self):
        self.doFinish()
        self.preselection = 0
        FRMTimerChannel.doPrepare(self)

    def valueInfo(self):
        return Value(self.name, unit=self.unit, type='time', fmtstr=self.fmtstr),


class Image(ImageChannelMixin, TacoDevice, PassiveChannel):
    """The TOFTOF histogram counter card accessed via TACO."""

    taco_class = HistogramCounter
    _preselection = 0

    parameters = {
        'timechannels': Param('Number of time channels per detector channel',
                              type=intrange(1, 4096), settable=True,
                              default=1024, volatile=True,
                              ),
        'timeinterval': Param('Time interval between pulses',
                              type=float, settable=True, volatile=True,
                              ),
        'delay': Param('TOF frame delay',
                       type=int, settable=True,  # volatile=True,
                       ),
        'channelwidth': Param('Channel width',
                              volatile=True,
                              ),
        'numinputs': Param('Number of detector channels',
                           type=int, volatile=True,
                           ),
        'monitorchannel': Param('Channel number of the monitor counter',
                                default=956,
                                type=intrange(1, 1024), settable=True,
                                ),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
    }

    def doPreinit(self, mode):
        TacoDevice.doPreinit(self, mode)
        self.arraydesc = ArrayDesc('data', (self.numinputs, self.timechannels),
                                   np.uint32)

    def valueInfo(self):
        return Value(name='total', type='counter', fmtstr='%d'),

    def doStart(self):
        # the deviceOn command on the server resets the delay time
        # store the value and reset the value back
        # Don't remove the next line !!!
        self.delay = self.delay
        self._taco_guard(self._dev.start)

    def doStop(self):
        if self.doStatus()[0] == status.BUSY:
            self._taco_guard(self._dev.stop)

    def doStatus(self, maxage=0):
        state = self._taco_guard(self._dev.deviceStatus)
        if state == 'counting':
            return status.BUSY, 'counting'
        elif state in ['init', 'unknown']:
            return status.OK, 'idle'
        else:
            return status.ERROR, state

    def doRead(self, maxage=0):
        return self.readresult

    def doReset(self):
        self._taco_guard(self._dev.deviceOn)

    def doReadTimechannels(self):
        return self._taco_guard(self._dev.timeChannels)

    def doWriteTimechannels(self, value):
        self.doStop()
        self._taco_guard(self._dev.setTimeChannels, value)

    def doReadTimeinterval(self):
        return self._taco_guard(self._dev.timeInterval)

    def doWriteTimeinterval(self, value):
        self.doStop()
        self._taco_guard(self._dev.setTimeInterval, value)

    def doWriteDelay(self, value):
        self.doStop()
        self.log.debug('set counter delay : %d' % value)
        self._taco_guard(self._dev.setDelay, value)

    def doReadChannelwidth(self):
        return self._taco_guard(self._dev.channelWidth)

    def doReadNuminputs(self):
        return self._taco_guard(self._dev.numInputs)

    def doPrepare(self):
        self.doFinish()
        self._taco_guard(self._dev.clear)

    def _read_full(self):
        if self._sim_active:
            arr = np.zeros(2 + self.numinputs * self.timechannels, np.uint32)
            arr[0] = self.numinputs
            arr[1] = self.timechannels
        else:
            arr = np.array(self._taco_guard(self._dev.read))
        ndata = np.reshape(arr[2:], (arr[1], arr[0]))
        self.readresult = [ndata[2:self.monitorchannel].sum() +
                           ndata[self.monitorchannel + 1:].sum()]
        self.arraydesc = ArrayDesc(self.name, ndata.shape, np.uint32)
        return ndata

    def doReadArray(self, quality):
        counts = self._read_full()
        return counts
