#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""RAW file format saver"""

import numpy as np

from nicos import session
from nicos.core import Override
from nicos.devices.abstract import ImageSaver


class RAWFileFormat(ImageSaver):
    """saves RAW image and header data into two separate files"""
    parameter_overrides = {
        'filenametemplate' : Override(mandatory=False, settable=False,
                                      userparam=False,
                                      default=['%(proposal)s_%(counter)s.raw',
                                      '%(proposal)s_%(session.experiment.lastscan)s'
                                      '_%(counter)s_%(scanpoint)s.raw']),
    }

    fileFormat = 'RAW'     # should be unique amongst filesavers!

    def acceptImageType(self,  imageType):
        # everything can be saved RAW
        return True

    def prepareImage(self, imageInfo,  subdir=''):
        ImageSaver.prepareImage(self,  imageInfo,  subdir)
        exp = session.experiment
        imageInfo.headerfile = \
            exp.createDataFile(self.filenametemplate.replace('.raw','.header'),
                                exp.lastimage, subdir, self.subdir,  scanpoint=imageInfo.scanpoint)[1]

    def updateImage(self, imageInfo, image):
        imageInfo.file.seek(0)
        imageInfo.file.write(np.array(image).tostring())
        imageInfo.file.flush()

    def saveImage(self, imageInfo, image):
        self.updateImage(imageInfo, image)
        imageInfo.headerfile.write('### NICOS %s File Header V2.0\n' % self.fileFormat)
        for category, valuelist in sorted(imageInfo.header.items()):
            if valuelist:
                imageInfo.headerfile.write('### %s\n' % category)
            for (dev, key, value) in valuelist:
                imageInfo.headerfile.write('%25s : %s\n' % ('%s_%s' % (dev.name,  key),  value))
        imageInfo.headerfile.write('\n%r\n' % imageInfo.imageType) # to ease interpreting the data....

    def finalizeImage(self, imageInfo):
        """finalizes the on-disk image, normally just a close"""
        ImageSaver.finalizeImage(self,  imageInfo)
        if imageInfo.headerfile:
            imageInfo.headerfile.close()
            imageInfo.headerfile = None


class SingleRAWFileFormat(ImageSaver):
    """saves RAW image and header data into a single file"""
    parameter_overrides = {
        'filenametemplate' : Override(mandatory=False, settable=False,
                                      userparam=False,
                                      default='%(proposal)s_%(counter)s.raw|'
                                      '%(proposal)s_%(session.experiment.lastscan)s'
                                      '_%(counter)s_%(scanpoint)s.raw'),
    }

    fileFormat = 'SingleRAW'     # should be unique amongst filesavers!

    # no need to define prepareImage and finalizeImage, as they do already all we need

    def acceptImageType(self,  imageType):
        # everything can be saved RAW
        return True

    def updateImage(self, imageInfo, image):
        """just write the raw data upon update"""
        imageInfo.file.seek(0)
        imageInfo.file.write(np.array(image).tostring())
        imageInfo.file.flush()

    def saveImage(self, imageInfo, image):
        self.updateImage(imageInfo, image)
        imageInfo.file.write('### NICOS %s File Header V2.0\n' % self.fileFormat)
        for category,  valuelist in sorted(imageInfo.header.items()):
            if valuelist:
                imageInfo.file.write('### %s\n' % category)
            for (dev, key, value) in valuelist:
                imageInfo.file.write('%25s : %s\n' % ('%s_%s' % (dev.name,  key),  value))
        imageInfo.file.write('\n%r\n' % imageInfo.imageType) # to ease interpreting the data....
        imageInfo.file.flush()

