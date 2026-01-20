# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Alexander Söderqvist <alexander.soederqvist@psi.ch>
#
# *****************************************************************************
"""This file contains manipulations of the Image for nexus writing"""

from nicos import session
from nicos.core import FINAL
from nicos.nexus.elements import CalcData


class SliceTofImage(CalcData):
    """
    This selects a subset of an image whose last
    dimension is a time series array. This code is adapted from focus.
    """
    def __init__(self, image_name, dev_name, start_slice, end_slice, **attrs):
        self._start_slice = start_slice
        self._end_slice = end_slice
        self._image_name = image_name
        self._dev_name = dev_name
        self.dtype = 'int32'
        CalcData.__init__(self, **attrs)

    def _shape(self, dataset):
        dev = session.getDevice(self._dev_name)
        return self._end_slice - self._start_slice, dev.dim[0]-1


    def _calcData(self, dataset):
        image = session.getDevice(self._image_name)
        # Be persistent in getting at array data
        arrayData = image.doReadArray(FINAL)
        if arrayData is not None:
            return arrayData[self._start_slice:self._end_slice][:]
        else:
            session.log.warning("NO IMAGE DATA")
            return arrayData[self._start_slice:self._end_slice][:]
