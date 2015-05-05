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

"""Live data 'file format saver' supporting the LiveWidget"""

import time

from nicos import session
from nicos.core import Override, ImageSink


class LiveViewSink(ImageSink):
    parameter_overrides = {
        # this is not really used, so we give it a default that would
        # raise if used as a template filename
        'filenametemplate' : Override(mandatory=False, settable=False,
                                      userparam=False, default=['']),
    }

    fileFormat = 'Live'     # should be unique amongst filesavers!

    def acceptImageType(self,  imagetype):
        return len(imagetype.shape) in (2, 3)

    def prepareImage(self, imageinfo, subdir=''):
        imageinfo.filename = 'live@%s' % session.experiment.lastimage

    def updateLiveImage(self, imageinfo, image):
        if len(image.shape) == 2:
            resX, resY = image.shape
            resZ = 1
        else:
            resX, resY, resZ = image.shape
        # see nicos.core.sessions.__init__:
        # updateLiveData(self, tag, filename, dtype, nx, ny, nt, time, data)
        session.updateLiveData(self.fileFormat, imageinfo.filename, '<u4', resX, resY, resZ,
            time.time() - imageinfo.begintime, buffer(image.astype('<u4')))

    def saveImage(self, imageinfo, image):
        self.updateLiveImage(imageinfo, image)

    def finalizeImage(self, imageinfo):
        pass
