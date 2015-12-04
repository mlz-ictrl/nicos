#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""Support for "auxiliary" windows containing panels."""

from PyQt4.QtGui import QWidget, QMainWindow, QSplitter, QFontDialog, \
    QColorDialog, QVBoxLayout
from PyQt4.QtCore import pyqtSlot, pyqtSignal

from nicos.utils.loggers import NicosLogger
from nicos.clients.gui.utils import SettingGroup, loadUi, \
    loadBasicWindowSettings, loadUserStyle

from nicos.clients.gui.panels.base import Panel, SetupDepWindowMixin


class AuxiliaryWindow(SetupDepWindowMixin, QMainWindow):

    closed = pyqtSignal('QMainWindow')

    def __init__(self, parent, wintype, config):
        from nicos.clients.gui.panels.utils import createWindowItem
        QMainWindow.__init__(self, parent)
        loadUi(self, 'auxwindow.ui')
        self.mainwindow = parent
        self.client = parent.client
        self.log = NicosLogger('AuxiliaryWindow')
        self.log.parent = self.mainwindow.log

        self.type = wintype
        self.panels = []
        self.splitters = []

        self.sgroup = SettingGroup(config.name)
        with self.sgroup as settings:
            loadUserStyle(self, settings)

        self.setWindowTitle(config.name)
        widget = createWindowItem(config.contents, self, self, self, self.log)
        if widget:
            self.centralLayout.addWidget(widget)
        self.centralLayout.setContentsMargins(6, 6, 6, 6)

        with self.sgroup as settings:
            loadBasicWindowSettings(self, settings)

        if len(self.splitstate) == len(self.splitters):
            for sp, st in zip(self.splitters, self.splitstate):
                sp.restoreState(st)

        SetupDepWindowMixin.__init__(self, self.client)

    def getPanel(self, panelName):
        for panelobj in self.panels:
            if panelobj.panelName == panelName:
                return panelobj

    def saveWindowLayout(self):
        with self.sgroup as settings:
            settings.setValue('geometry', self.saveGeometry())
            settings.setValue('windowstate', self.saveState())
            settings.setValue('splitstate',
                              [sp.saveState() for sp in self.splitters])
            settings.setValue('font', self.user_font)
            settings.setValue('color', self.user_color)

    def closeEvent(self, event):
        for pnl in self.panels:
            if not pnl.requestClose():
                event.ignore()
                return
        if self.mainwindow.autosavelayout:
            self.saveWindowLayout()
        for pnl in self.panels:
            with pnl.sgroup as settings:
                pnl.saveSettings(settings)
        event.accept()
        self.closed.emit(self)
        del self.panels[:]  # this is necessary to get the Qt objects destroyed

    @pyqtSlot()
    def on_actionFont_triggered(self):
        font, ok = QFontDialog.getFont(self.user_font, self)
        if not ok:
            return
        for pnl in self.panels:
            pnl.setCustomStyle(font, self.user_color)
        self.user_font = font

    @pyqtSlot()
    def on_actionColor_triggered(self):
        color = QColorDialog.getColor(self.user_color, self)
        if not color.isValid():
            return
        for pnl in self.panels:
            pnl.setCustomStyle(self.user_font, color)
        self.user_color = color


class AuxiliarySubWindow(QMainWindow):
    def __init__(self, item, window, menuwindow, parent):
        from nicos.clients.gui.panels.utils import createWindowItem
        QMainWindow.__init__(self, parent)
        # self.mainwindow = parent
        self.user_color = window.user_color
        self.mainwindow = window.mainwindow
        self.log = NicosLogger('AuxiliarySubWindow')
        self.log.parent = self.mainwindow.log

        self.panels = []

        # we have to nest one step to get consistent layout spacing
        # around the central widget
        central = QWidget(self)
        layout = QVBoxLayout()
        # only keep margin at the top (below the tabs)
        layout.setContentsMargins(0, 6, 0, 0)
        if len(item) == 2:
            (title, subitem, setupSpec) = item + (None,)
        else:
            (title, subitem, setupSpec) = item
        it = createWindowItem(subitem, window, menuwindow, self, self.log)
        if it:
            if isinstance(it, (Panel, QSplitter,)):
                if isinstance(it, Panel):
                    it.hideTitle()
                # if tab has its own setups overwrite panels setups
                if setupSpec:
                    it.setSetups(setupSpec)
                it.setWidgetVisible.connect(parent.setWidgetVisible)
            layout.addWidget(it)
            central.setLayout(layout)
            self.setCentralWidget(central)
            parent.addPanel(self, title)

    def getPanel(self, panelName):
        for panelobj in self.panels:
            if panelobj.panelName == panelName:
                return panelobj
