#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""
NICOS value plot widget.
"""

import operator
import functools

from time import time as currenttime, strftime, localtime

from nicos.guisupport.qt import pyqtSignal, QWidget, QTimer, QSize, \
    QHBoxLayout

import gr
from gr.pygr import Plot, PlotCurve, PlotAxes
from qtgr import InteractiveGRWidget
from qtgr.events import GUIConnector, MouseEvent, LegendEvent
import numpy.ma

from nicos.guisupport.timeseries import TimeSeries, buildTickDistAndSubTicks
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.utils import extractKeyAndIndex
from nicos.pycompat import zip_longest


DATEFMT = '%Y-%m-%d'
TIMEFMT = '%H:%M:%S'
SHORTTIMEFMT = '%H:%M'


class MaskedPlotCurve(PlotCurve):
    """Plot curve that handles masked arrays as X and Y data."""

    def __init__(self, *args, **kwargs):
        # fill values for masked x, y
        self.fillx = kwargs.pop('fillx', 0)
        self.filly = kwargs.pop('filly', 0)
        PlotCurve.__init__(self, *args, **kwargs)

    @property
    def x(self):
        x = PlotCurve.x.__get__(self)
        if numpy.ma.is_masked(x):
            return x.filled(self.fillx)
        return x

    @x.setter
    def x(self, x):
        PlotCurve.x.__set__(self, x)

    @property
    def y(self):
        y = PlotCurve.y.__get__(self)
        if numpy.ma.is_masked(y):
            return y.filled(self.filly)
        return y

    @y.setter
    def y(self, y):
        PlotCurve.y.__set__(self, y)


class NicosPlotAxes(PlotAxes):
    """Plot axes that enable automatic extension of the window by a tick
    distance in order to keep the curves from the edge of the grid.
    """

    def scaleWindow(self, xmin, xmax, xtick, ymin, ymax, ytick):
        dx, dy = 0, 0
        if self.autoscale & PlotAxes.SCALE_X:
            dx = xtick
        if self.autoscale & PlotAxes.SCALE_Y:
            dy = ytick
        return xmin - dx, xmax + dx, ymin - dy, ymax + dy

    def doAutoScale(self, curvechanged=None):
        vc = self.getVisibleCurves() or self.getCurves()
        original_win = self.getWindow()
        if original_win and curvechanged:
            xmin, xmax = original_win[:2]
            cmin, cmax = vc.xmin, vc.xmax
            new_x = curvechanged.x[-1]
            if cmax > xmax and new_x > xmax:
                return original_win
            elif cmin < xmin and new_x < xmin:
                return original_win
        return PlotAxes.doAutoScale(self, curvechanged)


class NicosTimePlotAxes(NicosPlotAxes):
    """Plot axes with automatic sensible formatting of time X axis."""

    def __init__(self, viewport, xtick=None, ytick=None, majorx=None,
                 majory=None, drawX=True, drawY=True, slidingwindow=None):
        NicosPlotAxes.__init__(self, viewport, xtick, ytick, majorx, majory,
                               drawX, drawY)
        self.slidingwindow = slidingwindow

    def setWindow(self, xmin, xmax, ymin, ymax):
        res = NicosPlotAxes.setWindow(self, xmin, xmax, ymin, ymax)
        if res:
            tickdist, self.majorx = buildTickDistAndSubTicks(xmin, xmax)
            self.xtick = tickdist / self.majorx
        return res

    def doAutoScale(self, curvechanged=None):
        vc = self.getVisibleCurves() or self.getCurves()
        win = NicosPlotAxes.doAutoScale(self, curvechanged)
        xmin, xmax, ymin, ymax = win  # pylint: disable=unpacking-non-sequence
        if self.slidingwindow and self.autoscale & PlotAxes.SCALE_X and \
           (vc.xmax - xmin) > self.slidingwindow:
            xmin = vc.xmax - self.slidingwindow
            self.setWindow(xmin, xmax, ymin, ymax)
        return self.getWindow()


class TrendPlot(QWidget, NicosWidget):

    designer_description = 'A trend plotter for one or more devices'
    designer_icon = ':/plotter'

    widgetInfo = pyqtSignal(str)
    timeSeriesUpdate = pyqtSignal(object)

    # colors = [Qt.red, Qt.darkGreen, Qt.blue, Qt.black, Qt.magenta, Qt.cyan,
    #           Qt.darkGray]

    devices = PropDef('devices', 'QStringList', [], '''
List of devices or cache keys that the plot should display.

For devices use device name. For keys use cache key with "." or "/" separator,
e.g. T.heaterpower.

To access items of a sequence, use subscript notation, e.g. T.userlimits[0]
''')
    names = PropDef('names', 'QStringList', [], 'Names for the plot curves, '
                    'defaults to the device names/keys.')
    legend = PropDef('legend', bool, False, 'If a legend should be shown.')
    plotwindow = PropDef('plotwindow', int, 3600, 'The range of time in '
                         'seconds that should be represented by the plot.')
    plotinterval = PropDef('plotinterval', float, 2, 'The minimum time in '
                           'seconds between two points that should be '
                           'plotted.')
    height = PropDef('height', int, 10, 'Height of the plot widget in units '
                     'of app font character width.')
    width = PropDef('width', int, 30, 'Width of the plot widget in units '
                    'of app font character width.')

    # pylint: disable=W0231
    def __init__(self, parent, designMode=False):
        self.ncurves = 0
        self.ctimers = {}
        self.keyindices = {}
        self.plotcurves = {}
        self.series = {}
        self.legendobj = None

        # X label settings, default values for default window of 3600s
        self._showdate = False
        self._showsecs = False

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    def initUi(self):
        # axes setup
        self.widget = InteractiveGRWidget(self)
        self.plot = Plot(viewport=(.1, .95, .25, .95))
        self.axes = NicosTimePlotAxes(self.plot._viewport)
        self.plot.addAxes(self.axes)
        self.plot.setLegend(True)
        self.plot.setLegendWidth(0.07)
        self.plot.offsetXLabel = -.2
        self.axes.setXtickCallback(self.xtickCallBack)
        self.widget.addPlot(self.plot)
        layout = QHBoxLayout()
        layout.addWidget(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.curves = []

        # event support
        guiConn = GUIConnector(self.widget)
        guiConn.connect(LegendEvent.ROI_CLICKED, self.on_legendItemClicked,
                        LegendEvent)
        guiConn.connect(MouseEvent.MOUSE_MOVE, self.on_mouseMove)

        self.timeSeriesUpdate.connect(self.on_timeSeriesUpdate)

    def xtickCallBack(self, x, y, _svalue, value):
        gr.setcharup(-1., 1.)
        gr.settextalign(gr.TEXT_HALIGN_RIGHT, gr.TEXT_VALIGN_TOP)
        dx = .02
        timeVal = localtime(value)
        if self._showdate:
            gr.text(x + dx, y - 0.01, strftime(DATEFMT, timeVal))
        if self._showsecs:
            gr.text(x - dx, y - 0.01, strftime(TIMEFMT, timeVal))
        else:
            gr.text(x - dx, y - 0.01, strftime(SHORTTIMEFMT, timeVal))
        gr.setcharup(0., 1.)

    def propertyUpdated(self, pname, value):
        if pname == 'plotwindow':
            self._showdate = value > 24*3600
            self._showsecs = value < 300
        elif pname in ('width', 'height'):
            self.setMinimumSize(
                QSize(self._scale * (self.props['width'] + .5),
                      self._scale * (self.props['height'] + .5)))
        elif pname == 'legend':
            self.plot.setLegend(value)
        NicosWidget.propertyUpdated(self, pname, value)

    def setFont(self, font):
        pass  # TODO: can't set font for GR right now

    def on_mouseMove(self, event):
        wc = event.getWC(self.plot.viewport)
        ts = strftime(DATEFMT + ' ' + TIMEFMT, localtime(wc.x))
        msg = 't = %s, y = %g' % (ts, wc.y)
        self.widgetInfo.emit(msg)

    def on_legendItemClicked(self, event):
        if event.getButtons() & MouseEvent.LEFT_BUTTON:
            event.curve.visible = not event.curve.visible
            self.update()

    def on_timeSeriesUpdate(self, series):
        curve = self.plotcurves[series]
        curve.x = series.x[:series.n]
        curve.y = series.y[:series.n]
        c = self.axes.getCurves()
        self.axes.setWindow(c.xmin, c.xmax, c.ymin, c.ymax)
        self.widget.update()
        self.ctimers[curve].start(5000)

    def on_keyChange(self, key, value, time, expired):
        if key not in self.keyindices or value is None:
            return
        for index in self.keyindices[key]:
            series = self.series[key, index]
            # restrict time of value to 1 minute past at
            # maximum, so that it doesn't get culled by the windowing
            time = max(time, currenttime() - 60)
            if index:
                try:
                    fvalue = functools.reduce(operator.getitem, index, value)
                    series.add_value(time, fvalue)
                except Exception:
                    pass
            else:
                series.add_value(time, value)

    def addcurve(self, key, index, title):
        series = TimeSeries(key, self.props['plotinterval'], 1.0, 0.0,
                            self.props['plotwindow'], self)
        series.init_empty()
        curve = PlotCurve([currenttime()], [0], legend=title)
        self.plotcurves[series] = curve
        self.ncurves += 1
        self.curves.append(curve)
        self.axes.addCurves(curve)
        self.series[key, index] = series
        self.widget.update()

        # record the current value at least every 5 seconds, to avoid curves
        # not updating if the value doesn't change
        def update():
            series.synthesize_value()
        self.ctimers[curve] = QTimer(singleShot=True)
        self.ctimers[curve].timeout.connect(update)

    def registerKeys(self):
        for key, name in zip_longest(self.props['devices'], self.props['names']):
            if name is None:
                name = key
            # TODO: support scale/offset
            key, index = extractKeyAndIndex(key)[:2]
            keyid = self._source.register(self, key)
            self.keyindices.setdefault(keyid, []).append(index)
            self.addcurve(keyid, index, name)
