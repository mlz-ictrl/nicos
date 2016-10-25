# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

import numpy
from PyTango import DevState

from nicos import session
from nicos.core import Moveable, status
from nicos.devices.tango import PyTangoDevice
from nicos.core.params import Attach, Param, Override, oneof, tupleof, ArrayDesc
from nicos.core.errors import NicosError, MoveError, InvalidValueError
from nicos.core.constants import FINAL, SIMULATION
from nicos.devices.generic.detector import Detector, PassiveChannel, \
    ImageChannelMixin
from nicos.jcns.shutter import OPEN, CLOSE


class ImagePlateDrum(PyTangoDevice, Moveable):
    """ImagePlateDrum implements erasing, moving to expo position and readout
    for MAATEL Image Plate Detectors.
    """

    DEFAULT_URL_FMT = "tango://%s/EMBL/Microdiff/General#dbase=no"

    tango_status_mapping = dict(PyTangoDevice.tango_status_mapping)
    tango_status_mapping[DevState.STANDBY] = status.OK
    tango_status_mapping[DevState.ALARM] = status.ERROR

    POS_ERASE = "erase"
    POS_EXPO = "expo"
    POS_READ = "read"

    valuetype = oneof(POS_ERASE, POS_EXPO, POS_READ)

    parameters = {
        "drumpos": Param("Drum position in degree", type=float,
                         settable=True, volatile=True, category="general"),
        "readheadpos": Param("Read head motor position in mm",
                             type=float, settable=True, volatile=True,
                             category="general"),
        "drumexpo": Param("Drum expo position in degree",
                          type=float, settable=True, volatile=True,
                          category="general"),
        "readspeed": Param("Readout velocity for the detector drum "
                           "in rpm", type=float, settable=True,
                           volatile=True, category="general"),
        "erasespeed": Param("Erase velocity for the detector drum "
                            "in rpm", type=float, settable=True,
                            volatile=True, category="general"),
        "freqlaser": Param("Frequency for the laser diode in Hz",
                           type=float, settable=True, volatile=True,
                           category="general"),
        "timeerase": Param("Erasure time in seconds", type=float,
                           settable=True, volatile=True, category="general"),
    }

    parameter_overrides = {
        "unit": Override(default="", mandatory=False, settable=False)
    }

    def doInit(self, mode):
        self._lastStatus = None
        self._moveTo = None
        if mode == SIMULATION:
            self._mapStart = {}
            self._mapStop = {}
            return
        self._mapStart = {
            ImagePlateDrum.POS_ERASE: self._dev.StartErasureProcess,
            ImagePlateDrum.POS_EXPO: self._dev.MoveExpoPosition,
            ImagePlateDrum.POS_READ: self._dev.StartReadProcess,
        }
        self._mapStop = {
            ImagePlateDrum.POS_ERASE: self._dev.AbortErasureProcess,
            ImagePlateDrum.POS_EXPO: self._dev.AbortExposureProcess,
            ImagePlateDrum.POS_READ: self._dev.AbortReadProcess,
        }

    def doStart(self, pos):
        self.log.debug("doStart: pos: %s" % pos)
        myStatus = self.status(0)
        if myStatus[0] == status.OK:
            self._moveTo = pos
            self._mapStart[pos]()
        else:
            raise MoveError(self, "Movement not allowed during device status "
                            "'%s'" % (status.statuses[myStatus[0]]))

    def doStop(self):
        self.log.debug("doStop")
        if self._moveTo in self._mapStop:
            self._mapStop[self._moveTo]()
        else:
            myStatus = self.status(0)
            if myStatus[0] == status.OK:
                self.log.warning("Device already stopped.")
            else:
                raise NicosError(self, "Internal moveTo state unknown. "
                                       "Check device status.")

    def doRead(self, maxage=0):
        return self.target

    def doStatus(self, maxage=0):
        # Workaround for status changes from busy to another state although the
        # operation has _not_ been completed.
        st, msg = PyTangoDevice.doStatus(self, maxage)
        if self._lastStatus == status.BUSY and st != status.BUSY:
            self.log.debug("doStatus: leaving busy state (%d)? %d. "
                           "Check again after a short delay."
                           % (status.BUSY, st))
            session.delay(5)
            st, msg = PyTangoDevice.doStatus(self, 0)
            self.log.debug("doStatus: recheck result: %d" % st)
        self._lastStatus = st
        return st, msg

    def doFinish(self):
        self._moveTo = None

    def doReadDrumpos(self):
        return self._dev.DrumPosition

    def doReadReadheadpos(self):
        return self._dev.ReadHeadPosition

    def doReadDrumexpo(self):
        return self._dev.DrumExpoPosition

    def doReadReadspeed(self):
        return self._dev.ReadingDrumJogSpeed

    def doReadErasespeed(self):
        return self._dev.ErasureDrumJogSpeed

    def doReadFreqlaser(self):
        return self._dev.LaserDiodeLevel

    def doReadTimeerase(self):
        return self._dev.ErasureDuration

    def doWriteDrumpos(self, value):
        self._dev.DrumPosition = value

    def doWriteReadheadpos(self, value):
        self._dev.ReadHeadPosition = value

    def doWriteDrumexpo(self, value):
        self._dev.DrumExpoPosition = value

    def doWriteReadspeed(self, value):
        self._dev.ReadingDrumJogSpeed = value

    def doWriteErasespeed(self, value):
        self._dev.ErasureDrumJogSpeed = value

    def doWriteFreqlaser(self, value):
        self._dev.LaserDiodeLevel = value

    def doWriteTimeerase(self, value):
        self._dev.ErasureDuration = value


