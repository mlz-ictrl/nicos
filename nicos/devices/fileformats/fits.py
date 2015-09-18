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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import time
import numpy


from nicos.core import ImageSink, NicosError
from nicos.pycompat import iteritems, to_ascii_escaped, OrderedDict
from nicos.utils import syncFile

try:
    import pyfits
except ImportError:
    pyfits = None


class FITSFileFormat(ImageSink):

    fileFormat = 'FITS'

    def doPreinit(self, _mode):
        # Stop creation of the FITSFileFormat as it would make no sense
        # without pyfits.
        if pyfits is None:
            raise NicosError(self, 'pyfits module is not available. Check'
                             ' if it\'s installed and in your PYTHONPATH')

    def acceptImageType(self, imageType):
        # Note: FITS would be capable of saving multiple images in one file
        # (as 3. dimension). May be implemented if necessary. For now, only
        # 2D data is supported.
        return (len(imageType.shape) == 2)

    def saveImage(self, info, data):
        # ensure numpy type
        npData = numpy.array(data)

        # create primary hdu from image data
        hdu = pyfits.PrimaryHDU(npData)

        # create fits header from nicos header and add entries to hdu
        self._buildHeader(info, hdu)

        hdu.writeto(info.file)

        # sync file to avoid caching problems (=> nfs)
        syncFile(info.file)

    def _buildHeader(self, imageinfo, hdu):

        header = OrderedDict({
            'begintime': time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime(imageinfo.begintime)),
            'endtime': time.strftime('%Y-%m-%d %H:%M:%S',
                                     time.localtime(imageinfo.endtime))
        })

        for _cat, dataSets in iteritems(imageinfo.header):
            for dev, attr, attrVal in dataSets:
                header['%s/%s' % (dev.name, attr)] = attrVal

        for key, value in iteritems(header):
            # The FITS standard defines max 8 characters for a header key.
            # To make longer keys possible, we use the HIERARCH keyword
            # here (67 chars max).
            # To get a consistent looking header, add it to every key
            key = 'HIERARCH %s' % key

            # use only ascii characters and escapes if necessary.
            value = to_ascii_escaped(str(value))

            # Determine maximum possible value length (key dependend).
            maxValLen = 63 - len(key)

            # Split the dataset into several header entries if necessary
            # (due to the limited length)
            splittedHeaderItems = [value[i:i + maxValLen]
                                   for i in range(0, len(value), maxValLen)]

            for item in splittedHeaderItems:
                hdu.header.append((key, item))
