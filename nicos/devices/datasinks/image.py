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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Base Image data sink classes for NICOS."""

from nicos import session
from nicos.core import FINAL, LIVE, Override
from nicos.core.data import DataSink, DataSinkHandler, dataman
from nicos.core.data.manager import DataFile
from nicos.devices.datasinks import FileSink
from nicos.utils import syncFile


class ImageSink(FileSink):
    """Base class for sinks that save arrays to "image" files."""

    parameter_overrides = {
        'subdir': Override(description='Filetype specific subdirectory name '
                           'for the image files'),
        'settypes': Override(default=['point'])
    }

    def isActiveForArray(self, arraydesc):
        return True

    def isActive(self, dataset):
        if not DataSink.isActive(self, dataset):
            return False
        for det in dataset.detectors:
            arrayinfo = det.arrayInfo()
            if arrayinfo:
                # XXX: support multiple arrays
                return self.isActiveForArray(arrayinfo[0])
        return False


class SingleFileSinkHandler(DataSinkHandler):
    """Provide a convenient base class for writing a single data file.

    Normally, the file consists of a header part and a data part.
    """

    # this is the filetype as transferred to live-view
    filetype = 'raw'

    # set this to True to create the datafile as latest as possible
    defer_file_creation = False

    # set this to True to save only FINAL images
    accept_final_images_only = False

    # DataFile class used for creating the data file (descriptor).
    fileclass = DataFile

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._file = None
        # determine which index of the detector value is our data array
        # XXX support more than one array
        arrayinfo = self.detector.arrayInfo()
        if len(arrayinfo) > 1:
            self.log.warning('image sink only supports one array per detector')
        self._arraydesc = arrayinfo[0]

    def _createFile(self):
        if self._file is None:
            dataman.assignCounter(self.dataset)
            self._file = dataman.createDataFile(self.dataset,
                                                self.sink.filenametemplate,
                                                self.sink.subdir,
                                                fileclass=self.fileclass)

    def prepare(self):
        if not self.defer_file_creation:
            self._createFile()

    def writeHeader(self, fp, metainfo, image):
        """Write the header part of the file (first part).

        Note that *image* is None if defer_file_creation is false, because in
        that case `writeHeader` is called before the image data is available.
        """
        pass

    def writeData(self, fp, image):
        """Write the image data part of the file (second part)."""
        pass

    def putResults(self, quality, results):
        if quality == LIVE:
            return
        if self.accept_final_images_only and (quality != FINAL):
            return
        if self.detector.name in results:
            image = results[self.detector.name][1][0]
            if self.defer_file_creation:
                self._createFile()
                self.writeHeader(self._file, self.dataset.metainfo, image)
            self.writeData(self._file, image)
            syncFile(self._file)
            session.notifyDataFile(self.filetype, self._file.filepath)

    def putMetainfo(self, metainfo):
        if not self.defer_file_creation:
            self._file.seek(0)
            self.writeHeader(self._file, self.dataset.metainfo, None)

    def end(self):
        if self._file:
            self._file.close()
