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

"""NICOS livewidget 2D data plot window/panel."""

import os
import time
from os import path

from PyQt4.QtGui import QPrinter, QPrintDialog, QDialog, QMenu, QToolBar, \
    QStatusBar, QSizePolicy, QListWidgetItem, QPushButton, QStyle, \
    QDialogButtonBox, QColor
from PyQt4.QtCore import Qt, QByteArray, SIGNAL, SLOT
from PyQt4.QtCore import pyqtSignature as qtsig

from nicos.clients.gui.utils import loadUi, dialogFromUi
from nicos.clients.gui.panels import Panel
from nicos.protocols.cache import cache_load
from nicos.guisupport.utils import setBackgroundColor

from nicoslivewidget import LWWidget, LWData, Logscale, MinimumMaximum, \
    Integrate, Histogram, CreateProfile

DATATYPES = frozenset(('<u4', '<i4', '>u4', '>i4', '<u2', '<i2', '>u2', '>i2',
                       'u1', 'i1', 'f8', 'f4'))


my_uipath = path.dirname(__file__)


class SANSPanel(Panel):
    panelName = 'SANS acquisition'
    bar = None
    menu = None

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'sanspanel.ui', my_uipath)

        self._format = '<u4'
        self._runtime = 0
        self._no_direct_display = False
        self._range_active = False
        self._filename = ''
        self._nx = self._ny = 128
        self._nz = 1
        self._last_data = '\x00' * 128*128*4
        self.current_status = None

        self._green = QColor('#99FF99')
        self._red = QColor('#FF9999')

        self.statusBar = QStatusBar(self)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.widget = LWWidget(self)
        self.widget.setAxisLabels('pixels x', 'pixels y')
        self.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.widget.setKeepAspect(True)
        self.widget.setControls(Logscale | MinimumMaximum | Integrate |
                                Histogram | CreateProfile)
        self.widgetLayout.addWidget(self.widget)

        self.liveitem = QListWidgetItem('<Live>', self.fileList)
        self.liveitem.setData(32, '')
        self.liveitem.setData(33, '')

        self.splitter.restoreState(self.splitterstate)

        self.connect(client, SIGNAL('livedata'), self.on_client_livedata)
        self.connect(client, SIGNAL('liveparams'), self.on_client_liveparams)
        if client.connected:
            self.on_client_connected()
        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('cache'), self.on_client_cache)

        self.connect(self.actionLogScale, SIGNAL("toggled(bool)"),
                     self.widget, SLOT("setLog10(bool)"))
        self.connect(self.widget,
                     SIGNAL('customContextMenuRequested(const QPoint&)'),
                     self.on_widget_customContextMenuRequested)
        self.connect(self.widget,
                     SIGNAL('profileUpdate(int, int, void*, void*)'),
                     self.on_widget_profileUpdate)

    def setSettings(self, settings):
        self._instrument = settings.get('instrument', '')
        self.widget.setInstrumentOption(self._instrument)

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', '', QByteArray)

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.setValue('geometry', self.saveGeometry())

    def getMenus(self):
        if not self.menu:
            menu = QMenu('&Live data', self)
            menu.addAction(self.actionPrint)
            menu.addSeparator()
            menu.addAction(self.actionSetAsROI)
            menu.addAction(self.actionUnzoom)
            menu.addAction(self.actionLogScale)
            menu.addAction(self.actionNormalized)
            menu.addAction(self.actionLegend)
            self.menu = menu
        return [self.menu]

    def getToolbars(self):
        if not self.bar:
            bar = QToolBar('Live data')
            bar.addAction(self.actionPrint)
            bar.addSeparator()
            bar.addAction(self.actionLogScale)
            bar.addSeparator()
            bar.addAction(self.actionUnzoom)
            # bar.addAction(self.actionSetAsROI)
            self.bar = bar
        return [self.bar]

    def updateStatus(self, status, exception=False):
        self.current_status = status
        if status == 'idle':
            setBackgroundColor(self.curstatus, self._green)
        else:
            setBackgroundColor(self.curstatus, self._red)

    def on_widget_customContextMenuRequested(self, point):
        self.menu.popup(self.mapToGlobal(point))

    def on_widget_profileUpdate(self, ptype, nbins, x, y):
        pass

    def on_fileList_itemClicked(self, item):
        if item is None:
            return
        fname = item.data(32)
        if fname == '':
            if self._no_direct_display:
                self._no_direct_display = False
                self.widget.setData(LWData(self._nx, self._ny, self._nz,
                                           self._format, self._last_data))
        else:
            self._no_direct_display = True
            fcontent = open(fname, 'rb').read()
            self.widget.setData(LWData(self._nx, self._ny, self._nz,
                                       self._format, fcontent))

    def on_fileList_currentItemChanged(self, item, previous):
        self.on_fileList_itemClicked(item)

    def on_client_cache(self, data):
        _time, key, _op, value = data
        if key == 'exp/action':
            self.curstatus.setText(cache_load(value) or 'Idle')

    def on_client_connected(self):
        self.fileList.clear()
        self.liveitem = QListWidgetItem('<Live>', self.fileList)
        self.liveitem.setData(32, '')
        self.liveitem.setData(33, '')

        datapath = self.client.eval('session.experiment.datapath', '')
        caspath = path.join(datapath, '2ddata')
        if path.isdir(caspath):
            for fn in sorted(os.listdir(caspath)):
                if fn.endswith('.dat'):
                    self.add_to_flist(path.join(caspath, fn), '', False)

    def on_client_liveparams(self, params):
        _tag, fname, dtype, nx, ny, nz, runtime = params
        self._runtime = runtime
        self._filename = fname
        if dtype not in DATATYPES:
            self._format = None
            self.log.warning('Unsupported live data format: %r' % params)
            return
        self._format = dtype
        self._nx = nx
        self._ny = ny
        self._nz = nz

    def on_client_livedata(self, data):
        self._last_data = data
        if not self._no_direct_display:
            self.widget.setData(
                LWData(self._nx, self._ny, self._nz, self._format, data))
        if self._filename:
            self.add_to_flist(self._filename, self._format)

    def add_to_flist(self, filename, fformat, scroll=True):
        shortname = path.basename(filename)
        item = QListWidgetItem(shortname)
        item.setData(32, filename)
        item.setData(33, fformat)
        self.fileList.insertItem(self.fileList.count()-1, item)
        if scroll:
            self.fileList.scrollToBottom()

    @qtsig('')
    def on_start_clicked(self):
        dpos = []
        for dp, cb in zip([1, 2, 5, 10, 20],
                          [self.dp1m, self.dp2m, self.dp5m, self.dp10m, self.dp20m]):
            if cb.isChecked():
                dpos.append(dp)
        if not dpos:
            self.showInfo('Select at least one detector position!')
            return
        ctime = self.ctime.value()
        coll = self.coll10.isChecked() and '10m' or \
            (self.coll15.isChecked() and '15m' or '20m')
        code = 'maw(coll, %r)\nscan(det_pos1, [%s], det, t=%.1f)\n' % \
            (coll, ', '.join(str(x) for x in dpos), ctime)
        self.execScript(code)

    @qtsig('')
    def on_actionUnzoom_triggered(self):
        self.widget.plot().getZoomer().zoom(0)

    @qtsig('')
    def on_actionPrint_triggered(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setColorMode(QPrinter.Color)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFileName('')
        if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
            self.widget.plot().print_(printer)

    def execScript(self, script):
        action = 'queue'
        if self.current_status != 'idle':
            qwindow = dialogFromUi(self, 'question.ui', 'panels')
            qwindow.questionText.setText('A script is currently running.  What '
                                         'do you want to do?')
            icon = qwindow.style().standardIcon
            qwindow.iconLabel.setPixmap(
                icon(QStyle.SP_MessageBoxQuestion).pixmap(32, 32))
            b0 = QPushButton(icon(QStyle.SP_DialogCancelButton), 'Cancel')
            b1 = QPushButton(icon(QStyle.SP_DialogOkButton), 'Queue script')
            b2 = QPushButton(icon(QStyle.SP_MessageBoxWarning), 'Execute now!')
            qwindow.buttonBox.addButton(b0, QDialogButtonBox.ApplyRole)
            qwindow.buttonBox.addButton(b1, QDialogButtonBox.ApplyRole)
            qwindow.buttonBox.addButton(b2, QDialogButtonBox.ApplyRole)
            qwindow.buttonBox.setFocus()
            result = [0]
            def pushed(btn):
                if btn is b1:
                    result[0] = 1
                elif btn is b2:
                    result[0] = 2
                qwindow.accept()
            self.connect(qwindow.buttonBox, SIGNAL('clicked(QAbstractButton*)'),
                         pushed)
            qwindow.exec_()
            if result[0] == 0:
                return
            elif result[0] == 2:
                action = 'execute'
        if action == 'queue':
            self.client.run(script)
            self.mainwindow.action_start_time = time.time()
        else:
            self.client.tell('exec', script)
