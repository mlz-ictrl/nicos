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

from collections import OrderedDict
from time import localtime, strftime, time as currenttime

import numpy

from nicos.core import NicosError
from nicos.core.params import Override
from nicos.devices.datasinks.image import ImageFileReader, ImageSink, \
    SingleFileSinkHandler
from nicos.utils import toAscii

try:
    from astropy.io import fits
except ImportError:
    fits = None


class FITSImageSinkHandler(SingleFileSinkHandler):

    filetype = 'fits'
    defer_file_creation = True
    accept_final_images_only = True

    def writeData(self, fp, image):
        # ensure numpy type
        npData = numpy.array(image)

        # create primary hdu from image data
        hdu = fits.PrimaryHDU(npData)

        # create fits header from nicos header and add entries to hdu
        self._buildHeader(self.dataset.metainfo, hdu)

        # write full fits file
        hdu.writeto(fp)

    def _collectHeaderItems(self, info):

        finished = currenttime()
        header = {}

        for (dev, param), pinfo in info.items():
            header['%s/%s' % (dev, param)] = ('%s %s' % (pinfo.strvalue,
                                                         pinfo.unit)).strip()

        header = OrderedDict(
            [('begintime',
              strftime('%Y-%m-%d %H:%M:%S', localtime(self.dataset.started))),
             ('endtime',
              strftime('%Y-%m-%d %H:%M:%S', localtime(finished)))
             ] + sorted(header.items())
        )
        return header

    def _buildHeader(self, info, hdu):

        for key, value in self._collectHeaderItems(info).items():
            # The FITS standard defines max 8 characters for a header key.
            # To make longer keys possible, we use the HIERARCH keyword
            # here (67 chars max).
            # To get a consistent looking header, add it to every key
            key = 'HIERARCH %s' % key

            # use only ascii characters and escapes if necessary.
            value = toAscii(str(value))

            # Determine maximum possible value length (key dependend).
            maxValLen = 63 - len(key)

            # Split the dataset into several header entries if necessary
            # (due to the limited length)
            splittedHeaderItems = [value[i:i + maxValLen]
                                   for i in range(0, len(value), maxValLen)]

            for item in splittedHeaderItems:
                hdu.header.append((key, item))


class FITSImageSink(ImageSink):
    """Writes data to a FITS (Flexible image transport system) format file.

    NICOS headers are also written into the file using the standard FITS header
    facility, with HIERARCH type keys.

    Requires the astropy library to be installed.
    """

    parameter_overrides = {
        'filenametemplate': Override(default=['%(pointcounter)08d.fits']),
    }

    handlerclass = FITSImageSinkHandler

    def doPreinit(self, _mode):
        # Stop creation of the FITSImageSink as it would make no sense
        # without astropy.
        if fits is None:
            raise NicosError(self, 'The astropy.io.fits module is not '
                             'available, check if it is installed')

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2


class FITSFileReader(ImageFileReader):
    filetypes = [('fits', 'FITS File (*.fits)')]

    @classmethod
    def fromfile(cls, filename):
        hdu_list = fits.open(filename)
        return numpy.flipud(hdu_list[0].data)
