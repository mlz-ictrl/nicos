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
from PyQt4.QtCore import Qt, pyqtProperty, SIGNAL, QTimer, QSize

try:
    from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtLegend, \
         QwtPlotZoomer, QwtPicker, QwtPlotPicker, QwtPlotPanner
    # XXX: move these to guisupport
    from nicos.clients.gui.widgets.plotting import TimeScaleEngine, TimeScaleDraw, \
         ActivePlotPicker
    plot_available = True
except (ImportError, RuntimeError):
    QwtPlot = QWidget
    plot_available = False

from nicos.guisupport.widget import DisplayWidget


class TrendPlot(QwtPlot, DisplayWidget):

    designer_description = 'A trend plotter for one or more devices'
    designer_icon = ':/plotter'

    colors = [Qt.red, Qt.darkGreen, Qt.blue, Qt.magenta, Qt.cyan, Qt.darkGray]

    #pylint: disable=W0231
    def __init__(self, parent, designMode=False):
        self.ncurves = 0
        self.ctimers = {}
        self.plotcurves = {}
        self.plotx = {}
        self.ploty = {}

        self._devices = []
        self._interval = 3600

        QwtPlot.__init__(self, parent)
        DisplayWidget.__init__(self)

    def initUi(self):
        if QwtPlot is QWidget:
            raise RuntimeError('Plotting is not available on this system, '
                               'please install PyQwt.')

        # appearance setup
        self.setCanvasBackground(Qt.white)

        # axes setup
        self.setAxisScaleEngine(QwtPlot.xBottom, TimeScaleEngine())
        showdate = self._interval > 24*3600
        showsecs = self._interval < 300
        self.setAxisScaleDraw(QwtPlot.xBottom,
                              TimeScaleDraw(showdate=showdate, showsecs=showsecs))
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

        self.connect(self, SIGNAL('updateplot'), self.updateplot)

    def setConfig(self, config, labelfont, valuefont, scale):
        self.plotInterval = config.get('plotinterval', 3600)
        self.setFont(labelfont)
        self.setMinimumSize(
            QSize(scale * (config.get('width', 20) + .5),
                  scale * (config.get('height', 20) + .5)))

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

    def addcurve(self, keyid, title):
        curve = QwtPlotCurve(title)
        curve.setPen(QPen(self.colors[self.ncurves % 6], 2))
        self.ncurves += 1
        curve.attach(self)
        curve.setRenderHint(QwtPlotCurve.RenderAntialiased)
        self.legend.find(curve).setIdentifierWidth(30)
        self.ctimers[curve] = QTimer(singleShot=True)

        self.plotcurves[keyid] = curve
        self.plotx[keyid] = []
        self.ploty[keyid] = []

        # record the current value at least every 5 seconds, to avoid curves
        # not updating if the value doesn't change
        def update():
            if self.plotx[keyid]:
                self.plotx[keyid].append(currenttime())
                self.ploty[keyid].append(self.ploty[keyid][-1])
                self.emit(SIGNAL('updateplot'), keyid, curve)
        self.connect(self.ctimers[curve], SIGNAL('timeout()'), update)

    def updateplot(self, keyid, curve):
        xx, yy = self.plotx[keyid], self.ploty[keyid]
        ll = len(xx)
        i = 0
        limit = currenttime() - self._interval
        while i < ll and xx[i] < limit:
            i += 1
        xx = self.plotx[keyid] = xx[i:]
        yy = self.ploty[keyid] = yy[i:]
        curve.setData(xx, yy)
        if self.zoomer.zoomRect() == self.zoomer.zoomBase():
            self.zoomer.setZoomBase(True)
        else:
            self.replot()
        self.ctimers[curve].start(5000)

    def on_keyChange(self, key, value, time, expired):
        if key not in self.plotx or value is None:
            return
        if not self.plotx[key]:
            # restrict time of first value to 1 minute past at
            # maximum, so that it doesn't get culled in updateplot()
            self.plotx[key].append(max(time, currenttime()-60))
        else:
            self.plotx[key].append(time)
        self.ploty[key].append(value)
        curve = self.plotcurves[key]
        self.updateplot(key, curve)

    def registerKeys(self):
        for key in self._devices:
            okey = key
            if '.' not in key and '/' not in key:
                key += '/value'
            keyid = self._source.register(self, key)
            self.addcurve(keyid, okey)

    def get_devices(self):
        return self._devices
    def set_devices(self, value):
        self._devices = map(str, value)
    def reset_devices(self):
        self.devices = []
    devices = pyqtProperty('QStringList', get_devices, set_devices, reset_devices)

    def get_plotInterval(self):
        return self._interval
    def set_plotInterval(self, value):
        self._interval = value
        showdate = self._interval > 24*3600
        showsecs = self._interval < 300
        self.setAxisScaleDraw(QwtPlot.xBottom,
                              TimeScaleDraw(showdate=showdate, showsecs=showsecs))
    def reset_plotInterval(self):
        self.plotInterval = 3600
    plotInterval = pyqtProperty(int, get_plotInterval, set_plotInterval,
                                reset_plotInterval)
