#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

"""Data handling classes for NICOS."""

__version__ = "$Revision$"

import os
import time
from os import path
from math import sqrt

try:
    import GracePlot
except ImportError:
    GracePlot = None

try:
    import Gnuplot
except ImportError:
    Gnuplot = None

from nicos import session
from nicos.core import listof, nonemptylistof, Device, Param, Override, \
     ConfigurationError, ProgrammingError, NicosError
from nicos.utils import readFileCounter, updateFileCounter, lazy_property
from nicos.commands.output import printinfo
from nicos.sessions.daemon import DaemonSession
from nicos.sessions.console import ConsoleSession


TIMEFMT = '%Y-%m-%d %H:%M:%S'


class Dataset(object):
    # unique id
    uid = ''
    # scan type
    scantype = None
    # start time
    started = 0
    # data sinks active for this data set
    sinks = []
    # devices to move
    devices = []
    # list of scan positions (can be empty if not known)
    positions = []
    # multi-steps for each scan point
    multistep = []
    # list of detectors for this dataset
    detlist = []
    # list of environment devices for this dataset
    envlist = []
    # preset dictionary of scan
    preset = {}
    # scan info
    scaninfo = ''
    # additional info from data sinks
    sinkinfo = {}
    # resulting x values (should coincide with positions)
    xresults = []
    # resulting y values at the positions
    yresults = []
    # index of the x value to use for plotting
    xindex = 0
    # current point number
    curpoint = 0

    # cached info for all sinks to use
    xvalueinfo = []
    xrange = None
    yvalueinfo = []
    yrange = None

    # info derived from valueinfo
    @lazy_property
    def xnames(self):
        return [v.name for v in self.xvalueinfo]
    @lazy_property
    def xunits(self):
        return [v.unit for v in self.xvalueinfo]
    @lazy_property
    def ynames(self):
        if self.multistep:
            ret = []
            mscount = len(self.multistep[0][1])
            nyvalues = len(self.yvalueinfo) // mscount
            for i in range(mscount):
                addname = '_' + '_'.join('%s_%s' % (mse[0], mse[1][i])
                                         for mse in self.multistep)
                ret.extend(val.name + addname
                           for val in self.yvalueinfo[:nyvalues])
            return ret
        return [v.name for v in self.yvalueinfo]
    @lazy_property
    def yunits(self):
        return [v.unit for v in self.yvalueinfo]


class NeedsDatapath(object):
    """
    A mixin interface that specifies that a device needs the current
    datapath.
    """

    parameters = {
        'datapath': Param('Do not set this, set the datapath on the '
                          'experiment device', type=nonemptylistof(str),
                          default=['.'], settable=True),
    }


class DataSink(Device):
    """
    A DataSink is a configurable object that receives measurement data.  All
    data handling is done by sinks; e.g. displaying it on the console or saving
    to a data file.
    """

    parameters = {
        'scantypes': Param('Scan types for which the sink is active',
                           type=listof(str), default=[]),
    }

    # Set to false in subclasses that e.g. write to the filesystem.
    activeInSimulation = True

    def isActive(self, scantype):
        if session.mode == 'simulation' and not self.activeInSimulation:
            return False
        if scantype is not None and scantype not in self.scantypes:
            return False
        return True

    def prepareDataset(self, dataset):
        """Prepare for a new dataset.

        Returns a list of info about the new dataset as ``(key, value)`` pairs.
        A list of all these pairs is then passed to all sinks' `beginDataset()`
        as the *sinkinfo* parameter.  This is meant for sinks that write files
        to communicate the file name to sinks that write the info to the console
        or display them otherwise.
        """
        pass

    def beginDataset(self, dataset):
        """Begin a new dataset.

        The dataset will contain x-values for all its *devices* (a list of
        `Device` objects), measured at *positions* (a list of lists, or None if
        the positions are not yet known).

        The dataset will contain y-values measured by the *detlist* using the
        given *preset* (a dictionary).

        *userinfo* is an arbitrary string.  *sinkinfo* is a list of ``(key,
        value)`` pairs as explained in `prepareDataset()`.
        """
        pass

    def addInfo(self, dataset, category, valuelist):
        """Add additional information to the dataset.

        This is meant to record e.g. device values at scan startup.  *valuelist*
        is a sequence of tuples ``(device, key, value)``.
        """
        pass

    def addPoint(self, dataset, xvalues, yvalues):
        """Add a point to the dataset.

        *xvalues* is a list of values with the same length as the initial
        *devices* list given to `beginDataset()`, and *yvalues* is a list of
        values with the same length as the all of detlist's value lists.
        """
        pass

    def addBreak(self, dataset):
        """Add a "break" to the dataset.

        A break indicates a division in the data, e.g. between successive rows
        of a 2-dimensional scan.
        """
        pass

    def endDataset(self, dataset):
        """End the current dataset."""
        pass


def safe_format(fmtstr, value):
    try:
        return fmtstr % value
    except (TypeError, ValueError):
        return str(value)

