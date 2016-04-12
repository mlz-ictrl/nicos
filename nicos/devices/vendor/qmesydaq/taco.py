#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Detector devices for QMesyDAQ type detectors."""

import numpy

import IO
import IOCommon
from Detector import Detector

from nicos.core import ArrayDesc, Param, MASTER, SIMULATION, FINAL, Value, \
    listof, oneof
from nicos.devices.generic import TimerChannelMixin, CounterChannelMixin, \
    PassiveChannel, ActiveChannel
from nicos.devices.taco.detector import BaseChannel as TacoBaseChannel
from nicos.devices.vendor.qmesydaq import Image as QMesyDAQImage


class BaseChannel(TacoBaseChannel):
    """Base class for one channel of the QMesyDaq.

    Use one of the concrete classes below.
    """

    def doResume(self):
        self._taco_guard(self._dev.start)

    def doWriteIsmaster(self, value):
        self._taco_guard(self._dev.stop)
        self._taco_guard(self._dev.setMode(IOCommon.MODE_PRESELECTION if value
                                           else IOCommon.MODE_NORMAL))
        self._taco_guard(self._dev.enableMaster, value)


class Timer(TimerChannelMixin, BaseChannel, ActiveChannel):
    """
    Timer channel for QMesyDAQ detector.
    """

    taco_class = IO.Timer


class Counter(CounterChannelMixin, BaseChannel, ActiveChannel):
    """
    Monitor/counter channel for QMesyDAQ detector.
    """

    taco_class = IO.Counter


class MultiCounter(BaseChannel, PassiveChannel):
    """Channel for QMesyDAQ that allows to access selected channels in a
    multi-channel setup.
    """

    parameters = {
        'channels': Param('tuple of active channels (1 based)', settable=True,
                          type=listof(int)),
    }

    taco_class = Detector

    def doRead(self, maxage=0):
        if self._mode == SIMULATION:
            res = [0] * (max(self.channels) + 3)
        else:
            # read data via taco and transform it
            res = self._taco_guard(self._dev.read)
        expected = 3 + max(self.channels or [0])
        # first 3 values are sizes of dimensions
        if len(res) >= expected:
            data = res[3:]
            # ch is 1 based, _data is 0 based
            total = sum([self._data[ch - 1] for ch in self.channels])
        else:
            self.log.warning(self, 'not enough data returned, check config! '
                             '(got %d elements, expected >=%d)' %
                             (len(res), expected))
            data = None
            total = 0
        resultlist = [total]
        if data is not None:
            for ch in self.channels:
                # ch is 1 based, _data is 0 based
                resultlist.append(data[ch - 1])
        return resultlist

    def valueInfo(self):
        resultlist = [Value('ch.sum', unit='cts', errors='sqrt',
                            type='counter', fmtstr='%d')]
        for ch in self.channels:
            resultlist.append(Value('ch%d' % ch, unit='cts', errors='sqrt',
                                    type='counter', fmtstr='%d'))
        return tuple(resultlist)

    def doReadFmtstr(self):
        resultlist = ['sum %d']
        for ch in self.channels:
            resultlist.append('ch%d %%d' % ch)
        return ', '.join(resultlist)


class Image(BaseChannel, QMesyDAQImage):
    """Channel for QMesyDAQ that returns the last image."""

    parameters = {
        'readout': Param('Readout mode of the Detector', settable=True,
                         type=oneof('raw', 'mapped', 'amplitude'),
                         default='mapped', mandatory=False, chatty=True)
    }

    taco_class = Detector

    def doInit(self, mode):
        if mode == MASTER:
            self.readArray(FINAL)  # also set arraydesc

    def doStart(self):
        self.readresult = [0]
        BaseChannel.doStart(self)

    def doWriteReadout(self, value):
        try:
            self._taco_guard(self._dev.deviceOff)
            self._taco_guard(self._dev.deviceUpdateResource, 'histogram',
                             value)
        finally:
            self._taco_guard(self._dev.deviceOn)
        return self._taco_guard(self._dev.deviceQueryResource, 'histogram')

    def doReadArray(self, quality):
        # read data via taco and transform it
        res = self._taco_guard(self._dev.read)
        # first 3 values are sizes of dimensions
        # evaluate shape return correctly reshaped numpy array
        if (res[1], res[2]) in [(1, 1), (0, 1), (1, 0), (0, 0)]:  # 1D array
            self.arraydesc = ArrayDesc('data', shape=(res[0], ), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0])
            self.readresult = [data.sum()]
            return data
        elif res[2] in [0, 1]:  # 2D array
            self.arraydesc = ArrayDesc('data', shape=(res[0], res[1]), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0]*res[1])
            self.readresult = [data.sum()]
            return data.reshape((res[0], res[1]), order='C')
        else:  # 3D array
            self.arraydesc = ArrayDesc('data', shape=(res[0], res[1], res[2]),
                                       dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0]*res[1]*res[3])
            self.readresult = [data.sum()]
            return data.reshape((res[0], res[1], res[2]), order='C')
        return None

    def doWriteListmodefile(self, value):
        self._taco_guard(self._dev.deviceUpdateResource, 'lastlistfile', '%s' %
                        value)

    def doWriteHistogramfile(self, value):
        self._taco_guard(self._dev.deviceQueryResource, 'lasthistfile', '%s' %
                         value)

    def doReadListmodefile(self, value):
        return self._taco_guard(self._dev.deviceQueryResource, 'lastlistfile'),

    def doReadHistogramfile(self, value):
        return self._taco_guard(self._dev.deviceQueryResource, 'lasthistfile'),
