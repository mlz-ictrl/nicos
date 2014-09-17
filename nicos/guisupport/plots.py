#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

from time import time as currenttime, strftime, localtime

from PyQt4.QtGui import QWidget, QPen, QBrush
from PyQt4.QtCore import Qt, SIGNAL, QTimer, QSize

from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtLegend, \
    QwtPlotZoomer, QwtPicker, QwtPlotPicker, QwtPlotPanner, QwtScaleDraw, \
    QwtText, QwtLinearScaleEngine, QwtScaleDiv, QwtDoubleInterval

import numpy as np

from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.guisupport.utils import extractKeyAndIndex
from nicos.pycompat import number_types, string_types, iteritems


class ActivePlotPicker(QwtPlotPicker):
    """QwtPlotPicker that emits mouse move events when activated."""
    def __init__(self, *args):
        QwtPlotPicker.__init__(self, *args)
        self.active = True

    def widgetMouseMoveEvent(self, event):
        if self.active:
            self.emit(SIGNAL('moved(const QPoint &)'), event.pos())
        return QwtPlotPicker.widgetMouseMoveEvent(self, event)


class TimeScaleDraw(QwtScaleDraw):
    def __init__(self, showdate=True, showsecs=True):
        QwtScaleDraw.__init__(self)
        self.fmtstring = '%y-%m-%d\n%H:%M:%S'
        if not showdate:
            self.fmtstring = self.fmtstring[9:]
        if not showsecs:
            self.fmtstring = self.fmtstring[:-3]

    def label(self, value, strf=strftime, localt=localtime):
        try:
            ret = QwtText(strf(self.fmtstring, localt(value)))
        except ValueError:
            ret = QwtText("<unknown>")
        return ret


class TimeScaleEngine(QwtLinearScaleEngine):
    def divideScale(self, x1, x2, maxmaj, maxmin, stepsize=0.):
        interval = QwtDoubleInterval(x1, x2).normalized()
        try:
            ticks = self._buildTimeTicks(x1, x2)
        except Exception:
            # print('!!! could not build ticking for', x1, 'and', x2)
            ticks = [], [], [x1, x2]
        #print ticks
        scalediv = QwtScaleDiv(interval, *ticks)
        if x1 > x2:
            scalediv.invert()
        return scalediv

    def _buildTimeTicks(self, mintime, maxtime, minticks=3):
        good = [1, 2, 5, 10, 30,                           # s
                60, 2*60, 5*60, 10*60, 15*60, 30*60,       # m
                3600, 2*3600, 3*3600, 6*3600, 12*3600,     # h
                24*3600, 2*24*3600, 3*24*3600, 7*24*3600]  # d
        divs = [5, 4, 5, 5, 6,
                6, 4, 5, 5, 3, 6,
                6, 4, 6, 6, 6,
                6, 6, 6, 7]
        upscaling = [1, 2, 5, 10]
        downscaling = [1, 0.5, 0.2, 0.1]

        # calculate maxticks, depends on 'good' values
        maxticks = minticks
        for i in range(len(good)-1):
            if maxticks < minticks * good[i+1]/float(good[i]):
                maxticks = minticks * good[i+1]/float(good[i])

        # determine ticking range
        length = maxtime - mintime
        maxd = length / float(minticks)
        mind = length / float(maxticks+1)

        # scale to useful numbers
        scale_ind = 0
        scale_fact = 1
        scale = 1
        while maxd * scale < good[0]:  # too small ticking, increase scaling
            scale_ind += 1
            if scale_ind >= len(upscaling):
                scale_fact *= upscaling[-1]
                scale_ind = 1
            scale = scale_fact * upscaling[scale_ind]
        scale_ind = 0
        while mind * scale > good[-1]:  # too big ticking, decrease scaling
            scale_ind += 1
            if scale_ind >= len(downscaling):
                scale_fact *= downscaling[-1]
                scale_ind = 1
            scale = scale_fact * downscaling[scale_ind]

        # find a good value for ticking
        tickdist = 0
        subticks = 0
        for i, d in enumerate(good):
            if mind * scale <= d <= maxd * scale:
                tickdist = d / float(scale)
                subticks = divs[i]

        # check ticking
        assert tickdist > 0

        # calculate tick positions
        minor, medium, major = [], [], []
        for i in range(int(mintime/tickdist)-1, int(maxtime/tickdist)+1):
            t = int(i+1) * tickdist
            major.append(t)
            for j in range(subticks):
                minor.append(t + j*tickdist/subticks)
        return minor, medium, major


