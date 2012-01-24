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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF histogram counter card Taco devices."""

__version__ = "$Revision$"

import numpy as np

import TacoDevice

from nicos.core import Measurable, Param, Value, intrange, status


# This is not a nicos.taco.TacoDevice subclass because it needs to use the
# generic and outdated TacoDevice client library

class TofCounter(Measurable):

    parameters = {
        'timechannels':   Param('Number of time channels per detector channel',
                                type=intrange(1, 1025), settable=True,
                                default=1024),
        'timeinterval':   Param('Time interval between pulses', type=float,
                                settable=True),
        'delay':          Param('TOF frame delay', type=int,
                                settable=True),
        'monitorchannel': Param('Channel number of the monitor counter',
                                default=956,
                                type=intrange(1, 1025), settable=True),
        'channelwidth':   Param('Channel width', volatile=True),
        'numinputs':      Param('Number of detector channels', type=int,
                                volatile=True),
    }

    def _create_dev(self, devname):
        dev = TacoDevice.TacoDevice(devname)
        TacoDevice.dev_tcpudp(devname, 'tcp')
        TacoDevice.dev_timeout(devname, 10.0)
        return dev

    def valueInfo(self):
        return Value('timer', unit='s', type='timer'), \
            Value('monitor', unit='cts', type='monitor'), \
            Value('total', unit='cts', type='counter')

    def doPreinit(self):
        if self._mode != 'simulation':
            self._counter = self._create_dev('//toftofsrv/toftof/tof/tofhistcntr')
            self._timer = self._create_dev('//toftofsrv/toftof/tof/toftimer')
            self._monitor = self._create_dev('//toftofsrv/toftof/tof/tofmoncntr')

    def doSetPreset(self, **preset):
        if 't' in preset:
            self._monitor.EnableMaster(0)
            self._timer.EnableMaster(1)
            self._timer.SetPreselectionDouble(preset['t'])
        elif 'm' in preset:
            self._monitor.EnableMaster(1)
            self._timer.EnableMaster(0)
            self._monitor.SetPreselectionUlong(int(preset['m']))

    def doStart(self, **preset):
        self.doStop()
        self.doSetPreset(**preset)
        self._counter.Start()
        self._timer.Start()
        self._monitor.Start()

    def duringMeasureHook(self, i):
        #print self._timer.ReadDouble()
        pass
    
    def doStop(self):
        self._counter.DevOn()
        self._timer.DevOn()
        self._monitor.DevOn()

    def doStatus(self):
        state = ''.join(map(chr, self._counter.DevStatus()))
        if state == 'counting':
            return status.BUSY, 'counting'
        elif state in ['init', 'unknown']:
            return status.OK, 'idle'
        else:
            return status.ERROR, state

    def doIsCompleted(self):
        # DevStatus "counting"
        return self._counter.DevStatus() != [99,111,117,110,116,105,110,103]

    def doRead(self):
        arr = self._counter.ReadULongArray()
        return [self._timer.ReadDouble(), self._monitor.ReadULong(), sum(arr[2:])]

    def read_full(self):
        arr = np.array(self._counter.ReadULongArray())
        ndata = np.reshape(arr[2:], (arr[1], arr[0]))
        return self._timer.ReadDouble(), self._monitor.ReadULong(), ndata

    def doReset(self):
        self._counter.DevOn()
        self._timer.DevOn()
        self._monitor.DevOn()

    def doReadTimechannels(self):
        return self._counter.TimeChannels()

    def doWriteTimechannels(self, value):
        self._counter.SetTimeChannels(value)

    def doReadTimeinterval(self):
        return self._counter.TimeInterval()

    def doWriteTimeinterval(self, value):
        self._counter.SetTimeInterval(value)

    def doReadDelay(self):
        return self._counter.GetDelay()

    def doWriteDelay(self, value):
        self._counter.SetDelay(value)

    def doReadChannelwidth(self):
        return self._counter.ChannelWidth()

    def doReadNuminputs(self):
        return self._counter.NumInputs()
