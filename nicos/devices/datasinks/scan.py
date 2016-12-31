#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

from time import strftime, localtime

from nicos import session
from nicos.core.constants import POINT, SCAN, SUBSCAN
from nicos.core import ConfigurationError, DataSink, DataSinkHandler, \
    INFO_CATEGORIES, Override, Param
from nicos.utils import tabulated
from nicos.devices.datasinks import FileSink
from nicos.pycompat import TextIOWrapper, iteritems


TIMEFMT = '%Y-%m-%d %H:%M:%S'


def safe_format(fmtstr, value):
    try:
        return fmtstr % value
    except (TypeError, ValueError):
        return str(value)


class ConsoleScanSinkHandler(DataSinkHandler):

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._indent = '' if self.dataset.settype != SUBSCAN else ' ' * 6
        self._colwidths = []
        self._rulerlen = 100

    def begin(self):
        ds = self.dataset
        valueinfo = ds.devvalueinfo + ds.envvalueinfo + ds.detvalueinfo
        # we write every data value as a column except for arrays
        names = ['#'] + [v.name for v in valueinfo]
        units = [''] + [v.unit for v in valueinfo]
        # minimum column length is 8: fits well for -123.456
        self._colwidths = [max(len(name), len(unit), 8)
                           for (name, unit) in zip(names, units)]
        self._rulerlen = max(100, sum(self._colwidths))
        if ds.settype != SUBSCAN:
            session.log.info('=' * self._rulerlen)
            session.log.info('Starting scan:      ' + (ds.info or ''))
            session.log.info('Started at:         ' +
                             strftime(TIMEFMT, localtime(ds.started)))
            session.log.info('Scan number:        ' + str(ds.counter))
            for filename in ds.filenames:
                session.log.info('Filename:           ' + filename)
            session.log.info('-' * self._rulerlen)
        else:
            session.log.info()
            for filename in ds.filenames:
                session.log.info(self._indent + 'Filename: ' + filename)
        session.log.info(self._indent + tabulated(self._colwidths, names))
        session.log.info(self._indent + tabulated(self._colwidths, units))
        session.log.info(self._indent + '-' * self._rulerlen)

    def addSubset(self, point):
        if point.settype != POINT:
            return
        ds = self.dataset
        if ds.npoints:
            pointstr = '%s/%s' % (len(ds.subsets), ds.npoints)
        else:
            pointstr = str(len(ds.subsets))
        cols = ([pointstr] +
                [safe_format(info.fmtstr, val) for (info, val) in
                 zip(ds.devvalueinfo, point.devvaluelist)] +
                [safe_format(info.fmtstr, val) for (info, val) in
                 zip(ds.envvalueinfo, point.envvaluelist)] +
                [safe_format(info.fmtstr, val) for (info, val) in
                 zip(ds.detvalueinfo, point.detvaluelist)] +
                point.filenames)
        session.log.info(self._indent + tabulated(self._colwidths, cols))

    def end(self):
        if self.dataset.settype != SUBSCAN:
            session.log.info('-' * self._rulerlen)
            session.log.info('Finished at:        ' +
                             strftime(TIMEFMT, localtime(self.dataset.finished)))
            session.log.info('=' * self._rulerlen)
        else:
            session.log.info()


class ConsoleScanSink(DataSink):
    """A DataSink that prints scan data onto the console."""

    activeInSimulation = True

    handlerclass = ConsoleScanSinkHandler

    parameter_overrides = {
        'settypes':  Override(default=[SCAN, SUBSCAN]),
    }


