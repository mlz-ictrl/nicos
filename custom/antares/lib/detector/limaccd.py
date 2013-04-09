# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Measurable
from nicos.core import Param
from nicos.core import status
from nicos.core import tupleof
from nicos.core import oneof
from nicos.core import Override

from nicos.antares.detector.pytangodevice import PyTangoDevice
from nicos.antares.detector import ImageStorageFits

import numpy
from os import path


class LimaCCD(PyTangoDevice, ImageStorageFits, Measurable):

    parameters = {
                  'hwdevice' : Param('Hardware device name', type=str, mandatory=True, preinit=True),
                  'imagewidth'     : Param('Image width', type=int, volatile=True),
                  'imageheight'    : Param('Image height', type=int, volatile=True),
                  'roi'            : Param('Region of interest', type=tupleof(int, int, int, int),
                                            settable=True, default=(0, 0, 0, 0)),
                  'bin'            : Param('Binning (x,y)', type=tupleof(int, int),
                                           settable=True, default=(1, 1)),
                  'flip'           : Param('Flipping (x,y)', type=tupleof(bool, bool),
                                           settable=True, default=(False, False)),
                  'rotation'       : Param('Rotation', type=oneof(0, 90, 180, 270),
                                           settable=True, default=0),
                  'shutteropentime': Param('Shutter open time', type=float,
                                           settable=True, default=0),
                  'shutterclosetime' : Param('Shutter open time', type=float,
                                           settable=True, default=0),
                  'shuttermode' : Param('Shutter mode', type=oneof('MANUAL', 'AUTO_FRAME', 'AUTO_SEQUENCE'),
                                           settable=True, default='AUTO_FRAME'),
                  'hsspeed' : Param('Horizontal shift speed (max:-1)', type=int,
                                           settable=True, default= -1),
                  'vsspeed' : Param('Vertical shift speed (max:-1)', type=int,
                                           settable=True, default= -1),
                  'pgain' : Param('Preamplifier gain (max:-1)', type=int,
                                           settable=True, default= -1),
                  }

    parameter_overrides = {
                           'subdir' : Override(settable=True)
                           }

    def doPreinit(self, mode):
        PyTangoDevice.doPreinit(self, mode)

        self._hwDev = self._createPyTangoDevice(self.hwdevice)

    def doInit(self, mode):
        self._fileCounter = 0

    def doStart(self):
        self._tangoFuncGuard(self._dev.prepareAcq)
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
        return self._tangoGetAttrGuard('image_roi')

    def doWriteRoi(self, value):
        self._tangoSetAttrGuard('image_roi', value)

    def doReadBin(self):
        return self._tangoGetAttrGuard('image_bin')

    def doWriteBin(self, value):
        self._tangoSetAttrGuard('image_bin', value)

    def doReadFlip(self):
        return self._tangoGetAttrGuard('image_flip')

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
        return self._tangoGetAttrGuard('shutter_mode')

    def doWriteShuttermode(self, value):
        self._tangoSetAttrGuard('shutter_mode', value)

    def doReadHsspeed(self):
        return self._tangoFuncGuard(self._hwDev.__getattr__, 'adc_speed')

    def doWriteHsspeed(self, value):
        self._tangoFuncGuard(self._hwDev.__setattr__, 'adc_speed', value)

    def doReadVsspeed(self):
        return self._tangoFuncGuard(self._hwDev.__getattr__, 'vs_speed')

    def doWriteVsspeed(self, value):
        self._tangoFuncGuard(self._hwDev.__setattr__, 'vs_speed', value)

    def doReadPgain(self):
        return self._tangoFuncGuard(self._hwDev.__getattr__, 'p_gain')

    def doWritePgain(self, value):
        self._tangoFuncGuard(self._hwDev.__setattr__, 'p_gain', value)

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
