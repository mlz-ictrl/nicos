#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
from nicos.utils import readFile, writeFile
from nicos.core import Param, SIMULATION, ArrayDesc, MASTER
from nicos.devices.generic.detector import ActiveChannel, TimerChannelMixin, \
    CounterChannelMixin
from nicos.core.errors import CommunicationError, ConfigurationError, \
    NicosError, ProgrammingError, InvalidValueError
from nicos.devices.vendor.qmesydaq import Image as QMesyDAQImage
from nicos.devices.vendor.caress.core import CORBA, CARESS, CARESSDevice, \
    LOADSLAVE, LOADMASTER, RESETMODULE, READBLOCK_NORMAL, OFF_LINE, \
    LOAD_NORMAL, INIT_NORMAL, INIT_REINIT, ON_LINE


class QMesydaqCaressDevice(CARESSDevice):

    def _init(self, cid):
        try:
            if not self._is_corba_device():
                raise ConfigurationError(self, 'Must be configured as '
                                         '"CORBA_device" (ID=500)')
            _config = ' '.join(self.config.split()[3:])
            self.log.debug('Reduced config: %s', _config)
            res = self._caressObject.init_module(INIT_NORMAL, cid, _config)
            self.log.debug('Init module (Connect): %r', res)
            if res not in [(0, ON_LINE), (CARESS.OK, ON_LINE)]:
                res = self._caressObject.init_module(INIT_REINIT, cid, _config)
                self.log.debug('Init module (Re-Init): %r', res)
                if res not in[(0, ON_LINE), (CARESS.OK, ON_LINE)]:
                    self.log.error('Init module (Re-Init): %r (%d, %s)',
                                   res, cid, _config)
                    raise NicosError(self, 'Could not initialize module!')
            self._initialized = True
        except CORBA.TRANSIENT as err:
            raise CommunicationError(self, 'could not init CARESS module %r '
                                     '(%d: %s)' % (err, cid, self.config)
                                     )

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        CARESSDevice.doInit(self, mode)
        if hasattr(self._caressObject, 'is_counting_module'):
            is_counting = \
                self._caress_guard(self._caressObject.is_counting_module,
                                   self.cid)
        self.log.debug('Counting module: %r', is_counting)
        if not is_counting:
            raise ConfigurationError(self, 'Object is not a measurable module')


class Channel(QMesydaqCaressDevice, ActiveChannel):

    parameters = {
        'runnumber': Param('Run number',
                           type=int, settable=True, default=0,
                           ),
        'counterfile': Param('File storing the run number',
                             type=str, default='runid.txt',
                             ),
    }

    def doSetPreset(self, **preset):
        raise ProgrammingError(self, 'Channel.setPreset should not be called')

    def doStart(self):
        self._reset()

        if not self.ismaster:
            self._load_preset(LOADSLAVE)
            # self._start(0)
        else:
            value = int(self.preselection)
            self._load_preset(LOADMASTER, value)
            self._start(0)
            self.runnumber += 1

    def _start(self, kind):
        if hasattr(self._caressObject, 'start_module'):
            result = self._caress_guard(self._caressObject.start_module, kind,
                                        self.cid, self.runnumber, 0)
        else:
            result = \
                self._caress_guard(self._caressObject.start_acquisition_orb,
                                   kind, self.runnumber, 0)
        if result[0] not in (0, CARESS.OK):
            raise NicosError(self, 'Could not start the module')

    def _stop(self):
        self._break(0)
        self._break(1)

    def doStop(self):
        self._stop()

    def doFinish(self):
        self._stop()

    def _break(self, kind=0):
        if hasattr(self._caressObject, 'stop_module'):
            result = self._caress_guard(self._caressObject.stop_module, kind,
                                        self.cid)
        elif self.ismaster:
            result = \
                self._caress_guard(self._caressObject.stop_acquisition_orb,
                                   kind)
        if result[0] not in [0, CARESS.OK]:
            raise NicosError('Could not set module into paused state!')

    def doPause(self):
        self._break(0)
        return True

    def doResume(self):
        self._start(1)

    def _reset(self):
        try:
            self._load_preset(RESETMODULE)
        except NicosError:
            raise NicosError(self, 'Could not reset module')

    def _load_preset(self, kind, preset=0):
        if hasattr(self._caressObject, 'load_module'):
            result, loaded = self._caress_guard(self._caressObject.load_module,
                                                kind, self.cid,
                                                CARESS.Value(l=preset))
            self.log.debug('Preset module: %r, %r', result, loaded)
        else:
            params = []
            params.append(CORBA.Any(CORBA._tc_long, self.cid))
            params.append(CORBA.Any(CORBA._tc_long, 0))  # status placeholder
            params.append(CORBA.Any(CORBA._tc_long, 1))  # 1 value
            params.append(CORBA.Any(CORBA._tc_long, 2))  # 32 bit int type
            params.append(CORBA.Any(CORBA._tc_long, preset))
            params.append(CORBA.Any(CORBA._tc_long, 0))  # no next module
            result, loaded = self._caress_guard(
                self._caressObject.load_module_orb, kind, params, 0)
            self.log.debug('Preset module: %r %r', result, loaded)
        if result not in [0, CARESS.OK]:
            raise NicosError(self, 'Could not preset module')

    def doReset(self):
        self._reset()

    @property
    def _counterpath(self):
        return path.join(session.experiment.dataroot, self.counterfile)

    def doReadRunnumber(self):
        return int(readFile(self._counterpath)[0])

    def doWriteRunnumber(self, value):
        writeFile(self._counterpath, [str(value)])

    def doRead(self, maxage=0):
        return [self._caress_guard(self._read)[1]]


