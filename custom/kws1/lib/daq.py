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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

from time import sleep

import numpy as np

from nicos.core import status, Moveable, Value, Param, Attach, oneof, \
    listof, intrange, ConfigurationError, ImageType, SIMULATION
from nicos.devices.generic.detector import ImageChannelMixin, ActiveChannel, \
    Detector
from nicos.jcns.fpga import FPGAChannelBase

import TacoDevice


RTMODES = ('standard', 'tof', 'realtime', 'realtime_external')
PIXELS = 128


class JDaqChannel(ImageChannelMixin, ActiveChannel):

    attached_devices = {
        'rtswitch':    Attach('SPS switch for realtime mode', Moveable),
    }

    parameters = {
        'tacodevice':  Param('Old TACO device name', type=str),
        'mode':        Param('Measurement mode switch', type=oneof(*RTMODES),
                             settable=True),
        'slices':      Param('Calculated TOF slices', userparam=False,
                             unit='us', settable=True, type=listof(int)),
    }

    def doPreinit(self, mode):
        if mode != SIMULATION:
            self._dev = TacoDevice.TacoDevice(self.tacodevice)
            self._dev.DevJudidt2Init()

    def _configure(self, tofsettings):
        self._dev.DevJudidt2Init()
        value = self.mode
        if value == 'standard':
            self._setup_standard()
        elif value == 'tof':
            self._setup_tof(False, tofsettings)
        elif value == 'realtime':
            self._setup_tof(False, tofsettings)
        elif value == 'realtime_external':
            self._setup_tof(True, tofsettings)

    def _setup_standard(self):
        self._dev.DevJudidt2SetMode(0)
        self.slices = []
        self.imagetype = ImageType((PIXELS, PIXELS), np.uint32)

    def _setup_tof(self, ext_trigger, tofsettings):
        if ext_trigger:
            self._dev.DevJudidt2SetMode(2)
            # number of external signal, != 1 not supported
            self._dev.DevJudidt2SetRtParam(1)
        else:
            self._dev.DevJudidt2SetMode(1)
        # set timing of TOF slices
        nslices, interval, q = tofsettings
        times = [0]
        for i in range(nslices - 1):
            times.append(times[-1] + int(interval * q**i))
        self.slices = times
        times = [nslices] + times
        self._dev.DevJudidt2SetTofParam(times)
        self.imagetype = ImageType((PIXELS, PIXELS, nslices), np.uint32)

    def doPrepare(self):
        self._dev.DevJudidt2ClrRecoHistoAll()

    def doStart(self):
        self.readresult = [0]
        self._dev.DevJudidt2Start()
        if self.mode == 'realtime_external':
            self.log.debug('triggering RT start')
            self._attached_rtswitch.move(1)
            sleep(1)
            self._attached_rtswitch.move(0)

    def doPause(self):
        self._dev.DevJudidt2Stop()

    def doResume(self):
        self._dev.DevJudidt2Start()

    def doFinish(self):
        self._dev.DevJudidt2Stop()

    def doStop(self):
        self.doFinish()

    def doStatus(self, maxage=0):
        if self._dev.DevJudidt2GetStatus()[-1] == 1:
            return status.BUSY, 'counting'
        return status.OK, 'idle'

    def valueInfo(self):
        return (Value(name='total', type='counter', fmtstr='%d'),)

    def readLiveImage(self):
        # update the total counter
        self.readresult = [self._dev.DevJudidt2GetStatus()[1]]
        return None  # different live view is used

    def readFinalImage(self):
        if self.mode == 'standard':
            array = self._dev.DevJudidt2GetRecoHistoSlot(0)
        else:
            array = self._dev.DevJudidt2GetRecoHistoAll()
        arr = np.array(array, np.uint32)
        shape = self.imagetype.shape
        if self.mode != 'standard':
            arr = arr[:shape[0]*shape[1]*shape[2]]
        arr = arr.reshape(shape)
        self.readresult = [arr.sum()]
        return arr


class KWSDetector(Detector):

    attached_devices = {
        'shutter':     Attach('Shutter for opening and closing', Moveable),
    }

    parameters = {
        'mode':        Param('Measurement mode switch', type=oneof(*RTMODES),
                             settable=True),
        'tofslices':   Param('Number of TOF timeslices',
                             type=intrange(1, 1023), settable=True),
        'tofinterval': Param('Interval dt between TOF channels', type=int,
                             unit='us', settable=True),
        'tofprog':     Param('Progression q of TOF intervals (t_i = dt * q^i)',
                             type=float, default=1.0, settable=True),
    }

    def doInit(self, session_mode):
        if not self._attached_images or \
           not isinstance(self._attached_images[0], JDaqChannel):
            raise ConfigurationError(self, 'KWSDetector needs a JDaqChannel '
                                     'as attached image')
        self._jdaq = self._attached_images[0]

    def doWriteMode(self, mode):
        self._jdaq.mode = mode

    def doPrepare(self):
        for ch in self._channels:
            if isinstance(ch, FPGAChannelBase):
                ch.extmode = self.mode == 'realtime_external'
        # TODO: ensure that total meas. time < 2**31 usec
        self._jdaq._configure((self.tofslices,
                               self.tofinterval,
                               self.tofprog))
        Detector.doPrepare(self)

    def doStart(self):
        self._attached_shutter.maw('open')
        Detector.doStart(self)

    def doFinish(self):
        Detector.doFinish(self)
        self._attached_shutter.maw('closed')

    def doStop(self):
        Detector.doStop(self)
        self._attached_shutter.maw('closed')
