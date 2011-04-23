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

"""NICOS live 2D data plot window."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import pyqtSignature as qtsig

from nicos.gui.utils import SettingGroup, loadUi, DlgUtils
from nicos.gui.cascadewidget import CascadeWidget, TmpImage


class LiveWindow(QMainWindow, DlgUtils):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        DlgUtils.__init__(self, 'Live data')
        loadUi(self, 'live.ui')

        self._format = None
        self._runtime = 0

        layout = QVBoxLayout(self)

        self.widget = CascadeWidget(self)
        # XXX display countrate/estimation
        self.label = QLabel('', self)

        layout.addWidget(self.widget)
        layout.addWidget(self.label)

        frame = QFrame(self)
        frame.setLayout(layout)
        self.setCentralWidget(frame)

        self.sgroup = SettingGroup('AnalysisWindow')
        self.loadSettings()

        self.connect(self.actionLogScale, SIGNAL("toggled(bool)"),
                     self.widget, SLOT("SetLog10(bool)"))
        self.connect(self.actionSelectChannels, SIGNAL("triggered()"),
                     self.widget, SLOT("showSumDlg()"))

    def loadSettings(self):
        with self.sgroup as settings:
            geometry = settings.value('geometry').toByteArray()
        self.restoreGeometry(geometry)

    def setParams(self, params):
        dtype, nx, ny, nt, runtime = params
        self._runtime = runtime
        if dtype == '<I4' and nx == 128 and ny == 128:
            if nt == 1:
                self._format = 'pad'
                return
            elif nt == 128:
                self._format = 'tof'
                return
        print 'Unsupported live data format:', params
        self._format = None

    def setData(self, data):
        if self._format == 'pad':
            self.widget.LoadPadMem(data, 128*128*4)
        elif self._format == 'tof':
            self.widget.LoadTofMem(data, 128*128*128*4)

    @qtsig('')
    def on_actionWriteXml_triggered(self):
        filename = str(QFileDialog.getSaveFileName(
            self, self.tr('Select file name'), '',
            self.tr('XML files (*.xml)')))
        if filename == '':
            return
        if not filename.endswith('.xml'):
            filename += '.xml'
        pad = self.widget.GetPad()
        if pad is None:
            return
        tmpimg = TmpImage()
        tmpimg.ConvertPAD(pad)
        tmpimg.WriteXML(filename)

    @qtsig('')
    def on_actionSetAsROI_triggered(self):
        zoom = self.widget.GetPlot().GetZoomer().zoomRect()
        self.parent().run_script('None', 'psd.roi = (%s, %s, %s, %s)' %
                                 (int(zoom.left()), int(zoom.top()),
                                  int(zoom.right()), int(zoom.bottom())))

    @qtsig('')
    def on_actionUnzoom_triggered(self):
        self.widget.GetPlot().GetZoomer().zoom(0)

    @qtsig('')
    def on_actionPrint_triggered(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setColorMode(QPrinter.Color)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFileName('')
        if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
            self.widget.GetPlot().print_(printer)
        self.statusBar.showMessage('Plot successfully printed to %s.' %
                                   str(printer.printerName()))

    def closeEvent(self, event):
        with self.sgroup as settings:
            settings.setValue('geometry', QVariant(self.saveGeometry()))
        event.accept()
        self.emit(SIGNAL('closed'), self)
