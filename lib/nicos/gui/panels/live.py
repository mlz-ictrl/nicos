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

"""NICOS live 2D data plot window/panel."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from PyQt4.QtCore import Qt, QVariant, SIGNAL, SLOT
from PyQt4.QtCore import pyqtSignature as qtsig
from PyQt4.QtGui import QLabel, QVBoxLayout, QFileDialog, QPrinter, \
     QPrintDialog, QDialog, QMenu, QToolBar

from nicos.gui.utils import loadUi
from nicos.gui.panels import Panel
from nicos.gui.cascadewidget import CascadeWidget, TmpImage


class LiveDataPanel(Panel):
    panelName = 'Live data view'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'live.ui')

        self._format = None
        self._runtime = 0

        layout = QVBoxLayout(self)

        self.widget = CascadeWidget(self)
        self.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        # XXX display countrate/estimation
        self.label = QLabel('', self)

        layout.addWidget(self.widget)
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.connect(client, SIGNAL('livedata'), self.on_client_livedata)
        self.connect(client, SIGNAL('liveparams'), self.on_client_liveparams)

        self.connect(self.actionLogScale, SIGNAL("toggled(bool)"),
                     self.widget, SLOT("SetLog10(bool)"))
        self.connect(self.actionSelectChannels, SIGNAL("triggered()"),
                     self.widget, SLOT("showSumDlg()"))
        self.connect(self.widget,
                     SIGNAL('customContextMenuRequested(const QPoint&)'),
                     self.on_widget_customContextMenuRequested)

    def getMenus(self):
        self.menu = menu = QMenu('&Live data', self)
        menu.addAction(self.actionLoadTOF)
        menu.addAction(self.actionLoadPAD)
        menu.addSeparator()
        menu.addAction(self.actionWriteXml)
        menu.addAction(self.actionPrint)
        menu.addSeparator()
        menu.addAction(self.actionSetAsROI)
        menu.addAction(self.actionUnzoom)
        menu.addAction(self.actionLogScale)
        menu.addAction(self.actionNormalized)
        menu.addAction(self.actionLegend)
        return [menu]

    def getToolbars(self):
        bar = QToolBar('Live data')
        bar.addAction(self.actionWriteXml)
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionLogScale)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionSetAsROI)
        bar.addSeparator()
        bar.addAction(self.actionSelectChannels)
        return [bar]

    def on_widget_customContextMenuRequested(self, point):
        self.menu.popup(self.mapToGlobal(point))

    def on_client_liveparams(self, params):
        tag, dtype, nx, ny, nt, runtime = params
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

    def on_client_livedata(self, data):
        if self._format == 'pad':
            self.widget.LoadPadMem(data, 128*128*4)
        elif self._format == 'tof':
            self.widget.LoadTofMem(data, 128*128*128*4)

    @qtsig('')
    def on_actionLoadTOF_triggered(self):
        filename = QFileDialog.getOpenFileName(self,
            'Open TOF File', '', 'TOF File (*.tof *.TOF);;All files (*)')
        if filename:
            self.widget.LoadTofFile(filename)

    @qtsig('')
    def on_actionLoadPAD_triggered(self):
        filename = QFileDialog.getOpenFileName(self,
            'Open PAD File', '', 'PAD File (*.pad *.PAD);;All files (*)')
        if filename:
            self.widget.LoadPadFile(filename)

    @qtsig('')
    def on_actionWriteXml_triggered(self):
        pad = self.widget.GetPad()
        if pad is None:
            return self.showError('No 2-d image is shown.')
        filename = str(QFileDialog.getSaveFileName(
            self, 'Select file name', '', 'XML files (*.xml)'))
        if filename == '':
            return
        if not filename.endswith('.xml'):
            filename += '.xml'
        tmpimg = TmpImage()
        tmpimg.ConvertPAD(pad)
        tmpimg.WriteXML(filename)

    @qtsig('')
    def on_actionSetAsROI_triggered(self):
        zoom = self.widget.GetPlot().GetZoomer().zoomRect()
        self.client.tell('queue', '', 'psd.roi = (%s, %s, %s, %s)' %
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
