#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""Classes to access to the DSpec detector."""

from time import time as currenttime

from nicos import session
from nicos.core import Measurable, Param, Value, status, usermethod
from nicos.core.errors import NicosError
from nicos.devices.tango import PyTangoDevice


class DSPec(PyTangoDevice, Measurable):

    parameters = {
        'prefix': Param('prefix for filesaving',
                        type=str, settable=False, mandatory=True),
    }

    # XXX: issues with ortec API -> workarounds and only truetime and livetime
    # working.

    @usermethod
    def getvals(self):
        spectrum = None
        try:
            spectrum = [int(i) for i in self._dev.Value.tolist()]
        except NicosError:
            # self._comment += 'CACHED'
            if self._read_cache is not None:
                self.log.warning('using cached spectrum')
                spectrum = [int(i) for i in self._read_cache.tolist()]
            else:
                self.log.warning('no spectrum cached')
        return spectrum

    @usermethod
    def getEcal(self):
        return str(self._dev.EnergyCalibration)

    @usermethod
    def getlive(self):
        return self._dev.LiveTime[0]

    @usermethod
    def getpoll(self):
        return self._dev.PollTime[0]

    @usermethod
    def gettrue(self):
        return self._dev.TrueTime[0]

    @usermethod
    def initdev(self):
        self._dev.Init()

    @usermethod
    def getstate(self):
        return self._dev.Status()

    @usermethod
    def savefile(self):
        self.doFinish()

    @usermethod
    def resetvals(self):
        self._started = None
        self._lastread = 0
        self._comment = ''
        self._name = ''
        self._stop = None
        self._preset = {}
        self._dont_stop_flag = False
        self._read_cache = None

    def doInit(self, mode):
        self._started = None
        self._lastread = 0
        self._comment = ''
        self._name = ''
        self._stop = None
        self._preset = {}
        self._dont_stop_flag = False
        self._read_cache = None

    def doReadIsmaster(self):
        pass

    def doRead(self, maxage=0):
        return self._dev.Value.tolist()

    # def doSetPreset(self, **preset):
    #     if not preset:
    #         return  # keep previous settings
    #     self._lastpreset = preset

    def doSetPreset(self, **preset):
        self._started = None
        self._lastread = None
        self._read_cache = None
        self._dont_stop_flag = False
        self._comment = ''
        self._name = ''
        self._stop = None
        self._preset = preset

        if preset['cond'] == 'TrueTime':
            try:
                self._dev.SyncMode = 'RealTime'
                self._dev.SyncValue = preset['value'] * 1000
            except NicosError:
                try:
                    self.doStop()
                    self._dev.Init()
                except NicosError:
                    return
                self._dev.SyncMode = 'RealTime'
                self._dev.SyncValue = preset['value'] * 1000
        elif preset['cond'] == 'LiveTime':
            try:
                self._dev.SyncMode = 'LiveTime'
                self._dev.SyncValue = preset['value'] * 1000
            except NicosError:
                try:
                    self.doStop()
                    self._dev.Init()
                except NicosError:
                    return
                self._dev.SyncMode = 'LiveTime'
                self._dev.SyncValue = preset['value'] * 1000
        elif preset['cond'] == 'ClockTime':
            self._stop = preset['value']

        self._name = preset['Name']
        self._comment = preset['Comment']

    def doStart(self):
        try:
            self._dev.Stop()
            self._dev.Clear()
            self._dev.Start()
        except NicosError:
            try:
                self._dev.stop()
                self._dev.Init()
                self._dev.Clear()
                self._dev.Start()
            except NicosError:
                pass

        self._started = currenttime()
        self._lastread = currenttime()

    def doPause(self):
        self._dev.Stop()
        return True

    def doResume(self):
        try:
            self._dev.Start()
        except NicosError:
            self._dev.Init()
            self._dev.Stop()
            self._dev.Start()
        return True

    def doPoll(self, maxage=0):
        return ((status.OK, ''), [0 for _i in range(16384)])

    def doStop(self):
        if self._dont_stop_flag:
            self._dont_stop_flag = False
            return
        try:
            self._dev.Stop()
        except NicosError:
            self._dev.Init()
            self._dev.Stop()

    def doIsCompleted(self):
        if self._started is None:
            return True
        if self._dont_stop_flag is True:
            return (currenttime() - self._started) >= self._preset['value']

        if (currenttime() - self._lastread) > (60 * 30):
            try:
                self._read_cache = self.doRead()
                self.log.warning('spectrum cached')
            except NicosError:
                self.log.warning('try to cache spectrum failed')
            finally:
                self._lastread = currenttime()

        if self._stop is not None:
            if currenttime() >= self._stop:
                return True

        if self._preset['cond'] in ['LiveTime', 'TrueTime']:
            if ((currenttime() - self._started) + 20) < self._preset['value']:
                # self.log.warning('poll every 0.2 secs')
                return False
            elif ((currenttime() - self._started) < self._preset['value']) or \
                 ((currenttime() - self._started) > self._preset['value']):
                self.log.warning('poll every 1 secs')
                session.delay(1)
            try:
                # self.log.warning('poll')
                stop = self._dev.PollTime[0]
            except NicosError:
                self._dont_stop_flag = True
                # self.log.warning('read poll time failed, waiting for other '
                #                  'detector(s)...')
                return False
            return stop < 0

        return False

    def valueInfo(self):
        return (Value('DSpecspectrum', type='counter'),)

    def doFinish(self):
        self.doStop()

        # reset preset values
        self._name = ''
        self._comment = ''

        self._started = None
        self._stop = None

        self._preset = {}

        self._read_cache = None
        self._lastread = None
        self._dont_stop_flag = False

    def presetInfo(self):
        return ('cond', 'value', 'Name', 'Name', 'Comment', 'Pos', 'Beam',
                'Attenuator', 'ElCol', 'started', 'Subfolder', 'Detectors',
                'Filename')
