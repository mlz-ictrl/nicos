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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import struct
import time

import numpy

from nicos.core import INTERRUPTED, SIMULATION, ArrayDesc, AutoDevice, \
    Device, HardwareError, NicosError, Param, none_or, oneof, status, \
    tangodev, tupleof
from nicos.devices.generic.detector import ActiveChannel, ImageChannelMixin, \
    PassiveChannel, TimerChannelMixin
from nicos.devices.tango import PyTangoDevice

from .optional import LimaShutter


class HwDevice(PyTangoDevice, AutoDevice, Device):
    pass


class LimaCCDTimer(PyTangoDevice, TimerChannelMixin, ActiveChannel):
    """
    Timer channel for Lima cameras.
    """

    parameters = {
        '_starttime': Param('Cached counting start time',
                            type=float, default=0, settable=False,
                            internal=True),
        '_stoptime':  Param('Cached counting start time',
                            type=float, default=0, settable=False,
                            internal=True),
    }

    def doWritePreselection(self, value):
        self._dev.acq_expo_time = value

    def doRead(self, maxage=0):
        if self._stoptime:
            return [min(self._stoptime - self._starttime,
                        self._dev.acq_expo_time)]
        return [min(time.time() - self._starttime, self._dev.acq_expo_time)]

    def doStart(self):
        self._setROParam('_starttime', time.time())
        self._setROParam('_stoptime', 0)

    def doFinish(self):
        self._setROParam('_stoptime', time.time())

    def doStop(self):
        self.doFinish()

    def doStatus(self, maxage=0):
        statusMap = {
            'Ready': status.OK,
            'Running': status.BUSY,
            'Fault': status.ERROR,
        }
        limaStatus = self._dev.acq_status
        nicosStatus = statusMap.get(limaStatus, status.UNKNOWN)
        return (nicosStatus, limaStatus)

    def doVersion(self):
        return [(self.tangodevice,
                 f'lima {self._dev.lima_version}, '
                 f'tango {self._dev.get_tango_lib_version() / 100:.02f}')]


