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

from os import path
from time import strftime, localtime

from nicos import session
from nicos.commands.output import printinfo
from nicos.core import ConfigurationError, Override, Param, listof, \
    INFO_CATEGORIES, DataSink, DataSinkHandler, dataman
from nicos.pycompat import TextIOWrapper, iteritems, cPickle as pickle


TIMEFMT = '%Y-%m-%d %H:%M:%S'


def safe_format(fmtstr, value):
    try:
        return fmtstr % value
    except (TypeError, ValueError):
        return str(value)


class ConsoleScanSinkHandler(DataSinkHandler):

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._indent = '' if self.dataset.settype != 'subscan' else ' ' * 6

    def begin(self):
        ds = self.dataset
        if ds.settype != 'subscan':
            printinfo('=' * 100)
            printinfo('Starting scan:      ' + (ds.info or ''))
            printinfo('Started at:         ' +
                      strftime(TIMEFMT, localtime(ds.started)))
            printinfo('Scan number:        ' + str(ds.counter))
            for filename in ds.filenames:
                printinfo('Filename:           ' + filename)
            printinfo('-' * 100)
        else:
            printinfo()
            for filename in ds.filenames:
                printinfo(self._indent + 'Filename: ' + filename)
        valueinfo = ds.devvalueinfo + ds.envvalueinfo + ds.detvalueinfo
        # we write every data value as a column except for arrays
        names = [v.name for v in valueinfo]
        units = [v.unit for v in valueinfo]
        printinfo(self._indent + '\t'.join(map(str, ['#'] + names)).expandtabs())
        printinfo(self._indent + '\t'.join([''] + units).expandtabs())
        printinfo(self._indent + '-' * (100 - len(self._indent)))

    def addSubset(self, point):
        ds = self.dataset
        if ds.npoints:
            pointstr = '%s/%s' % (len(ds.subsets), ds.npoints)
        else:
            pointstr = str(len(ds.subsets))
        printinfo(self._indent + '\t'.join(
            [pointstr] +
            [safe_format(info.fmtstr, val) for (info, val) in
             zip(ds.devvalueinfo, point.devvaluelist)] +
            [safe_format(info.fmtstr, val) for (info, val) in
             zip(ds.envvalueinfo, point.envvaluelist)] +
            [safe_format(info.fmtstr, val) for (info, val) in
             zip(ds.detvalueinfo, point.detvaluelist)]).expandtabs())

    def end(self):
        if self.dataset.settype != 'subscan':
            printinfo('-' * 100)
            printinfo('Finished at:        ' +
                      strftime(TIMEFMT, localtime(self.dataset.finished)))
            printinfo('=' * 100)
        else:
            printinfo()


class ConsoleScanSink(DataSink):
    """A DataSink that prints scan data onto the console."""

    activeInSimulation = True

    handlerclass = ConsoleScanSinkHandler

    parameter_overrides = {
        'settypes':  Override(default=['scan', 'subscan']),
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

    def start(self):
        self._number = dataman.assignCounter(self.dataset)
        fp = dataman.createDataFile(self.dataset, self._template)
        self._fname = fp.shortpath
        self._filepath = fp.filepath
        self._file = TextIOWrapper(fp)

    def _write_section(self, section):
        self._file.write('%s %s\n' % (self._commentc * 3, section))

    def _write_comment(self, comment):
        self._file.write('%s %s\n' % (self._commentc, comment))

    def _write_header(self, ds):
        self._write_section('NICOS data file, created at %s' % strftime(TIMEFMT))
        for name, value in [('number', self._number),
                            ('filename', self._fname),
                            ('filepath', self._filepath),
                            ('info', ds.info)]:
            self._write_comment('%25s : %s' % (name, value))
        bycategory = {}
        for (device, key), (_, val, unit, category) in iteritems(ds.metainfo):
            if category:
                bycategory.setdefault(category, []).append(
                    ('%s_%s' % (device.name, key), (val + ' ' + unit).strip()))
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
        if self._semicolon:
            self._colnames = xnames + [';'] + ynames
            # make sure there are no empty units
            self._colunits = [u or '-' for u in xunits + [';'] + yunits]
        else:
            self._colnames = xnames + ynames
            self._colunits = [u or '-' for u in xunits + yunits]
        self._file.flush()

    def addSubset(self, point):
        ds = self.dataset
        if not self._wrote_header:
            self._write_header(ds)
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
        if self._semicolon:
            values = xv + [';'] + yv
        else:
            values = xv + yv
        self._file.write('\t'.join(values) + '\n')
        self._file.flush()

    def end(self):
        if self._fname:
            self._write_section('End of NICOS data file %s' % self._fname)
            self._file.close()
            self._file = None


class AsciiScanfileSink(DataSink):
    """A data sink that writes to a plain ASCII data file.

    The current file counter as well as the name of the most recently written
    scanfile is managed by the experiment device.
    """
    parameters = {
        'commentchar':    Param('Comment character', type=str, default='#',
                                settable=True),
        'semicolon':      Param('Whether to add a semicolon between X and Y '
                                'values', type=bool, default=True),
        'filenametemplate': Param('Name template for the files written',
                                  type=listof(str), userparam=False,
                                  settable=False,
                                  default=['%(proposal)s_%(scancounter)08d.dat']),
    }

    handlerclass = AsciiScanfileSinkHandler

    parameter_overrides = {
        'settypes':  Override(default=['scan', 'subscan']),
    }

    def doUpdateCommentchar(self, value):
        if len(value) > 1:
            raise ConfigurationError('comment character should only be '
                                     'one character')


class SerializedSinkHandler(DataSinkHandler):

    def end(self):
        serial_file = path.join(session.experiment.datapath, '.all_datasets')
        if path.isfile(serial_file):
            try:
                with open(serial_file, 'rb') as fp:
                    datasets = pickle.load(fp)
            except Exception:
                self.log.warning('could not load serialized datasets', exc=1)
                datasets = {}
        else:
            datasets = {}
        datasets[self.dataset.counter] = self.dataset
        try:
            with open(serial_file, 'wb') as fp:
                pickle.dump(datasets, fp, pickle.HIGHEST_PROTOCOL)
        except Exception:
            self.log.warning('could not save serialized datasets', exc=1)


class SerializedSink(DataSink):
    """A data sink that writes serialized datasets to a single file.

    Can be used to retrieve and redisplay past datasets.
    """

    activeInSimulation = False

    handlerclass = SerializedSinkHandler

    parameter_overrides = {
        'settypes':  Override(default=['scan', 'subscan']),
    }
