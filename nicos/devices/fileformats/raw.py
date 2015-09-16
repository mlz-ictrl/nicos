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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""RAW file format saver

XXX: document the file format here.
"""

import numpy as np

from nicos import session
from nicos.core import Override, ImageSink


class RAWFileFormat(ImageSink):
    """Saves RAW image and header data into two separate files"""
    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['%(proposal)s_%(counter)s.raw',
                                              '%(proposal)s_%(session.experiment.lastscan)s'
                                              '_%(counter)s_%(scanpoint)s.raw']),
    }

    fileFormat = 'RAW'     # should be unique amongst filesavers!

    def acceptImageType(self, imagetype):
        # everything can be saved RAW
        return True

    def prepareImage(self, imageinfo, subdir=''):
        ImageSink.prepareImage(self, imageinfo, subdir)
        exp = session.experiment
        imageinfo.headerfile = \
            exp.createDataFile(self.filenametemplate[0].replace('.raw',
                                                                '.header'),
                               exp.lastimage, subdir, self.subdir,
                               scanpoint=imageinfo.scanpoint)[1]

    def updateImage(self, imageinfo, image):
        imageinfo.file.seek(0)
        imageinfo.file.write(np.array(image).tostring())
        imageinfo.file.flush()

    def _writeHeader(self, imagetype, header, fp):
        fp.write('### NICOS %s File Header V2.0\n' % self.fileFormat)
        for category, valuelist in sorted(header.items()):
            if valuelist:
                fp.write('### %s\n' % category)
            for (dev, key, value) in valuelist:
                fp.write('%25s : %s\n' % ('%s_%s' % (dev.name, key), value))
        # to ease interpreting the data...
        fp.write('\n%r\n' % imagetype)

    def saveImage(self, imageinfo, image):
        self.updateImage(imageinfo, image)
        self._writeHeader(imageinfo.imagetype, imageinfo.header,
                          imageinfo.headerfile)

    def finalizeImage(self, imageinfo):
        """finalizes the on-disk image, normally just a close"""
        ImageSink.finalizeImage(self, imageinfo)
        if imageinfo.headerfile:
            imageinfo.headerfile.close()
            imageinfo.headerfile = None


class SingleRAWFileFormat(ImageSink):
    """Saves RAW image and header data into a single file"""
    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['%(proposal)s_%(counter)s.raw',
                                              '%(proposal)s_%(session.experiment.lastscan)s'
                                              '_%(counter)s_%(scanpoint)s.raw']),
    }

    fileFormat = 'SingleRAW'     # should be unique amongst filesavers!

    # no need to define prepareImage and finalizeImage, as they do already
    # all we need

    def acceptImageType(self, imagetype):
        # everything can be saved RAW
        return True

    def updateImage(self, imageinfo, image):
        """just write the raw data upon update"""
        imageinfo.file.seek(0)
        imageinfo.file.write(np.array(image).tostring())
        imageinfo.file.flush()

    def _writeHeader(self, imagetype, header, fp):
        fp.write('\n### NICOS %s File Header V2.0\n' % self.fileFormat)
        for category, valuelist in sorted(header.items()):
            if valuelist:
                fp.write('### %s\n' % category)
            for (dev, key, value) in valuelist:
                fp.write('%25s : %s\n' % ('%s_%s' % (dev.name, key), value))
        # to ease interpreting the data...
        fp.write('\n%r\n' % imagetype)
        fp.flush()

    def saveImage(self, imageinfo, image):
        self.updateImage(imageinfo, image)
        self._writeHeader(imageinfo.imagetype, imageinfo.header, imageinfo.file)
