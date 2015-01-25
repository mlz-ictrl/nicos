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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Data sink classes (new API) for NICOS."""

from time import time as currenttime

import numpy as np

from nicos import session
from nicos.core import Override, Param, subdir, listof, INFO_CATEGORIES
from nicos.core.newdata import DataSink, DataSinkHandler, dataman, LIVE
from nicos.pycompat import iteritems


class ImageSink(DataSink):
    """Base class for sinks that save arrays to "image" files."""

    parameters = {
        'subdir': Param('Filetype specific subdirectory name for the image files',
                        type=subdir, mandatory=False, default=''),
        'filenametemplate': Param('List of templates for data file names '
                                  '(will be hardlinked)', type=listof(str),
                                  default=['%08d.dat'], settable=True),
    }

    parameter_overrides = {
        'settypes': Override(default=['point'])
    }

    def isActive(self, dataset):
        if not DataSink.isActive(self, dataset):
            return False
        for det in dataset.detectors:
            if det.arrayInfo():
                return True
        return False


class RawImageSinkHandler(DataSinkHandler):

    def init(self, sink):
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
        self._arrayinfo = arrayinfo[0]

    def begin(self):
        dataman.assignCounter(self.dataset)
        self._datafile = dataman.createDataFile(
            self.dataset, self._template, self._subdir)
        self._headerfile = dataman.createDataFile(
            self.dataset, self._headertemplate, self._subdir)
        self._logfile = dataman.createDataFile(
            self.dataset, self._logtemplate, self._subdir)

    def _writeHeader(self, fp, header):
        fp.seek(0)
        fp.write('### NICOS Raw File Header V3.0\n')
        bycategory = {}
        for (device, key), (_, val, unit, category) in iteritems(header):
            if category:
                bycategory.setdefault(category, []).append(
                    ('%s_%s' % (device.name, key), (val + ' ' + unit).strip()))
        for category, _catname in INFO_CATEGORIES:
            if category not in bycategory:
                continue
            fp.write('### %s\n' % category)
            for key, value in bycategory[category]:
                fp.write('%25s : %s\n' % (key, value))
        # to ease interpreting the data...
        fp.write('\n%r\n' % self._arrayinfo)
        fp.flush()

    def _writeLogs(self, fp, stats):
        fp.seek(0)
        fp.write('%-15s\tmean\tstdev\tmin\tmax\n' % '# dev')
        for dev in self.dataset.valuestats:
            fp.write('%-15s\t%.3f\t%.3f\t%.3f\t%.3f\n' %
                     ((dev,) + self.dataset.valuestats[dev]))
        fp.flush()

    def _writeData(self, fp, data):
        fp.seek(0)
        fp.write(np.asarray(data).tostring())
        fp.flush()

    def addResults(self, quality, results):
        if quality == LIVE:
            return
        if self.detector.name in results:
            data = results[self.detector.name][1][0]
            if data is not None:
                self._writeData(self._datafile, data)
                session.updateLiveData('raw', self._datafile.filepath,
                                       self._arrayinfo.dtype, 0, 0, 0, 0, b'')

    def addMetainfo(self, metainfo):
        self._writeHeader(self._headerfile, self.dataset.metainfo)

    def end(self):
        self._writeLogs(self._logfile, self.dataset.valuestats)
        if self._datafile:
            self._datafile.close()
        if self._headerfile:
            self._headerfile.close()


class RawImageSink(ImageSink):

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['%(proposal)s_%(pointcounter)s.raw',
                                              '%(proposal)s_%(scancounter)s'
                                              '_%(pointnumber)s.raw']),
    }

    handlerclass = RawImageSinkHandler


class LiveViewSinkHandler(DataSinkHandler):

    def init(self, sink):
        if len(self.detector.arrayInfo()) > 1:
            self.log.warning('image sink only supports one array per detector')

    def addResults(self, quality, results):
        if self.detector.name in results:
            data = results[self.detector.name][1][0]
            if data is not None:
                if len(data.shape) == 2:
                    (resX, resY), resZ = data.shape, 1
                else:
                    resX, resY, resZ = data.shape
                # XXX: tag = live?
                session.updateLiveData('', '', '<u4', resX, resY, resZ,
                                       currenttime() - self.dataset.started,
                                       buffer(data.astype('<u4')))


class LiveViewSink(ImageSink):
    parameter_overrides = {
        # this is not really used, so we give it a default that would
        # raise if used as a template filename
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False, default=['']),
    }

    handlerclass = LiveViewSinkHandler
