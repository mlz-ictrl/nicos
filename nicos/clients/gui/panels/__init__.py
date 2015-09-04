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

from time import time as currenttime

from PyQt4.QtGui import QWidget, QMainWindow, QSplitter, QFontDialog, \
    QColorDialog, QHBoxLayout, QVBoxLayout, QDockWidget, QDialog, QPalette, \
    QTabWidget
from PyQt4.QtCore import Qt, QObject, pyqtSlot, pyqtSignal

from nicos.clients.gui.panels.tabwidget import TearOffTabWidget

from nicos.utils import importString
from nicos.utils.loggers import NicosLogger
from nicos.clients.gui.utils import DlgUtils, SettingGroup, loadUi, \
    loadBasicWindowSettings, loadUserStyle
from nicos.clients.gui.config import hsplit, vsplit, tabbed, panel, docked
from nicos.guisupport.utils import checkSetupSpec


class AuxiliaryWindow(QMainWindow):

    closed = pyqtSignal('QMainWindow')

    def __init__(self, parent, wintype, config):
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
        widget = createWindowItem(config.contents, self, self, self)
        self.centralLayout.addWidget(widget)
        self.centralLayout.setContentsMargins(6, 6, 6, 6)

        with self.sgroup as settings:
            loadBasicWindowSettings(self, settings)

        if len(self.splitstate) == len(self.splitters):
            for sp, st in zip(self.splitters, self.splitstate):
                sp.restoreState(st)

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


class PanelDialog(QDialog):
    def __init__(self, parent, client, panelcfg, title):
        self.panels = []
        QDialog.__init__(self, parent)
        self.mainwindow = parent.mainwindow
        self.client = client
        self.user_color = self.palette().color(QPalette.Base)
        self.user_font = self.font()
        if isinstance(panelcfg, type) and issubclass(panelcfg, Panel):
            panelcfg = panel('%s.%s' % (panelcfg.__module__,
                                        panelcfg.__name__))
        elif isinstance(panelcfg, str):
            panelcfg = panel(panelcfg)
        pnl = createWindowItem(panelcfg, self, self, self.mainwindow)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(pnl)
        self.setLayout(hbox)
        self.setWindowTitle(title)

        if self.client._reg_keys:
            values = self.client.ask('getcachekeys',
                                     ','.join(self.client._reg_keys))
            if values is not None:
                for key, value in values:
                    if key in self.client._reg_keys and \
                       key == 'session/mastersetup':
                        for widget in self.client._reg_keys[key]:
                            if widget():
                                widget().on_keyChange(key, value,
                                                      currenttime(), False)


class SetupDepGuiMixin(QObject):
    ''' Mixin to handle setup-dependent visibility

    Note: You must explicity add the following class attribute in all
    classes using this mixin (A PyQt resctriction, see
    https://riverbankcomputing.com/pipermail/pyqt/2013-September/033199.html):

    `setWidgetVisible = SetupDepGuiMixin.setWidgetVisible`

    '''
    setupSpec = ()
    setWidgetVisible = pyqtSignal(QWidget, bool, name='setWidgetVisible')

    def __init__(self, client):
        client.register(self, 'session/mastersetup')

    def setOptions(self, options):
        setups = options.get('setups', ())
        if isinstance(setups, str):
            setups = (setups,)
        self.setSetups(list(setups))

    def setSetups(self, setupSpec):
        self.setupSpec = setupSpec
        self.log.debug('Setups are : %r' % self.setupSpec)

    def on_keyChange(self, key, value, time, expired):
        if key == 'session/mastersetup' and self.setupSpec:
            enabled = checkSetupSpec(self.setupSpec, value, log=self.log)
            if hasattr(self, 'setWidgetVisible'):
                self.setWidgetVisible.emit(self, enabled)


class Panel(QWidget, SetupDepGuiMixin, DlgUtils):
    panelName = ''

    setWidgetVisible = SetupDepGuiMixin.setWidgetVisible

    def __init__(self, parent, client):
        QWidget.__init__(self, parent)
        self.log = NicosLogger(self.panelName)
        SetupDepGuiMixin.__init__(self, client)
        DlgUtils.__init__(self, self.panelName)
        self.parentwindow = parent
        self.client = client
        self.mainwindow = parent.mainwindow
        self.actions = set()
        self.log.parent = self.mainwindow.log
        self.sgroup = SettingGroup(self.panelName)
        with self.sgroup as settings:
            self.loadSettings(settings)

    def postInit(self):
        """This method can be implemented to perform actions after all panels
        has been instantiated. It will be automatically called after all panels
        has been created. This can be useful e.g. for accessing other panels
        using their unique ``panelName``.

        """

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


class Splitter(QSplitter, SetupDepGuiMixin):
    setWidgetVisible = SetupDepGuiMixin.setWidgetVisible

    def __init__(self, item, window, menuwindow, topwindow, parent=None):
        QSplitter.__init__(self, parent)
        window.splitters.append(self)
        self.log = NicosLogger('Splitter')
        self.log.parent = topwindow.log
        SetupDepGuiMixin.__init__(self, window.client)
        self.setOptions(item.options)
        for subitem in item.children:
            sub = createWindowItem(subitem, window, menuwindow, topwindow)
            self.addWidget(sub)