class TimeSeries(object):
    """
    Represents a plot curve that shows a time series for a value.
    """
    minsize = 500

    def __init__(self, name, interval, window, signal_obj):
        self.name = name
        self.signal_obj = signal_obj
        self.info = None
        self.interval = interval
        self.window = window
        self.x = None
        self.y = None
        self.n = 0
        self.real_n = 0
        self.last_y = None

    def init_empty(self):
        self.x = np.zeros(self.minsize)
        self.y = np.zeros(self.minsize)

    def init_from_history(self, history, starttime, valueindex=-1):
        string_mapping = {}
        ltime = 0
        lvalue = None
        maxdelta = max(2 * self.interval, 11)
        x = np.zeros(3 * len(history))
        y = np.zeros(3 * len(history))
        i = 0
        vtime = value = None  # stops pylint from complaining
        for vtime, value in history:
            if valueindex > -1:
                try:
                    value = value[valueindex]
                except (TypeError, IndexError):
                    continue
            if value is None:
                continue
            delta = vtime - ltime
            if delta < self.interval:
                # value comes too fast -> ignore
                lvalue = value
                continue
            if not isinstance(value, number_types):
                # if it's a string, create a new unique integer value for the string
                if isinstance(value, string_types):
                    value = string_mapping.setdefault(value, len(string_mapping))
                # other values we can't use
                else:
                    continue
            if delta > maxdelta and lvalue is not None:
                # synthesize one or two points inbetween
                if vtime - self.interval > ltime + self.interval:
                    x[i] = ltime + self.interval
                    y[i] = lvalue
                    i += 1
                x[i] = vtime - self.interval
                y[i] = lvalue
                i += 1
            x[i] = ltime = max(vtime, starttime)
            y[i] = lvalue = value
            i += 1
        # In case the final value was discarded because it came too fast,
        # add it anyway, because it will potentially be the last one for
        # longer, and synthesized.
        if i and y[i-1] != value:
            x[i] = vtime
            y[i] = value
            i += 1
        self.n = self.real_n = i
        self.last_y = lvalue
        x.resize((2 * i or 500,))
        y.resize((2 * i or 500,))
        self.x = x
        self.y = y
        if string_mapping:
            self.info = ', '.join('%s=%s' % (v, k)
                                  for (k, v) in iteritems(string_mapping))

    def synthesize_value(self):
        if self.n and self.x[self.n - 1] < currenttime() - self.interval:
            self.add_value(currenttime(), self.last_y, real=False)

    def add_value(self, vtime, value, real=True):
        n, x, y = self.n, self.x, self.y
        real_n = self.real_n
        self.last_y = value
        # do not add value if it comes too fast
        if real_n > 0 and x[real_n - 1] > vtime - self.interval:
            return
        # double array size if array is full
        if n >= x.shape[0]:
            # we select a certain maximum # of points to avoid filling up memory
            # and taking forever to update
            if x.shape[0] > 5000:
                # don't add more points, make existing ones more sparse
                x[:n/2] = x[1::2]
                y[:n/2] = y[1::2]
                n = self.n = self.real_n = n / 2
            else:
                del x, y  # remove references
                self.x.resize((2 * self.x.shape[0],))
                self.y.resize((2 * self.y.shape[0],))
                x = self.x
                y = self.y
        # fill next entry
        if not real and real_n < n - 1:
            # do not generate endless amounts of synthesized points,
            # two are enough (one at the beginning, one at the end of
            # the interval without real points)
            x[n-1] = vtime
            y[n-1] = value
        else:
            x[n] = vtime
            y[n] = value
            self.n += 1
            if real:
                self.real_n = self.n
        # check sliding window
        if self.window:
            i = -1
            threshold = vtime - self.window
            while x[i+1] < threshold and i < n:
                if x[i+2] > threshold:
                    x[i+1] = threshold
                    break
                i += 1
            if i >= 0:
                x[0:n - i] = x[i+1:n+1].copy()
                y[0:n - i] = y[i+1:n+1].copy()
                self.n -= i+1
                self.real_n -= i+1
        self.signal_obj.emit(SIGNAL('timeSeriesUpdate'), self)


