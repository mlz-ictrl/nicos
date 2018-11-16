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

from __future__ import absolute_import, division, print_function

import numpy
from scipy.signal import convolve2d

from nicos.core import Attach, DeviceAlias, Measurable, Moveable, Override, \
    Param, Value, listof, oneof, status, tupleof
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


class ROIChannel(PostprocessPassiveChannel):
    """Calculates counts for a rectangular or ellipsoid region of interest."""

    parameters = {
        'roi':   Param('Rectangular region of interest (x1, y1, x2, y2)',
                       type=tupleof(int, int, int, int),
                       settable=True, category='general'),
        'shape': Param('Select the shape of the ROI',
                       type=oneof('rectangle', 'ellipse'),
                       settable=True, category='general'),
    }

    parameter_overrides = {
        'unit':   Override(default='cts'),
        'fmtstr': Override(default='%d'),
    }

    def getReadResult(self, arrays, _results, _quality):
        arr = arrays[0]
        if arr is None:
            return [0, 0]
        if any(self.roi):
            x1, y1, x2, y2 = self.roi
            if self.shape == 'rectangle':
                inner = arr[y1:y2, x1:x2].sum()
            else:
                cx = (x1 + x2)/2.
                cy = (y1 + y2)/2.
                y, x = numpy.indices(arr.shape)
                ix = ((y - cy)/(y2 - cy))**2 - ((x - cx)/(x2 - cx))**2 <= 1
                inner = arr[ix].sum()
            outer = arr.sum() - inner
            return [inner, outer]
        return [arr.sum(), 0]

    def valueInfo(self):
        return (Value(name=self.name + '.in', type='counter', fmtstr='%d'),
                Value(name=self.name + '.out', type='counter', fmtstr='%d'))
