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
#   Jens Krüger <jens.krueger@frm2.tum.de
#
# *****************************************************************************

"""Virtual devices for testing."""

from __future__ import absolute_import, division, print_function

import math
import time

import dataparser as DataParser
import numpy as np

from nicos.core import Override, Param
from nicos.devices.generic.virtual import VirtualImage as BaseImage
from nicos.utils import findResource


class VirtualImage(BaseImage):
    """A virtual 2-dimensional detector that generates SPODI data from real
    measured data weighted by time.
    """

    parameters = {
        'datafile': Param('File to load the pixel data',
                          type=str, settable=False, default='',
                          ),
        'detname': Param('Name of the whole detectordevice',
                         type=str, settable=False, default='adet',
                         ),
    }

    parameter_overrides = {
        'sizes': Override(default=(80, 256), prefercache=False),
    }

    _rawdata = None

    def doInit(self, mode):
        BaseImage.doInit(self, mode)
        try:
            data = DataParser.CaressFormat(findResource(self.datafile),
                                           self.sizes[1], self.sizes[0])
            self._rawdata = 0.1 * data[3]
            self._resosteps = data[1]
        except (IOError, ValueError):
            self.log.warning('data file %s not present, returning empty array '
                             'from virtual SPODI image', self.datafile)
            self._rawdata = np.zeros(
                self.sizes[0] * self.sizes[1]).reshape(self.sizes)
            self._resosteps = 1

    def _calc_ind_percentage(self, start, end):
        ret = []
        if start % 1:
            ret.append((int(start), 1 - start % 1))
            start = math.ceil(start)
        if end % 1:
            ret.append((int(end), end % 1))
            end = math.floor(end)
        for x in range(int(start), int(end)):
            ret.append((x, 1.))
        return ret

    def _generate(self, t):
        resosteps = self._cache.get(self.detname, 'resosteps')
        step = self._cache.get(self.detname, '_step')
        data = np.zeros(self.sizes[0] * self.sizes[1]).reshape(self.sizes)
        if step < resosteps:
            arng = np.arange(0, 80) * self._resosteps
            stepsize = self._resosteps / resosteps
            start = step * stepsize
            end = (step + 1) * stepsize
            for i, scale in self._calc_ind_percentage(start, end):
                data += self._rawdata[arng + i] * scale
        return t * np.random.poisson(data)

    def _run(self):
        while not self._stopflag:
            elapsed = self._timer.elapsed_time()
            self.log.debug('update image: elapsed = %.1f', elapsed)
            array = self._generate(self._base_loop_delay)
            self._buf = self._buf + array
            self.readresult = [self._buf.sum().astype('<u4')]
            time.sleep(self._base_loop_delay)

    def doReadArray(self, _quality):
        return self._buf.astype('<u4')
