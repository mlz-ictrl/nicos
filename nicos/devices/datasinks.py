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

"""Data sink classes for NICOS."""

import time
from os import path

from nicos import session
from nicos.core import listof, subdir, Param, Override, ConfigurationError, \
    DataSink
from nicos.commands.output import printinfo
from nicos.pycompat import iteritems, listitems, TextIOWrapper, cPickle as pickle


TIMEFMT = '%Y-%m-%d %H:%M:%S'


def safe_format(fmtstr, value):
    try:
        return fmtstr % value
    except (TypeError, ValueError):
        return str(value)


class ConsoleSink(DataSink):
    """A DataSink that prints scan data onto the console."""

    parameter_overrides = {
        'scantypes':  Override(default=['2D']),
    }

    def beginDataset(self, dataset):
        printinfo('=' * 100)
        printinfo('Starting scan:      ' + (dataset.scaninfo or ''))
        printinfo('Started at:         ' +
                  time.strftime(TIMEFMT, dataset.started))
        for name, value in iteritems(dataset.sinkinfo):
            if name == 'continuation':
                continue
            printinfo('%-20s%s' % (name+':', value))
        printinfo('-' * 100)
        printinfo('\t'.join(map(str, ['#'] + dataset.xnames + dataset.ynames)).
                  expandtabs())
        printinfo('\t'.join([''] + dataset.xunits + dataset.yunits).
                  expandtabs())
        printinfo('-' * 100)

    def addPoint(self, dataset, xvalues, yvalues):
        if dataset.npoints:
            point = '%s/%s' % (dataset.curpoint, dataset.npoints)
        else:
            point = str(dataset.curpoint)
        printinfo('\t'.join(
            [point] +
            [safe_format(info.fmtstr, val) for (info, val) in
             zip(dataset.xvalueinfo, xvalues)] +
            [safe_format(info.fmtstr, val) for (info, val) in
             zip(dataset.yvalueinfo, yvalues)]).expandtabs())

    def addBreak(self, dataset):
        printinfo('-' * 100)

    def endDataset(self, dataset):
        printinfo('-' * 100)
        printinfo('Finished at:        ' + time.strftime(TIMEFMT))
        printinfo('=' * 100)


class DaemonSink(DataSink):
    """A DataSink that sends datasets to connected GUI clients for live
    plotting.  Only active for daemon sessions.
    """

    activeInSimulation = False

    def isActive(self, scantype):
        from nicos.services.daemon.session import DaemonSession
        if not isinstance(session, DaemonSession):
            return False
        return DataSink.isActive(self, scantype)

    def beginDataset(self, dataset):
        session.emitfunc('dataset', dataset)

    def addPoint(self, dataset, xvalues, yvalues):
        session.emitfunc('datapoint', (xvalues, yvalues))

    def addFitCurve(self, dataset, result):
        session.emitfunc('datacurve', (result,))


class DatafileSink(DataSink):

    activeInSimulation = False


class AsciiDatafileSink(DatafileSink):
    """A data sink that writes to a plain ASCII data file.

    The `lastpoint` parameter is managed automatically.

    The current file counter as well as the name of the most recently written
    scanfile is managed by the experiment device.
    """
    parameters = {
        'commentchar':    Param('Comment character', type=str, default='#',
                                settable=True),
        'semicolon':      Param('Whether to add a semicolon between X and Y '
                                'values', type=bool, default=True),
        'lastpoint':      Param('The number of the last point in the data file',
                                type=int),
        'subdir':         Param('Filetype specific subdirectory for the image files',
                                type=subdir, mandatory=False, default=''),
        'filenametemplate':   Param('Name template for the files written',
                                    type=listof(str), userparam=False, settable=False,
                                    default=['%(proposal)s_%(counter)08d.dat']),
    }

    parameter_overrides = {
        'scantypes':      Override(default=['2D']),
    }

    def doUpdateCommentchar(self, value):
        if len(value) > 1:
            raise ConfigurationError('comment character should only be '
                                     'one character')
        self._commentc = value

    def prepareDataset(self, dataset):
        shortname, longname, fp = \
            session.experiment.createScanFile(self.filenametemplate, self.subdir)
        self._wrote_columninfo = False
        self._fname = shortname
        self._setROParam('lastpoint', 0)
        self._fullfname = longname
        self._file = TextIOWrapper(fp)
        dataset.sinkinfo['filepath'] = self._fullfname
        dataset.sinkinfo['filename'] = self._fname
        dataset.sinkinfo['number'] = session.experiment.lastscan

    def beginDataset(self, dataset):
        self._userinfo = dataset.scaninfo
        self._file.write('%s NICOS data file, created at %s\n' %
                         (self._commentc*3, time.strftime(TIMEFMT)))
        for name, value in listitems(dataset.sinkinfo) + \
                [('info', dataset.scaninfo)]:
            self._file.write('%s %25s : %s\n' % (self._commentc, name, value))
        self._file.flush()
        # to be written later (after info)
        if self.semicolon:
            self._colnames = dataset.xnames + [';'] + dataset.ynames
            # make sure there are no empty units
            self._colunits = [u or '-' for u in
                              dataset.xunits + [';'] + dataset.yunits]
        else:
            self._colnames = dataset.xnames + dataset.ynames
            self._colunits = [u or '-' for u in dataset.xunits + dataset.yunits]

    def addInfo(self, dataset, category, valuelist):
        self._file.write('%s %s\n' % (self._commentc*3, category))
        for device, key, value in valuelist:
            self._file.write('%s %25s : %s\n' %
                             (self._commentc, device.name + '_' + key, value))
        self._file.flush()

    def addPoint(self, dataset, xvalues, yvalues):
        if not self._wrote_columninfo:
            self._file.write('%s Scan data\n' % (self._commentc*3))
            self._file.write('%s %s\n' % (self._commentc,
                                          '\t'.join(self._colnames)))
            self._file.write('%s %s\n' % (self._commentc,
                                          '\t'.join(self._colunits)))
            self._wrote_columninfo = True
        xv = [safe_format(info.fmtstr, val) for (info, val) in
              zip(dataset.xvalueinfo, xvalues)]
        yv = [safe_format(info.fmtstr, val) for (info, val) in
              zip(dataset.yvalueinfo, yvalues)]
        if self.semicolon:
            values = xv + [';'] + yv
        else:
            values = xv + yv
        self._file.write('\t'.join(values) + '\n')
        self._file.flush()
        self._setROParam('lastpoint', dataset.curpoint)

    def addBreak(self, dataset):
        self._file.write('\n')

    def endDataset(self, dataset):
        self._file.write('%s End of NICOS data file %s\n' %
                         (self._commentc*3, self._fname))
        self._file.close()
        self._file = None
        self._setROParam('lastpoint', 0)


class SerializedSink(DatafileSink):
    """A data sink that writes serialized datasets to a single file.

    Can be used to retrieve and redisplay past datasets.
    """
    def endDataset(self, dataset):
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
        datasets[session.experiment.lastscan] = dataset
        try:
            with open(serial_file, 'wb') as fp:
                pickle.dump(datasets, fp, pickle.HIGHEST_PROTOCOL)
        except Exception:
            self.log.warning('could not save serialized datasets', exc=1)
