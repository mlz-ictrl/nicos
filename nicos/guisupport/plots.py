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

"""
NICOS value plot widget.
"""

import operator

from time import time as currenttime, strftime, localtime

from PyQt4.QtGui import QWidget, QPen, QBrush
from PyQt4.QtCore import Qt, SIGNAL, QTimer, QSize

from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtLegend, \
    QwtPlotZoomer, QwtPicker, QwtPlotPicker, QwtPlotPanner, QwtScaleDraw, \
    QwtText, QwtLinearScaleEngine, QwtScaleDiv, QwtDoubleInterval

from nicos.guisupport.timeseries import TimeSeries, buildTimeTicks
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.guisupport.utils import extractKeyAndIndex
from nicos.pycompat import zip_longest


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
            ticks = buildTimeTicks(x1, x2)
        except Exception:
            # print('!!! could not build ticking for', x1, 'and', x2)
            ticks = [], [], [x1, x2]
        # print ticks
        scalediv = QwtScaleDiv(interval, *ticks)
        if x1 > x2:
            scalediv.invert()
        return scalediv


class TrendPlot(QwtPlot, NicosWidget):

    designer_description = 'A trend plotter for one or more devices'
    designer_icon = ':/plotter'

    colors = [Qt.red, Qt.darkGreen, Qt.blue, Qt.black, Qt.magenta, Qt.cyan, Qt.darkGray]

    # pylint: disable=W0231
    def __init__(self, parent, designMode=False):
        self.ncurves = 0
        self.ctimers = {}
        self.keyindices = {}
        self.plotcurves = {}
        self.series = {}
        self.legendobj = None

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
        'legend':       PropDef(bool, False, 'If a legend should be shown.'),
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
        elif pname == 'legend':
            if value:
                self.legendobj = QwtLegend(self)
                self.legendobj.setMidLineWidth(100)
            else:
                self.legendobj = None
            self.insertLegend(self.legendobj, QwtPlot.TopLegend)
        NicosWidget.propertyUpdated(self, pname, value)

    def setFont(self, font):
        QwtPlot.setFont(self, font)
        if self.legendobj:
            self.legendobj.setFont(font)
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
            if index:
                try:
                    fvalue = reduce(operator.getitem, index, value)
                    series.add_value(time, fvalue)
                except Exception:
                    pass
            else:
                series.add_value(time, value)

    def addcurve(self, key, index, title):
        series = TimeSeries(key, self.props['plotinterval'],
                            self.props['plotwindow'], self)
        series.init_empty()
        curve = QwtPlotCurve(title)
        self.plotcurves[series] = curve
        curve.setPen(QPen(self.colors[self.ncurves % 6], 2))
        self.ncurves += 1
        curve.attach(self)
        curve.setRenderHint(QwtPlotCurve.RenderAntialiased)
        if self.legendobj:
            self.legendobj.find(curve).setIdentifierWidth(30)
        self.series[key, index] = series

        # record the current value at least every 5 seconds, to avoid curves
        # not updating if the value doesn't change
        def update():
            series.synthesize_value()
        self.ctimers[curve] = QTimer(singleShot=True)
        self.connect(self.ctimers[curve], SIGNAL('timeout()'), update)

    def registerKeys(self):
        for key, name in zip_longest(self.props['devices'], self.props['names']):
            if name is None:
                name = key
            key, index = extractKeyAndIndex(key)
            keyid = self._source.register(self, key)
            self.keyindices.setdefault(keyid, []).append(index)
            self.addcurve(keyid, index, name)
