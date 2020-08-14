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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

from nicos.core import Override, Param, Value, tupleof
from nicos.devices.generic.detector import PostprocessPassiveChannel
from nicos.devices.tango import ImageChannel


class LinearROIChannel(PostprocessPassiveChannel):
    """Calculates counts for a region of interest in a 1D spectrum."""

    parameters = {
        'roi': Param('Region of interest (start, end) including end',
                     tupleof(int, int),
                     settable=True, category='general'),
    }

    parameter_overrides = {
        'unit':   Override(default='cts'),
        'fmtstr': Override(default='%d'),
    }

    def getReadResult(self, arrays, _results, _quality):
        if any(self.roi):
            return [arr[self.roi[0]:self.roi[1]+1].sum() for arr in arrays]
        return [arr.sum() for arr in arrays]

    def valueInfo(self):
        if len(self.readresult) > 1:
            return tuple(Value(name=self.name + '[%d]' % i, type='counter',
                               fmtstr='%d')
                         for i in range(1, len(self.readresult) + 1))
        return Value(name=self.name, type='counter', fmtstr='%d'),


class SumImageChannel(ImageChannel):
    parameter_overrides = {
        'unit':   Override(default='cts'),
        'fmtstr': Override(default='%d'),
    }

    def doRead(self, maxage=0):
        return [self._dev.value.sum()]

    def valueInfo(self):
        return Value(name=self.name, type='counter', fmtstr='%d'),
