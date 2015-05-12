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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************

from os import path
import os

from PyQt4.QtGui import QTreeWidgetItem, QMenu, QIcon, \
    QInputDialog, QMessageBox
from PyQt4.QtCore import pyqtSignal, Qt

from setupfiletool.utilities.treewidgetcontextmenu import TreeWidgetContextMenu
from setupfiletool.utilities.utilities import ItemTypes, getNicosDir, getResDir
from setupfiletool.setup import Setup
from setupfiletool.devicewidget import DeviceWidget


class TreeWidget(TreeWidgetContextMenu):
    editedSetup = pyqtSignal()
    deviceRemoved = pyqtSignal(str, str)

    def __init__(self, parent=None):
        TreeWidgetContextMenu.__init__(self, parent)
        self.markedSetups = []
        self.manualDirectory = None
        self.showManualDirectoryBool = False
        self.holdingItem = False

        # don't allow dropping items in root
        root = self.invisibleRootItem()
        root.setFlags(root.flags() & ~Qt.ItemIsDropEnabled)

    def loadNicosData(self):
        while self.topLevelItemCount() > 0:
            self.takeTopLevelItem(0)
        # root directory containing all the setups or subdirs with setups.
        setupRoot = path.join(getNicosDir(), 'custom')

        # list of directories in */nicos-core/custom/
        setupDirectories = []
        for item in os.listdir(setupRoot):
            if path.isdir(path.join(setupRoot, item)):
                setupDirectories.append(item)

        # list of topLevelItems representing the directories in
        # */nicos-core/custom: for example instruments, ...
        self.topLevelItems = []
        for directory in sorted(setupDirectories):
            self.topLevelItems.append(
                QTreeWidgetItem([directory,
                                 'nicos-core/custom'], ItemTypes.Directory))
        self.addTopLevelItems(self.topLevelItems)

        # all these directories (may) have setups, find all of them and add
        # them as children, after that, add all their devices as children
        for item in self.topLevelItems:
            # directories can neither be dragged nor have something dropped on
            item.setFlags(item.flags() & ~Qt.ItemIsDragEnabled &
                          ~Qt.ItemIsDropEnabled)
            item.setIcon(0, QIcon(path.join(getResDir(), 'folder.png')))
            scriptList = [[]]  # list of rows, a row = list of strings
            if path.isdir(path.join(setupRoot, item.text(0), 'setups')):
                self.getSetupsForDir(path.join(setupRoot, item.text(0)),
                                     'setups', scriptList)
                for script in sorted(scriptList):
                    if script:
                        scriptItem = QTreeWidgetItem(script, ItemTypes.Setup)
                        # scripts cannot be dragged, but they can have
                        # something dropped on them (a device).
                        scriptItem.setFlags(scriptItem.flags() &
                                            ~Qt.ItemIsDragEnabled)
                        item.addChild(scriptItem)

            # setup for this directory has been loaded, add the devices.
            currentIndex = 0
            while currentIndex < item.childCount():
                currentPath = item.child(currentIndex).text(1)
                devices = Setup.getDeviceNamesOfSetup(currentPath, self.log)
                for device in devices:
                    # read setup and add all the devices as child tree items
                    deviceItem = QTreeWidgetItem([device,
                                                  'in file: ' +
                                                  item.child(
                                                      currentIndex).text(0)],
                                                 ItemTypes.Device)
                    # devices can be dragged, but they can't have something
                    # dropped on them.
                    deviceItem.setFlags(deviceItem.flags() &
                                        ~Qt.ItemIsDropEnabled)
                    item.child(currentIndex).addChild(deviceItem)
                item.child(currentIndex).setIcon(0, QIcon(
                    path.join(getResDir(), 'setup.png')))

                # icons for all devices
                deviceIndex = 0
                while deviceIndex < item.child(currentIndex).childCount():
                    item.child(currentIndex).child(deviceIndex).setIcon(
                        0, QIcon(path.join(getResDir(), 'device.png')))
                    deviceIndex += 1
                currentIndex += 1

        if self.showManualDirectoryBool:
            self.showManualDirectory()
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)

    def dragEnterEvent(self, event):
        # dragEnterEvent may occur while user still drags an item
        if self.holdingItem:
            TreeWidgetContextMenu.dragEnterEvent(self, event)
            return

        self.origin = self.currentItem()
        self.holdingItem = True
        TreeWidgetContextMenu.dragEnterEvent(self, event)

    def dropEvent(self, event):
        target = self.getSetupOfDropPos(event.pos())
        if target != self.origin.parent():
            childIndex = 0
            deviceItems = []
            while childIndex < target.childCount():
                deviceItems.append(target.child(childIndex).text(0))
                childIndex += 1

            if self.origin.text(0) in deviceItems:
                QMessageBox.warning(self,
                                    'Error',
                                    'The target setup already contains'
                                    'a device with that name!')
                self.holdingItem = False
                self.origin = None
                return
            device = self.currentItem()
            MainWindow = self.parent().parent().parent()

            MainWindow.loadSetup(self.origin.parent().text(1))
            MainWindow.loadSetup(target.text(1))

            newWidget = DeviceWidget()
            newWidget.editedDevice.connect(MainWindow.editedSetupSlot)
            newWidget.loadDevice(Setup.getDeviceOfSetup(
                self.origin.parent().text(1), device.text(0), self.log))
            MainWindow.workarea.addWidget(newWidget)
            MainWindow.deviceWidgets[
                target.text(1)][device.text(0)] = newWidget

            self.markItem(self.origin.parent())
            self.markItem(target)

        self.holdingItem = False
        self.origin = None
        TreeWidgetContextMenu.dropEvent(self, event)

    def getSetupOfDropPos(self, pos):
        # pos is event.pos() when dropping a device
        if self.itemAt(pos).type() == ItemTypes.Device:
            # dropped inside of the setup's device list
            return self.itemAt(pos).parent()
        else:
            # dropped on the setup itself
            return self.itemAt(pos)

    def setInstrumentMode(self):
        instrument = self.sender().text()
        self.setSingleInstrument(instrument)

    def setSingleInstrument(self, instrument):
        for directory in self.topLevelItems:
            directory.setHidden(not directory.text(0) == instrument)

    def setAllInstrumentsVisible(self):
        for directory in self.topLevelItems:
            directory.setHidden(False)

    def showManualDirectory(self):
        self.showManualDirectoryBool = True
        if self.manualDirectory is None:
            self.manualDirectory = QTreeWidgetItem(
                ['-manual-', '-'],
                ItemTypes.ManualDirectory)
            self.manualDirectory.setIcon(0, QIcon(path.join(getResDir(),
                                                            'folder.png')))
            self.manualDirectory.setFlags(self.manualDirectory.flags(
                ) & ~Qt.ItemIsDragEnabled &
                    ~Qt.ItemIsDropEnabled)
        self.addTopLevelItem(self.manualDirectory)

    def addManualFile(self, pathToFile):
        _, filename = path.split(pathToFile)
        manualSetup = QTreeWidgetItem([filename, pathToFile], ItemTypes.Setup)
        manualSetup.setIcon(0, QIcon(path.join(getResDir(), 'setup.png')))
        manualSetup.setFlags(manualSetup.flags() & ~Qt.ItemIsDragEnabled)
        self.manualDirectory.addChild(manualSetup)

        devices = Setup.getDeviceNamesOfSetup(pathToFile, self.log)
        for device in devices:
            deviceItem = QTreeWidgetItem(
                [device, 'in file: ' + filename],
                ItemTypes.Device)
            deviceItem.setIcon(0, QIcon(path.join(getResDir(), 'device.png')))
            deviceItem.setFlags(deviceItem.flags() & ~Qt.ItemIsDropEnabled)
            manualSetup.addChild(deviceItem)

    def getSetupsForDir(self, previousDir, newDir, listOfSetups):
        # gets a root directory: previousDir and a subdirectory in the root
        # walks down every directory starting from newDir and appends every
        # *.py file it finds to the initial listOfSetups which is passed to
        # each level of recursion
        # actually appends a list of strings: first string is filename, second
        # string is the full path.
        for item in os.listdir(path.join(previousDir, newDir)):
            if item.endswith('.py'):
                listOfSetups.append([item,
                                     str(path.join(previousDir,
                                                   newDir,
                                                   item))])
            elif path.isdir(path.join(previousDir, newDir, item)):
                self.getSetupsForDir(path.join(
                    previousDir, newDir), item, listOfSetups)

    def markItem(self, item):
        if item not in self.markedSetups:
            item.setText(0, '*' + item.text(0))
            self.markedSetups.append(item)

    def unmarkItem(self, item):
        item.setText(0, item.text(0)[1:])
        self.markedSetups.remove(item)

    def contextMenuOnItem(self, item, pos):
        if item is None:
            return  # invoked context menu on whitespace

        if item.type() == ItemTypes.Setup:
            menu = QMenu(self)
            addDeviceAction = menu.addAction('Add device...')
            addDeviceAction.triggered.connect(self.addDevice)
            menu.popup(pos)

        elif item.type() == ItemTypes.Directory:
            menu = QMenu(self)
            addSetupAction = menu.addAction('Add setup...')
            addSetupAction.triggered.connect(self.addSetup)
            menu.popup(pos)

        elif item.type() == ItemTypes.Device:
            menu = QMenu(self)
            removeDeviceAction = menu.addAction('Remove')
            removeDeviceAction.triggered.connect(self.removeDevice)
            menu.popup(pos)

        elif item.type() == ItemTypes.ManualDirectory:
            return

    def removeDevice(self):
        device = self.currentItem()
        setup = device.parent()
        indexOfDevice = setup.indexOfChild(device)

        self.markItem(setup)
        setup.takeChild(indexOfDevice)
        self.deviceRemoved.emit(setup.text(1), device.text(0))

    def addSetup(self):
        newSetup = QInputDialog.getText(self,
                                        'New setup...',
                                        'Enter name of new setup:')
        if not newSetup[1]:
            return  # user pressed cancel

        newSetup = str(newSetup[0])

        if not newSetup:
            return  # string is empty

        if not newSetup.endswith('.py'):
            newSetup += '.py'

        newPath = path.join(getNicosDir(),
                            'custom',
                            self.currentItem().text(0),
                            'setups',
                            newSetup)

        try:
            open(newPath, 'w').close()
        except IOError:
            QMessageBox.warning(self,
                                'Error',
                                'Could not create new setup!')
            return

        newItem = QTreeWidgetItem(
            [newSetup, newPath],
            ItemTypes.Setup)
        newItem.setIcon(0, QIcon(path.join(getResDir(), 'setup.png')))
        self.currentItem().addChild(newItem)
        self.markItem(newItem)
        self.itemActivated.emit(newItem, 0)

    def addDevice(self):
        newDevice = QInputDialog.getText(
            self,
            'New device...',
            'Enter name of new device:')
        if not newDevice[1]:
            return  # user pressed cancel

        newDevice = str(newDevice[0])

        if not newDevice:
            QMessageBox.warning(self,
                                'Error',
                                'No name entered for device.')
            return

        newItem = QTreeWidgetItem(
            [newDevice, 'in file: ' + self.currentItem().text(0)],
            ItemTypes.Device)
        newItem.setIcon(0, QIcon(path.join(getResDir(), 'device.png')))
        self.currentItem().addChild(newItem)
        self.markItem(self.currentItem())
        self.itemActivated.emit(newItem, 0)

    def setLogger(self, log):
        self.log = log