class ImagePlateImage(ImageChannelMixin, PassiveChannel):
    """Represents the client to a MAATEL Image Plate Detector."""

    MAP_SHAPE = {
        125: (10000, 900),
        250: (5000, 900),
        500: (2500, 900),
    }

    attached_devices = {
        "imgdrum":      Attach("Image Plate Detector Drum "
                               "control device.", ImagePlateDrum),
    }

    parameters = {
        "erase": Param("Erase image plate on next start?", type=bool,
                       settable=True, mandatory=False, default=True),
        "roi": Param("Region of interest",
                     type=tupleof(int, int, int, int),
                     default=(0, 0, 0, 0),
                     settable=True, volatile=True,
                     category="general"),
        "pixelsize": Param("Pixel size in microns",
                           type=oneof(125, 250, 500), default=500,
                           settable=True, volatile=True, category="general"),
        "file": Param("Image file location on maatel computer",
                      type=str, settable=True, volatile=True,
                      category="general"),
        "readout_millis": Param("Timeout in ms for the readout",
                                type=int, settable=True, default=60000),
    }

    def doInit(self, mode):
        self.arraydesc = ArrayDesc('data',
                                   self.MAP_SHAPE[self.pixelsize],
                                   numpy.uint16)

    def doPrepare(self):
        # erase and expo position
        if self.erase:
            self._attached_imgdrum.maw(ImagePlateDrum.POS_ERASE)
        self._attached_imgdrum.maw(ImagePlateDrum.POS_EXPO)

    def valueInfo(self):
        # no readresult -> no values
        return ()

    def doReadArray(self, quality):
        if quality == FINAL:
            # start readout
            self._attached_imgdrum.maw(ImagePlateDrum.POS_READ)
            narray = None
            timeout = self._attached_imgdrum._dev.get_timeout_millis()
            self._attached_imgdrum._dev.set_timeout_millis(self.readout_millis)
            try:
                narray = self._attached_imgdrum._dev.Bitmap16Bit
            finally:
                self._attached_imgdrum._dev.set_timeout_millis(timeout)
            return narray
        return None

    def doReadRoi(self):
        return (0, self._attached_imgdrum._dev.InterestZoneY, 1250,
                self._attached_imgdrum._dev.InterestZoneH)

    def doReadPixelsize(self):
        return self._attached_imgdrum._dev.PixelSize

    def doReadFile(self):
        return self._attached_imgdrum._dev.ImageFile

    def doWriteRoi(self, value):
        self.log.warning("setting x offset and width are not supported "
                         "- ignored.")
        self._attached_imgdrum._dev.InterestZoneY = value[1]
        self._attached_imgdrum._dev.InterestZoneH = value[3]

    def doWritePixelsize(self, value):
        self._attached_imgdrum._dev.PixelSize = value
        self.arraydesc = ArrayDesc('data', self.MAP_SHAPE[value], numpy.uint16)

    def doWriteFile(self, value):
        self._attached_imgdrum._dev.ImageFile = value


class BiodiffDetector(Detector):

    attached_devices = {
        "gammashutter": Attach("Gamma shutter", Moveable),
        "photoshutter": Attach("Photo shutter", Moveable),
    }

    parameters = {
        "ctrl_gammashutter": Param("Control gamma shutter?", type=bool,
                                   settable=True, mandatory=False,
                                   default=True),
        "ctrl_photoshutter": Param("Control photo shutter?", type=bool,
                                   settable=True, mandatory=False,
                                   default=True),
    }

    def doPrepare(self):
        # close shutter
        if self.ctrl_photoshutter:
            self._attached_photoshutter.maw(CLOSE)
        if self.ctrl_gammashutter:
            self._attached_gammashutter.maw(CLOSE)
        Detector.doPrepare(self)

    def doStart(self):
        # open shutter
        if self.ctrl_gammashutter:
            self._attached_gammashutter.maw(OPEN)
        if self.ctrl_photoshutter:
            self._attached_photoshutter.maw(OPEN)
        Detector.doStart(self)

    def _check_shutter(self):
        if (self.ctrl_photoshutter and
                self._attached_photoshutter.read() == CLOSE):
            raise InvalidValueError(self, 'photo shutter not open after '
                                    'exposure, check safety system')
        if (self.ctrl_gammashutter and
                self._attached_gammashutter.read() == CLOSE):
            raise InvalidValueError(self, 'gamma shutter not open after '
                                    'exposure, check safety system')

    def doFinish(self):
        Detector.doFinish(self)
        self._check_shutter()
        # close shutter
        if self.ctrl_photoshutter:
            self._attached_photoshutter.maw(CLOSE)
        if self.ctrl_gammashutter:
            self._attached_gammashutter.maw(CLOSE)

    def doStop(self):
        Detector.doStop(self)
        # close shutter
        if self.ctrl_photoshutter:
            self._attached_photoshutter.maw(CLOSE)
        if self.ctrl_gammashutter:
            self._attached_gammashutter.maw(CLOSE)
