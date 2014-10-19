# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

import time
import numpy

from nicos.core import ImageProducer, ImageType, Param, Device, \
    Measurable, AutoDevice, status, tupleof, oneof, tangodev, \
    Override, ConfigurationError, HasLimits, HasPrecision, Moveable
from nicos.devices.tango import PyTangoDevice


class HwDevice(PyTangoDevice, AutoDevice, Device):
    pass


class GenericLimaCCD(PyTangoDevice, ImageProducer, Measurable):
    """
    This device class can be used together with the LIMA TANGO server
    to control all common parameters and actions of the supported cameras.

    For hardware specific additions, have a look at the particular class.
    """
    parameters = {
        'hwdevice':         Param('Hardware specific tango device', type=tangodev,
                                  default='', preinit=True),
        'imagewidth':       Param('Image width',
                                  type=int, volatile=True, category='general'),
        'imageheight':      Param('Image height',
                                  type=int, volatile=True, category='general'),
        'roi':              Param('Region of interest',
                                  type=tupleof(int, int, int, int), settable=True,
                                  default=(0, 0, 0, 0), volatile=True,
                                  category='general'),
        'bin':              Param('Binning (x,y)',
                                  type=tupleof(int, int), settable=True,
                                  default=(1, 1), volatile=True, category='general'),
        'flip':             Param('Flipping (x,y)',
                                  type=tupleof(bool, bool), settable=True,
                                  default=(False, False), volatile=True,
                                  category='general'),
        'rotation':         Param('Rotation',
                                  type=oneof(0, 90, 180, 270), settable=True,
                                  default=0, volatile=True, category='general'),
        'shutteropentime':  Param('Shutter open time',
                                  type=float, settable=True, default=0,
                                  volatile=False, category='general'),
        'shutterclosetime': Param('Shutter open time',
                                  type=float, settable=True, default=0,
                                  volatile=False, category='general'),
        'shuttermode':      Param('Shutter mode',
                                  type=oneof('always_open', 'always_closed', 'auto'),
                                  settable=True, default='auto', volatile=True,
                                  category='general'),
        'expotime':         Param('Exposure time',
                                  type=float, settable=False, volatile=False,
                                  category='general'),
        'cameramodel':      Param('Camera type/model',
                                  type=str, settable=False,
                                  volatile=True,  # Necessary?
                                  category='general'),
    }

    parameter_overrides = {
        'subdir':      Override(settable=True),
    }

    def doPreinit(self, mode):
        PyTangoDevice.doPreinit(self, mode)

        # Create hw specific device if given
        self._hwDev = None
        if self.hwdevice:
            self._hwDev = HwDevice(self.name + '._hwDev',
                                   tangodevice=self.hwdevice, lowlevel=True)

    def doInit(self, mode):
        # Determine image type
        shape = (self.imagewidth, self.imageheight)
        self.imagetype = ImageType(shape, self._getImageType())

        self._startTime = None

    def doSetPreset(self, **preset):
        if 't' in preset:
            self._dev.acq_expo_time = preset['t']

    def doRead(self, _maxage=0):
        return self.lastfilename

    def doStart(self):
        self._dev.prepareAcq()

        self._startTime = time.time()

        self._dev.startAcq()

    def doStop(self):
        self._dev.stopAcq()

    def doStatus(self, maxage=0):  # pylint: disable=W0221
        statusMap = {
            'Ready': status.OK,
            'Running': status.BUSY,
            'Fault': status.ERROR,
        }

        limaStatus = self._dev.acq_status
        nicosStatus = statusMap.get(limaStatus, status.UNKNOWN)

        if nicosStatus == status.BUSY and self._startTime is not None:

            deltaTime = time.time() - self._startTime

            if deltaTime <= self.shutteropentime:
                limaStatus += ' (Opening shutter)'
            elif deltaTime <= (self.shutteropentime + self.expotime):
                remaining = self.expotime - (deltaTime - self.shutteropentime)
                limaStatus += ' (Exposing; Remaining: %.2f s)' % remaining
            elif deltaTime <= (self.shutteropentime + self.expotime +
                               self.shutterclosetime):
                limaStatus += ' (Closing shutter)'
            else:
                limaStatus += ' (Readout)'

        self.log.debug('## (%r, %r)' % (nicosStatus, limaStatus))

        return (nicosStatus, limaStatus)

    def doIsCompleted(self):
        if self.doStatus()[0] == status.BUSY:
            return False
        return True

    def doReadImagewidth(self):
        return self._dev.image_width

    def doReadImageheight(self):
        return self._dev.image_height

    def doReadRoi(self):
        return tuple(self._dev.image_roi.tolist())

    def doWriteRoi(self, value):
        self._dev.image_roi = value

    def doReadBin(self):
        return tuple(self._dev.image_bin.tolist())

    def doWriteBin(self, value):
        self._dev.image_bin = value

    def doReadFlip(self):
        return tuple(self._dev.image_flip.tolist())

    def doWriteFlip(self, value):
        self._dev.image_flip = value

    def doReadRotation(self):
        rot = self._dev.image_rotation

        if rot == 'NONE':
            return 0
        else:
            return int(rot)

    def doWriteRotation(self, value):
        writeVal = str(value)
        if value == 0:
            writeVal = 'NONE'

        self._dev.image_rotation = writeVal

    def doReadShutteropentime(self):
        return self._dev.shutter_open_time

    def doWriteShutteropentime(self, value):
        self._dev.shutter_open_time = value

    def doReadShutterclosetime(self):
        return self._dev.shutter_close_time

    def doWriteShutterclosetime(self, value):
        self._dev.shutter_close_time = value

    def doReadShuttermode(self):
        internalMode = self._dev.shutter_mode

        if internalMode in ['AUTO_FRAME', 'AUTO_SEQUENCE']:
            # this detector is only used in single acq mode,
            # so AUTO_FRAME and AUTO_SEQUENCE have the same
            # behaviour
            return 'auto'
        elif internalMode == 'MANUAL':
            shutterState = self._dev.shutter_manual_state

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
            self._dev.shutter_mode = 'AUTO_FRAME'
        elif value == 'always_open':
            self._dev.shutter_mode = 'MANUAL'
            self._dev.openShutterManual()
        elif value == 'always_closed':
            self._dev.shutter_mode = 'MANUAL'
            self._dev.closeShutterManual()

    def doReadExpotime(self):
        return self._dev.acq_expo_time

    def doReadCameramodel(self):
        camType = self._dev.camera_type
        camModel = self._dev.camera_model

        return '%s (%s)' % (camType, camModel)

    def readFinalImage(self):
        response = self._dev.readImage(0)
        imgDataStr = response[1]  # response is a tuple (type name, data)

        dt = numpy.dtype(self._getImageType())
        dt = dt.newbyteorder('<')

        imgData = numpy.frombuffer(imgDataStr,
                                   dt,
                                   offset=64)
        imgData = numpy.reshape(imgData, (self.imageheight, self.imagewidth))

        return imgData

    def _getImageType(self):
        imageType = self._dev.image_type

        mapping = {
            'Bpp8': numpy.uint8,
            'Bpp8S': numpy.int8,
            'Bpp16': numpy.uint16,
            'Bpp16S': numpy.int16,
            'Bpp32': numpy.uint32,
            'Bpp32S': numpy.int32,
        }

        return mapping.get(imageType, numpy.uint32)


