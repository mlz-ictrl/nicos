#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""Support for "auxiliary" windows containing panels."""

import time

from PyQt4.QtGui import QWidget, QMainWindow, QSplitter, QFontDialog, \
     QColorDialog, QVBoxLayout, QDockWidget, QDialogButtonBox, QScrollArea
from PyQt4.QtCore import Qt, QVariant, SIGNAL, pyqtSignature as qtsig

from nicos.clients.gui.panels.tabwidget import TearOffTabWidget, DetachedWindow

from nicos.utils import importString
from nicos.utils.loggers import NicosLogger
from nicos.clients.gui.utils import DlgUtils, SettingGroup, loadUi, \
    loadBasicWindowSettings, loadUserStyle, checkSetupSpec
from nicos.clients.gui.config import hsplit, vsplit, tabbed, panel, docked


class AuxiliaryWindow(QMainWindow):

    def __init__(self, parent, wintype, config):
        QMainWindow.__init__(self, parent)
        loadUi(self, 'auxwindow.ui')
        self.mainwindow = parent
        self.client = parent.client

        self.type = wintype
        self.panels = []
        self.splitters = []

        self.sgroup = SettingGroup(config.name)
        with self.sgroup as settings:
            loadUserStyle(self, settings)

        self.setWindowTitle(config.name)
        widget = createWindowItem(config.contents, self, self)
        self.centralLayout.addWidget(widget)
        self.centralLayout.setContentsMargins(0, 0, 0, 0)

        with self.sgroup as settings:
            loadBasicWindowSettings(self, settings)

        if len(self.splitstate) == len(self.splitters):
            for sp, st in zip(self.splitters, self.splitstate):
                sp.restoreState(st.toByteArray())

    def getPanel(self, panelName):
        for panelobj in self.panels:
            if panelobj.panelName == panelName:
                return panelobj

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
        del self.panels[:]  # this is necessary to get the Qt objects destroyed

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

    def __init__(self, parent, client):
        QWidget.__init__(self, parent)
        DlgUtils.__init__(self, self.panelName)
        self.parentwindow = parent
        self.client = client
        self.mainwindow = parent.mainwindow
        self.log = NicosLogger(self.panelName)
        self.log.parent = self.mainwindow.log
        self.sgroup = SettingGroup(self.panelName)
        with self.sgroup as settings:
            self.loadSettings(settings)

    def setOptions(self, options):
        pass

    def setExpertMode(self, expert):
        pass

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

    def hideTitle(self):
        """Called when the panel is shown in a dock or tab widget, which
        provides its own place for the panel title.

        If the panel has a title widget, it should hide it in this method.
        """
        pass

    def requestClose(self):
        return True

    def updateStatus(self, status, exception=False):
        pass


class CustomPanel(Panel, DlgUtils):
    """Base class for custom instrument specific panels

    without any buttons or fancy stuff...
    """
    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        DlgUtils.__init__(self, self.panelName)

        # we just provide a scrollArea, whose content must be set later with
        # self.scrollArea.setWidget(QWidget)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        # make a vertical layout for 'ourself'
        self.vBoxLayout = QVBoxLayout(self)

        # first 'line' is the normally used content (may be the only one !)
        self.vBoxLayout.addWidget(self.scrollArea)


class CustomButtonPanel(CustomPanel):
    """Base class for custom instrument specific panels

    with a QDialogButtonBox at the lower right and some glue magic for
    fancy stuff...
    """
    def __init__(self, parent, client,
                 buttons=QDialogButtonBox.Close|QDialogButtonBox.Apply):
        CustomPanel.__init__(self, parent, client)

        # make a buttonBox
        self.buttonBox = QDialogButtonBox(buttons, parent=self)
        self.buttonBox.setObjectName('buttonBox')

        # put buttonBox below main content
        self.vBoxLayout.addWidget(self.buttonBox)

        allButtons = 'Ok Open Save Cancel Close Discard Apply Reset '\
                     'RestoreDefaults Help SaveAll Yes YesToAll No NoToAll '\
                     'Abort Retry Ignore'.split()
        for n in allButtons:
            b = self.buttonBox.button(getattr(QDialogButtonBox, n))
            if b:
                m = getattr(self, 'on_buttonBox_%s_clicked' % n, None)
                if not m:
                    m = lambda self = self, n = n: self.showError(
                                'on_buttonBox_%s_clicked not implemented!' % n)
                self.connect(b, SIGNAL('clicked()'), m)

    def panelState(self):
        """returns current window state as obtained from the stack of parents"""
        obj = self
        while hasattr(obj, 'parent'):
            if isinstance(obj, AuxiliaryWindow):
                return "tab"
            elif isinstance(obj, DetachedWindow):
                return "detached"
            obj = obj.parent()
        return "main"

    def on_buttonBox_Close_clicked(self):
        """close the right instance"""
        # traverse stack of Widgets and close the right ones...
        obj = self
        tw = None
        while hasattr(obj, 'parent'):
            obj = obj.parent()
            if isinstance(obj, DetachedWindow):
                obj.close()
                return
            elif isinstance(obj, TearOffTabWidget):
                tw = obj
            elif isinstance(obj, AuxiliaryWindow):
                obj.close()
                return
        # no window closing, use the tab left of us (if available) or the leftmost
        if not(tw):
            self.showInfo('This button does not work in the current configuration.')
            return
        idx = tw.currentIndex()
        if idx + 1 < tw.count():
            tw.setCurrentIndex(idx + 1)
        elif idx > 0:
            tw.setCurrentIndex(idx - 1)
        else:
            tw.setCurrentIndex(0)

    def on_buttonBox_Ok_clicked(self):
        """OK = Apply + Close"""
        if hasattr(self, 'on_buttonBox_Apply_clicked'):
            self.on_buttonBox_Apply_clicked()
        self.on_buttonBox_Close_clicked()


