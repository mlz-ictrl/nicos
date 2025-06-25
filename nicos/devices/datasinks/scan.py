# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Data sink classes (new API) for NICOS."""

import datetime
import re
from io import TextIOWrapper
from os.path import basename
from time import localtime, mktime, strftime

from nicos import session
from nicos.core import INFO_CATEGORIES, ConfigurationError, DataSink, \
    DataSinkHandler, Override, Param, Value
from nicos.core.constants import POINT, SCAN, SUBSCAN
from nicos.core.data.dataset import PointDataset, ScanData, ScanDataset
from nicos.devices.datasinks import FileSink
from nicos.utils import LOCALE_ENCODING, tabulated

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
            session.log.info('Starting scan:      %s', ds.info or '')
            session.log.info('Started at:         %s',
                             strftime(TIMEFMT, localtime(ds.started)))
            session.log.info('Scan number:        %d', ds.counter)
            session.log.info('Sample name:        %s',
                             session.experiment.sample.read())
            for filename in ds.filenames:
                session.log.info('Filename:           %s', filename)
            session.log.info('-' * self._rulerlen)
        else:
            session.log.info()
            for filename in ds.filenames:
                session.log.info('%sFilename: %s', self._indent, filename)

        session.log.info('%s%s', self._indent, tabulated(self._colwidths, names))
        session.log.info('%s%s', self._indent, tabulated(self._colwidths, units))
        session.log.info('%s%s', self._indent, '-' * self._rulerlen)

    def addSubset(self, subset):
        if subset.settype != POINT:
            return
        point = subset
        ds = self.dataset
        if ds.npoints:
            pointstr = '%s/%s' % (point.number, ds.npoints)
        else:
            pointstr = str(point.number)
        cols = ([pointstr] +
                [safe_format(info.fmtstr, val) for (info, val) in
                 zip(ds.devvalueinfo, point.devvaluelist)] +
                [safe_format(info.fmtstr, val) for (info, val) in
                 zip(ds.envvalueinfo, point.envvaluelist)] +
                [safe_format(info.fmtstr, val) for (info, val) in
                 zip(ds.detvalueinfo, point.detvaluelist)] +
                point.filenames)
        session.log.info('%s%s', self._indent, tabulated(self._colwidths, cols))

    def end(self):
        if self.dataset.settype != SUBSCAN:
            session.log.info('-' * self._rulerlen)
            session.log.info('Finished at:        %s',
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
        self._file = None
        self._fname = None
        self._commentc = sink.commentchar
        self._template = sink.filenametemplate

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        fp = self.manager.createDataFile(self.dataset, self._template,
                                         self.sink.subdir,
                                         filemode=self.sink.filemode)
        self._fname = fp.shortpath
        self._filepath = fp.filepath
        self._file = TextIOWrapper(fp, encoding='utf-8')

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
        for (devname, key), info in ds.metainfo.items():
            if info.category:
                bycategory.setdefault(info.category, []).append(
                    ('%s_%s' % (devname, key),
                     (info.strvalue + ' ' + info.unit).strip()))
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
        self._colnames = xnames + [';'] + ynames + file_names
        # make sure there are no empty units
        self._colunits = [u or '-' for u in xunits + [';'] + yunits +
                          [''] * nfiles]
        self._file.flush()

    def addSubset(self, subset):
        if subset.settype != POINT:
            return
        point = subset
        ds = self.dataset
        if point.number == 1:
            self._write_header(ds, len(point.filenames))
            self._write_section('Scan data')
            self._write_comment('\t'.join(self._colnames))
            self._write_comment('\t'.join(self._colunits))
        values = [safe_format(info.fmtstr, val) for (info, val) in
                  zip(self.dataset.devvalueinfo, point.devvaluelist)] + \
                 [safe_format(info.fmtstr, val) for (info, val) in
                  zip(self.dataset.envvalueinfo, point.envvaluelist)]
        values += [';']
        values += [safe_format(info.fmtstr, val) for (info, val) in
                   zip(self.dataset.detvalueinfo, point.detvaluelist)]
        values += self.getFilenames(point)

        self._file.write('\t'.join(values) + '\n')
        self._file.flush()

    def getFilenames(self, point):
        return point.filenames

    def end(self):
        if self._fname:
            self._write_section('End of NICOS data file %s' % self._fname)
            self._file.close()
            self._file = None


class AsciiScanfileReader:

    re_number_unit = re.compile(r'^(\d+\.?\d*)(\s(.+)|)')
    re_collection_unit = re.compile(r'^((\(|\[).+(\)|\]))(\s(.+)|)')

    class DevFake:

        def __init__(self, name):
            self.name = name

    def __init__(self, filename):
        self.scandataset = ScanDataset()
        self.metainfo = {}
        self.readFile(filename)

    def getCategory(self, text):
        for cat, txt in INFO_CATEGORIES:
            if text == txt:
                return cat
        return ''

    def getKeyValue(self, line):
        k, v = line[1:].split(':', 1)
        return k.strip(), v.strip()

    def getDevicesDetectors(self, line):
        devs, dets = line.split(';')
        return devs.split(), dets.split()

    def getMetainfoKey(self, line):
        return line.rsplit('_', 1)

    def getMetainfoValue(self, line):
        session.log.debug(line)
        if line:
            res = self.re_number_unit.match(line)
            if res:
                v = res.group(1)
                return (v, v, res.group(2))
            res = self.re_collection_unit.match(line)
            if res:
                v = res.group(1)
                return (v, v, res.group(5) or '')
        return (line, line, '')

    @property
    def scandata(self):
        return ScanData(self.scandataset)

    def readFile(self, filename):
        entry = ''
        scanheader = 0

        def guess_det_type(name, unit):
            if unit in ['s']:
                return 'time'
            elif unit in ['cts']:
                if name.startswith('m'):
                    return 'monitor'
                return 'counter'
            return 'other'

        with open(filename, 'r', encoding=LOCALE_ENCODING) as f:
            for line in f:
                lin = line.strip()
                if lin.startswith('###'):
                    _, t = lin.split(' ', 1)
                    cat = self.getCategory(t)
                    if cat:
                        session.log.debug('cat: %s, t: %s', cat, t)
                        entry = cat
                    elif t.startswith('NICOS data file,'):
                        entry = 'header'
                        created = t.split(' ', 5)[5]
                        self.scandataset.started = mktime(
                            datetime.datetime.strptime(
                                created, TIMEFMT).timetuple())
                        session.log.debug('created: %s, started: %s',
                                          created, self.scandataset.started)
                    elif t.startswith('Scan data'):
                        entry = 'data'
                    elif t.startswith('End of NICOS data file'):
                        entry = ''
                elif lin.startswith('#'):
                    if entry == 'header':
                        key, value = self.getKeyValue(lin)
                        if key == 'filename':
                            self.scandataset.filenames = [value]
                        elif key == 'filepath':
                            self.scandataset.filepaths = [value]
                        elif key == 'number':
                            self.scandataset.counter = '%s (%s)' % (
                                value, basename(filename))
                        elif key == 'info':
                            self.scandataset.info = value
                        else:
                            session.log.warning('unknown header: %s=%s',
                                                key, value)
                    elif entry == 'data':
                        # get header lines devices and units
                        if not scanheader:
                            devs, dets = self.getDevicesDetectors(line[1:])
                            session.log.debug('devs: %s, dets: %s', devs, dets)
                            self.devs = [self.DevFake(dev) for dev in devs]
                            self.dets = [self.DevFake(det) for det in dets]
                        else:
                            devunits, detunits = self.getDevicesDetectors(
                                line[1:])
                            session.log.debug('units: dev %s, det: %s',
                                              devunits, detunits)
                            self.scandataset.devvalueinfo = [
                                Value(d.name, unit=u)
                                for d, u in zip(self.devs, devunits)]
                            self.scandataset.detvalueinfo = [
                                Value(d.name, unit=u,
                                      type=guess_det_type(d.name, u))
                                for d, u in zip(self.dets, detunits)]
                            self.scandataset.envvalueinfo = []
                        scanheader += 1
                    elif not entry:
                        break
                    else:
                        key, value = self.getKeyValue(lin)
                        devname, devkey = self.getMetainfoKey(key)
                        self.metainfo[devname, devkey] = self.getMetainfoValue(
                            value) + (entry,)
                        session.log.debug('%s: %s=%s', entry, key, value)
                        session.log.debug('    %s %s', devname, devkey)
                else:
                    # get scan data
                    devvals, detvals = self.getDevicesDetectors(line)
                    pds = PointDataset(devices=self.devs, detectors=self.dets)
                    pds._addvalues({dev.name: (None, val)
                                    for dev, val in zip(self.devs, devvals)})
                    pds.results.update({det.name: [val]
                                       for det, val in zip(self.dets, detvals)}
                                       )
                    pds.metainfo.update(self.metainfo)
                    pds.finished = True  # better to use a finish date?
                    self.scandataset.subsets.append(pds)


class AsciiScanfileSink(FileSink):
    """A data sink that writes to a plain ASCII data file."""
    parameters = {
        'commentchar': Param('Comment character', type=str, default='#',
                             settable=True),
    }

    handlerclass = AsciiScanfileSinkHandler

    parameter_overrides = {
        'settypes': Override(default=[SCAN, SUBSCAN]),
        'filenametemplate': Override(default=['%(proposal)s_%(scancounter)08d.dat']),
    }

    def doUpdateCommentchar(self, value):
        if len(value) > 1:
            raise ConfigurationError('comment character should only be '
                                     'one character')
