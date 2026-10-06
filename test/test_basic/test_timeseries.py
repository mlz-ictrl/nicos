# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Jonas Petersson <jonas.petersson@ess.eu>
#
# *****************************************************************************


"""NICOS tests for the TimeSeries class and its downsampling capabilities."""

import numpy as np
import pytest

from nicos.guisupport.timeseries import TimeSeries


class SeriesUpdates:
    """Record the signal payload without needing a GUI or event loop."""

    def __init__(self):
        self.timeSeriesUpdate = self
        self.count = 0
        self.last_series = None

    def emit(self, series):
        self.count += 1
        self.last_series = series


@pytest.mark.parametrize('count', [128000, 128001, 320001])
@pytest.mark.parametrize('pattern', ['line', 'spike'])
def test_full_history_buffer_keeps_accepting_values(count, pattern):
    updates = SeriesUpdates()
    series = TimeSeries('temperature', 2, None, None, updates)
    series.initEmpty()
    start = 1_700_000_000.0
    spike_index = 64000

    # Two-second cache updates are replayed without waiting three days in real
    # time. A slow temperature ramp or brief excursion is valid device data.
    # The background changes every sample: the cache suppresses identical values.
    for index in range(count):
        value = (
            100 if pattern == 'spike' and index == spike_index else 20 + index * 0.0001
        )
        series.addValue(start + index * 2, float(value))

    assert updates.count == count
    assert updates.last_series is series
    assert series.real_n == series.n
    assert 0 < series.n <= series.data.shape[0]
    assert series.data.shape[0] <= 2 * series.maxsize
    assert series.x[0] == start
    assert series.x[-1] == start + (count - 1) * 2
    assert np.all(np.diff(series.x) > 0)
    indices = (series.x - start) / 2
    if pattern == 'line':
        np.testing.assert_allclose(series.y, 20 + indices * 0.0001)
    else:
        assert series.y.max() == 100
        np.testing.assert_allclose(
            series.y, np.where(indices == spike_index, 100, 20 + indices * 0.0001)
        )
