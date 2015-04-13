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


class TreeWidget(TreeWidgetContextMenu):
    editedSetup = pyqtSignal()
    deviceRemoved = pyqtSignal(str, str)

    def __init__(self, parent=None):
        TreeWidgetContextMenu.__init__(self, parent)
        self.markedSetups = []
        self.manualDirectory = None
        self.showManualDirectoryBool = False

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
        topLevelItems = []
        for directory in sorted(setupDirectories):
            topLevelItems.append(
                QTreeWidgetItem([directory,
                                 'nicos-core/custom'], ItemTypes.Directory))
        self.addTopLevelItems(topLevelItems)

        # all these directories (may) have setups, find all of them and add
        # them as children, after that, add all their devices as children
        for item in topLevelItems:
            item.setIcon(0, QIcon(path.join(getResDir(), 'folder.png')))
            scriptList = [[]]  # list of rows, a row = list of strings
            if path.isdir(path.join(setupRoot, item.text(0), 'setups')):
                self.getSetupsForDir(path.join(setupRoot, item.text(0)),
                                     'setups', scriptList)
                for script in sorted(scriptList):
                    if script:
                        item.addChild(QTreeWidgetItem(script, ItemTypes.Setup))

            # setup for this directory has been loaded, add the devices.
            currentIndex = 0
            while currentIndex < item.childCount():
                currentPath = item.child(currentIndex).text(1)
                devices = Setup.getDeviceNamesOfSetup(currentPath, self.log)
                for device in devices:
                    # read setup and add all the devices as child tree items
                    item.child(currentIndex).addChild(
                        QTreeWidgetItem([device,
                                         'in file: ' + item.child(currentIndex
                                                                  ).text(0)],
                                        ItemTypes.Device))
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

    def showManualDirectory(self):
        self.showManualDirectoryBool = True
        if self.manualDirectory is None:
            self.manualDirectory = QTreeWidgetItem(
                ['-manual-', '-'],
                ItemTypes.ManualDirectory)
            self.manualDirectory.setIcon(0, QIcon(path.join(getResDir(),
                                                            'folder.png')))
        self.addTopLevelItem(self.manualDirectory)

    def addManualFile(self, pathToFile):
        _, filename = path.split(pathToFile)
        manualSetup = QTreeWidgetItem([filename, pathToFile], ItemTypes.Setup)
        manualSetup.setIcon(0, QIcon(path.join(getResDir(), 'setup.png')))
        self.manualDirectory.addChild(manualSetup)

        devices = Setup.getDeviceNamesOfSetup(pathToFile, self.log)
        for device in devices:
            deviceItem = QTreeWidgetItem(
                [device, 'in file: ' + filename],
                ItemTypes.Device)
            deviceItem.setIcon(0, QIcon(path.join(getResDir(), 'device.png')))
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
