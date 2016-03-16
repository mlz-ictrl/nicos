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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Devices via the CARESS device service."""

from os import path

import numpy

from nicos import session
from nicos.utils import readFileCounter, updateFileCounter
from nicos.core import Param, SIMULATION, ImageType, MASTER
from nicos.devices.generic.detector import ActiveChannel, TimerChannelMixin, \
    CounterChannelMixin
from nicos.core.errors import CommunicationError, ConfigurationError, \
    NicosError, ProgrammingError, InvalidValueError
from nicos.devices.vendor.qmesydaq import Image as QMesyDAQImage
from nicos.devices.vendor.caress.core import CORBA, CARESS, CARESSDevice, \
    LOADSLAVE, LOADMASTER, RESETMODULE, READBLOCK_NORMAL, OFF_LINE, LOAD_NORMAL


class Channel(CARESSDevice, ActiveChannel):

    parameters = {
        'runnumber': Param('Run number',
                           type=int, settable=True,
                           ),
        'counterfile': Param('File storing the run number',
                             type=str, default='runid.txt',
                             ),
    }

    def doInit(self, mode):
        CARESSDevice.doInit(self, mode)
        if mode == SIMULATION:
            return
        if hasattr(self._caressObject, 'is_counting_module'):
            is_counting = \
                self._caress_guard(self._caressObject.is_counting_module,
                                   self._cid)
        else:
            is_counting = self._device_kind() in [1, 2, 5, 8, 19, 20, 58, 59,
                                                  63, 64, 74, 101, 102, 109,
                                                  113, 116, 117, 121, 122]
        self.log.debug('Counting module: %r' % (is_counting,))
        if not is_counting:
            raise ConfigurationError(self, 'Object is not a measurable module')

    def doSetPreset(self, **preset):
        raise ProgrammingError(self, 'Channel.setPreset should not be called')

    def doStart(self):
        self._reset()

        if not self.ismaster:
            self._load_preset(LOADSLAVE)
            # self._start(0)
        else:
            if isinstance(self, (Timer,)):
                value = 5 * int(self.preselection * 100)
            else:
                value = int(self.preselection)
            self._load_preset(LOADMASTER, value)
            self._start(0)
            self.runnumber += 1

    def _start(self, kind):
        if hasattr(self._caressObject, 'start_module'):
            result = self._caress_guard(self._caressObject.start_module, kind,
                                        self._cid, self.runnumber, 0)
            if result[0] != CARESS.OK:
                raise NicosError(self, 'Could not start the module')
        else:
            result = \
                self._caress_guard(self._caressObject.start_acquisition_orb,
                                   kind, self.runnumber, 0)
            if result[0] != 0:
                raise NicosError(self, 'Could not start the module')

    def doFinish(self):
        self._break(0)
        self._break(1)

    def _break(self, kind=0):
        if hasattr(self._caressObject, 'stop_module'):
            result = self._caress_guard(self._caressObject.stop_module, kind,
                                        self._cid)
            if result[0] != CARESS.OK:
                raise NicosError('Could not set module into paused state!')
        elif self.ismaster:
            result = \
                self._caress_guard(self._caressObject.stop_acquisition_orb,
                                   kind)
            if result[0] != 0:
                raise NicosError('Could not set module into paused state!')

    def doPause(self):
        self._break(0)

    def doResume(self):
        self._start(1)

    def _reset(self):
        self._load_preset(RESETMODULE)

    def _load_preset(self, kind, preset=0):
        if hasattr(self._caressObject, 'load_module'):
            result, loaded = self._caress_guard(self._caressObject.load_module,
                                                kind, self._cid,
                                                CARESS.Value(l=preset))
            self.log.debug('Preset module: %r, %r' % (result, loaded))
            if result != CARESS.OK:
                raise NicosError(self, 'Could not reset module')
        else:
            params = []
            params.append(CORBA.Any(CORBA._tc_long, self._cid))
            params.append(CORBA.Any(CORBA._tc_long, 0))  # status placeholder
            params.append(CORBA.Any(CORBA._tc_long, 1))  # 1 value
            params.append(CORBA.Any(CORBA._tc_long, 2))  # 32 bit int type
            params.append(CORBA.Any(CORBA._tc_long, preset))
            params.append(CORBA.Any(CORBA._tc_long, 0))  # no next module
            result = self._caress_guard(self._caressObject.load_module_orb,
                                        kind, params, 0)
            self.log.debug('Preset module: %r' % (result,))
            if result[0] != 0:
                raise NicosError(self, 'Could not reset module')

    def doReset(self):
        self._reset()

    def doReadRunnumber(self):
        return readFileCounter(path.join(session.experiment.dataroot,
                                         self.counterfile))

    def doWriteRunnumber(self, value):
        updateFileCounter(path.join(session.experiment.dataroot,
                                    self.counterfile), value)


class Timer(TimerChannelMixin, Channel):

    def doRead(self, maxage=0):
        return [(self._caress_guard(self._read)[1] / 100.) / 5]


class Counter(CounterChannelMixin, Channel):

    def doRead(self, maxage=0):
        return [self._caress_guard(self._read)[1]]


class Image(CARESSDevice, QMesyDAQImage):
    """Channel for CARESS that returns the image, histogram, or spectrogram."""

    def doInit(self, mode):
        lconfig = self.config.split()
        lconfig = lconfig[:2] + lconfig[4:]
        self._width = int(lconfig[2])
        self._height = int(lconfig[3])
        self._setROParam('config', ' '.join(lconfig))
        CARESSDevice.doInit(self, mode)
        if mode == SIMULATION:
            return
        if hasattr(self._caressObject, 'is_counting_module'):
            is_counting = \
                self._caress_guard(self._caressObject.is_counting_module,
                                   self._cid)
        else:
            is_counting = self._device_kind() in [1, 2, 5, 8, 19, 20, 58, 59,
                                                  63, 64, 74, 101, 102, 109,
                                                  113, 116, 117, 121, 122]
        self.log.debug('Counting module: %r' % (is_counting,))
        if not is_counting:
            raise ConfigurationError(self, 'Object is not a measurable module')
        if mode == MASTER:
            # self.readImage()  # also set imagetype
            pass
        self._set_option(text='mesydaq_32bit=True')

    def doStart(self):
        self.readresult = [0]

    def doRead(self, maxage=0):
        return [self._caress_guard(self._read)[1]]

#   def doWriteReadout(self, value):
#       try:
#           self._taco_guard(self._dev.deviceOff)
#           self._taco_guard(self._dev.deviceUpdateResource, 'histogram',
#                            value)
#       finally:
#           self._taco_guard(self._dev.deviceOn)
#       return self._taco_guard(self._dev.deviceQueryResource, 'histogram')

    def _readblock(self):
        if hasattr(self._caressObject, 'readblock_module') and \
           hasattr(self._caressObject, 'readblock_params'):
            _type = CARESS.TypeLong
            _start = 0
            _end = 0
            try:
                result, _start, _end, _type = \
                    self._caress_guard(self._caressObject.readblock_params,
                                       READBLOCK_NORMAL, self._cid, _start,
                                       _end, _type)
                if result != CARESS.OK:
                    raise CommunicationError(self,
                                             'Could not read the CARESS '
                                             'module')
                result, _status, data = \
                    self._caress_guard(self._caressObject.readblock_module,
                                       READBLOCK_NORMAL, self._cid, _start,
                                       _end)
                if result != CARESS.OK:
                    raise CommunicationError(self,
                                             'Could not read the CARESS '
                                             'module')
                # self.log.warning('%r' % data)
                return [self._width, self._height, 1] + data.al
            except CORBA.COMM_FAILURE as ex:
                raise CommunicationError(self, 'Could not read the CARESS '
                                         'module : %s' % (ex, ))
        else:
            _ = ()
            result = self._caress_guard(self._caressObject.read_module_orb, 0,
                                        self._cid, _)
            self.log.debug('read_module: %r' % (result,))
            if result[0] != 0:
                raise CommunicationError(self,
                                         'Could not read the CARESS module')
            if result[1][0].value() != self._cid:
                raise NicosError(self, 'Answer from wrong module!: %d %r' %
                                 (self._cid, result[1][0]))
            if result[1][1].value() == OFF_LINE:
                raise NicosError(self, 'Module is off line!')
            if result[1][2].value() < 1:
                raise InvalidValueError(self, 'No position in data')
            return result[1][1].value(), result[1][4].value()

    def readFinalImage(self):
        if self._mode == SIMULATION:
            # simulated readout of an 128*128 image
            res = [128, 128, 1] + [0] * (128 * 128)
        else:
            # read data via taco and transform it
            res = self._caress_guard(self._readblock)
        # first 3 values are sizes of dimensions
        # evaluate shape return correctly reshaped numpy array
        if (res[1], res[2]) in [(1, 1), (0, 1), (1, 0), (0, 0)]:  # 1D array
            self.imagetype = ImageType('data', shape=(res[0], ), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0])
            self.readresult = [data.sum()]
            return data
        elif res[2] in [0, 1]:  # 2D array
            self.imagetype = ImageType('data', shape=(res[0], res[1]), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0]*res[1])
            self.readresult = [data.sum()]
            return data.reshape((res[0], res[1]), order='C')
        else:  # 3D array
            self.imagetype = ImageType('data', shape=(res[0], res[1], res[2]),
                                       dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0]*res[1]*res[3])
            self.readresult = [data.sum()]
            return data.reshape((res[0], res[1], res[2]), order='C')
        return None

    def _set_option(self, text):
        self.log.debug('set_option: %s' % text)
        if hasattr(self._caressObject, 'loadblock_module'):
            self._caressObject.loadblock_module(LOAD_NORMAL, self._cid, 1,
                                                len(text),
                                                CARESS.Value(ab=text))

    def doWriteListmodefile(self, value):
        self._set_option(text='mesydaq_listmodefile=%s' % value)

    def doWriteHistogramfile(self, value):
        self._set_option(text='mesydaq_histogramfile=%s' % value)
