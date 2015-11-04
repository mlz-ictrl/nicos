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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Virtual TAS devices."""

from time import time as currenttime
from numpy import random

from nicos.core import Readable, Measurable, Param, Value, Attach, status


class VirtualTasDetector(Measurable):
    attached_devices = {
        'tas': Attach('TAS device to read', Readable),
    }

    parameters = {
        'realtime':   Param('Whether to wait for the preset counting time',
                            type=bool, default=False, settable=True),
        'background': Param('Instrumental background', unit='cts/min',
                            default=1.0, settable=True),
        'mcpoints':   Param('Number of Monte-Carlo points', type=int,
                            default=1000, settable=True),
    }

    def doInit(self, mode):
        self._lastpreset = {'t': 1}
        self._lastresult = [0, 0, 0]
        self._counting_started = 0
        self._pause_time = 0

    def presetInfo(self):
        return ['t', 'mon']

    def valueInfo(self):
        return Value('t', unit='s', type='time', fmtstr='%.3f'), \
            Value('mon', unit='cts', type='monitor', errors='sqrt', fmtstr='%d'), \
            Value('ctr', unit='cts', type='counter', errors='sqrt', fmtstr='%d')

    def doSetPreset(self, **preset):
        self._lastpreset = preset

    def doStart(self):
        self._counting_started = currenttime()

    def doPause(self):
        self._pause_time = currenttime()
        return True

    def doResume(self):
        if self._pause_time:
            self._counting_started += (currenttime() - self._pause_time)
        return True

    def doFinish(self):
        self._counting_started = 0

    def doStop(self):
        self.doFinish()

    def doStatus(self, maxage=0):
        if 't' in self._lastpreset and self.realtime:
            if not (currenttime() - self._counting_started >= self._lastpreset['t']):
                return status.BUSY, 'counting'
        return status.OK, 'idle'

    def doRead(self, maxage=0):
        return self._lastresult

    def doSave(self):
        from nicos.devices.tas.rescalc import resmat, calc_MC, demosqw
        from nicos.commands.tas import _resmat_args
        taspos = self._attached_tas.read(0)
        mat = resmat(*_resmat_args(taspos, {}))
        # monitor rate (assume constant flux distribution from source)
        # is inversely proportional to k_i
        ki = self._attached_tas._attached_mono.read(0)
        monrate = 50000. / ki
        if 't' in self._lastpreset:
            time = float(self._lastpreset['t'])
            moni = random.poisson(int(monrate * time))
        elif 'mon' in self._lastpreset:
            moni = int(self._lastpreset['mon'])
            time = float(moni) / random.poisson(monrate)
        else:
            time = 1
            moni = monrate
        bg = random.poisson(int(self.background * time / 60))
        counts = int(calc_MC([taspos], [bg, time], demosqw, mat,
                             self.mcpoints)[0])
        self._counting_started = 0
        self._lastresult = [time, moni, counts]

    def doEstimateTime(self, elapsed):
        eta = set()
        monrate = 50000. / self._attached_tas._attached_mono.read()
        if 't' in self._lastpreset:
            eta.add(float(self._lastpreset['t']) - elapsed)
        if 'mon' in self._lastpreset:
            eta.add(float(self._lastpreset['mon'])/monrate - elapsed)
        if eta:
            return min(eta)
        return None
