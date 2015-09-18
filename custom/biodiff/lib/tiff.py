# -*- coding: utf-8 -*-
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

from nicos.core.errors import NicosError
from nicos.core import ImageSink
from nicos.core.params import Param


class TIFFFileFormat(ImageSink):
    """..."""

    fileFormat = "TIFF"

    parameters = {
        "mode": Param("Image mode (PIL)",
                      type=str, default="I;16", mandatory=False,
                      settable=True),
    }

    def doPreinit(self, mode):
        self.log.debug("INITIALISE TIFFFileFormat")
        # Enforce PIL requirement. Do not create TIFFFileFormat instance if
        # PIL is not available.
        if PIL is None:
            self.log.error(_import_error)
            raise NicosError(self, "Python Image Library (PIL) is not "
                             "available. Please check wether it is installed "
                             "and in your PYTHONPATH")

    def acceptImageType(self, imagetype):
        self.log.debug("accetImageType: %s" % imagetype)
        return (len(imagetype.shape) == 2)

    def saveImage(self, imageinfo, image):
        self.log.debug("save file: %s" % imageinfo)
        Image.fromarray(numpy.array(image), self.mode).save(imageinfo.file)
