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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from nicos import session

from nicos.core import Measurable
from nicos.core import Param
from nicos.core import status
from nicos.core import tupleof
from nicos.core import oneof
from nicos.core import Override
from nicos.core import ConfigurationError

from nicos.antares.detector.pytangodevice import PyTangoDevice
from nicos.antares.detector import ImageStorageFits

import numpy
from os import path
import time


class LimaCCD(PyTangoDevice, ImageStorageFits, Measurable):

    HSSPEEDS = [5, 3, 1, 0.05]  # Values from camera manual
    VSSPEEDS = [38.55, 76.95]  # Values from camera manual
    PGAINS = [1, 2, 4]  # Values from camera manual


    parameters = {
                  'hwdevice' : Param('Hardware device name', type=str,
                                     mandatory=True, preinit=True),
                  'fastshutter' : Param('Fast shutter device name', type=str,
                                     mandatory=True),
                  'imagewidth'     : Param('Image width',
                                           type=int,
                                           volatile=True,
                                           category='general'),
                  'imageheight'    : Param('Image height',
                                           type=int,
                                           volatile=True,
                                           category='general'),
                  'roi'            : Param('Region of interest',
                                           type=tupleof(int, int, int, int),
                                           settable=True,
                                           default=(0, 0, 0, 0),
                                           volatile=True,
                                           category='general'),
                  'bin'            : Param('Binning (x,y)',
                                           type=tupleof(int, int),
                                           settable=True,
                                           default=(1, 1),
                                           volatile=True,
                                           category='general'),
                  'flip'           : Param('Flipping (x,y)',
                                           type=tupleof(bool, bool),
                                           settable=True,
                                           default=(False, False),
                                           volatile=True,
                                           category='general'),
                  'rotation'       : Param('Rotation',
                                           type=oneof(0, 90, 180, 270),
                                           settable=True,
                                           default=0,
                                           volatile=True,
                                           category='general'),
                  'shutteropentime': Param('Shutter open time',
                                           type=float,
                                           settable=True,
                                           default=0,
                                           volatile=True,
                                           category='general'),
                  'shutterclosetime' : Param('Shutter open time',
                                           type=float,
                                           settable=True,
                                           default=0,
                                           volatile=True,
                                           category='general'),
                  'shuttermode' : Param('Shutter mode',
                                           type=oneof('always_open',
                                                      'always_closed', 'auto'),
                                           settable=True,
                                           default='auto',
                                           volatile=True,
                                           category='general'),
                  'hsspeed' : Param('Horizontal shift speed',
                                           type=oneof(*HSSPEEDS),
                                           settable=True,
                                           default=5,
                                           unit='MHz',
                                           volatile=True,
                                           category='general'),
                  'vsspeed' : Param('Vertical shift speed',
                                           type=oneof(*VSSPEEDS),
                                           settable=True,
                                           default=76.95,
                                           unit='ms/shift',
                                           volatile=True,
                                           category='general'),
                  'pgain' : Param('Preamplifier gain',
                                           type=oneof(*PGAINS),
                                           settable=True,
                                           default=4,
                                           volatile=True,
                                           category='general'),
                  'expotime' : Param('Exposure time',
                                           type=float,
                                           settable=False,
                                           volatile=True,
                                           category='general'),
                  'cameramodel' : Param('Camera type/model',
                                           type=str,
                                           settable=False,
                                           volatile=True, # Necessary?
                                           category='general'),
                  }

    parameter_overrides = {
                           'subdir' : Override(settable=True)
                           }
    def doPreinit(self, mode):
        PyTangoDevice.doPreinit(self, mode)

        self._hwDev = self._createPyTangoDevice(self.hwdevice)

    def doInit(self, mode):
        self._fileCounter = 0
        self._fastShutter = session.getDevice(self.fastshutter)

    def doStart(self, **preset):
        self.doSetPreset(**preset)

        self._tangoFuncGuard(self._dev.prepareAcq)

        # open the fast shutter automatically if the shutter mode is
        # always_open or auto.
        # Note: Closing the shutter is not necessary. This will be handled
        # by a hardware signal.
        if self.shuttermode in ['always_open', 'auto']:
            self._fastShutter.maw('open')

            # sleep is necessary as the jcns tango server does not provide
            # a proper status.
            time.sleep(0.1)

        self._tangoFuncGuard(self._dev.startAcq)
        self._newFile()

    def doStop(self):
        self._tangoFuncGuard(self._dev.stopAcq)

    def doStatus(self, maxage=0):
        statusMap = {
             'Ready' : status.OK,
             'Running' : status.BUSY,
             'Fault' : status.ERROR,
             }

        # limaStatus = self._tangoGetAttrGuard('acq_status')
        limaStatus = self._tangoGetAttrGuard('acq_status')
        nicosStatus = statusMap.get(limaStatus, status.UNKNOWN)

        return (nicosStatus, limaStatus)


    def doSetPreset(self, **preset):
        if 't' in preset:
            exposureTime = preset['t']
            self._tangoSetAttrGuard('acq_expo_time', exposureTime)

    def doIsCompleted(self):
        if self.doStatus()[0] == status.BUSY:
            return False
        return True

    def doReadImagewidth(self):
        return self._tangoGetAttrGuard('image_width')

    def doReadImageheight(self):
        return self._tangoGetAttrGuard('image_height')

    def doReadRoi(self):
        return tuple(self._tangoGetAttrGuard('image_roi').tolist())

    def doWriteRoi(self, value):
        self._tangoSetAttrGuard('image_roi', value)

    def doReadBin(self):
        return tuple(self._tangoGetAttrGuard('image_bin').tolist())

    def doWriteBin(self, value):
        self._tangoSetAttrGuard('image_bin', value)

    def doReadFlip(self):
        return tuple(self._tangoGetAttrGuard('image_flip').tolist())

    def doWriteFlip(self, value):
        self._tangoSetAttrGuard('image_flip', value)

    def doReadRotation(self):
        rot = self._tangoGetAttrGuard('image_rotation')

        if rot == 'NONE':
            return 0
        else:
            return int(rot)

    def doWriteRotation(self, value):
        writeVal = str(value)
        if value == 0:
            writeVal = 'NONE'

        self._tangoSetAttrGuard('image_rotation', writeVal)

    def doReadShutteropentime(self):
        return self._tangoGetAttrGuard('shutter_open_time')

    def doWriteShutteropentime(self, value):
        self._tangoSetAttrGuard('shutter_open_time', value)

    def doReadShutterclosetime(self):
        return self._tangoGetAttrGuard('shutter_close_time')

    def doWriteShutterclosetime(self, value):
        self._tangoSetAttrGuard('shutter_close_time', value)

    def doReadShuttermode(self):
        internalMode = self._tangoGetAttrGuard('shutter_mode')

        if internalMode in ['AUTO_FRAME', 'AUTO_SEQUENCE']:
            # this detector is only used in single acq mode,
            # so AUTO_FRAME and AUTO_SEQUENCE have the same
            # behaviour
            return 'auto'
        elif internalMode == 'MANUAL':
            shutterState = self._tangoGetAttrGuard('shutter_manual_state')

            if shutterState == 'OPEN':
                return 'always_open'
            elif shutterState == 'CLOSED':
                return 'always_closed'
            else:
                raise ConfigurationError(self, 'Camera shutter has unknown '
                                         + 'state in manual mode (%s)'
                                         % shutterState)
        else:
            raise ConfigurationError(self,
                                     'Camera has unknown shutter mode (%s)'
                                     % internalMode)



    def doWriteShuttermode(self, value):

        if value == 'auto':
            self._tangoSetAttrGuard('shutter_mode', 'AUTO_FRAME')
        elif value == 'always_open':
            self._tangoSetAttrGuard('shutter_mode', 'MANUAL')
            self._tangoFuncGuard(self._dev.openShutterManual)
        elif value == 'always_closed':
            self._tangoSetAttrGuard('shutter_mode', 'MANUAL')
            self._tangoFuncGuard(self._dev.closeShutterManual)

    def doReadHsspeed(self):
        index = self._tangoFuncGuard(self._hwDev.__getattr__, 'adc_speed')

        try:
            return self.HSSPEEDS[index]
        except IndexError:
            raise ConfigurationError(self, 'Camera uses unknown hs speed (index: %d)' % index)

    def doWriteHsspeed(self, value):
        index = self.HSSPEEDS.index(value)  # value can only be valid thanks to param validation
        self._tangoFuncGuard(self._hwDev.__setattr__, 'adc_speed', index)

    def doReadVsspeed(self):
        index = self._tangoFuncGuard(self._hwDev.__getattr__, 'vs_speed')

        try:
            return self.VSSPEEDS[index]
        except IndexError:
            raise ConfigurationError(self, 'Camera uses unknown vs speed (index: %d)' % index)


    def doWriteVsspeed(self, value):
        index = self.VSSPEEDS.index(value)  # value can only be valid thanks to param validation
        self._tangoFuncGuard(self._hwDev.__setattr__, 'vs_speed', index)

    def doReadPgain(self):
        index = self._tangoFuncGuard(self._hwDev.__getattr__, 'p_gain')

        try:
            return self.PGAINS[index]
        except IndexError:
            raise ConfigurationError(self, 'Camera uses unknown preamplifier gain (index: %d)' % index)

    def doWritePgain(self, value):
        index = self.PGAINS.index(value)  # value can only be valid thanks to param validation
        self._tangoFuncGuard(self._hwDev.__setattr__, 'p_gain', index)

    def doReadExpotime(self):
        return self._tangoFuncGuard(self._dev.__getattr__, 'acq_expo_time')

    def doReadCameramodel(self):
        camType = self._tangoFuncGuard(self._dev.__getattr__, 'camera_type')
        camModel = self._tangoFuncGuard(self._dev.__getattr__, 'camera_model')

        return '%s (%s)' % (camType, camModel)

    def doWriteSubdir(self, value):
        self._datapath = path.join(self.datapath[0], value)
        self._readCurrentCounter()

    def _readImageFromHw(self):
        response = self._tangoFuncGuard(self._dev.readImage, 0)
        imgDataStr = response[1]  # response is a tuple (type name, data)
        imgHeader = imgDataStr[:64]

        imgData = numpy.frombuffer(imgDataStr, '<u2', offset=64)
        imgData = numpy.reshape(imgData, (self.imageheight, self.imagewidth))

        self.log.debug('Image header:')
        self._hexdump(imgHeader)

        return imgData

    def _hexdump(self, data, logFunc=None):

        # IMPROVABLE!!

        if logFunc is None:
            logFunc = self.log.debug

        for i in range((len(data) + 7) / 8):
            startByte = hex(i * 8)

            wordStr = ' '.join('{0:<6}'.format(hex(ord(data[j + 1])
                           * 256 + ord(data[j])))[2:] for j in range(i * 8, i * 8 + 8, 2))

            byteStr = ' '.join('{0:<4}'.format(hex(ord(c)))[2:] for c in data[i * 8:i * 8 + 7])

            charStr = ''.join(c if 32 < ord(c) < 128 else '.' for c in data[i * 8:i * 8 + 7])

            line = '%s: \t%s - %s\t%s' % (startByte, wordStr, byteStr, charStr)

            logFunc(line)
