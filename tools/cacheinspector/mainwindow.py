#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#   Pascal Neubert <pascal.neubert@frm2.tum.de>
#
# *****************************************************************************

from os import path
from os.path import join
from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMainWindow, QTreeWidgetItem, QMenu, QAction, QDialog, \
    QWidgetItem

# The pylint errors must be fixed, but later
from .dialogconnect import DialogConnect    # pylint: disable=F0401
from .windowwatcher import WindowWatcher    # pylint: disable=F0401
from .widgetkeyentry import WidgetKeyEntry  # pylint: disable=F0401
from .windowaddkey import WindowAddKey      # pylint: disable=F0401


class MainWindow(QMainWindow):

    def __init__(self, cacheclient, parent=None):
        QMainWindow.__init__(self)
        self._cacheClient = cacheclient
        self._treeitems = {}
        uic.loadUi(join(path.dirname(path.abspath(__file__)), 'ui',
                        'MainWindow.ui'), self)
        self.watcherWindow = WindowWatcher(self)
        self.contextMenuTreeCache = QMenu(self.treeCache)
        self.contextMenuTreeCache.actionAddToWatcher = QAction(
            'Add to Watcher', self.contextMenuTreeCache)
        self.contextMenuTreeCache.actionSubscribe = QAction(
            'Subscribe', self.contextMenuTreeCache)
        self.treeCache.addAction(self.contextMenuTreeCache.actionAddToWatcher)
        self.treeCache.addAction(self.contextMenuTreeCache.actionSubscribe)
        self.setupEvents()
        self.ipAddress = '127.0.0.1'
        self.port = 14869
        self.progressLoading.hide()
        self.showTimeStamp = False
        self.showTTL = False

    def setupEvents(self):
        """ Sets up all events. """
        self.actionConnect.triggered.connect(self.openConnectDialog)
        self.actionDisconnect.triggered.connect(self.closeConnection)
        self.actionRefresh.triggered.connect(self.refreshAll)
        self.actionQuit.triggered.connect(self.quit)
        self.actionAddNewKey.triggered.connect(self.addNewKey)
        self.actionSearch.triggered.connect(self.search)
        self.actionToggleTimeStamp.triggered.connect(self.toggleTimeStamp)
        self.actionToggleTTL.triggered.connect(self.toggleTTL)
        self.actionWatcher.triggered.connect(self.showWatcher)
        # self.comboFilter.editTextChanged.connect(self.updateTree)
        self.buttonSearch.clicked.connect(self.updateTree)
        self.treeCache.itemClicked.connect(self.updateView)
        self.treeCache.customContextMenuRequested.connect(self.showContextMenu)
        self.treeCache.sortByColumn(0, Qt.AscendingOrder)
        self.contextMenuTreeCache.actionAddToWatcher.triggered.connect(
            self.addKeyToWatcher)
        self.contextMenuTreeCache.actionSubscribe.triggered.connect(
            self.subscribeKey)
        self._cacheClient.signals.connected.connect(self.refreshAll)
        self._cacheClient.signals.disconnected.connect(self.refreshAll)

    def quit(self):
        """Quit the inspector."""
        self.watcherWindow.close()
        self.close()

    def openConnectDialog(self):
        """ Opens the connect dialog. """
        dlg = DialogConnect(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        self.ipAddress = dlg.valueServerAddress.text()
        self.port = int(dlg.valuePort.text())
        self._cacheClient.connect(self.ipAddress, self.port)

    def closeConnection(self):
        """ Closes the connection of the cache inspector. """
        self._cacheClient.disconnect()

    def refreshAll(self):
        """ Refreshes local data and the view. """
        self.actionConnect.setDisabled(self._cacheClient.is_connected())
        self.actionDisconnect.setEnabled(self._cacheClient.is_connected())
        self.actionRefresh.setEnabled(self._cacheClient.is_connected())
        self.updateTree()
        for item in self.treeCache.selectedItems():
            self.updateView(item, 0)

    def addNewKey(self):
        """ Adds a key using the data given via the add key window. """
        dlg = WindowAddKey(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        #timeStamp = self.addKeyWindow.dateTimeStamp.text()
        #print timeStamp
        timeStamp = ''
        ttl = dlg.valueTTL.text()
        key = dlg.valueKey.text()
        value = dlg.valueValue.text()
        self._cacheClient.put_raw(key, value, timeStamp, ttl)

    def search(self):
        pass

    def toggleTimeStamp(self):
        """
        Toggles whether or not the time stamp is shown and updates the view
        respectively.
        """
        self.showTimeStamp = not self.showTimeStamp
        for item in self.treeCache.selectedItems():
            self.updateView(item, 0)

    def toggleTTL(self):
        """
        Toggles whether or not the time to live is shown and updates the view
        respectively.
        """
        self.showTTL = not self.showTTL
        for item in self.treeCache.selectedItems():
            self.updateView(item, 0)

    def showWatcher(self):
        """ Shows the window of the watcher. """
        self.watcherWindow.show()

    def updateTree(self):
        """ Updates the elements shown in the tree. """
        self.clearCacheTree()
        filterStr = self.comboFilter.currentText() or ''
        for key in self._cacheClient.keys():
            if filterStr not in key:
                continue
            # split the key into parts
            parts = key.split('/')
            # keys without category need a node too
            if len(parts) == 1:
                parts = ['<no category>'] + parts
            # add a node to the tree for each part of the key except the last
            prefix = ''
            parent = None
            for part in parts[:-1]:
                prefix = part if not prefix else prefix + '/' + part
                node = self._treeitems.get(prefix)
                if not node:
                    node = QTreeWidgetItem()
                    node.setText(0, part)
                    node.setData(0, 32, prefix)
                    if parent:
                        parent.addChild(node)
                    else:
                        self.treeCache.addTopLevelItem(node)
                        node.setExpanded(True)
                    self._treeitems[prefix] = node
                parent = node

    def updateView(self, item, column):
        """ Updates the values shown in the right pane. """
        if not item.text(0):  # it's the hidden root item
            return
        self.clearWidgetView()
        prefix = item.data(0, 32)
        if prefix == '<no category>':
            prefix = ''
        keys = [key for key in self._cacheClient.keys()
                if key.rpartition('/')[0] == prefix]
        for key in sorted(keys):
            entry = self._cacheClient.get(key)
            widget = WidgetKeyEntry(self._cacheClient, entry,
                                    self.showTimeStamp, self.showTTL, self)
            self.layoutContent.addWidget(widget)
        self.layoutContent.addStretch()

    def showContextMenu(self, position):
        """ Shows the context menu. """
        self.contextMenuTreeCache.exec_(self.treeCache.mapToGlobal(position))

    def addKeyToWatcher(self):
        """ Adds a key to the watcher window. """
        for item in self.treeCache.selectedItems():
            widgetsEntry = ''
            for entry in self._cacheClient._db:
                if entry.find(item.text(0)[:-1]):
                    widgetsEntry = entry
            widget = WidgetKeyEntry(self._cacheClient, widgetsEntry,
                                    item.text(0), '', self.showTimeStamp,
                                    self.showTTL)
            self.watcherWindow.addWidgetKey(widget)

    def subscribeKey(self):
        """ Subscribes a key. """
        strKey = ''
        for item in self.treeCache.selectedItems():
            while item is not None:
                for i in range(self.treeCache.topLevelItemCount()):
                    if item != self.treeCache.topLevelItem(i):
                        break
                else:
                    strKey = item.text(0) + '/' + strKey
                    break
                strKey = item.text(0) + '/' + strKey
                item = item.parent()
            #self._cacheClient.addCallback()

    def clearCacheTree(self):
        """ Removes all elements in the tree. """
        self.treeCache.clear()
        self._treeitems.clear()

    def clearWidgetView(self):
        """ Removes all widgets in the right pane. """
        for i in range(self.layoutContent.count()-1, -1, -1):
            item = self.layoutContent.takeAt(i)
            if isinstance(item, QWidgetItem):
                item.widget().deleteLater()
