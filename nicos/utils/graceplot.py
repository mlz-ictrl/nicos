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

"""Utilities for plotting with Grace."""

from os import path
from math import sqrt
from time import strftime

try:
    import nicos._vendor.GracePlot as GracePlot
    grace_available = True
except ImportError:
    GracePlot = None
    grace_available = False


TIMEFMT = '%Y-%m-%d %H:%M:%S'


class GracePlotter(object):
    """Proxy for plotting NICOS datasets with Grace.

    All "dataset" arguments must be :class:`nicos.core.data.Dataset` objects.
    """

    def __init__(self, activecounter):
        self._grpl = None
        self.activecounter = activecounter

    def openPlot(self, dataset, secondchance=False):
        filename = dataset.sinkinfo.get('filename', '')
        filepath = dataset.sinkinfo.get('filepath', '')
        self._grpl = GracePlot.GracePlot(workingdir=path.dirname(filepath))
        self._pl = self._grpl.curr_graph
        self._pl.clear()
        self._pl.title('scan %s\\nstarted %s' % (filename,
                       strftime(TIMEFMT, dataset.started)))
        self._pl.subtitle(dataset.scaninfo)
        self._pl.xaxis(label=GracePlot.Label(
            '%s (%s)' % (dataset.xnames[dataset.xindex],
                         dataset.xunits[dataset.xindex])))
        if self.activecounter:
            self._pl.yaxis(label=GracePlot.Label(self.activecounter))

        self._xdata = []
        self._nperstep = len(dataset.ynames)
        self._ydata = [[] for _ in range(self._nperstep)]
        self._dydata = [[] for _ in range(self._nperstep)]
        self._ynames = dataset.ynames

        for (xvalues, yvalues) in zip(dataset.xresults, dataset.yresults):
            self.addPoint(dataset, xvalues, yvalues, secondchance=secondchance)

    def beginDataset(self, dataset):
        try:
            if dataset.sinkinfo.get('continuation'):
                return True
            self.openPlot(dataset)
            return True
        except Exception:
            self._grpl = None
            return False

    def addPoint(self, dataset, xvalues, yvalues, secondchance=False):
        if self._grpl is None:
            return
        try:
            self._xdata.append(xvalues[dataset.xindex])
            for i in range(len(yvalues)):
                self._ydata[i].append(yvalues[i])
                if dataset.yvalueinfo[i].errors == 'sqrt':
                    try:
                        self._dydata[i].append(sqrt(yvalues[i]))
                    except ValueError:
                        self._dydata[i].append(0)
                else:
                    self._dydata[i].append(0)

            self._pl.clear()
            data = []
            color = GracePlot.colors.black
            l = GracePlot.Line(type=GracePlot.lines.solid)
            for i, ys in enumerate(self._ydata):
                if not ys:
                    continue
                if self.activecounter:
                    if self._ynames[i] != self.activecounter:
                        continue
                elif dataset.yvalueinfo[i % self._nperstep].type != 'counter':
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
            return True
        except Exception:
            # try again or give up for this set
            if secondchance:
                return False
            try:
                self.openPlot(dataset, secondchance=True)
            except Exception:
                self._grpl = None
                return False

    def addFitCurve(self, dataset, title, xvalues, yvalues):
        if self._grpl is None:
            return
        l = GracePlot.Line(type=GracePlot.lines.solid, linewidth=2)
        d = GracePlot.Data(x=xvalues, y=yvalues, line=l, legend=title)
        self._pl.clear()
        self._pl.plot(self._pl.datasets + [d])
        self._pl.legend()
        return True
