#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Param, Override, Value, status, oneofdict, oneof, \
    ImageProducer, ImageType, Attach, ConfigurationError, listof, SIMULATION
from nicos.devices.fileformats import LiveViewSink
from nicos.devices.generic.detector import Channel, MultiChannelDetector
from nicos.devices.taco.detector import FRMChannel, FRMTimerChannel, \
    FRMCounterChannel
from nicos.devices.taco.core import TacoDevice

import IOCommon
import TACOStates
from Detector import Detector


class QMesyDAQChannel(FRMChannel):
    """Base class for one channel of the QMesyTec.

    Use one of the concrete classes below.
    """

    hardware_access = True

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
        'mode': Override(type=oneofdict({
                             IOCommon.MODE_NORMAL: 'normal',
                             # IOCommon.MODE_RATEMETER: 'ratemeter', # not working
                             IOCommon.MODE_PRESELECTION: 'preselection'})),
    }

    def doStart(self):
        self._taco_guard(self._dev.clear)
        self._taco_guard(self._dev.start)


class QMesyDAQTimer(QMesyDAQChannel, FRMTimerChannel):
    """
    Timer channel for QMesyDAQ detector.
    """


class QMesyDAQCounter(QMesyDAQChannel, FRMCounterChannel):
    """
    Monitor/counter channel for QMesyDAQ detector.
    """


class QMesyDAQBase(TacoDevice, MultiChannelDetector):
    """
    Detector for QMesyDAQ that combines multiple channels to a single Measurable
    detector device.
    """

    # we also may have an total event counter
    # timer, monitors and counters ae defined in MultiChannelDetector
    attached_devices = {
        'events':  Attach('Events channel', Channel, optional=True),
    }

    parameters = {
        'lastcounts':    Param('Current total number of counts', settable=True,
                               type=int, userparam=False),
        'lastlistfile':  Param('last eventmode list file on QMesyDAQ Server',
                               settable=False, mandatory=False, volatile=True,
                               type=str, category='general'),
        'lasthistfile':  Param('last histogrammed file on QMesyDAQ Server',
                               settable=False, mandatory=False, volatile=True,
                               type=str, category='general'),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%s'),
        'mode':   Override(userparam=False, default='normal',
                           type=oneofdict({IOCommon.MODE_NORMAL: 'normal'})),
    }

    taco_class = Detector

    _TACO_STATUS_MAPPING = {
        TACOStates.DEVICE_NORMAL: (status.OK, 'idle'),
        TACOStates.PRESELECTION_REACHED: (status.OK, 'idle'),
        TACOStates.STOPPED: (status.OK, 'paused'),
        TACOStates.COUNTING: (status.BUSY, 'counting'),
    }

    hardware_access = True
    multi_master = False

    def _presetiter(self):
        dev = self._adevs['events']
        if dev:
            yield ('events', dev)
        for name, dev in MultiChannelDetector._presetiter(self):
            yield (name, dev)

    def doPreinit(self, mode):
        self._isPause = False
        self._data  = []
        TacoDevice.doPreinit(self, mode)
        MultiChannelDetector.doPreinit(self, mode)

    #
    # Measurable/TacoDevice interface
    #
    def doStart(self):
        self.doStop()
        self._getMasters()
        self.log.debug('clearing old data')
        self._taco_guard(self._dev.clear)
        self.log.debug('starting subdevices')
        for dev in self._slaves:
            dev.start()
        for master in self._masters:
            master.start()
        if not self._masters:
            self.log.warning('counting without master, use "stop(%s)" to '
                             'finish the counting...' % self.name)
        # qmesydaq special: Histogramming/2D device is started last
        self.lastcounts = 0
        self._taco_guard(self._dev.start)
        self.log.debug('Image acquisition started')

    def doStop(self):
        self._taco_guard(self._dev.stop)
        for dev in self._counters:
            dev.stop()
        self._isPause = False

    def doPause(self):
        self._isPause = True
        self._taco_guard(self._dev.stop)

    def doResume(self):
        self._taco_guard(self._dev.start)
        self._isPause = False

    def doReset(self):
        for dev in self._counters:
            dev.reset()
        self._taco_guard(self._dev.reset)
        self._isPause = False
        self._getMasters()

    def doIsCompleted(self):
        if self._isPause:
            return False
        state = self.doStatus(0)[0]
        return state == status.OK

    def doRead(self, maxage=None):
        raise ConfigurationError(self, 'QMesyDAQBase should not be used for a Device!')

    #
    # Parameter
    #
    def doReadLastlistfile(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'lastlistfile')

    def doReadLasthistfile(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'lasthistfile')


