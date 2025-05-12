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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
File writer for tiff files compatible with ESMERALDA
"""

import numpy

from nicos.core import NicosError
from nicos.core.params import Override
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler

try:
    from PIL import Image
    from PIL.TiffImagePlugin import STRIPOFFSETS, ImageFileDirectory_v2
except ImportError:
    Image = None



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

    filetype = 'tiff'
    defer_file_creation = True

    def doPreinit(self, _mode):
        # Stop creation of the TIFFLaueFileFormat as it would make no sense
        # without correct PIL version.
        if Image is None:
            raise NicosError(self, 'PIL/Pillow module is not available. Check'
                             " if it's installed and in your PYTHONPATH")

    def writeHeader(self, fp, metainfo, image):
        self.metainfo = metainfo

    def writeData(self, fp, image):
        # ensure numpy type, with float values for PIL
        npData = numpy.asarray(image, dtype='<u2')
        buf = numpy.getbuffer(npData)
        # TODO: check if this still works.
        ifile = Image.frombuffer('I;16', npData.shape[::-1], buf, 'raw',
                                 'I;16', 0, -1)

        ifile.save(fp, 'TIFF', tiffinfo=self._buildHeader(self.metainfo))

    def _buildHeader(self, imageinfo):
        ifd = ImageFileDirectory_v2()
        ifd[TAGMAP['startx'][0]] = 1
        ifd[TAGMAP['starty'][0]] = 1
        for (dev, attr), attrVal in imageinfo.items():
            key = '%s/%s' % (dev, attr)
            if key in TAGMAP:
                tag = TAGMAP[key][0]
                typ = TAGMAP[key][2]
                ifd.tagtype[tag] = typ
                if typ == 11:
                    attrVal = float(attrVal[0])
                ifd[tag] = attrVal

        ifd = dict(ifd)
        # increase stripoffset, otherwise ESMERALDA can not read metadata
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
