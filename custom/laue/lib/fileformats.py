#  -*- coding: utf-8 -*-
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""ASCII file format saver

File format description:

Every line starting with a '#' char is a comment line.
It consists of a header and a data section.
The header starts with line:

### NICOS SingleASCII File Header V2.0

The header is devided into sections starting with '###' and followed by section
description:

### Device positions and sample environment state

The entries inside a section give information about the device and its
parameter followed by a colon and the value:

        det_time : 297.089000

which has to be interpreted as device named 'det' has a parameter 'time' and
the value is '297.089000'

The data section starts with line:

### Start data

Each line represents a datapoint (point #, value):

        0       1925
"""

from nicos.core import Override, ImageSink

# TODO: port to new data API
class ASCIIFileFormat(ImageSink):
    """Saves header data and single spectrum data into a single file"""

    fileFormat = 'SingleASCII'     # should be unique amongst filesavers!

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False, prefercache=False,
                                     default=['%(proposal)s_'
                                              '%(pointcounter)s.txt',
                                              ]),
    }

    def acceptImageType(self, imagetype):
        return len(imagetype.shape) == 1

    def updateImage(self, imageinfo, image):
        """just write the raw data upon update"""
        text = ''
        for (i, value) in enumerate(image):
            text += '%10d %10d\n' % (i, value, )
        imageinfo.file.write(text)
        imageinfo.file.flush()

    def _writeHeader(self, imagetype, header, fp):
        fp.write('### NICOS %s File Header V2.0\n' % self.fileFormat)
        for category, valuelist in sorted(header.items()):
            if valuelist:
                fp.write('### %s\n' % category)
                for (dev, key, value) in valuelist:
                    fp.write('%25s : %s\n' % ('%s_%s' % (dev.name, key),
                                              value))
        # to ease interpreting the data...
        fp.write('### Start data\n')
        fp.flush()

    def saveImage(self, imageinfo, image):
        self._writeHeader(imageinfo.imagetype, imageinfo.header,
                          imageinfo.file)
        self.updateImage(imageinfo, image)