class ConsoleSink(DataSink):
    """
    A DataSink that prints scan data onto the console.
    """

    parameter_overrides = {
        'scantypes':  Override(default=['2D']),
    }

    def beginDataset(self, dataset):
        printinfo('=' * 100)
        printinfo('Starting scan:      ' + (dataset.scaninfo or ''))
        for name, value in dataset.sinkinfo.iteritems():
            printinfo('%-20s%s' % (name+':', value))
        printinfo('Started at:         ' +
                  time.strftime(TIMEFMT, dataset.started))
        printinfo('-' * 100)
        printinfo('\t'.join(map(str, ['#'] + dataset.xnames + dataset.ynames)).
                  expandtabs())
        printinfo('\t'.join([''] + dataset.xunits + dataset.yunits).
                  expandtabs())
        printinfo('-' * 100)
        if dataset.positions:
            self._npoints = len(dataset.positions)
        else:
            self._npoints = 0

    def addPoint(self, dataset, xvalues, yvalues):
        if self._npoints:
            point = '%s/%s' % (dataset.curpoint, self._npoints)
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
    """
    A DataSink that sends datasets to connected GUI clients.  Only active for
    daemon sessions.
    """

    activeInSimulation = False

    def isActive(self, scantype):
        if not isinstance(session, DaemonSession):
            return False
        return DataSink.isActive(self, scantype)

    def beginDataset(self, dataset):
        session.emitfunc('dataset', dataset)

    def addPoint(self, dataset, xvalues, yvalues):
        session.emitfunc('datapoint', (xvalues, yvalues))


class GraceSink(DataSink):
    """
    A DataSink that plots datasets in the Grace plotting program.  Needs the
    GracePlot module.  Only active for console sessions.
    """

    activeInSimulation = False

    def isActive(self, scantype):
        if not GracePlot or not isinstance(session, ConsoleSession):
            return False
        return DataSink.isActive(self, scantype)

    def beginDataset(self, dataset):
        try:
            self._grpl = GracePlot.GracePlot()
            self._pl = self._grpl.curr_graph
            self._pl.clear()
            filename = dataset.sinkinfo.get('filename', '')
            self._pl.title('scan %s started %s' % (filename,
                           time.strftime(TIMEFMT, dataset.started)))
            self._pl.subtitle(dataset.scaninfo)
            self._pl.xaxis(label=GracePlot.Label(
                '%s (%s)' % (dataset.xnames[dataset.xindex],
                             dataset.xunits[dataset.xindex])))
            try:
                # XXX
                self._pl.yaxis(label=GracePlot.Label(str(dataset.detlist[0])))
            except IndexError:
                # no detectors in current scan, cannot plot
                self._grpl = None
                return

            self._xdata = []
            self._nperstep = len(dataset.ynames)
            self._ydata = [[] for _ in range(self._nperstep)]
            self._dydata = [[] for _ in range(self._nperstep)]
            self._ynames = dataset.ynames
        except Exception:
            self.log.warning('could not create Grace plot', exc=1)
            self._grpl = None

    def addPoint(self, dataset, xvalues, yvalues):
        if self._grpl is None:
            return
        try:
            self._xdata.append(xvalues[dataset.xindex])
            for i in range(len(yvalues)):
                self._ydata[i].append(yvalues[i])
                if dataset.yvalueinfo[i].errors == 'sqrt':
                    self._dydata[i].append(sqrt(yvalues[i]))
                else:
                    self._dydata[i].append(0)

            self._pl.clear()
            data = []
            color = GracePlot.colors.black
            l = GracePlot.Line(type=GracePlot.lines.solid)
            for i, ys in enumerate(self._ydata):
                if not ys:
                    continue
                if dataset.yvalueinfo[i % self._nperstep].type != 'counter':
                    continue
                s = GracePlot.Symbol(symbol=GracePlot.symbols.circle,
                                     fillcolor=color, color=color, size=0.4)
                d = GracePlot.DataXYDY(x=self._xdata[:len(ys)], y=ys,
                                       dy=self._dydata[i], symbol=s, line=l,
                                       legend=self._ynames[i])
                data.append(d)
                color += 1
            self._pl.plot(data)
            self._pl.legend()
        except Exception:
            self.log.warning('could not add point to Grace', exc=1)
            # give up for this set
            self._grpl = None