def createWindowItem(item, window, menuwindow):
    dockPosMap = {'left':   Qt.LeftDockWidgetArea,
                  'right':  Qt.RightDockWidgetArea,
                  'top':    Qt.TopDockWidgetArea,
                  'bottom': Qt.BottomDockWidgetArea}
    prefixes = ('nicos.clients.gui.panels.',)

    if isinstance(item, panel):
        cls = importString(item.clsname, prefixes=prefixes)
        p = cls(menuwindow, window.client)
        p.setOptions(item.options)
        window.panels.append(p)
        for toolbar in p.getToolbars():
            # this helps for serializing window state
            toolbar.setObjectName(toolbar.windowTitle())
            if hasattr(menuwindow, 'toolBarWindows'):
                menuwindow.insertToolBar(menuwindow.toolBarWindows, toolbar)
            else:
                menuwindow.addToolBar(toolbar)
        for menu in p.getMenus():
            if hasattr(menuwindow, 'menuWindows'):
                menuwindow.menuBar().insertMenu(
                    menuwindow.menuWindows.menuAction(), menu)
            else:
                menuwindow.menuBar().addMenu(menu)
        p.setCustomStyle(window.user_font, window.user_color)
        return p
    elif isinstance(item, hsplit):
        sp = QSplitter(Qt.Horizontal)
        window.splitters.append(sp)
        for subitem in item:
            sub = createWindowItem(subitem, window, menuwindow)
            sp.addWidget(sub)
        return sp
    elif isinstance(item, vsplit):
        sp = QSplitter(Qt.Vertical)
        window.splitters.append(sp)
        for subitem in item:
            sub = createWindowItem(subitem, window, menuwindow)
            sp.addWidget(sub)
        return sp
    elif isinstance(item, tabbed):
        tw = TearOffTabWidget()
        for _ in range(5):
            loaded_setups = window.client.eval('session.loaded_setups', [])
            if loaded_setups: # sometimes the first request returns nothing useful..???
                break
            time.sleep(0.1) # UGLY: a local, synchronized copy would be more elegant...
        for entry in item:
            if len(entry) == 2:
                (title, subitem) = entry
            else:
                (title, subitem, setupSpec) = entry
                if not checkSetupSpec(setupSpec, loaded_setups):
                    continue
            subwindow = QMainWindow(tw)
            subwindow.mainwindow = window.mainwindow
            subwindow.user_color = window.user_color
            # we have to nest one step to get consistent layout spacing
            # around the central widget
            central = QWidget(subwindow)
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            item = createWindowItem(subitem, window, subwindow)
            if isinstance(item, Panel):
                item.hideTitle()
            layout.addWidget(item)
            central.setLayout(layout)
            subwindow.setCentralWidget(central)
            tw.addTab(subwindow, title)
        return tw
    elif isinstance(item, docked):
        mainitem, dockitems = item
        main = createWindowItem(mainitem, window, menuwindow)
        for title, item in dockitems:
            dw = QDockWidget(title, window)
            # prevent closing the dock widget
            dw.setFeatures(QDockWidget.DockWidgetMovable |
                           QDockWidget.DockWidgetFloatable)
            # make the dock title bold
            dw.setStyleSheet('QDockWidget { font-weight: bold; }')
            dw.setObjectName(title)
            sub = createWindowItem(item, window, menuwindow)
            if isinstance(sub, Panel):
                sub.hideTitle()
            dw.setWidget(sub)
            dw.setContentsMargins(5, 5, 5, 5)
            dockPos = item.options.get('dockpos', 'left')
            if dockPos not in dockPosMap:
                menuwindow.log.warn('Illegal dockpos specification %s for '
                                    'panel %r' % (dockPos, title))
                dockPos = 'left'
            menuwindow.addDockWidget(dockPosMap[dockPos], dw)
        return main
