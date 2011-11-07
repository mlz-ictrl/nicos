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

"""NICOS live 2D data plot window/panel."""

__version__ = "$Revision$"

from os import path

from PyQt4.QtCore import Qt, QVariant, SIGNAL, SLOT
from PyQt4.QtCore import pyqtSignature as qtsig
from PyQt4.QtGui import QStatusBar, QFileDialog, QPrinter, QPrintDialog, \
     QDialog, QMenu, QToolBar, QSizePolicy, QListWidgetItem

from nicos.gui.utils import loadUi
from nicos.gui.panels import Panel
from nicos.gui.cascadewidget import CascadeWidget, TmpImage


class LiveDataPanel(Panel):
    panelName = 'Live data view'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'live.ui', 'panels')

        self._format = None
        self._runtime = 0
        self._no_direct_display = False

        self.statusBar = QStatusBar(self)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.widget = CascadeWidget(self)
        self.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.widgetLayout.addWidget(self.widget)

        self.splitter.restoreState(self.splitterstate)

        self.connect(client, SIGNAL('livedata'), self.on_client_livedata)
        self.connect(client, SIGNAL('liveparams'), self.on_client_liveparams)

        self.connect(self.actionLogScale, SIGNAL("toggled(bool)"),
                     self.widget, SLOT("SetLog10(bool)"))
        self.connect(self.actionSelectChannels, SIGNAL("triggered()"),
                     self.widget, SLOT("showSumDlg()"))
        self.connect(self.widget,
                     SIGNAL('customContextMenuRequested(const QPoint&)'),
                     self.on_widget_customContextMenuRequested)

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter').toByteArray()

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())

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
        tag, filename, dtype, nx, ny, nt, runtime = params
        self._runtime = runtime
        self._filename = filename
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
        if self._format not in ('pad', 'tof'):
            return
        self._last_data = data
        if not self._no_direct_display:
            if self._format == 'pad':
                self.widget.LoadPadMem(data, 128*128*4)
            else:
                self.widget.LoadTofMem(data, 128*128*128*4)
        if self._filename and path.isfile(self._filename):
            shortname = path.basename(self._filename)
            item = QListWidgetItem(shortname, self.fileList)
            item.setData(32, self._filename)
            item.setData(33, self._format)

    def on_fileList_itemClicked(self, item):
        if item is None:
            return
        fname = item.data(32).toString()
        format = item.data(33).toString()
        self._no_direct_display = True
        if format == 'pad':
            self.widget.LoadPadFile(fname)
        elif format == 'tof':
            self.widget.LoadTofFile(fname)

    @qtsig('')
    def on_liveButton_clicked(self):
        if self._no_direct_display:
            self._no_direct_display = False
            if self._format == 'pad':
                self.widget.LoadPadMem(self._last_data, 128*128*4)
            elif self._format == 'tof':
                self.widget.LoadTofMem(self._last_data, 128*128*128*4)

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