class VerticalSplitter(Splitter):

    def __init__(self, item, window, menuwindow, topwindow, parent=None):
        Splitter.__init__(self, item, window, menuwindow, topwindow, parent)
        self.setOrientation(Qt.Vertical)


class HorizontalSplitter(Splitter):

    def __init__(self, item, window, menuwindow, topwindow, parent=None):
        Splitter.__init__(self, item, window, menuwindow, topwindow, parent)
        self.setOrientation(Qt.Horizontal)


def createPanel(item, window, menuwindow, topwindow):
    prefixes = ('nicos.clients.gui.panels.',)
    cls = importString(item.clsname, prefixes=prefixes)
    p = cls(menuwindow, window.client)
    p.setOptions(item.options)
    window.panels.append(p)
    if p not in topwindow.panels:
        topwindow.panels.append(p)

    for toolbar in p.getToolbars():
        # this helps for serializing window state
        toolbar.setObjectName(toolbar.windowTitle())
        if hasattr(menuwindow, 'toolBarWindows'):
            menuwindow.insertToolBar(menuwindow.toolBarWindows, toolbar)
        else:
            menuwindow.addToolBar(toolbar)
    for menu in p.getMenus():
        if hasattr(menuwindow, 'menuWindows'):
            p.actions.update((menuwindow.menuBar().insertMenu(
                              menuwindow.menuWindows.menuAction(),
                              menu),))
        else:
            p.actions.update((menuwindow.menuBar().addMenu(menu),))

    p.setCustomStyle(window.user_font, window.user_color)
    return p


def createVerticalSplitter(item, window, menuwindow, topwindow):
    return VerticalSplitter(item, window, menuwindow, topwindow)


def createHorizontalSplitter(item, window, menuwindow, topwindow):
    return HorizontalSplitter(item, window, menuwindow, topwindow)


def createDockedWidget(item, window, menuwindow, topwindow):
    dockPosMap = {'left':   Qt.LeftDockWidgetArea,
                  'right':  Qt.RightDockWidgetArea,
                  'top':    Qt.TopDockWidgetArea,
                  'bottom': Qt.BottomDockWidgetArea}

    mainitem, dockitems = item
    main = createWindowItem(mainitem, window, menuwindow, topwindow)
    for title, item in dockitems:
        dw = QDockWidget(title, window)
        # prevent closing the dock widget
        dw.setFeatures(QDockWidget.DockWidgetMovable |
                       QDockWidget.DockWidgetFloatable)
        # make the dock title bold
        dw.setStyleSheet('QDockWidget { font-weight: bold; }')
        dw.setObjectName(title)
        sub = createWindowItem(item, window, menuwindow, topwindow)
        if isinstance(sub, Panel):
            sub.hideTitle()
        dw.setWidget(sub)
        dw.setContentsMargins(6, 6, 6, 6)
        dockPos = item.options.get('dockpos', 'left')
        if dockPos not in dockPosMap:
            menuwindow.log.warn('Illegal dockpos specification %s for panel %r'
                                % (dockPos, title))
            dockPos = 'left'
        menuwindow.addDockWidget(dockPosMap[dockPos], dw)
    return main


class AuxiliarySubWindow(QMainWindow):
    def __init__(self, item, window, menuwindow, parent):
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
        it = createWindowItem(subitem, window, menuwindow, self)
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


def createTabWidget(item, window, menuwindow, topwindow):
    tw = TearOffTabWidget(menuwindow)
    for entry in item:
        _ = AuxiliarySubWindow(entry, window, menuwindow, tw)
    return tw


def createWindowItem(item, window, menuwindow, topwindow):

    if isinstance(item, panel):
        return createPanel(item, window, menuwindow, topwindow)
    elif isinstance(item, hsplit):
        return createHorizontalSplitter(item, window, menuwindow, topwindow)
    elif isinstance(item, vsplit):
        return createVerticalSplitter(item, window, menuwindow, topwindow)
    elif isinstance(item, tabbed):
        return createTabWidget(item, window, menuwindow, topwindow)
    elif isinstance(item, docked):
        return createDockedWidget(item, window, menuwindow, topwindow)


def showPanel(panel):
    """Ensure that the given panel is visible in its window."""
    widget = panel
    parents = []
    while 1:
        parent = widget.parent()
        if parent is None:
            # reached toplevel!
            break
        elif isinstance(parent, QTabWidget):
            # tab widget: select tab (it is wrapped in a QStackedWidget)
            index = parent.indexOf(parents[-2])
            parent.setCurrentIndex(index)
        elif isinstance(parent, QSplitter):
            # splitter: make sure the widget is not collapsed
            index = parent.indexOf(widget)
            sizes = parent.sizes()
            if sizes[index] == 0:
                sizes[index] = sum(sizes)
                parent.setSizes(sizes)
        parents.append(parent)
        widget = parent
    panel.activateWindow()


def findTab(tab, w):
    widget = w
    while True:
        parent = widget.parent()
        if not parent:
            return False
        widget = parent
        if isinstance(widget, AuxiliarySubWindow) and tab == widget:
            return True
    return False


def findTabIndex(tabwidget, w):
    for i in range(len(tabwidget)):
        if findTab(tabwidget.widget(i), w):
            return i
    return None
