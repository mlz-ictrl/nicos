# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Petr Čermák <cermak@mag.mff.cuni.cz>
#
# ****************************************************************************

"""Module handles communication with webcam."""

from nicos.core import NicosError, Override, Param, status
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.devices.generic.detector import ActiveChannel, ImageChannelMixin

try:
    import cv2
except ImportError as e:
    cv2 = None
    _import_error = e


class Webcam(ImageChannelMixin, ActiveChannel):
    parameters = {
        'device': Param('Device number',
                        type=int, default=0),
    }

    parameter_overrides = {
        'preselection': Override(type=float),
    }

    def doInit(self, mode):
        if cv2 is None:
            raise _import_error
        self._cam = cv2.VideoCapture(self.device)
        if not self._cam.isOpened():
            raise NicosError(f"Couldn't open camera #{self.device}")
        self._result = True
        self._image = None
        # check for error

    def doStart(self):
        self._result = False
        self._result, self._image = self._cam.read()

    def valueInfo(self):
        return ()

    def doStatus(self, maxage=0):
        if self._result:
            return status.OK, 'Idle'
        else:
            self.doStart()
            return status.BUSY, 'Trying to get image'

    def doReadArray(self, quality):
        return self._image

    def doStop(self):
        pass

    def doFinish(self):
        pass


class JPGImageSinkHandler(SingleFileSinkHandler):

    filetype = 'jpg'
    defer_file_creation = True
    accept_final_images_only = True

    def writeData(self, fp, image):
        ret = cv2.imwrite(fp.name, image)
        if not ret:
            raise NicosError(f'Unable to write image {fp.name}')


class JPGImageSink(ImageSink):
    """JPEG image sink, without metadata.

    This data sink writes jpeg format files without any metadata.
    """

    parameter_overrides = {
        'filenametemplate': Override(default=['%(pointcounter)08d.jpg'])
    }

    handlerclass = JPGImageSinkHandler

    def doPreinit(self, mode):
        if cv2 is None:
            self.log.error(_import_error)
            raise NicosError(self, 'The OpenCV (cv2) is not available. '
                             'Please check whether it is installed and '
                             'in your PYTHONPATH')

    def isActiveForArray(self, arraydesc):
        # TODO: Check which line of code should be used
        return True
        # return len(arraydesc.shape) == 2
