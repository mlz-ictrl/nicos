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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Virtual TAS devices."""

from time import time as currenttime
import numpy as np

from nicos.core import Readable, Measurable, Param, Value, Attach, status, vec3


class VirtualSXtalDetector(Measurable):
    attached_devices = {
        'sxtal': Attach('SXTAL device to read', Readable),
    }

    parameters = {
        'realtime':   Param('Whether to wait for the preset counting time',
                            type=bool, default=False, settable=True),
        'background': Param('Instrumental background', unit='cts/s',
                            default=1.0, settable=True),
        'peakwidth':   Param('Apparent peakwidth (rlu)', type=vec3,
                            default=(0.001,0.002,0.003), settable=True),
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
        monrate = 50000.
        if 't' in self._lastpreset:
            time = float(self._lastpreset['t'])
            moni = np.random.poisson(int(monrate * time))
        elif 'mon' in self._lastpreset:
            moni = int(self._lastpreset['mon'])
            time = float(moni) / np.random.poisson(monrate)
        else:
            time = 1
            moni = monrate
        bg = np.random.poisson(int(self.background * time))
        counts = int(self._peak(time)) + bg
        self._counting_started = 0
        self._lastresult = [time, moni, counts]

    def _peak(self, time):
        from scipy import stats
        width = np.array(self.peakwidth) / 10
        hkl = np.array(self._attached_sxtal.read(0))
        hkli = np.round(hkl)
        dhkl = (hkli - hkl)
        x = stats.multivariate_normal([0, 0, 0], width)
        return int(self.background * time) * x.pdf(dhkl)

    def doEstimateTime(self, elapsed):
        eta = set()
        monrate = 50000. / self._attached_sxtal._attached_mono.read()
        if 't' in self._lastpreset:
            eta.add(float(self._lastpreset['t']) - elapsed)
        if 'mon' in self._lastpreset:
            eta.add(float(self._lastpreset['mon']) / monrate - elapsed)
        if eta:
            return min(eta)
        return None
