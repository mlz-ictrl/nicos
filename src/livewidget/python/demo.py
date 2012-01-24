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

"""Live widget demonstration."""

__version__ = "$Revision$"

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
        #self.livewidget.setKeepAspect(False)
        #self.livewidget.setControlsVisible(False)
        self.plotLayout.addWidget(self.livewidget)
        self.livewidget.setAxisLabels('detectors', 'time channels')

        #x = open("test1.fits").read()[5760:-1664]
        #data = LWData(2048, 2048, 1, ">f4", x)
        x = open("testdata.npy").read()[80:]
        data = LWData(1024, 1024, 1, ">i4", x)
        self.livewidget.setData(data)
        #self.livewidget.setLog10(True)

    def setColormap(self, on):
        self.livewidget.setStandardColorMap(self.grayscaleBox.isChecked(),
                                            self.cyclicBox.isChecked())


if __name__ == '__main__':
    app = QApplication(sys.argv[1:])
    window = MainWindow(None)
    window.setWindowTitle('LiveWidget demo')
    window.resize(1000, 600)
    window.show()
    app.exec_()
