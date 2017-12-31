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

import numpy
from scipy.signal import convolve2d

from nicos.core import DeviceAlias, Attach, Param, Override, Moveable, \
    Value, Measurable, status, oneof, listof
from nicos.devices.generic.detector import PostprocessPassiveChannel


class DetSwitcher(Moveable):
    """Switches the channel alias device between HRD and VHRD."""

    attached_devices = {
        'alias': Attach('the alias to switch', DeviceAlias),
        'hrd':   Attach('the HRD device', Measurable),
        'vhrd':  Attach('the VHRD device', Measurable),
    }

    _values = ['HRD', 'VHRD']

    parameters = {
        'values': Param('Possible values', type=listof(str),
                        default=_values, settable=False, userparam=False),
    }

    parameter_overrides = {
        'unit':  Override(default='', mandatory=False),
    }

    valuetype = oneof(*_values)

    def doRead(self, maxage=0):
        if self._attached_alias.alias == self._attached_hrd.name:
            return 'HRD'
        elif self._attached_alias.alias == self._attached_vhrd.name:
            return 'VHRD'
        return 'unknown'

    def doStatus(self, maxage=0):
        if self.doRead(maxage) == 'unknown':
            return status.WARN, ''
        return status.OK, ''

    def doStart(self, target):
        if target == 'HRD':
            self._attached_alias.alias = self._attached_hrd
        else:
            self._attached_alias.alias = self._attached_vhrd


class ConvolutionMax(PostprocessPassiveChannel):
    """Convolves the detector image with NxN ones and returns the maximum."""

    parameters = {
        'npixels': Param('Size of kernel', type=int, default=5, settable=True),
    }

    parameter_overrides = {
        'unit':   Override(default='cts'),
        'fmtstr': Override(default='%d'),
    }

    def setReadResult(self, arrays):
        kern = numpy.ones((self.npixels, self.npixels))
        self.readresult = [convolve2d(a, kern, mode='valid').max()
                           if a is not None else 0
                           for a in arrays]

    def valueInfo(self):
        return Value(name=self.name, type='counter', fmtstr='%d'),
