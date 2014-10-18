#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""
NICOS value plot widget.
"""

import numpy as np
from time import time as currenttime

from PyQt4.QtCore import SIGNAL

from nicos.pycompat import number_types, string_types, iteritems


class TimeSeries(object):
    """
    Represents a plot curve that shows a time series for a value.
    """
    minsize = 500

    def __init__(self, name, interval, window, signal_obj):
        self.name = name
        self.signal_obj = signal_obj
        self.info = None
        self.interval = interval
        self.window = window
        self.x = None
        self.y = None
        self.n = 0
        self.real_n = 0
        self.last_y = None

    def init_empty(self):
        self.x = np.zeros(self.minsize)
        self.y = np.zeros(self.minsize)

    def init_from_history(self, history, starttime, valueindex=-1):
        string_mapping = {}
        ltime = 0
        lvalue = None
        maxdelta = max(2 * self.interval, 11)
        x = np.zeros(3 * len(history))
        y = np.zeros(3 * len(history))
        i = 0
        vtime = value = None  # stops pylint from complaining
        for vtime, value in history:
            if valueindex > -1:
                try:
                    value = value[valueindex]
                except (TypeError, IndexError):
                    continue
            if value is None:
                continue
            delta = vtime - ltime
            if delta < self.interval:
                # value comes too fast -> ignore
                lvalue = value
                continue
            if not isinstance(value, number_types):
                # if it's a string, create a new unique integer value for the string
                if isinstance(value, string_types):
                    value = string_mapping.setdefault(value, len(string_mapping))
                # other values we can't use
                else:
                    continue
            if delta > maxdelta and lvalue is not None:
                # synthesize one or two points inbetween
                if vtime - self.interval > ltime + self.interval:
                    x[i] = ltime + self.interval
                    y[i] = lvalue
                    i += 1
                x[i] = vtime - self.interval
                y[i] = lvalue
                i += 1
            x[i] = ltime = max(vtime, starttime)
            y[i] = lvalue = value
            i += 1
        # In case the final value was discarded because it came too fast,
        # add it anyway, because it will potentially be the last one for
        # longer, and synthesized.
        if i and y[i-1] != value:
            x[i] = vtime
            y[i] = value
            i += 1
        self.n = self.real_n = i
        self.last_y = lvalue
        x.resize((2 * i or 500,))
        y.resize((2 * i or 500,))
        self.x = x
        self.y = y
        if string_mapping:
            self.info = ', '.join('%s=%s' % (v, k)
                                  for (k, v) in iteritems(string_mapping))

    def synthesize_value(self):
        if self.n and self.x[self.n - 1] < currenttime() - self.interval:
            self.add_value(currenttime(), self.last_y, real=False)

    def add_value(self, vtime, value, real=True):
        n, x, y = self.n, self.x, self.y
        real_n = self.real_n
        self.last_y = value
        # do not add value if it comes too fast
        if real_n > 0 and x[real_n - 1] > vtime - self.interval:
            return
        # double array size if array is full
        if n >= x.shape[0]:
            # we select a certain maximum # of points to avoid filling up memory
            # and taking forever to update
            if x.shape[0] > 5000:
                # don't add more points, make existing ones more sparse
                x[:n/2] = x[1::2]
                y[:n/2] = y[1::2]
                n = self.n = self.real_n = n / 2
            else:
                del x, y  # remove references
                self.x.resize((2 * self.x.shape[0],))
                self.y.resize((2 * self.y.shape[0],))
                x = self.x
                y = self.y
        # fill next entry
        if not real and real_n < n - 1:
            # do not generate endless amounts of synthesized points,
            # two are enough (one at the beginning, one at the end of
            # the interval without real points)
            x[n-1] = vtime
            y[n-1] = value
        else:
            x[n] = vtime
            y[n] = value
            self.n += 1
            if real:
                self.real_n = self.n
        # check sliding window
        if self.window:
            i = -1
            threshold = vtime - self.window
            while x[i+1] < threshold and i < n:
                if x[i+2] > threshold:
                    x[i+1] = threshold
                    break
                i += 1
            if i >= 0:
                x[0:n - i] = x[i+1:n+1].copy()
                y[0:n - i] = y[i+1:n+1].copy()
                self.n -= i+1
                self.real_n -= i+1
        self.signal_obj.emit(SIGNAL('timeSeriesUpdate'), self)
