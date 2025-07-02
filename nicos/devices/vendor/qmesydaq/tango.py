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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Detector devices for QMesyDAQ type detectors (TANGO)."""

import numpy as np

from nicos.core.params import Override, Param, Value, listof, oneof
from nicos.devices.entangle import CounterChannel as BaseCounterChannel, \
    ImageChannel as BaseImageChannel, TimerChannel as BaseTimerChannel
from nicos.devices.vendor.qmesydaq import Image as QMesyDAQImage


class TimerChannel(BaseTimerChannel):
    """Detector channel to measure time."""

    def doFinish(self):
        self.doStatus(0)
        BaseTimerChannel.doFinish(self)

    def doStop(self):
        self.doStatus(0)
        BaseTimerChannel.doStop(self)


class CounterChannel(BaseCounterChannel):
    """Detector channel to count events."""

    def doFinish(self):
        self.doStatus(0)
        BaseCounterChannel.doFinish(self)

    def doStop(self):
        self.doStatus(0)
        BaseCounterChannel.doStop(self)


class ImageChannel(QMesyDAQImage, BaseImageChannel):
    """Detector channel for delivering images.

    It automatically returns the sum of all counts.
    """

    parameters = {
        'readout': Param('Readout mode of the Detector', settable=True,
                         type=oneof('raw', 'mapped', 'amplitude'),
                         default='mapped', mandatory=False, chatty=True),
        'flipaxes': Param('Flip data along these axes after reading from det',
                          type=listof(int), default=[], unit=''),
        'transpose': Param('Whether to transpose the image',
                           type=bool, default=False),
    }

    # Use the configuration from QMesyDAQ
    parameter_overrides = {
        'listmode': Override(volatile=True),
        'histogram': Override(volatile=True),
    }

    def doReadRoisize(self):
        tmp = self._dev.roiSize.tolist()
        return tmp if sum(tmp) else (1, 1)

    def doWriteListmode(self, value):
        self._dev.SetProperties(['writelistmode', ('%s' % value).lower()])
        return self.doReadListmode()

    def doReadListmode(self):
        return {'false': False, 'true': True}[
            self._getProperty('writelistmode')]

    def doWriteHistogram(self, value):
        self._dev.SetProperties(['writehistogram', ('%s' % value).lower()])
        return self.doReadHistogram()

    def doReadHistogram(self):
        return {'false': False, 'true': True}[
            self._getProperty('writehistogram')]

    def doWriteReadout(self, value):
        self._dev.SetProperties(['histogram', value])
        return self._getProperty('histogram')

    def doWriteListmodefile(self, value):
        self._dev.SetProperties(['lastlistfile', value])
        return self._getProperty('lastlistfile')

#   def doReadListmodefile(self):
#       return self._getProperty('lastlistfile')

    def doWriteHistogramfile(self, value):
        self._dev.SetProperties(['lasthistfile', value])
        return self._getProperty('lasthistfile')

#   def doReadHistogramfile(self):
#       return self._getProperty('lasthistfile')

    def doReadConfigfile(self):
        return self._getProperty('configfile')

    def doReadCalibrationfile(self):
        return self._getProperty('calibrationfile')

    def doReadArray(self, quality):
        narray = BaseImageChannel.doReadArray(self, quality)
        if self.transpose:
            narray = np.transpose(narray)
        for axis in self.flipaxes:
            narray = np.flip(narray, axis)
        return narray

    def doFinish(self):
        self.doStatus(0)
        BaseImageChannel.doFinish(self)

    def doStop(self):
        self.doStatus(0)
        BaseImageChannel.doStop(self)


class MultiCounter(BaseImageChannel):
    """Channel for QMesyDAQ that allows to access selected channels in a
    multi-channel setup.
    """

    parameters = {
        'channels': Param('Tuple of active channels (1 based)', settable=True,
                          type=listof(int)),
    }

    def doRead(self, maxage=0):
        # read data via Tango and transform it
        val = self._dev.value
        res = val.tolist() if isinstance(val, np.ndarray) else val
        expected = max(self.channels or [0])
        if len(res) >= expected:
            # ch is 1 based, data is 0 based
            total = sum(res[ch - 1] for ch in self.channels)
        else:
            self.log.warning('not enough data returned, check config! '
                             '(got %d elements, expected >=%d)',
                             len(res), expected)
            res = None
            total = 0
        resultlist = [total]
        if res is not None:
            for ch in self.channels:
                # ch is 1 based, data is 0 based
                resultlist.append(res[ch - 1])
        return resultlist

    def doFinish(self):
        self.doStatus(0)
        BaseImageChannel.doFinish(self)

    def doStop(self):
        self.doStatus(0)
        BaseImageChannel.doStop(self)

    def valueInfo(self):
        resultlist = [Value('ch.sum', unit='cts', errors='sqrt',
                            type='counter', fmtstr='%d')]
        for ch in self.channels:
            resultlist.append(Value('ch%d' % ch, unit='cts', errors='sqrt',
                                    type='counter', fmtstr='%d'))
        return tuple(resultlist)

    def doReadIscontroller(self):
        return False

    def doReadFmtstr(self):
        return ', '.join(['sum %d'] + ['ch%d %%d' % ch for ch in self.channels])
