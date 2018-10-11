#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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

from __future__ import absolute_import, division

from nicos.core import Override, Param, intrange, status, tupleof, usermethod
from nicos.devices.generic.detector import Detector
from nicos.devices.generic.virtual import VirtualImage


class Spectrum(VirtualImage):

    parameters = {
        'preselection': Param('Preset value for this channel', type=float,
                              settable=True),
    }

    parameter_overrides = {
        'sizes': Override(type=tupleof(intrange(1, 1), intrange(1, 16384)),
                          default=(1, 16384)),
        'ismaster': Override(settable=True),
    }

    # set to True to get a simplified doEstimateTime
    is_timer = False

    def doEstimateTime(self, elapsed):
        if not self.ismaster or self.doStatus()[0] != status.BUSY:
            return None
        if self.is_timer:
            return self.preselection - elapsed
        else:
            counted = float(self.doRead()[0])
            # only estimated if we have more than 3% or at least 100 counts
            if counted > 100 or counted > 0.03 * self.preselection:
                if 0 <= counted <= self.preselection:
                    return (self.preselection - counted) * elapsed / counted


class DSPec(Detector):

    parameters = {
        'prefix': Param('prefix for filesaving',
                        type=str, settable=False, mandatory=True,
                        category='general'),
        'ecalslope': Param('Energy Calibration Slope',
                           type=int, mandatory=False, settable=True,
                           prefercache=True, default=0, category='general'),
        'ecalintercept': Param('Energy Calibration Slope',
                               type=int, mandatory=False, settable=True,
                               prefercache=True, default=0,
                               category='general'),
    }

    def _presetiter(self):
        for k in ('info', 'Filename'):
            yield k, None
        for dev in self._attached_timers:
            if dev.name == 'truetim':
                yield 'TrueTime', dev
            elif dev.name == 'livetim':
                yield 'LiveTime', dev
            elif dev.name == 'clocktim':
                yield 'ClockTime', dev
        for dev in self._attached_images:
            yield 'counts', dev

    def _clear(self):
        self._started = None
        self._stop = None
        self._preset = {}
        self._lastread = None
        self._read_cache = None
        self._dont_stop_flag = False
        self._comment = ''
        self._name_ = ''

    def doReset(self):
        self._clear()
        Detector.doReset(self)

    def doPreinit(self, mode):
        Detector.doPreinit(self, mode)
        self._clear()

    def doSetPreset(self, **preset):
        self._clear()
        for master in self._masters:
            master.ismaster = False
        if 'TrueTime' in preset:
            for d in self._attached_timers:
                if d.name == 'truetim':
                    d.ismaster = True
                    d.preselection = preset['TrueTime'] * 1
        elif 'LiveTime' in preset:
            for d in self._attached_timers:
                if d.name == 'livetim':
                    d.ismaster = True
                    d.preselection = preset['LiveTime'] * 1
        elif 'ClockTime' in preset:
            self._stop = preset['ClockTime']
        elif 'counts' in preset:
            for d in self._attached_images:
                d.ismaster = True
                d.preselection = preset['counts']

        self._preset = preset
        for k in ('Filename',
                  'LiveTime', 'TrueTime', 'ClockTime', 'counts'):
            preset.pop(k, '')
        self.log.debug('Preset keys: %r', self._presetkeys)
        Detector.doSetPreset(self, **preset)

    @usermethod
    def resetvals(self):
        self._clear()

    def presetInfo(self):
        return set(['info', 'Filename',
                    'TrueTime', 'LiveTime', 'ClockTime', 'counts'])
