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

        self.lw = LWWidget(self)
        self.plotLayout.addWidget(self.lw)

        self.hist = QwtPlot(self)
        self.hist.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.hist.enableAxis(QwtPlot.yLeft, False)
        afnt = QFont(self.font())
        afnt.setPointSize(afnt.pointSize() * 0.7)
        self.hist.setAxisFont(QwtPlot.xBottom, afnt)
        self.histogramLayout.addWidget(self.hist)

        data = LWData(2048, 2048, 1, "f4", open("test.img").read())
        self.lw.setData(data)

        # XXX add histogram
        self.updateSliders(data)

        self.connect(self.logscaleBox, SIGNAL('toggled(bool)'), self.setLogscale)
        self.connect(self.grayscaleBox, SIGNAL('toggled(bool)'), self.setColormap)
        self.connect(self.cyclicBox, SIGNAL('toggled(bool)'), self.setColormap)
        self.connect(self.minSlider, SIGNAL('valueChanged(int)'), self.updateRange)
        self.connect(self.maxSlider, SIGNAL('valueChanged(int)'), self.updateRange)

    def updateSliders(self, data):
        if data.isLog10():
            print data.min() * 100, data.max() * 100
            self.minSlider.setRange(data.min() * 100, data.max() * 100)
            self.maxSlider.setRange(data.min() * 100, data.max() * 100)
            print data.min() * 100, data.max() * 100
            self.minSlider.setValue(data.customRangeMin() * 100)
            self.maxSlider.setValue(data.customRangeMax() * 100)
        else:
            self.minSlider.setRange(data.min(), data.max())
            self.maxSlider.setRange(data.min(), data.max())
            self.minSlider.setValue(data.customRangeMin())
            self.maxSlider.setValue(data.customRangeMax())

    def updateRange(self):
        if self.lw.data().isLog10():
            self.lw.setCustomRange(self.minSlider.value()/100., self.maxSlider.value()/100.)
        else:
            self.lw.setCustomRange(self.minSlider.value(), self.maxSlider.value())

    def setLogscale(self, on):
        self.lw.setLog10(on)
        self.updateSliders(self.lw.data())

    def setColormap(self, on):
        self.lw.setStandardColorMap(self.grayscaleBox.isChecked(),
                                    self.cyclicBox.isChecked())


if __name__ == '__main__':
    app = QApplication(sys.argv[1:])
    window = MainWindow(None)
    window.show()
    app.exec_()
