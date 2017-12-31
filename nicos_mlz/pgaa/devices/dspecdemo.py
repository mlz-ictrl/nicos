#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
"""Classes to simulate the DSpec detector."""

from nicos.core import Override, Param, intrange, tupleof
from nicos.devices.generic.detector import Detector
from nicos.devices.generic.virtual import VirtualImage


class Spectrum(VirtualImage):

    parameter_overrides = {
        'sizes': Override(type=tupleof(intrange(1, 1), intrange(1, 16384)),
                          default=(1, 16384)),
    }


class DSPec(Detector):

    parameters = {
        'prefix': Param('prefix for filesaving',
                        type=str, settable=False, mandatory=True),
        'preselection': Param('presel', type=dict, settable=True,
                              userparam=False, mandatory=False),
    }

    def _presetiter(self):
        for dev in self._attached_timers:
            yield(dev.name, dev)
        # yield Detector._presetiter(self)

    def getEcal(self):
        return '0 0 0'

    def _clear(self):
        self._started = None
        self._stop = None
        self._preset = {}

    def doReset(self):
        self._clear()
        Detector.doReset(self)

    def doPreinit(self, mode):
        Detector.doPreinit(self, mode)
        self._clear()

    def doSetPreset(self, **preset):
        self._clear()
        self.preselection = preset

        if 'cond' in preset and preset['cond'] == 'ClockTime':
            self._stop = preset['value']
        if preset:
            self._time_preset = preset['t'] if 't' in preset else 0
            self._mon_preset = preset['mon1'] if 'mon1' in preset else \
                preset['mon2'] if 'mon2' in preset else 0
        Detector.doSetPreset(self, **preset)
