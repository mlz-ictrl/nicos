#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

import numpy as np

from nicos.core import ArrayDesc, Attach, Measurable, Moveable, Param, Value, \
    anytype, listof, status
from nicos.core.constants import LIVE
from nicos.core.errors import NicosError
from nicos.core.utils import multiWait
from nicos.devices.tango import PyTangoDevice


class DSPec(PyTangoDevice, Measurable):

    attached_devices = {
        'gates':   Attach('Gating devices', Moveable,
                          multiple=True, optional=True),
    }

    parameters = {
        'prefix': Param('prefix for filesaving',
                        type=str, settable=False, mandatory=True,
                        category='general'),
        'ecalslope': Param('Energy calibration slope',
                           type=float, mandatory=False, settable=True,
                           volatile=True, default=0),
        'ecalintercept': Param('Energy calibration interception',
                               type=float, mandatory=False, settable=True,
                               volatile=True, default=0),
        'poll': Param('Polling time of the TANGO device driver',
                      type=float, settable=False, volatile=True),
        'cacheinterval': Param('Interval to cache intermediate spectra',
                               type=float, unit='s', settable=True,
                               default=1800),
        'enablevalues':  Param('List of values to enable the gates',
                               type=listof(anytype), default=[],
                               settable=True, category='general'),
        'disablevalues': Param('List of values to disable the gates',
                               type=listof(anytype), default=[]),
    }

    def _enable_gates(self):
        self.log.debug('enabling gates')
        for dev, val in zip(self._attached_gates, self.enablevalues):
            dev.move(val)
        multiWait(self._attached_gates)
        self.log.debug('gates enabled')

    def _disable_gates(self):
        self.log.debug('disabling gates')
        for dev, val in zip(reversed(self._attached_gates),
                            reversed(self.disablevalues)):
            dev.move(val)
        multiWait(self._attached_gates)
        self.log.debug('gates disabled')

    # XXX: issues with ortec API -> workarounds and only truetime and livetime
    # working.

    def doReadEcalslope(self):
        ec = self._dev.EnergyCalibration.strip()
        return float(ec.split()[1])

    def doReadEcalintercept(self):
        ec = self._dev.EnergyCalibration.strip()
        return float(ec.split()[2])

    def doReadArrays(self, quality):
        spectrum = None
        try:
            spectrum = self._dev.Value
        except NicosError:
            # self._comment += 'CACHED'
            if self._read_cache is not None:
                self.log.warning('using cached spectrum')
                spectrum = self._read_cache
            else:
                self.log.warning('no spectrum cached')
        return [spectrum]

    def doRead(self, maxage=0):
        ret = [self._dev.TrueTime[0], self._dev.LiveTime[0],
               sum(self._dev.Value.tolist())]
        return ret

    def doReadPoll(self):
        return self._dev.PollTime[0]

    def _clear(self):
        self._started = None
        self._lastread = 0
        self._comment = ''
        self._name_ = ''
        self._stop = None
        self._preset = {}
        self._dont_stop_flag = False
        self._read_cache = None

    def doReset(self):
        self._clear()
        self._dev.Init()

    def doInit(self, mode):
        self._clear()
        self.arraydesc = ArrayDesc('data', (1, 16384), np.uint32)

    def doFinish(self):
        self.doStop()
        # reset preset values
        self._clear()

    def doReadIsmaster(self):
        pass

    def presetInfo(self):
        return {'info', 'Filename',
                'TrueTime', 'LiveTime', 'ClockTime', 'counts'}

    def doSetPreset(self, **preset):
        self._clear()

        if 'TrueTime' in preset:
            try:
                self._dev.SyncMode = 'RealTime'
                self._dev.SyncValue = preset['TrueTime'] * 1000
            except NicosError:
                try:
                    self.doStop()
                    self._dev.Init()
                except NicosError:
                    return
                self._dev.SyncMode = 'RealTime'
                self._dev.SyncValue = preset['TrueTime'] * 1000
        elif 'LiveTime' in preset:
            try:
                self._dev.SyncMode = 'LiveTime'
                self._dev.SyncValue = preset['LiveTime'] * 1000
            except NicosError:
                try:
                    self.doStop()
                    self._dev.Init()
                except NicosError:
                    return
                self._dev.SyncMode = 'LiveTime'
                self._dev.SyncValue = preset['LiveTime'] * 1000
        elif 'ClockTime' in preset:
            self._stop = preset['ClockTime']
        elif 'counts' in preset:
            pass

        self._preset = preset

    def doTime(self, preset):
        if 'TrueTime' in preset:
            return preset['TrueTime']
        elif 'LiveTime' in preset:
            return preset['LiveTime']
        elif 'ClockTime' in preset:
            return abs(float(preset['ClockTime']) - currenttime())
        elif 'counts' in preset:
            return 1
        return None

    def doEstimateTime(self, elapsed):
        if self.doStatus()[0] == status.BUSY:
            if 'TrueTime' in self._preset:
                return self._preset['TrueTime'] - elapsed
            elif 'LiveTime' in self._preset:
                return self._preset['LiveTime'] - elapsed
            elif 'ClockTime' in self._preset:
                return abs(float(self._preset['ClockTime']) - currenttime())
        return None

    def doStart(self):
        self._enable_gates()
        try:
            self._dev.Stop()
            self._dev.Clear()
            self._dev.Start()
        except NicosError:
            try:
                self._dev.Stop()
                self._dev.Init()
                self._dev.Clear()
                self._dev.Start()
            except NicosError:
                pass
        self._started = currenttime()
        self._lastread = currenttime()

    def doPause(self):
        self._dev.Stop()
        self._disable_gates()
        return True

    def doResume(self):
        # check first gate to see if we need to (re-)enable them
        if self._attached_gates[0].read(0) != self.enablevalues[0]:
            self._enable_gates()
        try:
            self._dev.Start()
        except NicosError:
            self._dev.Init()
            self._dev.Stop()
            self._dev.Start()

    def doStop(self):
        if self._dont_stop_flag:
            self._dont_stop_flag = False
            return
        try:
            self._dev.Stop()
        except NicosError:
            self._dev.Init()
            self._dev.Stop()
        self._disable_gates()

    def duringMeasureHook(self, elapsed):
        if (elapsed - self._lastread) > self.cacheinterval:
            try:
                self._read_cache = self._dev.Value
                self.log.debug('spectrum cached')
            except NicosError:
                self.log.warning('caching spectrum failed')
            finally:
                self._lastread = elapsed
            return LIVE
        return None

    def doSimulate(self, preset):
        for t in 'TrueTime', 'LiveTime', 'ClockTime':
            if t in preset:
                return [preset[t], preset[t], 0]
        if 'counts' in preset:
            return [1, 1, preset['counts']]
        return [0, 0, 0]

    def doIsCompleted(self):
        if self._started is None:
            return True
        if self._dont_stop_flag is True:
            return (currenttime() - self._started) >= self._preset['value']

        if self._stop is not None:
            if currenttime() >= self._stop:
                return True

        if 'TrueTime' in self._preset:
            return self._dev.TrueTime >= self._preset['TrueTime']
        elif 'LiveTime' in self._preset:
            return self._dev.LiveTime >= self._preset['LiveTime']
        elif 'counts' in self._preset:
            return self.doRead(0)[2] >= self._preset['counts']
        try:
            # self.log.warning('poll')
            stop = self.poll[0]
            return stop < 0
        except NicosError:
            self._dont_stop_flag = True
            # self.log.warning('read poll time failed, waiting for other '
            #                  'detector(s)...')
            return False
        return False

    def valueInfo(self):
        return (Value(name='truetim', type='time', fmtstr='%.3f', unit='s'),
                Value(name='livetim', type='time', fmtstr='%.3f', unit='s'),
                Value('DSpec', type='counter', fmtstr='%d', unit='cts'),
                )

    def arrayInfo(self):
        return (self.arraydesc,)
