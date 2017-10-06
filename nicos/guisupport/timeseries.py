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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************
"""
NICOS value plot widget.
"""

import operator
import functools
from time import time as currenttime

import numpy as np

from nicos.pycompat import number_types, string_types, iteritems


def buildTickDistAndSubTicks(mintime, maxtime, minticks=3):
    """Calculates tick distance and subticks for a given domain."""
    good = [1, 2, 5, 10, 30,                           # s
            60, 2*60, 5*60, 10*60, 15*60, 30*60,       # m
            3600, 2*3600, 3*3600, 6*3600, 12*3600,     # h
            24*3600, 2*24*3600, 3*24*3600, 7*24*3600]  # d
    divs = [5, 4, 5, 5, 6,
            6, 4, 5, 5, 3, 6,
            6, 4, 6, 6, 6,
            6, 6, 6, 7]
    upscaling = [1, 2, 5, 10]
    downscaling = [1, 0.5, 0.2, 0.1]

    # calculate maxticks, depends on 'good' values
    maxticks = minticks
    for i in range(len(good)-1):
        if maxticks < minticks * good[i+1]/float(good[i]):
            maxticks = minticks * good[i+1]/float(good[i])

    # determine ticking range
    length = maxtime - mintime
    maxd = length / float(minticks)
    mind = length / float(maxticks+1)

    # scale to useful numbers
    scale_ind = 0
    scale_fact = 1
    scale = 1
    while maxd * scale < good[0]:  # too small ticking, increase scaling
        scale_ind += 1
        if scale_ind >= len(upscaling):
            scale_fact *= upscaling[-1]
            scale_ind = 1
        scale = scale_fact * upscaling[scale_ind]
    scale_ind = 0
    while mind * scale > good[-1]:  # too big ticking, decrease scaling
        scale_ind += 1
        if scale_ind >= len(downscaling):
            scale_fact *= downscaling[-1]
            scale_ind = 1
        scale = scale_fact * downscaling[scale_ind]

    # find a good value for ticking
    tickdist = 0
    subticks = 0
    for i, d in enumerate(good):
        if mind * scale <= d <= maxd * scale:
            tickdist = d / float(scale)
            subticks = divs[i]

    # check ticking
    assert tickdist > 0
    return tickdist, int(subticks)


def buildTimeTicks(mintime, maxtime, minticks=3):
    """Calculates time ticks for a given domain."""
    tickdist, subticks = buildTickDistAndSubTicks(mintime, maxtime, minticks)
    # calculate tick positions
    minor, medium, major = [], [], []
    for i in range(int(mintime/tickdist)-1, int(maxtime/tickdist)+1):
        t = int(i+1) * tickdist
        major.append(t)
        for j in range(subticks):
            minor.append(t + j*tickdist/subticks)
    return minor, medium, major


