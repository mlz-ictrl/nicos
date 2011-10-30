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

"""NICOS GUI application package."""

__version__ = "$Revision$"

from PyQt4.QtCore import Qt, QVariant, SIGNAL, pyqtSignature as qtsig
from PyQt4.QtGui import QWidget, QMainWindow, QSplitter, QFont, QColor, \
     QFontDialog, QColorDialog

from nicos.gui.utils import DlgUtils, SettingGroup, loadUi, importString
from nicos.gui.config import hsplit, vsplit, panel


class AuxiliaryWindow(QMainWindow):

    def __init__(self, parent, type, config, profile):
        QMainWindow.__init__(self, parent)
        loadUi(self, 'auxwindow.ui')
        self.mainwindow = parent
        self.client = parent.client
        self.curprofile = profile

        self.type = type
        self.panels = []
        self.splitters = []

        self.sgroup = SettingGroup(config[0] + '-' + profile)
        with self.sgroup as settings:
            geometry = settings.value('geometry').toByteArray()
            self.restoreGeometry(geometry)
            windowstate = settings.value('windowstate').toByteArray()
            self.restoreState(windowstate)
            self.splitstate = settings.value('splitstate').toList()
            self.user_font = QFont(settings.value('font'))
            color = QColor(settings.value('color'))
            if color.isValid():
                self.user_color = color
            else:
                self.user_color = QColor(Qt.white)

        createWindowItem(config[3], self, self.centralLayout)
        self.setWindowTitle(config[0])

        if len(self.splitstate) == len(self.splitters):
            for sp, st in zip(self.splitters, self.splitstate):
                sp.restoreState(st.toByteArray())

    def closeEvent(self, event):
        for pnl in self.panels:
            if not pnl.requestClose():
                event.ignore()
                return
        with self.sgroup as settings:
            settings.setValue('geometry', QVariant(self.saveGeometry()))
            settings.setValue('windowstate', QVariant(self.saveState()))
            settings.setValue('splitstate',
                              QVariant([sp.saveState() for sp in self.splitters]))
            settings.setValue('font', QVariant(self.user_font))
            settings.setValue('color', QVariant(self.user_color))
        for pnl in self.panels:
            with pnl.sgroup as settings:
                pnl.saveSettings(settings)
        event.accept()
        self.emit(SIGNAL('closed'), self)

    @qtsig('')
    def on_actionFont_triggered(self):
        font, ok = QFontDialog.getFont(self.user_font, self)
        if not ok:
            return
        for pnl in self.panels:
            pnl.setCustomStyle(font, self.user_color)
        self.user_font = font

    @qtsig('')
    def on_actionColor_triggered(self):
        color = QColorDialog.getColor(self.user_color, self)
        if not color.isValid():
            return
        for pnl in self.panels:
            pnl.setCustomStyle(self.user_font, color)
        self.user_color = color


class Panel(QWidget, DlgUtils):
    panelName = ''
    subpanels = 0

    def __init__(self, parent, client):
        QWidget.__init__(self, parent)
        DlgUtils.__init__(self, self.panelName)
        self.parentwindow = parent
        self.client = client
        self.mainwindow = parent.mainwindow
        self.sgroup = SettingGroup(self.panelName + '-' + parent.curprofile)
        with self.sgroup as settings:
            self.loadSettings(settings)

    def loadSettings(self, settings):
        pass

    def saveSettings(self, settings):
        pass

    def setCustomStyle(self, font, back):
        pass

    def getToolbars(self):
        return []

    def getMenus(self):
        return []

    def requestClose(self):
        return True

    def updateStatus(self, status, exception=False):
        pass


def createWindowItem(item, window, container):
    if isinstance(item, panel):
        cls = importString(item[0])
        p = cls(window, window.client)
        window.panels.append(p)
        for toolbar in p.getToolbars():
            # this helps for serializing window state
            toolbar.setObjectName(toolbar.windowTitle())
            if hasattr(window, 'toolBarWindows'):
                window.insertToolBar(window.toolBarWindows, toolbar)
            else:
                window.addToolBar(toolbar)
        for menu in p.getMenus():
            if hasattr(window, 'menuWindows'):
                window.menuBar().insertMenu(window.menuWindows.menuAction(), menu)
            else:
                window.menuBar().addMenu(menu)
        p.setCustomStyle(window.user_font, window.user_color)
        container.addWidget(p)
    elif isinstance(item, hsplit):
        sp = QSplitter(Qt.Horizontal)
        window.splitters.append(sp)
        for subitem in item:
            createWindowItem(subitem, window, sp)
        container.addWidget(sp)
    elif isinstance(item, vsplit):
        sp = QSplitter(Qt.Vertical)
        window.splitters.append(sp)
        for subitem in item:
            createWindowItem(subitem, window, sp)
        container.addWidget(sp)
