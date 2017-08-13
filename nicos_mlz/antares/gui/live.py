#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""NICOS livewidget 2D data plot window/panel."""

import os
from os import path

from nicos.guisupport.qt import pyqtSlot, Qt, QByteArray, QPrinter, QDialog, \
    QPrintDialog, QMenu, QToolBar, QStatusBar, QSizePolicy, QDoubleSpinBox, \
    QListWidgetItem

from nicos.clients.gui.utils import loadUi
from nicos.clients.gui.panels import Panel
from nicos.utils import findResource

from nicoslivewidget import LWWidget, LWData

DATATYPES = frozenset(('<u4', '<i4', '>u4', '>i4', '<u2', '<i2', '>u2', '>i2',
                       'u1', 'i1', 'f8', 'f4'))


class LiveDataPanel(Panel):
    panelName = 'Live data view'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, findResource('nicos_mlz/antares/gui/live.ui'))

        self._format = None
        self._runtime = 0
        self._no_direct_display = False
        self._range_active = False

        self.statusBar = QStatusBar(self)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.widget = LWWidget(self)
        self.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.widgetLayout.addWidget(self.widget)

        self.rangeFrom = QDoubleSpinBox(self)
        self.rangeTo = QDoubleSpinBox(self)
        for ctrl in [self.rangeFrom, self.rangeTo]:
            ctrl.setEnabled(False)
            ctrl.setMaximumWidth(90)
            ctrl.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Fixed))
            ctrl.valueChanged.connect(self.on_rangeChanged)

        self.liveitem = QListWidgetItem('<Live>', self.fileList)
        self.liveitem.setData(32, '')
        self.liveitem.setData(33, '')

        self.splitter.restoreState(self.splitterstate)

        client.livedata.connect(self.on_client_livedata)
        client.liveparams.connect(self.on_client_liveparams)
        if client.isconnected:
            self.on_client_connected()
        client.connected.connect(self.on_client_connected)
        client.setup.connect(self.on_client_connected)

        self.actionLogScale.toggled.connect(self.widget.setLog10)
        self.widget.customContextMenuRequested.connect(
            self.on_widget_customContextMenuRequested)

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', '', QByteArray)

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())

    def getMenus(self):
        self.menu = menu = QMenu('&Live data', self)
        # menu.addAction(self.actionLoadTOF)
        # menu.addAction(self.actionLoadPAD)
        # menu.addSeparator()
        # menu.addAction(self.actionWriteXml)
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
        # bar.addAction(self.actionWriteXml)
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionLogScale)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionSetAsROI)
        # bar.addSeparator()
        # bar.addAction(self.actionSelectChannels)
        return [bar]

    def on_widget_customContextMenuRequested(self, point):
        self.menu.popup(self.mapToGlobal(point))

    def on_client_connected(self):
        self.client.tell('eventunmask', ['livedata', 'liveparams'])
        datapath = self.client.eval('session.experiment.datapath', '')
        if not datapath:
            return
        caspath = path.join(datapath, 'cascade')
        if path.isdir(caspath):
            for fn in sorted(os.listdir(caspath)):
                if fn.endswith('.pad'):
                    self.add_to_flist(path.join(caspath, fn), 'pad', False)
                elif fn.endswith('tof'):
                    self.add_to_flist(path.join(caspath, fn), 'tof', False)

    def on_client_liveparams(self, params):
        # TODO: remove compatibility code
        if len(params) == 7:  # Protocol version < 16
            _tag, _fname, dtype, nx, ny, nz, runtime = params
        elif len(params) == 9:  # Protocol version >= 16
            _tag, _uid, _det, _fname, dtype, nx, ny, nz, runtime = params

        self._runtime = runtime
        if dtype not in DATATYPES:
            self._format = None
            self.log.warning('Unsupported live data format: %r', params)
            return
        self._format = dtype
        self._nx = nx
        self._ny = ny
        self._nz = nz

    def on_client_livedata(self, data):
        if self._format:
            self.widget.setData(
                LWData(self._nx, self._ny, self._nz, self._format, data))

    @pyqtSlot()
    def on_actionSetAsROI_triggered(self):
        zoom = self.widget.plot().getZoomer().zoomRect()
        # XXX this is detector specific!
        self.client.run('det.setRelativeRoi(%s, %s, %s, %s)' %
                        (int(zoom.left()), int(zoom.top()),
                         int(zoom.right()), int(zoom.bottom())))

    @pyqtSlot()
    def on_actionUnzoom_triggered(self):
        self.widget.plot().getZoomer().zoom(0)

    @pyqtSlot()
    def on_actionPrint_triggered(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setColorMode(QPrinter.Color)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFileName('')
        if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
            self.widget.plot().print_(printer)

    def on_actionCustomRange_toggled(self, on):
        self.rangeFrom.setEnabled(on)
        self.rangeTo.setEnabled(on)
        self.widget.SetAutoCountRange(not on)
        self._range_active = on
        if on:
            self.on_rangeChanged(0)
        else:
            self.updateRange()

    def on_rangeChanged(self, val):
        if self._range_active:
            self.widget.SetCountRange(self.rangeFrom.value(),
                                      self.rangeTo.value())

    def updateRange(self):
        if not self.actionCustomRange.isChecked():
            crange = self.widget.GetData2d().range()
            self.rangeFrom.setValue(crange.minValue())
            self.rangeTo.setValue(crange.maxValue())

    def closeEvent(self, event):
        with self.sgroup as settings:
            settings.setValue('geometry', self.saveGeometry())
        event.accept()
