#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

import threading
from time import sleep

import numpy as np

class Local_Taco_Exception(Exception):
    pass

import TacoDevice

# The TypeError will be thrown since the taco calls throw a string as exception
TacoDevice.Dev_Exception = Local_Taco_Exception

from nicos.core import Measurable, Param, Value, intrange, status, \
                       CommunicationError

# This is not a nicos.devices.taco.TacoDevice subclass because it needs to use
# the generic and outdated TacoDevice client library

class TofCounter(Measurable):

    parameters = {
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
        'tacodelay':      Param('Delay between retries', unit='s', default=0.1,
                                settable=True),
        'tacotries':      Param('Number of tries per TACO call', default=3,
                                type=intrange(1, 10), settable=True),
    }

    def _create_dev(self, devname):
        try:
            dev = TacoDevice.TacoDevice(devname)
            TacoDevice.dev_tcpudp(devname, 'tcp')
            TacoDevice.dev_timeout(devname, 10.0)
            return dev
        except Local_Taco_Exception, e:
            raise CommunicationError(self, 'Could not create device : %s (%s)'
                                     % (devname, str(e)))

    def _taco_guard(self, function, *args):
        self.__lock.acquire()
        try:
            return function(*args)
        except Local_Taco_Exception, e:
            if self.tacotries > 1:
                tries = self.tacotries - 1
                self.log.warning('TACO %s failed, retrying up to %d times' %
                                 (function.__name__, tries))
                while True:
                    sleep(self.tacodelay)
                    tries -= 1
                    try:
                        return function(*args)
                    except Local_Taco_Exception, e:
                        if tries == 0:
                            break  # and fall through to raise Comm...Error
            raise CommunicationError(self, 'TACO %s call failed : %s'
                                     % (function.__name__, str(e)))
        finally:
            self.__lock.release()

    def valueInfo(self):
        return Value('timer', unit='s', type='timer'), \
            Value('monitor', unit='cts', type='monitor'), \
            Value('total', unit='cts', type='counter')

    def presetInfo(self):
        return ['t', 'm']

    def doPreinit(self, mode):
        self.__lock = threading.Lock()
        self._nethost = 'toftofsrv.toftof.frm2'
        if mode != 'simulation':
            self._counter = self._create_dev('//%s/toftof/tof/tofhistcntr'
                                             % (self._nethost))
            self._timer = self._create_dev('//%s/toftof/tof/toftimer'
                                           % (self._nethost))
            self._monitor = self._create_dev('//%s/toftof/tof/tofmoncntr'
                                             % (self._nethost))

    def doSetPreset(self, **preset):
        if 't' in preset:
            self._taco_guard(self._monitor.EnableMaster, 0)
            self._taco_guard(self._timer.EnableMaster, 1)
            self._taco_guard(self._timer.SetPreselectionDouble, preset['t'])
        elif 'm' in preset:
            self._taco_guard(self._monitor.EnableMaster, 1)
            self._taco_guard(self._timer.EnableMaster, 0)
            self._taco_guard(self._monitor.SetPreselectionUlong, int(preset['m']))

    def doStart(self, **preset):
        # the deviceOn command on the server resets the delay time
        # store the value
        tmp = self.doReadDelay()
        self.doStop()
        # and reset the value back
        self.doWriteDelay(tmp)
        self.doSetPreset(**preset)
        self._taco_guard(self._counter.Start)
        self._taco_guard(self._timer.Start)
        self._taco_guard(self._monitor.Start)

    def doStop(self):
        self._taco_guard(self._counter.DevOn)
        self._taco_guard(self._timer.DevOn)
        self._taco_guard(self._monitor.DevOn)

    def doStatus(self, maxage=0):
        state = ''.join(map(chr, self._taco_guard(self._counter.DevStatus)))
        if state == 'counting':
            return status.BUSY, 'counting'
        elif state in ['init', 'unknown']:
            return status.OK, 'idle'
        else:
            return status.ERROR, state

    def doIsCompleted(self):
        # DevStatus "counting"
        return self._taco_guard(self._counter.DevStatus) != [99,111,117,110,
                                                             116,105,110,103]

    def doRead(self, maxage=0):
        arr = self._taco_guard(self._counter.ReadULongArray)
        return [self._taco_guard(self._timer.ReadDouble),
                                 self._taco_guard(self._monitor.ReadULong),
                                 sum(arr[2:])]

    def read_full(self):
        arr = np.array(self._taco_guard(self._counter.ReadULongArray))
        ndata = np.reshape(arr[2:], (arr[1], arr[0]))
        return self._taco_guard(self._timer.ReadDouble), \
                                self._taco_guard(self._monitor.ReadULong), \
                                ndata

    def doReset(self):
        self._taco_guard(self._counter.DevOn)
        self._taco_guard(self._timer.DevOn)
        self._taco_guard(self._monitor.DevOn)

    def doReadTimechannels(self):
        return self._taco_guard(self._counter.TimeChannels)

    def doWriteTimechannels(self, value):
        self._taco_guard(self._counter.SetTimeChannels, value)

    def doReadTimeinterval(self):
        return self._taco_guard(self._counter.TimeInterval)

    def doWriteTimeinterval(self, value):
        self._taco_guard(self._counter.SetTimeInterval, value)

    def doReadDelay(self):
        return self._taco_guard(self._counter.GetDelay)

    def doWriteDelay(self, value):
        self._taco_guard(self._counter.SetDelay, value)

    def doReadChannelwidth(self):
        return self._taco_guard(self._counter.ChannelWidth)

    def doReadNuminputs(self):
        return self._taco_guard(self._counter.NumInputs)
