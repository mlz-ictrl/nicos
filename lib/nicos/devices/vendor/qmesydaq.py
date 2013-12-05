#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
    ImageProducer, ImageType, Measurable
from nicos.devices.fileformats import LiveViewSink
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

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
        'mode': Override(type=oneofdict({
                             IOCommon.MODE_NORMAL: 'normal',
                             #IOCommon.MODE_RATEMETER: 'ratemeter', # not working
                             IOCommon.MODE_PRESELECTION: 'preselection'})),
    }

    def doStatus(self, maxage=0):
        state = self._taco_guard(self._dev.deviceState)
        if state == TACOStates.PRESELECTION_REACHED:
            return status.OK, 'preselection reached'
        elif state == TACOStates.STOPPED:
            return status.OK, 'idle or paused'
        elif state == TACOStates.DEVICE_NORMAL:
            return status.OK, 'idle'
        else:
            return status.BUSY, TACOStates.stateDescription(state)

    def doIsCompleted(self):
        state = self._taco_guard(self._dev.deviceState)
        self.log.debug('doIsCompleted: state=%d' % state)
        return state in [TACOStates.PRESELECTION_REACHED, TACOStates.DEVICE_NORMAL]

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


class QMesyDAQDet(ImageProducer, TacoDevice, Measurable):
    """
    Detector for QMesyDAQ that combines multiple channels to a single Measurable
    detector device.

    It also contains the managing and start/stop logic and reads the histogram
    data which is provided to the attached filesavers for storage.
    """

    # only one of those is required, all others are optional!
    attached_devices = {
        'events' : (QMesyDAQCounter, 'Timer channel'),
        'timer':    (QMesyDAQTimer, 'Timer channel'),
        'monitors': ([QMesyDAQCounter], 'Monitor channels'),
        'counters': ([QMesyDAQCounter], 'Counter channels')
    }

    taco_class = Detector
    _filesavers = []

    parameters = {
        'lastcounts' : Param('Current total number of counts', settable=True,
                             type=int, userparam=False),
        'readout'    : Param('Readout mode of the Detector', settable=True,
                             type=oneof('raw','mapped','amplitude','none'),
                             default='mapped', mandatory=False, chatty=True)
    }

    parameter_overrides = {
        'fmtstr': Override(default='%s'),
        'mode': Override(userparam=False, default='normal', type=oneofdict({
                             IOCommon.MODE_NORMAL: 'normal'})),
    }

    # initial imagetype, will be updated upon readImage
    _imagetype = ImageType((128, 128), '<u4')

    def doPreinit(self, mode):
        self._counters = []
        self._presetkeys = {}
        self._master = None
        self._isPause = False
        self._filesavers = []

        TacoDevice.doPreinit(self, mode)
        def myiter(self):
            # return name, device for all devices we allow to be preset
            dev = self._adevs['timer']
            if dev:
                yield ('t', dev)
                yield ('time', dev)
            dev = self._adevs['events']
            if dev:
                yield ('events', dev)
            for i, dev in enumerate(self._adevs['monitors']):
                yield ('mon%d' % (i+1), dev)
            for i, dev in enumerate(self._adevs['counters']):
                yield ('ctr%d' % (i+1), dev)
            for dev in self._adevs['monitors'] + self._adevs['counters']:
                yield (dev.name, dev)

        for name, dev in myiter(self):
            if dev not in self._counters:
                self._counters.append(dev)
            # later mentioned presetnames dont overwrite earlier ones
            self._presetkeys.setdefault(name, dev)
        self._getMaster()

    def doInit(self, mode):
        self._filesavers = [ff for ff in self._adevs['fileformats']
                             if not isinstance(ff, LiveViewSink)]
        self.readImage() # also set imagetype

    def _getMaster(self):
        """Internal method to get the current master."""
        self._master = None
        for counter in self._counters:
            if counter.ismaster:
                self._master = counter

    def doSetPreset(self, **preset):
        self.doStop()
        self.log.debug('setting preset info %r' % preset)
        if self._master:
            self._master.ismaster = False
            self._master.mode = 'normal'
        master = None
        for name in preset:
            if name in self._presetkeys:
                if master:
                    self.log.error('Only one Master is supported, ignoring '
                                   'preset %s=%s'%(name, preset[name]))
                    continue
                dev = self._presetkeys[name]
                dev.ismaster = True
                dev.mode = 'preselection'
                dev.preselection = preset[name]
                master = dev
        if not master:
            self.log.warning('No usable preset given, '
                             'detector will not stop by itself!')
        self._getMaster()

    #
    # Measurable/TacoDevice interface
    #
    def doStart(self):
        self.doStop()
        self._getMaster()
        self.log.debug('starting subdevices')
        for dev in self._counters:
            if dev != self._master:
                dev.start()
        if self._master:
            self._master.start()
        else:
            self.log.warning('counting without master, use "stop(%s)" to '
                             'finish the counting...' % self.name)
        # qmesydaq special: 2D device is started last
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
        self._getMaster()

    def presetInfo(self):
        return set(self._presetkeys)

    def doStatus(self, maxage=0):
        state = self._taco_guard(self._dev.deviceState)
        if state in (TACOStates.PRESELECTION_REACHED, TACOStates.DEVICE_NORMAL):
            return status.OK, 'idle'
        elif state == TACOStates.STOPPED:
            return status.PAUSED, 'paused'
        elif state == TACOStates.COUNTING:
            return status.BUSY, 'counting'
        return status.ERROR, TACOStates.stateDescription(state)

    def doIsCompleted(self):
        if self._isPause:
            return False
        state = self._taco_guard(self._dev.deviceState)
        return state in (TACOStates.PRESELECTION_REACHED, TACOStates.DEVICE_NORMAL)

    def duringMeasureHook(self, elapsed):
        self.log.debug('duringMeasureHook(%f)' % elapsed)
        # XXX only do this every 0.X seconds!
        self.updateImage()

    def doRead(self, maxage=0):
        resultlist = [i for ctr in self._counters for i in ctr.read()] + \
                     [self.lastcounts]
        # appending image infos is a litle more difficult as not all filesavers may be active....
        for ff in self._filesavers:
            for ii in self._imageinfos:
                if ii.filesaver == ff:
                    resultlist.append(ii.filename)
                    break
            else: # no match, 'invent' some value as placeholder
                resultlist.append('-')
        if self.readout == 'none': # no readout, transfer qmesydaqs version of filenames...
            resultlist.append(self._taco_guard(self._dev.deviceQueryResource, 'lastlistfile'))
            resultlist.append(self._taco_guard(self._dev.deviceQueryResource, 'lasthistfile'))
        return resultlist

    def valueInfo(self):
        resultlist = [i for ctr in self._counters for i in ctr.valueInfo()] + \
                     [Value(self.name+'.sum', unit='cts', errors='sqrt', type='counter', fmtstr='%d')] + \
                     [Value(self.name+'.'+ff.fileFormat, unit='file', type='info', fmtstr='%s') for ff in self._filesavers]
        if self.readout == 'none': # no readout, transfer qmesydaqs version of filenames...
            resultlist.append(Value('listfile', unit='file', type='info',fmtstr='%s'))
            resultlist.append(Value('histfile', unit='file', type='info',fmtstr='%s'))
        return tuple(resultlist)

    #
    # Parameters
    #
    def doReadFmtstr(self):
        resultlist = ['%s: %s' % (ctr.name, ctr.fmtstr) for ctr in self._counters] + \
                     ['lastcounts %d'] + \
                     ['%s %%s' % ff.fileFormat for ff in self._filesavers]
        if self.readout == 'none': # no readout, transfer qmesydaqs version of filenames...
            resultlist.append('listfile %s')
            resultlist.append('histfile %s')
        return ', '.join(resultlist)

    #~ def doReadReadout(self):
        #~ return 'mapped'

    def doWriteReadout(self, value):
        if value != 'none':
            self._taco_guard(self._dev.deviceOff)
            self._taco_guard(self._dev.deviceUpdateResource, 'histogram', value)
            self._taco_guard(self._dev.deviceOn)

    #
    # ImageProducer interface
    #
    def clearImage(self):
        self._taco_guard(self._dev.clear)

    def readImage(self):
        # read data via taco and transform it
        res = self._taco_guard(self._dev.read)
        # first 3 values are sizes of dimensions
        self.lastcounts = sum(res[3:]) # maybe also evaluate roi...?
        # evaluate shape return correctly reshaped numpy array
        if res[1:3] in [(1, 1), (0, 1), (1, 0), (0, 0)]: #1D array
            self._imagetype = ImageType(shape=(res[0], ), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0])
            return data
        elif res[2] in [0, 1]: #2D array
            self._imagetype = ImageType(shape=(res[0], res[1]), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0]*res[1])
            return data.reshape((res[0], res[1]), order='C')
        else: #3D array
            self._imagetype = ImageType(shape=(res[0], res[1], res[2]), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0]*res[1]*res[3])
            return data.reshape((res[0], res[1], res[2]), order='C')
        return None

    def readFinalImage(self):
        return self.readImage()
