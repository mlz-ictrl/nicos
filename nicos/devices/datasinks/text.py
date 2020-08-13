# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from gzip import GzipFile as StdGzipFile

import numpy

from nicos.core.data.sink import GzipFile
from nicos.devices.datasinks.image import ImageFileReader, ImageSink, \
    MultipleFileSinkHandler
from nicos.utils import File


class NPImageSinkHandler(MultipleFileSinkHandler):
    """Numpy text format filesaver using `numpy.savetxt`"""

    filetype = "TXT"

    def writeData(self, fp, image):
        numpy.savetxt(fp, numpy.asarray(image), fmt="%u")


class NPFileSink(ImageSink):
    handlerclass = NPImageSinkHandler


class NPImageFileReader(ImageFileReader):
    filetypes = [("txt", "Numpy Text Format (*.txt)")]

    @classmethod
    def fromfile(cls, filename):
        """Reads numpy array from .txt file."""
        return numpy.loadtxt(File(filename, 'r'))


class NPGZImageSinkHandler(NPImageSinkHandler):
    """Compressed Numpy text format filesaver using `numpy.savetxt`"""

    filetype = "NPGZ"
    fileclass = GzipFile

    def writeData(self, fp, image):
        numpy.savetxt(fp, numpy.asarray(image), fmt="%u")


class NPGZFileSink(ImageSink):
    handlerclass = NPGZImageSinkHandler


class NPGZImageFileReader(ImageFileReader):
    filetypes = [("npgz", "Compressed Numpy Text Format (*.gz)")]

    @classmethod
    def fromfile(cls, filename):
        """Reads numpy array from .gz file."""
        return numpy.loadtxt(StdGzipFile(filename, 'r'))
