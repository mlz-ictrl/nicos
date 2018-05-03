# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2021 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from nicos.core.constants import FINAL, INTERRUPTED
from nicos.core.device import Measurable
from nicos.core.params import Attach, Value
from nicos.devices.tango import BaseImageChannel


def calculateRate(store, quality, cts, seconds):
    """Calculate counts/second rate from given data.

    While the detector is counting, an instantaneous rate is calculated from
    the difference between the current and last values.  When finished, the
    rate is calculated over the whole counting time.
    """
    rate = 0
    if seconds > 1e-8:
        if quality in (FINAL, INTERRUPTED) or seconds <= store[1]:
            # rate for full detector / time
            rate = cts / seconds
        elif seconds > store[1]:
            # live rate on detector (using deltas)
            rate = (cts - store[0]) / (seconds - store[1])
    store[:] = [cts, seconds]
    return rate


class RateImageChannel(BaseImageChannel):
    """Subclass of the Tango image channel that automatically returns the
    sum of all counts and the momentary count rate as scalar values.
    """

    attached_devices = {
        'timer': Attach('The timer channel', Measurable),
    }

    def doInit(self, mode):
        BaseImageChannel.doInit(self, mode)
        self._rate_data = [0, 0]

    def doReadArray(self, quality):
        narray = BaseImageChannel.doReadArray(self, quality)
        seconds = self._attached_timer.read(0)[0]
        cts = narray.sum()
        rate = calculateRate(self._rate_data, quality, cts, seconds)
        self.readresult = [cts, rate]
        return narray

    def valueInfo(self):
        return (Value(name=self.name + ' (total)', type='counter', fmtstr='%d',
                      errors='sqrt', unit='cts'),
                Value(name=self.name + ' (rate)', type='monitor',
                      fmtstr='%.1f', unit='cps'),)
