#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
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
# *****************************************************************************

"""Data handling classes for NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import time
import errno
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
from nicos.utils import listof, readFileCounter, updateFileCounter
from nicos.device import Device, Param
from nicos.errors import ConfigurationError, ProgrammingError
from nicos.sessions import DaemonSession, InteractiveSession
from nicos.commands.output import printinfo


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
    # resulting y values at the positions
    results = []
    # index of the x value to use for plotting
    xindex = 0

    # cached info for all sinks to use
    xnames = []
    xunits = []
    ynames = []
    yunits = []
    yvalueinfo = []


class NeedsDatapath(object):
    """
    A mixin interface that specifies that a device needs the current
    datapath.
    """

    parameters = {
        'datapath': Param('Do not set this, set the datapath on the '
                          'experiment device', type=listof(str), settable=True),
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

    def endDataset(self, dataset):
        """End the current dataset."""
        pass


class ConsoleSink(DataSink):
    """
    A DataSink that prints scan data onto the console.
    """

    def beginDataset(self, dataset):
        printinfo('=' * 80)
        printinfo('Starting scan:      ' + (dataset.scaninfo or ''))
        for name, value in dataset.sinkinfo.iteritems():
            printinfo('%-20s%s' % (name+':', value))
        printinfo('Started at:         ' +
                  time.strftime(TIMEFMT, dataset.started))
        printinfo('-' * 80)
        printinfo('\t'.join(map(str, ['#'] + dataset.xnames + dataset.ynames)).
                  expandtabs())
        printinfo('\t'.join([''] + dataset.xunits + dataset.yunits).
                  expandtabs())
        printinfo('-' * 80)
        if dataset.positions:
            self._npoints = len(dataset.positions)
        else:
            self._npoints = 0

    def addPoint(self, dataset, xvalues, yvalues):
        if self._npoints:
            point = '%s/%s' % (len(dataset.results), self._npoints)
        else:
            point = str(len(dataset.results))
        printinfo('\t'.join(
            [point] +
            [dev.format(val) for (dev, val) in
             zip(dataset.devices + dataset.envlist, xvalues)] +
            [str(val) for val in yvalues]).expandtabs())

    def endDataset(self, dataset):
        printinfo('-' * 80)
        printinfo('Finished at:        ' + time.strftime(TIMEFMT))
        printinfo('=' * 80)


class DaemonSink(DataSink):
    """
    A DataSink that sends datasets to connected GUI clients.  Only active for
    daemon sessions.
    """

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

    def isActive(self, scantype):
        if not GracePlot or not isinstance(session, InteractiveSession):
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
            self._pl.yaxis(label=GracePlot.Label(str(dataset.detlist[0]))) # XXX

            self._xdata = []
            self._nperstep = len(dataset.ynames)
            self._ydata = [[] for i in range(self._nperstep)]
            self._dydata = [[] for i in range(self._nperstep)]
            self._ynames = dataset.ynames
        except Exception:
            self.printwarning('could not create Grace plot', exc=1)
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
            self.printwarning('could not add point to Grace', exc=1)
            # give up for this set
            self._grpl = None


class GnuplotSink(DataSink):
    """
    A DataSink that plots datasets in the Gnuplot plotting program.  Needs the
    Gnuplot module.  Only active for console sessions.
    """

    def isActive(self, scantype):
        if not Gnuplot or not isinstance(session, InteractiveSession):
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
            self._ydata = [[] for i in range(self._nperstep)]
            self._dydata = [[] for i in range(self._nperstep)]
            self._ynames = dataset.ynames
        except Exception:
            self.printwarning('could not create Gnuplot instance', exc=1)
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
            self.printwarning('could not add point to Gnuplot', exc=1)
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
    }

    def doPreinit(self):
        self._counter = 0

    def doUpdateDatapath(self, value):
        if value:
            self._path = value[0]
            self._addpaths = value[1:]
            # determine current file counter value
            if self.globalcounter:
                self._counter = readFileCounter(self.globalcounter)
            else:
                self._counter = readFileCounter(
                    path.join(self._path, 'filecounter'))
            self._setROParam('lastfilenumber', self._counter)
        else:
            self._path = None
            self._file = None
            self._fname = ''

    def doWriteCommentchar(self, value):
        if len(value) > 1:
            raise ConfigurationError('comment character should only be '
                                     'one character')

    def doUpdateCommentchar(self, value):
        self._scomment = value
        self._tcomment = value * 3

    def doReadLastfilenumber(self):
        return self._counter

    def nextFileName(self):
        """Return the file name for the next data file.  Can be overwritten in
        instrument-specific subclasses.
        """
        pstr = session.experiment.proposal
        return '%s_%08d.dat' % (pstr, self._counter)

    def prepareDataset(self, dataset):
        if self._path is None:
            self._setDatapath(session.experiment.datapath)
        self._wrote_columninfo = False
        self._counter += 1
        if self.globalcounter:
            updateFileCounter(self.globalcounter, self._counter)
        else:
            updateFileCounter(path.join(self._path, 'filecounter'),
                              self._counter)
        self._setROParam('lastfilenumber', self._counter)
        self._fname = self.nextFileName()
        self._fullfname = path.join(self._path, self._fname)
        dataset.sinkinfo['filename'] = self._fname
        dataset.sinkinfo['number'] = self._counter

    def beginDataset(self, dataset):
        if path.isfile(self._fullfname):
            # XXX for now, prevent from ever overwriting data files
            raise ProgrammingError('Data file named %r already exists!' %
                                   self._fullfname)
        self._file = open(self._fullfname, 'w')
        for addpath in self._addpaths:
            os.link(self._fullfname, path.join(addpath, self._fname))
        self._userinfo = dataset.scaninfo
        self._file.write('%s NICOS data file, created at %s\n' %
                         (self._tcomment, time.strftime(TIMEFMT)))
        for name, value in dataset.sinkinfo.items() + \
                [('info', dataset.scaninfo)]:
            self._file.write('%s %25s : %s\n' % (self._scomment, name, value))
        self._file.flush()
        # to be written later (after info)
        if self.semicolon:
            self._colnames = dataset.xnames + [';'] + dataset.ynames
            self._colunits = dataset.xunits + [';'] + dataset.yunits
        else:
            self._colnames = dataset.xnames + dataset.ynames
            self._colunits = dataset.xunits + dataset.yunits

    def addInfo(self, dataset, category, valuelist):
        self._file.write('%s %s\n' % (self._tcomment, category))
        for device, key, value in valuelist:
            self._file.write('%s %25s : %s\n' %
                             (self._scomment, device.name + '_' + key, value))
        self._file.flush()

    def addPoint(self, dataset, xvalues, yvalues):
        if not self._wrote_columninfo:
            self._file.write('%s Scan data\n' % self._tcomment)
            self._file.write('%s %s\n' % (self._scomment,
                                          '\t'.join(self._colnames)))
            self._file.write('%s %s\n' % (self._scomment,
                                          '\t'.join(self._colunits)))
            self._wrote_columninfo = True
        xv = [dev.format(val) for (dev, val) in
              zip(dataset.devices + dataset.envlist, xvalues)]
        yv = map(str, yvalues)
        if self.semicolon:
            values = xv + [';'] + yv
        else:
            values = xv + yv
        self._file.write('\t'.join(values) + '\n')
        self._file.flush()

    def endDataset(self, dataset):
        self._file.write('%s End of NICOS data file %s\n' %
                         (self._tcomment, self._fname))
        self._file.close()
        self._file = None