class QMesyDAQMultiChannel(QMesyDAQBase):
    """
    Detector for QMesyDAQ that alles to access selected channels in a multi-channel setup.
    """

    parameters = {
        'channels': Param('tuple of active channels (1 based)', settable=True,
                          type=listof(int)),
    }

    def _readData(self):
        if self._mode == SIMULATION:
            res = [0] * (max(self.channels) + 3)
        else:
            # read data via taco and transform it
            res = self._taco_guard(self._dev.read)
        expected = 3 + max(self.channels or [0])
        # first 3 values are sizes of dimensions
        if len(res) >= expected:
            self._data = res[3:]
            # ch is 1 based, _data is 0 based
            self.lastcounts = sum([self._data[ch - 1] for ch in self.channels])
        else:
            self.log.warning(self, 'not enough data returned, check config! '
                                   '(got %d elements, expected >=%d)' % (len(res), expected))
            self._data = None
            self.lastcounts = 0

    def doRead(self, maxage=0):
        resultlist = [i for ctr in self._counters for i in ctr.read()]
        self._readData()
        resultlist.append(self.lastcounts)
        if self._data is not None:
            for ch in self.channels:
                # ch is 1 based, _data is 0 based
                resultlist.append(self._data[ch - 1])
        return resultlist

    def valueInfo(self):
        resultlist = [i for ctr in self._counters for i in ctr.valueInfo()] + \
                     [Value('ch.sum', unit='cts', errors='sqrt',
                            type='counter', fmtstr='%d')]
        for ch in self.channels:
            resultlist.append(Value('ch%d' % ch, unit='cts', errors='sqrt',
                                    type='counter', fmtstr='%d'))
        return tuple(resultlist)

    #
    # Parameters
    #
    def doReadFmtstr(self):
        resultlist = ['%s: %s' % (ctr.name, ctr.fmtstr) for ctr in self._counters] + \
                     ['lastcounts: %d']
        for ch in self.channels:
            resultlist.append('ch%d: %%d' % ch)
        return ', '.join(resultlist)


class QMesyDAQImage(ImageProducer, QMesyDAQBase):
    """
    Extending QMesyDAQBase with an ImageProducer.

    It also contains the managing and start/stop logic and reads the histogram
    data which is provided to the attached filesavers for storage.
    """

    parameters = {
        'readout': Param('Readout mode of the Detector', settable=True,
                         type=oneof('raw', 'mapped', 'amplitude', 'none'),
                         default='mapped', mandatory=False, chatty=True)
    }

    # initial imagetype, will be updated upon readImage
    imagetype = ImageType((128, 128), '<u4')
    _filesavers = []

    def doInit(self, mode):
        self._filesavers = [ff for ff in self._adevs['fileformats']
                            if not isinstance(ff, LiveViewSink)]
        self.readImage()  # also set imagetype

    def duringMeasureHook(self, elapsed):
        self.log.debug('duringMeasureHook(%f)' % elapsed)
        # XXX only do this every 0.X seconds!
        self.updateImage()

    def doRead(self, maxage=0):
        resultlist = [i for ctr in self._counters for i in ctr.read()] + \
                     [self.lastcounts]
        # appending image infos is a litle more difficult as not all filesavers
        # may be active...
        for ff in self._filesavers:
            for ii in self._imageinfos:
                if ii.filesaver == ff:
                    resultlist.append(ii.filename)
                    break
            else:  # no match, 'invent' some value as placeholder
                resultlist.append('-')
        if self.readout == 'none':  # no readout, transfer qmesydaqs version
                                    # of filenames...
            resultlist.append(self.lastlistfile)
            resultlist.append(self.lasthistfile)
        return resultlist

    def valueInfo(self):
        resultlist = [i for ctr in self._counters for i in ctr.valueInfo()] + \
                     [Value(self.name + '.sum', unit='cts', errors='sqrt',
                            type='counter', fmtstr='%d')] + \
                     [Value(self.name + '.' + ff.fileFormat, unit='file',
                            type='info', fmtstr='%s') for ff in self._filesavers]
        if self.readout == 'none':  # no readout, transfer qmesydaqs version of filenames...
            resultlist.append(Value('listfile', unit='file', type='info', fmtstr='%s'))
            resultlist.append(Value('histfile', unit='file', type='info', fmtstr='%s'))
        return tuple(resultlist)

    #
    # Parameters
    #
    def doReadFmtstr(self):
        resultlist = ['%s: %s' % (ctr.name, ctr.fmtstr) for ctr in self._counters] + \
                     ['lastcounts %d'] + \
                     ['%s %%s' % ff.fileFormat for ff in self._filesavers]
        if self.readout == 'none':  # no readout, transfer qmesydaqs version of filenames...
            resultlist.append('listfile %s')
            resultlist.append('histfile %s')
        return ', '.join(resultlist)

    # def doReadReadout(self):
    #     return 'mapped'

    def doWriteReadout(self, value):
        if value != 'none':
            try:
                self._taco_guard(self._dev.deviceOff)
                self._taco_guard(self._dev.deviceUpdateResource, 'histogram', value)
            finally:
                self._taco_guard(self._dev.deviceOn)
            return self._taco_guard(self._dev.deviceQueryResource, 'histogram')

    #
    # ImageProducer Interface
    #
    def clearImage(self):
        if self._mode != SIMULATION:
            self._taco_guard(self._dev.clear)

    def readImage(self):
        if self._mode == SIMULATION:
            # simulated readout of an 128*128 image
            res = [128, 128, 1] + [0] * (128 * 128)
        else:
            # read data via taco and transform it
            res = self._taco_guard(self._dev.read)
        # first 3 values are sizes of dimensions
        # evaluate shape return correctly reshaped numpy array
        if (res[1], res[2]) in [(1, 1), (0, 1), (1, 0), (0, 0)]:  # 1D array
            self.imagetype = ImageType(shape=(res[0], ), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0])
            self.lastcounts = data.sum()
            return data
        elif res[2] in [0, 1]:  # 2D array
            self.imagetype = ImageType(shape=(res[0], res[1]), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0]*res[1])
            self.lastcounts = data.sum()
            return data.reshape((res[0], res[1]), order='C')
        else:  # 3D array
            self.imagetype = ImageType(shape=(res[0], res[1], res[2]), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0]*res[1]*res[3])
            self.lastcounts = data.sum()
            return data.reshape((res[0], res[1], res[2]), order='C')
        return None

    def readFinalImage(self):
        return self.readImage()
