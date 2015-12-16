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

"""QMesydaq file writer classes"""

import os

from nicos.core import Override, Attach, ImageSink, SIMULATION
from nicos.devices.vendor.qmesydaq import Image


class QMesydaqFormat(ImageSink):
    """Base class for the QMesyDAQ related data files.

    The class reimplements all methods to avoid real data writing in NICOS
    itself. It ensures that the listmode and/or histogram data files will be
    written via QMesyDAQ itself. It uses the settings of the NICOS to define the
    names of the files but the directory to write the data is set in QMesyDAQ.
    """
    attached_devices = {
        'image': Attach('Image device to set the file name',
                        Image, optional=True),
    }

    def acceptImageType(self, imagetype):
        return len(imagetype.shape) == 2

    def prepareImage(self, imageinfo, subdir=''):
        """Prepares an Imagefile in the given subdir.

        It will be removed since it is not needed anymore, but the filename is
        needed.
        """
        ImageSink.prepareImage(self, imageinfo, subdir)
        self._removeImagefile(imageinfo)

    def _removeImagefile(self, imageinfo):
        if self._mode != SIMULATION and imageinfo.file:
            imageinfo.file.close()
            self.log.debug('removing file: %s' % imageinfo.filepath)
            os.remove(imageinfo.filepath)
            imageinfo.file = None

    def saveImage(self, imageinfo,  image):
        pass

    def finalizeImage(self, imageinfo):
        pass


class HistogramFileFormat(QMesydaqFormat):
    """Writer for the histogram files via QMesyDAQ itself."""
    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['D%(counter)07d.mtxt'],
                                     ),
    }

    fileFormat = 'MesytecHistogram'  # should be unique amongst filesavers!

    def prepareImage(self, imageinfo, subdir=''):
        QMesydaqFormat.prepareImage(self, imageinfo, subdir)
        self._attached_image.histogramfile = imageinfo.filename


class ListmodeFileFormat(QMesydaqFormat):
    """Writer for the list mode files via QMesyDAQ itself."""

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['D%(counter)07d.mdat'],
                                     ),
    }

    fileFormat = 'MesytecListMode'  # should be unique amongst filesavers!

    def prepareImage(self, imageinfo, subdir=''):
        QMesydaqFormat.prepareImage(self, imageinfo, subdir)
        self._attached_image.listmodefile = imageinfo.filename