class Andor2LimaCCD(GenericLimaCCD):
    """
    This device class is an extension to the GenericLimaCCD that adds the
    hardware specific functionality for all Andor SDK2 based cameras.
    """

    HSSPEEDS = [5, 3, 1, 0.05]  # Values from sdk manual
    VSSPEEDS = [38.55, 76.95]  # Values from sdk manual
    PGAINS = [1, 2, 4]  # Values from sdk manual

    parameters = {
        'hsspeed': Param('Horizontal shift speed',
                         type=oneof(*HSSPEEDS), settable=True, default=5,
                         unit='MHz', volatile=True, category='general'),
        'vsspeed': Param('Vertical shift speed',
                         type=oneof(*VSSPEEDS), settable=True, default=76.95,
                         unit='ms/shift', volatile=True, category='general'),
        'pgain':   Param('Preamplifier gain',
                         type=oneof(*PGAINS), settable=True, default=4,
                         volatile=True, category='general'),
    }

    parameter_overrides = {
        'hwdevice': Override(mandatory=True),
    }

    def doReadHsspeed(self):
        index = self._hwDev._dev.adc_speed

        try:
            return self.HSSPEEDS[index]
        except IndexError:
            raise ConfigurationError(self, 'Camera uses unknown hs speed '
                                     '(index: %d)' % index)

    def doWriteHsspeed(self, value):
        index = self.HSSPEEDS.index(value)
        self._hwDev._dev.adc_speed = index

    def doReadVsspeed(self):
        index = self._hwDev._dev.vs_speed

        try:
            return self.VSSPEEDS[index]
        except IndexError:
            raise ConfigurationError(self, 'Camera uses unknown vs speed '
                                     '(index: %d)' % index)

    def doWriteVsspeed(self, value):
        index = self.VSSPEEDS.index(value)
        self._hwDev._dev.vs_speed = index

    def doReadPgain(self):
        index = self._hwDev._dev.p_gain

        try:
            return self.PGAINS[index]
        except IndexError:
            raise ConfigurationError(self, 'Camera uses unknown preamplifier '
                                     'gain (index: %d)' % index)

    def doWritePgain(self, value):
        index = self.PGAINS.index(value)
        self._hwDev._dev.p_gain = index


class Andor2TemperatureController(PyTangoDevice,
                                  HasLimits, HasPrecision, Moveable):
    """
    This devices provides access to the cooling feature of Andor2 cameras.
    """

    def doRead(self, maxage=0):
        return self._dev.temperature

    def doStatus(self, maxage=0):  # pylint: disable=W0221
        coolerState = self._dev.cooler
        temperature = self.doRead()
        sp = self._dev.temperature_sp

        nicosState = status.UNKNOWN

        if self._isCoolerEnabled():
            if abs(temperature - sp) < self.precision:
                nicosState = status.OK
            else:
                nicosState = status.BUSY
        else:
            if temperature > -10:
                nicosState = status.OK
            else:
                nicosState = status.BUSY

        return (nicosState, coolerState)

    def doStart(self, value):
        if value > -10:
            self._setCoolerEnabled(False)
        else:
            self._dev.temperature_sp = value
            self._setCoolerEnabled(True)

    def _setCoolerEnabled(self, value):
        if value:
            self._dev.cooler = 'ON'
        else:
            self._dev.cooler = 'OFF'

    def _isCoolerEnabled(self):
        return True if self._dev.cooler == 'ON' else False
