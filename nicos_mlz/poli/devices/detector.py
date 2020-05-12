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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""POLI up/down measuring detector."""

from __future__ import absolute_import, division, print_function

from math import sqrt

from nicos.core import Attach, ConfigurationError, Moveable, Param, Value, \
    anytype, tupleof
from nicos.devices.generic.detector import Detector as GenericDetector
from nicos.devices.generic.sequence import MeasureSequencer, SeqCall, SeqWait


class AsymDetector(MeasureSequencer):
    """POLI specific detector that counts twice in an "up" and "down" state
    determined by a flipper device.  The result contains calculated flipping
    ratio and asymmetry as given by ::

        F = U/D
        A = (U - D)/(U + D)
    """

    attached_devices = {
        'detector': Attach('Standard detector device', GenericDetector),
        'flipper': Attach('Flipper to switch on/off', Moveable),
    }

    parameters = {
        'flipvalues': Param('On/off values for the flipper',
                            type=tupleof(anytype, anytype)),
        'counter':    Param('Name of the counter to use for calculation',
                            type=str, default='ctr1'),
    }

    _vindex = 0
    _up_preset = {}
    _dn_preset = {}

    def doInit(self, mode):
        upvalues = []
        dnvalues = []
        det_values = self._attached_detector.valueInfo()
        self._nvalues = len(det_values)
        for v in det_values:
            vup = v.copy()
            vup.name += '_up'
            upvalues.append(vup)
            vdn = v.copy()
            vdn.name += '_dn'
            dnvalues.append(vdn)
        calcvalues = [Value('FR', unit='', type='other'),
                      Value('Asym', unit='', type='other', errors='next'),
                      Value('dAsym', unit='', type='error')]
        self._valueinfo = tuple(calcvalues + upvalues + dnvalues)

        pinfo = set(self._attached_detector.presetInfo())
        self._presetinfo = pinfo | \
            {p + '_up' for p in pinfo} | {p + '_dn' for p in pinfo}

        self._results = [0.0, 0.0, 0.0] + self._attached_detector.read() + \
            self._attached_detector.read()

    def doUpdateCounter(self, name):
        for (i, value) in enumerate(self._attached_detector.valueInfo()):
            if value.name == name:
                self._vindex = i
                break
        else:
            raise ConfigurationError(self, "Counter '%s' not present" % name)

    def doSetPreset(self, **preset):
        if not preset:
            return
        self._up_preset.clear()
        self._dn_preset.clear()
        for v in self._attached_detector.presetInfo():
            if v in preset:
                self._up_preset[v] = self._dn_preset[v] = preset[v]
            if v + '_up' in preset:
                self._up_preset[v] = preset[v + '_up']
            if v + '_dn' in preset:
                self._dn_preset[v] = preset[v + '_dn']

    def doStart(self):
        self._results[:3] = [0.0, 0.0, 0.0]
        MeasureSequencer.doStart(self)

    def _getWaiters(self):
        return [self._attached_detector]

    def doRead(self, maxage=0):
        return self._results

    def presetInfo(self):
        return self._presetinfo

    def valueInfo(self):
        return self._valueinfo

    def _startDet(self, phase):
        if phase == 0:
            self._attached_detector.setPreset(**self._up_preset)
        else:
            self._attached_detector.setPreset(**self._dn_preset)
        self._attached_detector.start()

    def _readDet(self, phase):
        if phase == 0:
            self._results[3:3 + self._nvalues] = self._attached_detector.read()
        else:
            self._results[3 + self._nvalues:] = self._attached_detector.read()
            TU = self._results[3]
            TD = self._results[3 + self._nvalues]
            if TU == 0 or TD == 0:
                U = D = 0
            else:
                U = float(self._results[3 + self._vindex]) / TU
                D = float(self._results[3 + self._nvalues + self._vindex]) / TD
            if D == 0:
                self._results[:3] = [0.0, 0.0, 0.0]
            else:
                A = (U - D) / (U + D)
                dA = sqrt((1 - A)**2 * (U / TU) + (1 + A)**2 * (D / TD)) / (U + D)
                self._results[:3] = [U / D, A, dA]

    def _generateSequence(self):
        seq = []
        for phase in (0, 1):
            seq.append(SeqCall(self._attached_flipper.start, self.flipvalues[phase]))
            seq.append(SeqCall(self._startDet, phase))
            seq.append(SeqWait(self._attached_detector))
            seq.append(SeqCall(self._readDet, phase))
        return seq

    def doPause(self):
        self._attached_detector.doPause()

    def doResume(self):
        self._attached_detector.doResume()

    def doFinish(self):
        self._attached_detector.doFinish()
