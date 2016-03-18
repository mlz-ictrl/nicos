#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2015-2016 by the NICOS contributors (see AUTHORS)
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
    if LooseVersion(PILLOW_VERSION) < LooseVersion('2.7.0'):
        raise ImportError
    from PIL import Image
    from PIL.TiffImagePlugin import ImageFileDirectory, STRIPOFFSETS
    from nicos.laue.patch_tiff_image_plugin import save
    ImageFileDirectory.save = save
except ImportError:
    Image = None

import numpy

from nicos.core import ImageSink, NicosError
from nicos.pycompat import iteritems


# tag values for esmeralda /Image_Modules_Src/Laue_tiff_read.f90
# format: nicos key: ( tiff tag nr, descr, tiff valuetype (3=str, 11, float)
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


# TODO: port to new data API
class TIFFLaueFileFormat(ImageSink):

    fileFormat = 'TIFF'

    def doPreinit(self, _mode):
        # Stop creation of the TIFFLaueFileFormat as it would make no sense
        # without correct PIL version.
        if Image is None:
            raise NicosError(self, 'PIL/Pillow module is not available. Check'
                             ' if it\'s installed and in your PYTHONPATH')

    def acceptImageType(self, imageType):
        # Note: FITS would be capable of saving multiple images in one file
        # (as 3. dimension). May be implemented if necessary. For now, only
        # 2D data is supported.
        return (len(imageType.shape) == 2)

    def saveImage(self, info, data):
        # ensure numpy type, with float values for PIL
        npData = numpy.asarray(data, dtype='<u2')
        buf = numpy.getbuffer(npData)
        ifile = Image.frombuffer('I;16', npData.shape, buf, "raw", 'I;16', 0, 1)

        ifile.save(info.file, 'TIFF', tiffinfo=self._buildHeader(info))

    def _buildHeader(self, imageinfo):
        ifd = ImageFileDirectory()  # pylint: disable=E1120
        ifd[TAGMAP['startx'][0]] = 1
        ifd[TAGMAP['starty'][0]] = 1
        ifd[STRIPOFFSETS] = 8
        for _cat, dataSets in iteritems(imageinfo.header):
            for dev, attr, attrVal in dataSets:
                key = '%s/%s' % (dev.name, attr)
                if key in TAGMAP:
                    tag = TAGMAP[key][0]
                    typ = TAGMAP[key][2]
                    ifd.tagtype[tag] = typ
                    if typ == 11:
                        attrVal = float(attrVal.split(' ')[0])
                    ifd[tag] = attrVal

        return ifd