class AsciiScanfileSinkHandler(DataSinkHandler):

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._wrote_header = False
        self._wrote_columninfo = False
        self._file = None
        self._fname = None
        self._semicolon = sink.semicolon
        self._commentc = sink.commentchar
        self._template = sink.filenametemplate

    def prepare(self):
        session.data.assignCounter(self.dataset)
        fp = session.data.createDataFile(self.dataset, self._template,
                                         self.sink.subdir)
        self._fname = fp.shortpath
        self._filepath = fp.filepath
        self._file = TextIOWrapper(fp)

    def _write_section(self, section):
        self._file.write('%s %s\n' % (self._commentc * 3, section))

    def _write_comment(self, comment):
        self._file.write('%s %s\n' % (self._commentc, comment))

    def _write_header(self, ds, nfiles):
        self._write_section('NICOS data file, created at %s' % strftime(TIMEFMT))
        for name, value in [('number', self.dataset.counter),
                            ('filename', self._fname),
                            ('filepath', self._filepath),
                            ('info', ds.info)]:
            self._write_comment('%25s : %s' % (name, value))
        bycategory = {}
        for (devname, key), (_, val, unit, category) in iteritems(ds.metainfo):
            if category:
                bycategory.setdefault(category, []).append(
                    ('%s_%s' % (devname, key), (val + ' ' + unit).strip()))
        for category, catname in INFO_CATEGORIES:
            if category not in bycategory:
                continue
            self._write_section(catname)
            for key, value in bycategory[category]:
                self._write_comment('%25s : %s' % (key, value))
        self._file.flush()
        # we write every data value as a column except for arrays
        xnames = [v.name for v in ds.devvalueinfo + ds.envvalueinfo]
        xunits = [v.unit for v in ds.devvalueinfo + ds.envvalueinfo]
        ynames = [v.name for v in ds.detvalueinfo]
        yunits = [v.unit for v in ds.detvalueinfo]
        # to be written later (after info)
        file_names = ['file%d' % i for i in range(1, nfiles + 1)]
        if self._semicolon:
            self._colnames = xnames + [';'] + ynames + file_names
            # make sure there are no empty units
            self._colunits = [u or '-' for u in xunits + [';'] + yunits +
                              [''] * nfiles]
        else:
            self._colnames = xnames + ynames + file_names
            self._colunits = [u or '-' for u in xunits + yunits +
                              [''] * nfiles]
        self._file.flush()

    def addSubset(self, point):
        if point.settype != POINT:
            return
        ds = self.dataset
        if not self._wrote_header:
            self._write_header(ds, len(point.filenames))
            self._wrote_header = True
        if not self._wrote_columninfo:
            self._write_section('Scan data')
            self._write_comment('\t'.join(self._colnames))
            self._write_comment('\t'.join(self._colunits))
            self._wrote_columninfo = True
        xv = [safe_format(info.fmtstr, val) for (info, val) in
              zip(self.dataset.devvalueinfo, point.devvaluelist)] + \
             [safe_format(info.fmtstr, val) for (info, val) in
              zip(self.dataset.envvalueinfo, point.envvaluelist)]
        yv = [safe_format(info.fmtstr, val) for (info, val) in
              zip(self.dataset.detvalueinfo, point.detvaluelist)]
        fv = point.filenames
        if self._semicolon:
            values = xv + [';'] + yv + fv
        else:
            values = xv + yv + fv
        self._file.write('\t'.join(values) + '\n')
        self._file.flush()

    def end(self):
        if self._fname:
            self._write_section('End of NICOS data file %s' % self._fname)
            self._file.close()
            self._file = None


class AsciiScanfileSink(FileSink):
    """A data sink that writes to a plain ASCII data file."""
    parameters = {
        'commentchar':      Param('Comment character', type=str, default='#',
                                  settable=True),
        'semicolon':        Param('Whether to add a semicolon between X and Y '
                                  'values', type=bool, default=True),
    }

    handlerclass = AsciiScanfileSinkHandler

    parameter_overrides = {
        'settypes':  Override(default=[SCAN, SUBSCAN]),
        'filenametemplate': Override(default=['%(proposal)s_%(scancounter)08d.dat']),
    }

    def doUpdateCommentchar(self, value):
        if len(value) > 1:
            raise ConfigurationError('comment character should only be '
                                     'one character')
