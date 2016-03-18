# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
try:
    import PIL
    from PIL import Image
except ImportError as e:
    PIL = None
    _import_error = e

from nicos.core import NicosError, Param
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler


class TIFFImageSinkHandler(SingleFileSinkHandler):

    filetype = 'TIFF'
    defer_file_creation = True
    accept_final_images_only = True

    def writeData(self, fp, image):
        Image.fromarray(numpy.array(image), self.sink.mode).save(fp)


class TIFFImageSink(ImageSink):
    """TIFF image sink, without metadata."""

    fileFormat = "TIFF"

    parameters = {
        "mode": Param("Image mode (PIL)",
                      type=str, default="I;16", mandatory=False,
                      settable=True),
    }

    handlerclass = TIFFImageSinkHandler

    def doPreinit(self, mode):
        self.log.debug("INITIALISE TIFFFileFormat")
        # Enforce PIL requirement. Do not create TIFFFileFormat instance if
        # PIL is not available.
        if PIL is None:
            self.log.error(_import_error)
            raise NicosError(self, "Python Image Library (PIL) is not "
                             "available. Please check wether it is installed "
                             "and in your PYTHONPATH")

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2