class Timer(TimerChannelMixin, Channel):
    """Timer for CARESS."""

    pass


class Counter(CounterChannelMixin, Channel):
    """Counter for CARESS."""

    pass


class Image(QMesydaqCaressDevice, QMesyDAQImage):
    """Channel for CARESS that returns the image, histogram, or spectrogram."""

    def doInit(self, mode):
        QMesydaqCaressDevice.doInit(self, mode)
        lconfig = self.config.split()
        self._width = int(lconfig[5])
        self._height = int(lconfig[6])
        if mode == MASTER:
            # self.readImage()  # also set arraydesc
            pass
        if self._mode == SIMULATION:
            return
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
                                       READBLOCK_NORMAL, self.cid, _start,
                                       _end, _type)
                if result != CARESS.OK:
                    raise CommunicationError(self,
                                             'Could not read the CARESS '
                                             'module')
                result, _status, data = \
                    self._caress_guard(self._caressObject.readblock_module,
                                       READBLOCK_NORMAL, self.cid, _start,
                                       _end)
                if result != CARESS.OK:
                    raise CommunicationError(self,
                                             'Could not read the CARESS '
                                             'module')
                # self.log.warning('%r', data)
                return [self._width, self._height, 1] + data.al
            except CORBA.COMM_FAILURE as ex:
                raise CommunicationError(self, 'Could not read the CARESS '
                                         'module : %s' % (ex, ))
        else:
            _ = ()
            result = self._caress_guard(self._caressObject.read_module_orb, 0,
                                        self.cid, _)
            self.log.debug('read_module: %r', result)
            if result[0] != 0:
                raise CommunicationError(self,
                                         'Could not read the CARESS module')
            if result[1][0].value() != self.cid:
                raise NicosError(self, 'Answer from wrong module!: %d %r' %
                                 (self.cid, result[1][0]))
            if result[1][1].value() == OFF_LINE:
                raise NicosError(self, 'Module is off line!')
            if result[1][2].value() < 1:
                raise InvalidValueError(self, 'No position in data')
            return result[1][1].value(), result[1][4].value()

    def doReadArray(self, quality):
        # read data via CARESS and transform it
        res = self._caress_guard(self._readblock)
        # first 3 values are sizes of dimensions
        # evaluate shape return correctly reshaped numpy array
        if (res[1], res[2]) in [(1, 1), (0, 1), (1, 0), (0, 0)]:  # 1D array
            self.arraydesc = ArrayDesc('data', shape=(res[0], ), dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0])
            self.readresult = [data.sum()]
            return data
        elif res[2] in [0, 1]:  # 2D array
            self.arraydesc = ArrayDesc('data', shape=(res[0], res[1]),
                                       dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0] * res[1])
            self.readresult = [data.sum()]
            return data.reshape((res[0], res[1]), order='C')
        else:  # 3D array
            self.arraydesc = ArrayDesc('data', shape=(res[0], res[1], res[2]),
                                       dtype='<u4')
            data = numpy.fromiter(res[3:], '<u4', res[0] * res[1] * res[3])
            self.readresult = [data.sum()]
            return data.reshape((res[0], res[1], res[2]), order='C')
        return None

    def _set_option(self, text):
        self.log.debug('set_option: %s', text)
        if hasattr(self._caressObject, 'loadblock_module'):
            self._caressObject.loadblock_module(LOAD_NORMAL, self.cid, 1,
                                                len(text),
                                                CARESS.Value(ab=text))

    def doWriteListmodefile(self, value):
        self._set_option(text='mesydaq_listmodefile=%s' % value)

    def doWriteHistogramfile(self, value):
        self._set_option(text='mesydaq_histogramfile=%s' % value)

    def doWriteListmode(self, value):
        self._set_option(text='mesydaq_listmode=%s' % value)

    def doWriteHistogram(self, value):
        self._set_option(text='mesydaq_histogram=%s' % value)

    def doReadConfigfile(self):
        # return self._taco_guard(self._dev.deviceQueryResource, 'configfile')
        return ''

    def doReadCalibrationfile(self):
        # return self._taco_guard(self._dev.deviceQueryResource,
        #                         'calibrationfile')
        return ''