class TimeSeries(object):
    """
    Represents a plot curve that shows a time series for a value.
    """
    minsize = 500
    maxsize = 5000

    def __init__(self, name, interval, scale, offset, window, signal_obj,
                 info=None, mapping=None):
        self.name = name
        self.disabled = False
        self.signal_obj = signal_obj
        self.info = info
        self.interval = interval
        self.window = window
        self.scale = scale
        self.offset = offset
        self.data = None
        self.n = 0
        self.real_n = 0
        self.last_y = None
        self.string_mapping = mapping or {}
        self._last_update_time = currenttime()

    @property
    def title(self):
        return (self.name + ('*%g' % self.scale if self.scale != 1 else '') +
                ('%+g' % self.offset if self.offset else '') +
                (' (' + self.info + ')' if self.info else ''))

    @property
    def x(self):
        return np.hsplit(self.data, 2)[0].view()

    @property
    def y(self):
        return np.hsplit(self.data, 2)[1].view()

    def init_empty(self):
        self.data = np.zeros((self.minsize, 2))

    def init_from_history(self, history, starttime, endtime, valueindex=()):
        ltime = 0
        lvalue = None
        maxdelta = max(2 * self.interval, 11)
        self.data = np.zeros((max(self.minsize, (3 * len(history) + 2)), 2))
        i = 0
        vtime = value = None  # stops pylint from complaining
        for vtime, value in history:
            if value is None:
                continue
            if valueindex:
                try:
                    value = functools.reduce(operator.getitem, valueindex, value)
                except (TypeError, IndexError):
                    continue
            delta = vtime - ltime
            if not isinstance(value, number_types):
                # if it's a string, create a new unique integer value for the string
                if isinstance(value, string_types):
                    value = self.string_mapping.setdefault(value, len(self.string_mapping))
                # other values we can't use
                else:
                    continue
            value = value * self.scale + self.offset
            if delta < self.interval:
                # value comes too fast -> ignore
                lvalue = value
                continue
            if delta > maxdelta and lvalue is not None:
                # synthesize one or two points inbetween
                if vtime - self.interval > ltime + self.interval:
                    self.x[i] = ltime + self.interval
                    self.y[i] = lvalue
                    i += 1
                self.x[i] = vtime - self.interval
                self.y[i] = lvalue
                i += 1
            self.x[i] = ltime = max(vtime, starttime)
            self.y[i] = lvalue = value
            i += 1
        if i and self.y[i-1] != value:
            # In case the final value was discarded because it came too fast,
            # add it anyway, because it will potentially be the last one for
            # longer, and synthesized.
            self.x[i] = vtime
            self.y[i] = value
            i += 1
        elif i and self.x[i-1] < endtime - self.interval:
            # In case the final value is very old, synthesize a point
            # right away at the end of the interval.
            self.x[i] = endtime
            self.y[i] = value
            i += 1
        self.n = self.real_n = i
        self.last_y = lvalue
        if self.string_mapping:
            self.info = ', '.join(
                '%g=%s' % (v * self.scale + self.offset, k) for (k, v) in
                sorted(iteritems(self.string_mapping), key=lambda x: x[1]))

    def synthesize_value(self):
        if not self.n:
            return
        delta = currenttime() - self._last_update_time
        if delta > self.interval:
            self.add_value(self.x[self.n - 1] + delta, self.last_y, real=False,
                           use_scale=False)

    def add_value(self, vtime, value, real=True, use_scale=True):
        if not isinstance(value, number_types):
            if isinstance(value, string_types):
                value = self.string_mapping.setdefault(value, len(self.string_mapping))
                self.info = ', '.join(
                    '%g=%s' % (v * self.scale + self.offset, k) for (k, v) in
                    sorted(iteritems(self.string_mapping), key=lambda x: x[1]))
            else:
                return
        elif use_scale:
            value = value * self.scale + self.offset
        n = self.n
        real_n = self.real_n
        self.last_y = value
        # do not add value if it comes too fast
        if real_n > 0 and self.x[real_n - 1] > vtime - self.interval:
            return
        self._last_update_time = currenttime()
        xsize = self.data.shape[0]
        # double array size if array is full
        if n >= xsize:

            # we select a certain maximum # of points to avoid filling up memory
            # and taking forever to update
            if xsize > self.maxsize:
                # don't add more points, make existing ones more sparse
                self.x[:n/2] = self.x[1::2]
                self.y[:n/2] = self.y[1::2]
                n = self.n = self.real_n = n // 2
            else:
                self.data.resize((2 * xsize, 2))
        # fill next entry
        if not real and real_n < n - 1:
            # do not generate endless amounts of synthesized points,
            # two are enough (one at the beginning, one at the end of
            # the interval without real points)
            self.x[n-1] = vtime
            self.y[n-1] = value
        else:
            self.x[n] = vtime
            self.y[n] = value
            self.n += 1
            if real:
                self.real_n = self.n
        # check sliding window
        if self.window:
            i = -1
            threshold = vtime - self.window
            while self.x[i+1] < threshold and i < n:
                if self.x[i+2] > threshold:
                    self.x[i+1] = threshold
                    break
                i += 1
            if i >= 0:
                self.x[0:n - i] = self.x[i+1:n+1].copy()
                self.y[0:n - i] = self.y[i+1:n+1].copy()
                self.n -= i+1
                self.real_n -= i+1
        self.signal_obj.timeSeriesUpdate.emit(self)
