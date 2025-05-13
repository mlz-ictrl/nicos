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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

import numpy

from nicos.core import NicosError, Override, Param
from nicos.devices.datasinks.image import ImageFileReader, ImageSink, \
    SingleFileSinkHandler

try:
    import PIL
    from PIL import Image
except ImportError as e:
    PIL = None
    _import_error = e


class TIFFImageSinkHandler(SingleFileSinkHandler):

    filetype = 'tiff'
    defer_file_creation = True
    accept_final_images_only = True

    def writeData(self, fp, image):
        Image.fromarray(numpy.array(image), self.sink.mode).save(fp, 'TIFF')


class TIFFImageSink(ImageSink):
    """TIFF image sink, without metadata.

    This data sink writes TIFF format files without any metadata.
    """

    parameters = {
        'mode': Param('Image mode (PIL format)', type=str, default='I;16',
                      settable=True),
    }

    parameter_overrides = {
        'filenametemplate': Override(default=['%(pointcounter)08d.tiff'])
    }

    handlerclass = TIFFImageSinkHandler

    def doPreinit(self, mode):
        # Enforce PIL requirement. Do not create TIFFFileFormat instance if
        # PIL is not available.
        if PIL is None:
            self.log.error(_import_error)
            raise NicosError(self, 'The Python Image Library (PIL) is not '
                             'available. Please check whether it is installed '
                             'and in your PYTHONPATH')

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2


class TIFFFileReader(ImageFileReader):
    filetypes = [
        ('tiff', 'TIFF File (*.tiff *.tif)'),
    ]

    @classmethod
    def fromfile(cls, filename):
        if PIL is None:
            raise NicosError('%s: The Python Image Library (PIL) is not '
                             'available. Please check whether it is installed '
                             'and in your PYTHONPATH' % _import_error)
        with Image.open(filename) as im:
            if im.getbands() in ('I', ('I',)):  # single band == gray picture
                return numpy.asarray(im)
            raise NicosError('Only monochrome pictures supported')
