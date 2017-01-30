#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   pedersen
#
# *****************************************************************************

"""
File writer for tiff files compatible with ESMERALDA
"""

try:
    from PIL import PILLOW_VERSION  # pylint: disable=E0611
    from distutils.version import LooseVersion  # pylint: disable=E0611
    if LooseVersion(PILLOW_VERSION) < LooseVersion('3.99.0'):
        raise ImportError
    from PIL import Image
    from PIL.TiffImagePlugin import ImageFileDirectory_v2, STRIPOFFSETS

except ImportError:
    Image = None

import numpy

from nicos.core import NicosError
from nicos.core.params import Override
from nicos.devices.datasinks.image import SingleFileSinkHandler, ImageSink
from nicos.pycompat import iteritems

# tag values for esmeralda /Image_Modules_Src/Laue_tiff_read.f90
# format: nicos key: ( tiff tag nr, descr, tiff valuetype (2=str, 11, float)
TAGMAP = {'T/svalue': (1000, 'ICd%temp_begin', 11),
          'T/evalue': (1001, 'ICd%temp_end', 11),
          'Sample/name': (1002, 'ICd%sample', 2),
          'det1/preset': (1003, 'ICd%expose_time', 11),
          'phi/value': (1004, 'ICd%expose_phi', 11),
          'startx': (1005, 'ICd%startx', 11),
          'starty': (1006, 'ICd%starty', 11),
          '???3': (1007, 'ICd%speed', 11),
          'T/min': (1008, 'ICd%temp_min', 11),
          'T/max': (1009, 'ICd%temp_max', 11),
          }


class TiffLaueImageSinkHandler(SingleFileSinkHandler):

    filetype = 'TIFF'
    defer_file_creation = True

    def doPreinit(self, _mode):
        # Stop creation of the TIFFLaueFileFormat as it would make no sense
        # without correct PIL version.
        if Image is None:
            raise NicosError(self, 'PIL/Pillow module is not available. Check'
                             ' if it\'s installed and in your PYTHONPATH')

    def writeHeader(self, fp, metainfo, image):
        self.metainfo = metainfo

    def writeData(self, fp, image):
        # ensure numpy type, with float values for PIL
        npData = numpy.asarray(image, dtype='<u2')
        buf = numpy.getbuffer(npData)
        ifile = Image.frombuffer('I;16', npData.shape, buf, "raw", 'I;16', 0, 1)

        ifile.save(fp, 'TIFF', tiffinfo=self._buildHeader(self.metainfo))

    def _buildHeader(self, imageinfo):
        ifd = ImageFileDirectory_v2()  # pylint: disable=E1120
        ifd[TAGMAP['startx'][0]] = 1
        ifd[TAGMAP['starty'][0]] = 1
        for (dev, attr), attrVal in iteritems(imageinfo):
            key = '%s/%s' % (dev, attr)
            if key in TAGMAP:
                tag = TAGMAP[key][0]
                typ = TAGMAP[key][2]
                ifd.tagtype[tag] = typ
                if typ == 11:
                    attrVal = float(attrVal[0])
                ifd[tag] = attrVal

        ifd = dict(ifd)
        # increase stripoffset, otherwise ESMERALDA can not read meta data
        ifd[STRIPOFFSETS] = 186
        return ifd


class TIFFLaueSink(ImageSink):
    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['%(proposal)s_%(pointcounter)07d.tif']),
    }

    handlerclass = TiffLaueImageSinkHandler

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2
