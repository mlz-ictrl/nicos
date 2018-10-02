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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

from __future__ import absolute_import, division

from nicos.core import FINAL, INTERRUPTED, SIMULATION, Attach, Measurable, \
    Override, Param, Readable, Value, tupleof
from nicos.devices.generic.detector import PostprocessPassiveChannel

from nicos_mlz.kws1.devices.daq import KWSImageChannel


class GEImageChannel(KWSImageChannel):
    """GE detector image with the flag to rebin to 8x8 pixel size."""

    parameters = {
        'rebin8x8': Param('Rebin data to 8x8 mm pixel size', type=bool,
                          default=False, settable=True, mandatory=False),
    }

    def _configure(self, tofsettings):
        if self._mode != SIMULATION:
            self._dev.binning = [1, 2, 1] if self.rebin8x8 else [1, 1, 1]
        KWSImageChannel._configure(self, tofsettings)


class ROIRateChannel(PostprocessPassiveChannel):
    """Calculates rate on the detector outside of the beamstop."""

    attached_devices = {
        'bs_x':  Attach('Beamstop x position', Readable),
        'bs_y':  Attach('Beamstop y position', Readable),
        'timer': Attach('The timer channel', Measurable),
    }

    parameters = {
        'xscale':    Param('Pixel (scale, offset) for calculating the beamstop '
                           'X center position from motor position',
                           type=tupleof(float, float), settable=True),
        'yscale':    Param('Pixel (scale, offset) for calculating the beamstop '
                           'Y center position from motor position',
                           type=tupleof(float, float), settable=True),
        'size':      Param('Size of beamstop in pixels (w, h)',
                           type=tupleof(int, int), settable=True),
        'roi':       Param('Rectangular region of interest (x, y, w, h)',
                           type=tupleof(int, int, int, int), settable=False),
    }

    parameter_overrides = {
        'unit':   Override(default='cps'),
        'fmtstr': Override(default='%d'),
    }

    _cts_seconds = [0, 0]

    def getReadResult(self, arrays, _results, quality):
        arr = arrays[0]
        if arr is None:
            return [0, 0]

        if any(self.size):
            w, h = self.size
            bs_x = self._attached_bs_x.read() * self.xscale[0] + self.xscale[1]
            bs_y = self._attached_bs_y.read() * self.yscale[0] + self.yscale[1]
            x = int(round(bs_x - w/2.))
            y = int(round(bs_y - h/2.))
            self._setROParam('roi', (x, y, w, h))
            outer = arr[y:y+h, x:x+w].sum()
            cts = outer
        else:
            self._setROParam('roi', (0, 0, 0, 0))
            cts = arr.sum()

        seconds = self._attached_timer.read(0)[0]
        cts_per_second = 0

        if seconds > 1e-8:
            if quality in (FINAL, INTERRUPTED) or seconds <= \
                    self._cts_seconds[1]:  # rate for full detector / time
                cts_per_second = cts / seconds
            elif cts > self._cts_seconds[0]:  # live rate on detector (using deltas)
                cts_per_second = (cts - self._cts_seconds[0]) / (
                    seconds - self._cts_seconds[1])
            else:
                cts_per_second = 0
        self._cts_seconds = [cts, seconds]

        return [cts, cts_per_second]

    def valueInfo(self):
        return (
            Value(name=self.name + '.roi', type='counter', fmtstr='%d', errors='sqrt'),
            Value(name=self.name + '.signal', type='monitor', fmtstr='%.2f'),
        )
