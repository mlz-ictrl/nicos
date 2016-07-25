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

"""Raw image formats."""

import numpy as np

from nicos import session
from nicos.core import Override, INFO_CATEGORIES, DataSinkHandler, LIVE, \
    ConfigurationError
from nicos.pycompat import iteritems, TextIOWrapper
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler


class SingleRawImageSinkHandler(SingleFileSinkHandler):

    defer_file_creation = True

    def writeHeader(self, fp, metainfo, image):
        fp.seek(0)
        fp.write(np.asarray(image).tostring())
        wrapper = TextIOWrapper(fp)
        wrapper.write('\n### NICOS Raw File Header V2.0\n')
        # XXX(dataapi): add a utility function to convert metainfo to old
        # by-category format
        bycategory = {}
        for (device, key), (_, val, unit, category) in iteritems(metainfo):
            if category:
                bycategory.setdefault(category, []).append(
                    ('%s_%s' % (device, key), (val + ' ' + unit).strip()))
        for category, catname in INFO_CATEGORIES:
            if category not in bycategory:
                continue
            wrapper.write('### %s\n' % catname)
            for key, value in sorted(bycategory[category]):
                wrapper.write('%25s : %s\n' % (key, value))
        # to ease interpreting the data...
        wrapper.write('\n%r\n' % self._arraydesc)
        wrapper.detach()
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


class RawImageSinkHandler(DataSinkHandler):

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
        session.data.assignCounter(self.dataset)
        self._datafile = session.data.createDataFile(
            self.dataset, self._template, self._subdir)
        self._headerfile = session.data.createDataFile(
            self.dataset, self._headertemplate, self._subdir)
        self._logfile = session.data.createDataFile(
            self.dataset, self._logtemplate, self._subdir)

    def _writeHeader(self, fp, header):
        fp.seek(0)
        wrapper = TextIOWrapper(fp)
        wrapper.write('### NICOS Raw File Header V2.0\n')
        bycategory = {}
        for (device, key), (_, val, unit, category) in iteritems(header):
            if category:
                bycategory.setdefault(category, []).append(
                    ('%s_%s' % (device, key), (val + ' ' + unit).strip()))
        for category, catname in INFO_CATEGORIES:
            if category not in bycategory:
                continue
            wrapper.write('### %s\n' % catname)
            for key, value in sorted(bycategory[category]):
                wrapper.write('%25s : %s\n' % (key, value))
        # to ease interpreting the data...
        wrapper.write('\n%r\n' % self._arraydesc)
        wrapper.detach()
        fp.flush()

    def _writeLogs(self, fp, stats):
        fp.seek(0)
        wrapper = TextIOWrapper(fp)
        wrapper.write('%-15s\tmean\tstdev\tmin\tmax\n' % '# dev')
        for dev in self.dataset.valuestats:
            wrapper.write('%-15s\t%.3f\t%.3f\t%.3f\t%.3f\n' %
                          ((dev,) + self.dataset.valuestats[dev]))
        wrapper.detach()
        fp.flush()

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
                session.notifyDataFile('raw', self._datafile.filepath)

    def putMetainfo(self, metainfo):
        self._writeHeader(self._headerfile, self.dataset.metainfo)

    def end(self):
        self._writeLogs(self._logfile, self.dataset.valuestats)
        if self._datafile:
            self._datafile.close()
        if self._headerfile:
            self._headerfile.close()


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
