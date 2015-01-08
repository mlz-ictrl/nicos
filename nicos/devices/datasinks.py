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

"""Data sink classes for NICOS."""

import time
from os import path

from nicos import session
from nicos.core import listof, none_or, Device, Param, Override, \
    ConfigurationError, DataSink, usermethod
from nicos.utils import parseDateString
from nicos.utils.graceplot import GracePlot, GracePlotter
from nicos.commands.output import printinfo, printwarning
from nicos.core.sessions.console import ConsoleSession
from nicos.pycompat import iteritems, listitems, TextIOWrapper, string_types, \
    cPickle as pickle


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
        for name, value in iteritems(dataset.sinkinfo):
            if name == 'continuation':
                continue
            printinfo('%-20s%s' % (name+':', value))
        printinfo('Started at:         ' +
                  time.strftime(TIMEFMT, dataset.started))
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

    def addFitCurve(self, dataset, title, xvalues, yvalues):
        session.emitfunc('datacurve', (title, xvalues, yvalues))


class GraceSink(DataSink):
    """A DataSink that plots datasets in the Grace plotting program.

    Needs the GracePlot module.  Only active for console sessions.
    """

    parameters = {
        'activecounter': Param('Name of active counter to plot',
                               type=none_or(str), settable=True),
    }

    activeInSimulation = False

    def doInit(self, mode):
        self._plotter = GracePlotter(self.activecounter)

    def isActive(self, scantype):
        if not GracePlot or not isinstance(session, ConsoleSession):
            return False
        return DataSink.isActive(self, scantype)

    def doUpdateActivecounter(self, val):
        if hasattr(self, '_plotter'):
            self._plotter.activecounter = val

    def beginDataset(self, dataset):
        if not self._plotter.beginDataset(dataset):
            self.log.warning('could not create Grace plot')

    def addPoint(self, dataset, xvalues, yvalues):
        if not self._plotter.addPoint(dataset, xvalues, yvalues):
            self.log.warning('could not add point to Grace')

    def addFitCurve(self, dataset, title, xvalues, yvalues):
        if not self._plotter.addFitCurve(dataset, title, xvalues, yvalues):
            self.log.warning('could not add curve to Grace')

    # pylint: disable=W0221
    @usermethod
    def history(self, dev, key='value', fromtime=None, totime=None):
        """Plot history of the given key and time interval in a Grace window.
        See the `history()` command for the meaning of the *key*, *fromtime* and
        *totime* arguments.  Examples (for a GraceSink called "liveplot")::

            liveplot.history(T, '12:00', '18:00')  # from 12-18 h today
            liveplot.history(T, -6)                # last 6 hours
            liveplot.history(T, 'setpoint', -72)   # setpoint in the last 3 days

        Multiple devices can be given as a list::

            liveplot.history([TA, TB, TC], -24)    # TA, TB, TC in the last 24 h
        """
        ltime = time.localtime
        tz = time.timezone
        az = time.altzone
        # if "key" is a string we have to determine if it's a parameter name or
        # a date string; since valid date strings cannot be parameter names this
        # is quite easy to do
        if isinstance(key, string_types):
            try:
                key = parseDateString(key)
            except ValueError:
                pass
        # now either key is a valid parameter name or a number, which means a
        # timestamp or number of hours back
        if isinstance(key, (int, float)):
            totime = fromtime
            fromtime = key
            key = 'value'
        # the default is just -1 hour, which is fine for value and status, but
        # probably not for other parameters
        if key not in ('value', 'status') and fromtime is None:
            fromtime = -24

        # function to retrieve respective history for a single device
        def get_one_history(dev):
            dev = session.getDevice(dev, Device)
            ts, vs = [], []
            for t, v in dev.history(key, fromtime, totime):
                # Grace likes dates in Julian days, but we have to consider GMT
                # offset as well...
                lt = ltime(t)
                ts.append((t - (lt[8] and az or tz)) / 86400. + 2440587.5)
                vs.append(v)
            if len(ts) < 2:
                printwarning('not enough values in history query for %s' % dev)
                return None, None
            return ts, vs

        # determine plotting mode, exit early if there is no data to show
        if isinstance(dev, list):
            multi = True
            ds, tss, vss = [], [], []
            for dv in dev:
                ts, vs = get_one_history(dv)
                if ts is not None:
                    ds.append(dv)
                    tss.append(ts)
                    vss.append(vs)
            if not tss:
                return
        else:
            multi = False
            ts, vs = get_one_history(dev)
            if ts is None:
                return
            ds, tss, vss = [dev], [ts], [vs]

        # set up a new Grace window
        grpl = GracePlot.GracePlot()
        pl = grpl.curr_graph
        pl.clear()

        # set graph attributes depending on plotting mode
        if multi:
            pl.title('history query')
            pl.yaxis(label=GracePlot.Label(key))
        else:
            pl.title('history: %s.%s' % (dev, key))
            if key == 'value':
                unit = getattr(dev, 'unit', '')
                pl.yaxis(label=GracePlot.Label(
                    dev.name + (unit and ' (%s)' % unit or '')))
            else:
                unit = dev.parameters[key].unit
                pl.yaxis(label=GracePlot.Label(
                    '%s.%s%s' % (dev, key, unit and ' (%s)' % unit or '')))

        # select appropriate X format and scaling
        minx = min(ts[1] for ts in tss)
        maxx = max(ts[-1] for ts in tss)
        xfmt = 'HMS'
        if maxx - minx > 1:
            xfmt = 'YYMMDDHMS'
        pl.xaxis(label=GracePlot.Label('time'),
                 tick=GracePlot.Tick(TickLabel=
                                     GracePlot.TickLabel(format=xfmt)))
        pl.grace().send_commands('world xmin %s' % (int(minx*24)/24.))
        pl.grace().send_commands('world xmax %s' % (int(maxx*24 + 1)/24.))

        # plot all datasets
        l = GracePlot.Line(type=GracePlot.lines.solid)
        datas = []
        color = GracePlot.colors.black
        for dv, ts, vs in zip(ds, tss, vss):
            s = GracePlot.Symbol(symbol=GracePlot.symbols.circle, size=0.3,
                                 color=color, fillcolor=color)
            d = GracePlot.Data(x=ts, y=vs, line=l, symbol=s,
                               legend='%s.%s' % (dv, key))
            d.x_format_string = '%r'  # the default %s cuts precision too much
            datas.append(d)
            color += 1
        pl.plot(datas, autoscale=False)
        if multi:
            pl.legend()
        pl.autoscale('y')
        pl.autotick()


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
            session.experiment.createScanFile(self.filenametemplate)
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
