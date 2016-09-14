#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from time import time as currenttime, strftime, localtime
from collections import OrderedDict

import numpy

from nicos.core.params import Override
from nicos.devices.datasinks.image import SingleFileSinkHandler, ImageSink
from nicos.core import NicosError
from nicos.pycompat import iteritems, to_ascii_string

try:
    import pyfits
except ImportError:
    pyfits = None


class FITSImageSinkHandler(SingleFileSinkHandler):

    filetype = 'fits'
    defer_file_creation = True
    accept_final_images_only = True

    def writeData(self, fp, data):
        # ensure numpy type
        npData = numpy.array(data)

        # create primary hdu from image data
        hdu = pyfits.PrimaryHDU(npData)

        # create fits header from nicos header and add entries to hdu
        self._buildHeader(self.dataset.metainfo, hdu)

        # write full fits file
        hdu.writeto(fp)

    def _buildHeader(self, info, hdu):

        finished = currenttime()
        header = {}

        for (dev, param), (_, strvalue, unit, _) in iteritems(info):
            header['%s/%s' % (dev, param)] = ('%s %s' % (strvalue,
                                                         unit)).strip()

        header = OrderedDict(
            [('begintime',
              strftime('%Y-%m-%d %H:%M:%S', localtime(self.dataset.started))),
             ('endtime',
              strftime('%Y-%m-%d %H:%M:%S', localtime(finished)))
            ] + sorted(header.items())
        )

        for key, value in iteritems(header):
            # The FITS standard defines max 8 characters for a header key.
            # To make longer keys possible, we use the HIERARCH keyword
            # here (67 chars max).
            # To get a consistent looking header, add it to every key
            key = 'HIERARCH %s' % key

            # use only ascii characters and escapes if necessary.
            value = to_ascii_string(str(value))

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

    Requires the pyfits library to be installed.
    """

    parameter_overrides = {
        'filenametemplate': Override(default=['%(pointcounter)08d.fits']),
    }

    handlerclass = FITSImageSinkHandler

    def doPreinit(self, _mode):
        # Stop creation of the FITSImageSink as it would make no sense
        # without pyfits.
        if pyfits is None:
            raise NicosError(self, 'pyfits module is not available. Check'
                             ' if it is installed and in your PYTHONPATH')

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2
