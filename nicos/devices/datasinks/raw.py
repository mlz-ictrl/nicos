#  -*- coding: utf-8 -*-
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Raw image formats."""

from __future__ import absolute_import, division, print_function

import re
from os import path

import numpy as np

from nicos import session
from nicos.core import LIVE, ConfigurationError, DataSinkHandler, Override
from nicos.core.data.sink import NicosMetaWriterMixin
from nicos.devices.datasinks.image import ImageFileReader, ImageSink, \
    SingleFileSinkHandler
from nicos.pycompat import TextIOWrapper


class SingleRawImageSinkHandler(NicosMetaWriterMixin, SingleFileSinkHandler):

    defer_file_creation = True
    update_headerinfo = True

    def writeHeader(self, fp, metainfo, image):
        fp.seek(0)
        fp.write(np.asarray(image).tostring())
        fp.write(b'\n')
        self.writeMetaInformation(fp)
        fp.flush()


class SingleRawImageSink(ImageSink):
    """Writes raw (binary) image data and header into a single file."""

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, userparam=False,
                                     default=['%(proposal)s_%(pointcounter)s.raw',
                                              '%(proposal)s_%(scancounter)s'
                                              '_%(pointnumber)s.raw']),
    }

    handlerclass = SingleRawImageSinkHandler


class RawImageSinkHandler(NicosMetaWriterMixin, DataSinkHandler):

    update_headerinfo = False

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._datafile = self._headerfile = None
        self._subdir = sink.subdir
        self._template = sink.filenametemplate
        self._headertemplate = self._template[0].replace('.raw', '.header')
        self._logtemplate = self._template[0].replace('.raw', '.log')
        # determine which index of the detector value is our data array
        # XXX support more than one array
        arrayinfo = self.detector.arrayInfo()
        if len(arrayinfo) > 1:
            self.log.warning('image sink only supports one array per detector')
        self._arraydesc = arrayinfo[0]

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        self._datafile = self.manager.createDataFile(
            self.dataset, self._template, self._subdir)
        self._headerfile = self.manager.createDataFile(
            self.dataset, self._headertemplate, self._subdir)
        self._logfile = self.manager.createDataFile(
            self.dataset, self._logtemplate, self._subdir)

    def _writeHeader(self):
        if self._headerfile is None:
            return
        self._headerfile.seek(0)
        self.writeMetaInformation(self._headerfile)
        self._headerfile.flush()

    def _writeLogs(self):
        if self._logfile is None:
            return
        self._logfile.seek(0)
        wrapper = TextIOWrapper(self._logfile)
        wrapper.write('%-15s\tmean\tstdev\tmin\tmax\n' % '# dev')
        for dev in self.dataset.valuestats:
            wrapper.write('%-15s\t%.3f\t%.3f\t%.3f\t%.3f\n' %
                          ((dev,) + self.dataset.valuestats[dev]))
        wrapper.detach()
        self._logfile.flush()

    def _writeData(self, fp, data):
        fp.seek(0)
        fp.write(np.asarray(data).tostring())
        fp.flush()

    def putResults(self, quality, results):
        if quality == LIVE:
            return
        if self.detector.name in results:
            result = results[self.detector.name]
            if result is None:
                return
            data = result[1][0]
            if data is not None:
                self._writeData(self._datafile, data)
                self._writeHeader()
                session.notifyDataFile('raw', self.dataset.uid,
                                       self.detector.name,
                                       self._datafile.filepath)

    def putMetainfo(self, metainfo):
        self._writeHeader()

    def end(self):
        self._writeLogs()
        if self.update_headerinfo:
            self._writeHeader()
        if self._datafile:
            self._datafile.close()
        if self._headerfile:
            self._headerfile.close()
        if self._logfile:
            self._logfile.close()


class RawImageSink(ImageSink):
    """Writes raw (binary) image data, metadata header, and environment device
    logs into three separate files.

    The primary filename template must contain `.raw`, which is then replaced
    by `.header` for the header file, and `.log` for the device log file.
    """

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, userparam=False,
                                     default=['%(proposal)s_%(pointcounter)s.raw',
                                              '%(proposal)s_%(scancounter)s'
                                              '_%(pointnumber)s.raw']),
    }

    handlerclass = RawImageSinkHandler

    def doInit(self, mode):
        if '.raw' not in self.filenametemplate[0]:
            raise ConfigurationError(self, 'first filenametemplate must '
                                     'contain .raw which is then exchanged '
                                     'to .header and .log for additional '
                                     'data files')


class RawImageFileReader(ImageFileReader):
    filetypes = [('raw', 'NICOS Raw Image File (*.raw)')]

    @classmethod
    def fromfile(cls, filename):
        fheader = path.splitext(filename)[0] + '.header'
        if path.isfile(fheader) and path.isfile(filename):
            with open(fheader, 'r') as fd:
                for line in fd:
                    # TODO: ArrayDesc currently uses nx, ny, nz, ... as shape
                    if line.startswith('ArrayDesc('):
                        m = re.match(r'.*\((\d+),\s*(\d+)\).*dtype\('
                                     r'\'(.*)\'\).*', line)
                        if m:
                            nx, ny = int(m.group(1)), int(m.group(2))
                            dtype = m.group(3)
                            return np.fromfile(filename, dtype).reshape((ny,
                                                                         nx))