class TrendPlot(QwtPlot, NicosWidget):

    designer_description = 'A trend plotter for one or more devices'
    designer_icon = ':/plotter'

    colors = [Qt.red, Qt.darkGreen, Qt.blue, Qt.black, Qt.magenta, Qt.cyan, Qt.darkGray]

    #pylint: disable=W0231
    def __init__(self, parent, designMode=False):
        self.ncurves = 0
        self.ctimers = {}
        self.keyindices = {}
        self.plotcurves = {}
        self.series = {}

        QwtPlot.__init__(self, parent)
        NicosWidget.__init__(self)

    def initUi(self):
        if QwtPlot is QWidget:
            raise RuntimeError('Plotting is not available on this system, '
                               'please install PyQwt.')

        # appearance setup
        self.setCanvasBackground(Qt.white)

        # axes setup
        self.setAxisScaleEngine(QwtPlot.xBottom, TimeScaleEngine())
        self.setAxisScaleDraw(QwtPlot.xBottom,
                              TimeScaleDraw(showdate=False, showsecs=False))
        self.setAxisLabelAlignment(QwtPlot.xBottom,
                                   Qt.AlignBottom | Qt.AlignLeft)
        self.setAxisLabelRotation(QwtPlot.xBottom, -45)

        # subcomponents: grid, legend, zoomer
        grid = QwtPlotGrid()
        grid.setPen(QPen(QBrush(Qt.gray), 1, Qt.DotLine))
        grid.attach(self)
        self.legend = QwtLegend(self)
        self.legend.setMidLineWidth(100)
        self.insertLegend(self.legend, QwtPlot.TopLegend)
        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft,
                                    self.canvas())
        self.zoomer.initMousePattern(2)  # don't bind middle button
        self.connect(self.zoomer, SIGNAL('zoomed(const QwtDoubleRect &)'),
                     self.on_zoomer_zoomed)

        self.panner = QwtPlotPanner(self.canvas())
        self.panner.setMouseButton(Qt.MidButton)

        self.picker = ActivePlotPicker(QwtPlot.xBottom, QwtPlot.yLeft,
                                       QwtPicker.PointSelection |
                                       QwtPicker.DragSelection,
                                       QwtPlotPicker.NoRubberBand,
                                       QwtPicker.AlwaysOff,
                                       self.canvas())
        self.canvas().setMouseTracking(True)
        self.connect(self.picker, SIGNAL('moved(const QPoint &)'),
                     self.on_picker_moved)

        self.connect(self, SIGNAL('timeSeriesUpdate'), self.on_timeSeriesUpdate)

    properties = {
        'devices':      PropDef('QStringList', [], '''
List of devices or cache keys that the plot should display.
For devices, use device name.
For keys, use cache key with "." or "/" separator, e.g. T.heaterpower
To access items of a sequence, use subscript notation, e.g. T.userlimits[0]
'''),
        'names':        PropDef('QStringList', [], 'Names for the plot curves, '
                                'defaults to the device names/keys.'),
        'plotwindow':   PropDef(int, 3600, 'The range of time in seconds that '
                                'should be represented by the plot.'),
        'plotinterval': PropDef(float, 2, 'The minimum time in seconds between '
                                'two points that should be plotted.'),
        'height':       PropDef(int, 10, 'Height of the plot widget in units '
                                'of app font character width.'),
        'width':        PropDef(int, 30, 'Width of the plot widget in units '
                                'of app font character width.'),
    }

    def propertyUpdated(self, pname, value):
        if pname == 'plotwindow':
            showdate = value > 24*3600
            showsecs = value < 300
            self.setAxisScaleDraw(QwtPlot.xBottom,
                TimeScaleDraw(showdate=showdate, showsecs=showsecs))
        elif pname in ('width', 'height'):
            self.setMinimumSize(
                QSize(self._scale * (self.props['width'] + .5),
                      self._scale * (self.props['height'] + .5)))
        NicosWidget.propertyUpdated(self, pname, value)

    def setFont(self, font):
        QwtPlot.setFont(self, font)
        self.legend.setFont(font)
        self.setAxisFont(QwtPlot.yLeft, font)
        self.setAxisFont(QwtPlot.xBottom, font)

    def on_picker_moved(self, point):
        info = "t = %s, y = %g" % (
            strftime('%y-%m-%d %H:%M:%S', localtime(
                self.invTransform(QwtPlot.xBottom, point.x()))),
            self.invTransform(QwtPlot.yLeft, point.y()))
        self.emit(SIGNAL('widgetInfo'), info)

    def on_zoomer_zoomed(self, rect):
        # when zooming completely out, reset to auto scaling
        if self.zoomer.zoomRectIndex() == 0:
            self.setAxisAutoScale(QwtPlot.xBottom)
            self.setAxisAutoScale(QwtPlot.yLeft)
            self.zoomer.setZoomBase()

    def addcurve(self, key, index, title):
        series = self.series[key, index] = TimeSeries(
            key, self.props['plotinterval'], self.props['plotwindow'], self)
        series.init_empty()
        curve = QwtPlotCurve(title)
        self.plotcurves[series] = curve
        curve.setPen(QPen(self.colors[self.ncurves % 6], 2))
        self.ncurves += 1
        curve.attach(self)
        curve.setRenderHint(QwtPlotCurve.RenderAntialiased)
        self.legend.find(curve).setIdentifierWidth(30)
        self.ctimers[curve] = QTimer(singleShot=True)

        # record the current value at least every 5 seconds, to avoid curves
        # not updating if the value doesn't change
        def update():
            series.synthesize_value()
        self.connect(self.ctimers[curve], SIGNAL('timeout()'), update)

    def on_timeSeriesUpdate(self, series):
        curve = self.plotcurves[series]
        curve.setData(series.x[:series.n], series.y[:series.n])
        if self.zoomer.zoomRect() == self.zoomer.zoomBase():
            self.zoomer.setZoomBase(True)
        else:
            self.replot()
        self.ctimers[curve].start(5000)

    def on_keyChange(self, key, value, time, expired):
        if key not in self.keyindices or value is None:
            return
        for index in self.keyindices[key]:
            series = self.series[key, index]
            # restrict time of value to 1 minute past at
            # maximum, so that it doesn't get culled by the windowing
            time = max(time, currenttime() - 60)
            if index >= 0:
                try:
                    series.add_value(time, value[index])
                except (ValueError, IndexError):
                    pass
            else:
                series.add_value(time, value)

    def registerKeys(self):
        for key, name in map(None, self.props['devices'], self.props['names']):
            if name is None:
                name = key
            key, index = extractKeyAndIndex(key)
            keyid = self._source.register(self, key)
            self.keyindices.setdefault(keyid, []).append(index)
            self.addcurve(keyid, index, name)
