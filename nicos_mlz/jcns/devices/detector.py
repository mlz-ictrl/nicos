# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

from nicos.core.constants import FINAL, INTERRUPTED
from nicos.core.device import Measurable
from nicos.core.params import Attach, Value
from nicos.devices.tango import BaseImageChannel


class RateImageChannel(BaseImageChannel):
    """Subclass of the Tango image channel that automatically returns the
    sum of all counts and the momentary count rate as scalar values.
    """

    attached_devices = {
        'timer': Attach('The timer channel', Measurable),
    }

    _cts_seconds = [0, 0]

    def doReadArray(self, quality):
        narray = BaseImageChannel.doReadArray(self, quality)
        seconds = self._attached_timer.read(0)[0]
        cts = narray.sum()
        cts_per_second = 0

        if seconds > 1e-8:
            if quality in (FINAL, INTERRUPTED) or seconds <= \
                    self._cts_seconds[1]:  # rate for full detector / time
                cts_per_second = cts / seconds
            else:  # live rate on detector (using deltas)
                cts_per_second = (cts - self._cts_seconds[0]) / (
                    seconds - self._cts_seconds[1])
        self._cts_seconds = [cts, seconds]

        self.readresult = [cts, cts_per_second]
        return narray

    def valueInfo(self):
        return (Value(name=self.name + ' (total)', type='counter', fmtstr='%d',
                      errors='sqrt', unit='cts'),
                Value(name=self.name + ' (rate)', type='monitor',
                      fmtstr='%.1f', unit='cps'),)