class GnuplotSink(DataSink):
    """
    A DataSink that plots datasets in the Gnuplot plotting program.  Needs the
    Gnuplot module.  Only active for console sessions.
    """

    activeInSimulation = False

    def isActive(self, scantype):
        if not Gnuplot or not isinstance(session, ConsoleSession):
            return False
        return DataSink.isActive(self, scantype)

    def beginDataset(self, dataset):
        try:
            self._gnpl = Gnuplot.Gnuplot()
            self._gnpl('set terminal wx')
            self._gnpl('set key outside below')
            self._gnpl('set pointsize 1.5')
            #self._gnpl('set style increment user')
            self._gnpl.set_range('xrange', '[*:*]')
            self._gnpl.set_range('yrange', '[0:*]')
            filename = dataset.sinkinfo.get('filename', '')
            self._gnpl.title('scan %s started %s' % (filename,
                time.strftime(TIMEFMT, dataset.started)))
            self._gnpl.xlabel('%s (%s)' % (dataset.xnames[dataset.xindex],
                                           dataset.xunits[dataset.xindex]))
            self._gnpl.ylabel(str(dataset.detlist[0])) # XXX

            self._xdata = []
            self._nperstep = len(dataset.ynames)
            self._ydata = [[] for _ in range(self._nperstep)]
            self._dydata = [[] for _ in range(self._nperstep)]
            self._ynames = dataset.ynames
        except Exception:
            self.log.warning('could not create Gnuplot instance', exc=1)
            self._gnpl = None

    def addPoint(self, dataset, xvalues, yvalues):
        if self._gnpl is None:
            return
        try:
            self._xdata.append(xvalues[dataset.xindex])
            for i in range(len(yvalues)):
                self._ydata[i].append(yvalues[i])
                if dataset.yvalueinfo[i].errors == 'sqrt':
                    self._dydata[i].append(sqrt(yvalues[i]))
                else:
                    self._dydata[i].append(0)

            data = []
            for i, ys in enumerate(self._ydata):
                if not ys:
                    continue
                if dataset.yvalueinfo[i % self._nperstep].type != 'counter':
                    continue
                d = Gnuplot.Data(self._xdata[:len(ys)], ys, self._dydata[i],
                                 with_='errorlines', title=self._ynames[i])
                data.append(d)
            self._gnpl.plot(*data)
        except Exception:
            self.log.warning('could not add point to Gnuplot', exc=1)
            # give up for this set
            self._gnpl = None


class DatafileSink(DataSink, NeedsDatapath):

    activeInSimulation = False


class AsciiDatafileSink(DatafileSink):
    parameters = {
        'globalcounter':  Param('File name for a global file counter instead '
                                'of one per datapath', type=str, default=''),
        'commentchar':    Param('Comment character', type=str, default='#',
                                settable=True),
        'semicolon':      Param('Whether to add a semicolon between X and Y '
                                'values', type=bool, default=True),
        'lastfilenumber': Param('The number of the last written data file',
                                type=int),
        'lastpoint':      Param('The number of the last point in the data file',
                                type=int),
    }

    parameter_overrides = {
        'scantypes':      Override(default=['2D']),
    }

    def doReadDatapath(self):
        return session.experiment.datapath

    def doUpdateDatapath(self, value):
        self._path = value[0]
        self._addpaths = value[1:]
        # determine current file counter value
        if self.globalcounter:
            self._counter = readFileCounter(self.globalcounter)
        else:
            self._counter = readFileCounter(
                path.join(self._path, 'filecounter'))
        self._setROParam('lastfilenumber', self._counter)
        self._setROParam('lastpoint', 0)

    def doUpdateCommentchar(self, value):
        if len(value) > 1:
            raise ConfigurationError('comment character should only be '
                                     'one character')
        self._commentc = value

    def nextFileName(self):
        """Return the file name for the next data file.  Can be overwritten in
        instrument-specific subclasses.
        """
        pstr = session.experiment.proposal
        if not pstr:
            raise NicosError('Please initialize the experiment first using '
                             'the NewExperiment() command')
        return '%s_%08d.dat' % (pstr, self._counter + 1)

    def prepareDataset(self, dataset):
        self._wrote_columninfo = False
        self._fname = self.nextFileName()
        self._counter += 1
        if self.globalcounter:
            updateFileCounter(self.globalcounter, self._counter)
        else:
            updateFileCounter(path.join(self._path, 'filecounter'),
                              self._counter)
        self._setROParam('lastfilenumber', self._counter)
        self._setROParam('lastpoint', 0)
        self._fullfname = path.join(self._path, self._fname)
        dataset.sinkinfo['filename'] = self._fname
        dataset.sinkinfo['number'] = self._counter

    def beginDataset(self, dataset):
        if path.isfile(self._fullfname):
            raise ProgrammingError('Data file named %r already exists!' %
                                   self._fullfname)
        self._file = open(self._fullfname, 'w')
        for addpath in self._addpaths:
            os.link(self._fullfname, path.join(addpath, self._fname))
        self._userinfo = dataset.scaninfo
        self._file.write('%s NICOS data file, created at %s\n' %
                         (self._commentc*3, time.strftime(TIMEFMT)))
        for name, value in dataset.sinkinfo.items() + \
                [('info', dataset.scaninfo)]:
            self._file.write('%s %25s : %s\n' % (self._commentc, name, value))
        self._file.flush()
        # to be written later (after info)
        if self.semicolon:
            self._colnames = dataset.xnames + [';'] + dataset.ynames
            self._colunits = dataset.xunits + [';'] + dataset.yunits
        else:
            self._colnames = dataset.xnames + dataset.ynames
            self._colunits = dataset.xunits + dataset.yunits

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