class GenericLimaCCD(PyTangoDevice, ImageChannelMixin, PassiveChannel):
    """
    This device class can be used together with the LIMA TANGO server
    to control all common parameters and actions of the supported cameras.

    For hardware specific additions, have a look at the particular class.
    """
    parameters = {
        'hwdevice':         Param('Hardware specific tango device',
                                  type=none_or(tangodev), preinit=True),
        'imagewidth':       Param('Image width',
                                  type=int, volatile=True, category='general'),
        'imageheight':      Param('Image height',
                                  type=int, volatile=True, category='general'),
        'roi':              Param('Region of interest',
                                  type=tupleof(int, int, int, int),
                                  default=(0, 0, 0, 0), volatile=True,
                                  settable=True, category='general'),
        'bin':              Param('Binning (x,y)',
                                  type=tupleof(int, int), settable=True,
                                  default=(1, 1), volatile=True,
                                  category='general'),
        'flip':             Param('Flipping (x,y)',
                                  type=tupleof(bool, bool), settable=True,
                                  volatile=True, default=(False, False),
                                  category='general'),
        'rotation':         Param('Rotation',
                                  type=oneof(0, 90, 180, 270), settable=True,
                                  volatile=True, default=0,
                                  category='general'),
        'expotime':         Param('Exposure time',
                                  type=float, settable=False, volatile=True,
                                  category='general'),
        'cameramodel':      Param('Camera type/model',
                                  type=str, settable=False,
                                  volatile=True,  # Necessary?
                                  category='general'),
        'shutteropentime':  Param('Shutter open time',
                                  type=none_or(float), settable=True,
                                  default=0, volatile=False,
                                  category='general'),
        'shutterclosetime': Param('Shutter open time',
                                  type=none_or(float), settable=True,
                                  default=0, volatile=False,
                                  category='general'),
        'shuttermode':      Param('Shutter mode',
                                  type=none_or(oneof('always_open',
                                                     'always_closed',
                                                     'auto')),
                                  settable=True, default='auto', volatile=True,
                                  category='general'),
        '_starttime':   Param('Cached counting start time',
                              type=float, default=0, settable=False,
                              internal=True),
        # some cached values are necessary as hw params are volatile on request
        '_curexpotime': Param('Cached exposure time for current acquisition',
                              type=float,
                              default=0,
                              settable=False,
                              internal=True),
        '_curshutteropentime':  Param('Cached shutter open time for current'
                                      ' acquisition',
                                      type=float,
                                      default=0,
                                      settable=False,
                                      internal=True),
        '_curshutterclosetime': Param('Cached shutter close time for current'
                                      ' acquisition',
                                      type=float,
                                      default=0,
                                      settable=False,
                                      internal=True),

    }

    _hwDev = None

    def doPreinit(self, mode):
        PyTangoDevice.doPreinit(self, mode)

        # Create hw specific device if given
        if self.hwdevice:
            self._hwDev = HwDevice(self.name + '._hwDev',
                                   tangodevice=self.hwdevice, visibility=())

        # optional components
        self._shutter = None

        if mode != SIMULATION:
            self._initOptionalComponents()

            if self._dev.camera_model.startswith('SIMCAM'):
                self.log.warning('Using lima simulation camera! If that\'s not'
                                 ' intended, please check the cables and '
                                 'restart the camera and the lima server')

            self._specialInit()
            # cache full detector size
            self._width_height = (self.imagewidth, self.imageheight)
        else:
            # some dummy shape for simulation
            self._width_height = (2048, 1536)

    def doInit(self, mode):
        # Determine image type
        self.arraydesc = ArrayDesc(self.name, self._width_height[::-1],
                                   self._getImageType())

    def doShutdown(self):
        if self._hwDev:
            self._hwDev.shutdown()

    def doInfo(self):
        for p in ('imagewidth', 'imageheight', 'roi', 'bin', 'expotime',
                  'cameramodel', 'shutteropentime', 'shutterclosetime',
                  'shuttermode'):
            self._pollParam(p)
        return []

    def valueInfo(self):
        # no readresult by default
        return ()

    def doStart(self):
        # ignore prep in time calc
        self._dev.prepareAcq()

        self._setROParam('_starttime', time.time())
        self._setROParam('_curexpotime', self.expotime)

        if self._shutter is not None:
            self._setROParam('_curshutteropentime', self.shutteropentime)
            self._setROParam('_curshutterclosetime', self.shutterclosetime)

        self._dev.startAcq()

    def doFinish(self):
        self._dev.stopAcq()

    def doStop(self):
        self.doFinish()

    def doStatus(self, maxage=0):
        statusMap = {
            'Ready': status.OK,
            'Running': status.BUSY,
            'Fault': status.ERROR,
        }

        limaStatus = self._dev.acq_status
        nicosStatus = statusMap.get(limaStatus, status.UNKNOWN)

        if nicosStatus == status.BUSY:
            deltaTime = time.time() - self._starttime

            if self._shutter and deltaTime <= self._curshutteropentime:
                limaStatus += ' (Opening shutter)'
            elif deltaTime <= (self._curexpotime):
                remaining = self._curexpotime - deltaTime
                limaStatus += ' (Exposing; Remaining: %.2f s)' % remaining
            elif self._shutter and deltaTime <= sum(self._curshutteropentime,
                                                    self._curexpotime,
                                                    self._curshutterclosetime):
                limaStatus += ' (Closing shutter)'
            else:
                limaStatus += ' (Readout)'

        return (nicosStatus, limaStatus)

    def doVersion(self):
        return [(self.tangodevice,
                 f'lima {self._dev.lima_version}, '
                 f'tango {self._dev.get_tango_lib_version() / 100:.02f}')]

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

    def doWriteFlip(self, value):
        self._dev.image_flip = value

    def doReadFlip(self):
        return tuple(self._dev.image_flip.tolist())

    def doWriteRotation(self, value):
        self._dev.image_rotation = 'NONE' if value == 0 else str(value)

    def doReadRotation(self):
        rot = self._dev.image_rotation
        return 0 if rot == 'NONE' else int(rot)

    def doReadExpotime(self):
        return self._dev.acq_expo_time

    def doReadCameramodel(self):
        camType = self._dev.camera_type
        camModel = self._dev.camera_model
        return '%s (%s)' % (camType, camModel)

    def doReadShutteropentime(self):
        if self._shutter:
            return self._shutter.doReadShutteropentime()
        return None  # will be overwritten

    def doWriteShutteropentime(self, value):
        if self._shutter:
            return self._shutter.doWriteShutteropentime(value)
        raise HardwareError('Not supported')

    def doReadShutterclosetime(self):
        if self._shutter:
            return self._shutter.doReadShutterclosetime()
        return None

    def doWriteShutterclosetime(self, value):
        if self._shutter:
            return self._shutter.doWriteShutterclosetime(value)
        raise HardwareError('Not supported')

    def doReadShuttermode(self):
        if self._shutter:
            return self._shutter.doReadShuttermode()
        return None

    def doWriteShuttermode(self, value):
        if self._shutter:
            return self._shutter.doWriteShuttermode(value)
        raise HardwareError('Not supported')

    def doReadArray(self, quality):
        if quality == INTERRUPTED:
            return None

        response = self._dev.readImage(0)

        img_data_str = response[1]  # response is a tuple (type name, data)
        _magic, _, headersize = struct.unpack('<IHH', img_data_str[:8])
        if _magic != 0x44544159:
            self.log.warning('Seems to be not a valid LImA image')

        dt = numpy.dtype(self._getImageType())
        dt = dt.newbyteorder('<')

        img_data = numpy.frombuffer(img_data_str, dt, offset=headersize)
        img_data = numpy.reshape(img_data, (self.imageheight, self.imagewidth))
        return img_data

    def _initOptionalComponents(self):
        try:
            self._shutter = LimaShutter(self._dev, self._hwDev)
        except NicosError:
            self._shutter = None
        except AttributeError:
            self._shutter = None

    def _specialInit(self):
        pass

    def _getImageType(self):
        if self._mode == SIMULATION:
            return numpy.uint32

        imageType = self._dev.image_type

        mapping = {
            'Bpp8': numpy.uint8,
            'Bpp8S': numpy.int8,
            'Bpp12': numpy.uint16,
            'Bpp16': numpy.uint16,
            'Bpp16S': numpy.int16,
            'Bpp32': numpy.uint32,
            'Bpp32S': numpy.int32,
        }

        return mapping.get(imageType, numpy.uint32)
