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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Detector devices for QMesyDAQ type detectors (TANGO)."""

import numpy

from nicos.core.constants import SIMULATION
from nicos.core.params import Param, Value, listof, oneof
from nicos.devices.tango import ImageChannel as BaseImageChannel
from nicos.devices.vendor.qmesydaq import Image as QMesyDAQImage


class ImageChannel(QMesyDAQImage, BaseImageChannel):

    parameters = {
        'readout': Param('Readout mode of the Detector', settable=True,
                         type=oneof('raw', 'mapped', 'amplitude'),
                         default='mapped', mandatory=False, chatty=True),
    }

    def doWriteListmode(self, value):
        self._dev.SetProperties(['writelistmode', '%s' % value])
        return self._getProperty('writelistmode')

    def doWriteHistogram(self, value):
        self._dev.SetProperties('writehistogram', '%s' % value)
        return self._getProperty('writehistogram')

    def doWriteReadout(self, value):
        self._dev.SetProperties(['histogram', '%s' % value])
        return self._getProperty('histogram')

    def doWriteListmodefile(self, value):
        self._dev.SetProperties(['lastlistfile', '%s' % value])
        return self._getProperty('lastlistfile')

#   def doReadListmodefile(self):
#       return self._getProperty('lastlistfile')

    def doWriteHistogramfile(self, value):
        self._taco_update_resource('lasthistfile', '%s' % value)
        return self._getProperty('lasthistfile')

#   def doReadHistogramfile(self):
#       return self._getProperty('lasthistfile')

    def doReadConfigfile(self):
        return self._getProperty('configfile')

    def doReadCalibrationfile(self):
        return self._getProperty('calibrationfile')


class MultiCounter(BaseImageChannel):
    """Channel for QMesyDAQ that allows to access selected channels in a
    multi-channel setup.
    """

    parameters = {
        'channels': Param('Tuple of active channels (1 based)', settable=True,
                          type=listof(int)),
    }

    def doRead(self, maxage=0):
        if self._mode == SIMULATION:
            res = [0] * (max(self.channels) + 3)
        else:
            # read data via Tango and transform it
            val = self._dev.value
            res = val.tolist() if isinstance(val, numpy.ndarray) else val
        expected = 3 + max(self.channels or [0])
        # first 3 values are sizes of dimensions
        if len(res) >= expected:
            data = res[3:]
            # ch is 1 based, data is 0 based
            total = sum([data[ch - 1] for ch in self.channels])
        else:
            self.log.warning('not enough data returned, check config! '
                             '(got %d elements, expected >=%d)',
                             len(res), expected)
            data = None
            total = 0
        resultlist = [total]
        if data is not None:
            for ch in self.channels:
                # ch is 1 based, data is 0 based
                resultlist.append(data[ch - 1])
        return resultlist

    def valueInfo(self):
        resultlist = [Value('ch.sum', unit='cts', errors='sqrt',
                            type='counter', fmtstr='%d')]
        for ch in self.channels:
            resultlist.append(Value('ch%d' % ch, unit='cts', errors='sqrt',
                                    type='counter', fmtstr='%d'))
        return tuple(resultlist)

    def doReadIsmaster(self):
        return False

    def doReadFmtstr(self):
        return ', '.join(['sum %d'] + ['ch%d %%d' % ch for ch in self.channels])
