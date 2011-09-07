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

"""Live widget demonstration."""

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qwt5 import *
from PyQt4.uic import loadUi

from livewidget import LWWidget, LWData


class MainWindow(QMainWindow):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        loadUi('demo.ui', self)

        self.livewidget = LWWidget(self)
        self.plotLayout.addWidget(self.livewidget)

        self.histoplot = QwtPlot(self)
        self.histoplot.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.histoplot.enableAxis(QwtPlot.yLeft, False)
        afnt = QFont(self.font())
        afnt.setPointSize(afnt.pointSize() * 0.7)
        self.histoplot.setAxisFont(QwtPlot.xBottom, afnt)
        self.histogramLayout.addWidget(self.histoplot)

        x = open("test1.fits").read()[5760:-1664]
        data = LWData(2048, 2048, 1, ">f4", x)
        self.livewidget.setData(data)

        self._absmin = self.livewidget.data().min()
        self._absmax = self.livewidget.data().max()
        self._absrange = self._absmax - self._absmin
        self._curmin = self._absmin
        self._curmax = self._absmax
        self._currange = self._absrange
        self._sliderupdating = False

        self.rangemarker = QwtPlotCurve()
        self.rangemarker.setPen(QPen(QBrush(QColor(0, 0, 255, 64)), 1000, Qt.SolidLine, Qt.FlatCap))
        self.rangemarker.attach(self.histoplot)
        self.rangemarker.setData([self._curmin, self._curmax], [0, 0])

        xs, ys = data.histogram(100)
        self.histogram = QwtPlotCurve()
        self.histogram.setData(xs, ys)
        self.histogram.setRenderHint(QwtPlotCurve.RenderAntialiased)
        self.histogram.attach(self.histoplot)

        self.histopicker = QwtPlotPicker(QwtPlot.xBottom, QwtPlot.yLeft,
                                         QwtPicker.RectSelection,
                                         QwtPicker.RectRubberBand,
                                         QwtPicker.AlwaysOff,
                                         self.histoplot.canvas())
        self.histopicker.setRubberBandPen(QPen(Qt.red))
        self.connect(self.histopicker, SIGNAL('selected(const QwtDoubleRect&)'),
                     self.histogramPicked)

        self.connect(self.logscaleBox, SIGNAL('toggled(bool)'), self.setLogscale)
        self.connect(self.grayscaleBox, SIGNAL('toggled(bool)'), self.setColormap)
        self.connect(self.cyclicBox, SIGNAL('toggled(bool)'), self.setColormap)
        self.connect(self.minSlider, SIGNAL('valueChanged(int)'), self.updateMinMax)
        self.connect(self.maxSlider, SIGNAL('valueChanged(int)'), self.updateMinMax)
        self.connect(self.brtSlider, SIGNAL('valueChanged(int)'), self.updateBrightness)
        self.connect(self.ctrSlider, SIGNAL('valueChanged(int)'), self.updateContrast)

    def histogramPicked(self, rect):
        self._sliderupdating = True
        self.minSlider.setValue((rect.left() - self._absmin)/self._absrange * 256)
        self.maxSlider.setValue((rect.right() - self._absmin)/self._absrange * 256)
        self._sliderupdating = False
        self.updateMinMax()

    def updateMinMax(self):
        if self._sliderupdating:
            return
        self._curmin = self._absmin + self._absrange * self.minSlider.value() / 256.
        self._curmax = self._absmin + self._absrange * self.maxSlider.value() / 256.
        self._currange = self._curmax - self._curmin
        self.livewidget.setCustomRange(self._curmin, self._curmax)
        self.rangemarker.setData([self._curmin, self._curmax], [0, 0])
        self.histoplot.replot()
        brightness = 1.0 - (self._curmin + self._currange/2. - self._absmin)/self._absrange
        contrast = self._absrange/self._currange * 0.5
        if contrast > 0.5:
            contrast = 1 - self._currange/self._absrange * 0.5
        self._sliderupdating = True
        self.ctrSlider.setValue(256 * contrast)
        self.brtSlider.setValue(256 * brightness)
        self._sliderupdating = False

    def updateBrightness(self, level):
        if self._sliderupdating:
            return
        level /= 256.
        center = self._absmin + self._absrange * (1 - level)
        width = self._curmax - self._curmin
        self._curmin = center - width/2.
        self._curmax = center + width/2.
        self._currange = self._curmax - self._curmin
        self.livewidget.setCustomRange(self._curmin, self._curmax)
        self.rangemarker.setData([self._curmin, self._curmax], [0, 0])
        self.histoplot.replot()
        self._sliderupdating = True
        self.minSlider.setValue((self._curmin - self._absmin)/self._absrange * 256)
        self.maxSlider.setValue((self._curmax - self._absmin)/self._absrange * 256)
        self._sliderupdating = False

    def updateContrast(self, level):
        if self._sliderupdating:
            return
        level /= 256.
        center = self._curmin + self._currange/2.
        if level <= 0.5:
            slope = level / 0.5
        else:
            slope = 0.5 / (1 - level)
        if slope > 0:
            self._curmin = center - (0.5 * self._absrange)/slope
            self._curmax = center + (0.5 * self._absrange)/slope
            self._currange = self._curmax - self._curmin
            self.livewidget.setCustomRange(self._curmin, self._curmax)
            self.rangemarker.setData([self._curmin, self._curmax], [0, 0])
            self.histoplot.replot()
            self._sliderupdating = True
            self.minSlider.setValue((self._curmin - self._absmin)/self._absrange * 256)
            self.maxSlider.setValue((self._curmax - self._absmin)/self._absrange * 256)
            self._sliderupdating = False

    def setLogscale(self, on):
        data = self.livewidget.data()
        self.livewidget.setLog10(on)
        self._absmin = data.min()
        self._absmax = data.max()
        self._absrange = self._absmax - self._absmin
        xs, ys = data.histogram(100)
        self.histogram.setData(xs, ys)
        self.histoplot.replot()

    def setColormap(self, on):
        self.livewidget.setStandardColorMap(self.grayscaleBox.isChecked(),
                                            self.cyclicBox.isChecked())


if __name__ == '__main__':
    app = QApplication(sys.argv[1:])
    window = MainWindow(None)
    window.show()
    app.exec_()
