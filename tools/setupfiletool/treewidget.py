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

from PyQt4.QtGui import QTreeWidgetItem, QMenu, QIcon, QInputDialog, QMessageBox
from PyQt4.QtCore import pyqtSignal, Qt

from setupfiletool.utilities.treewidgetcontextmenu import TreeWidgetContextMenu
from setupfiletool.utilities.utilities import ItemTypes, getNicosDir, getResDir

class TreeWidget(TreeWidgetContextMenu):
    editedSetup = pyqtSignal()


    def __init__(self, parent=None):
        TreeWidgetContextMenu.__init__(self, parent)
        self.markedItem = None


    def loadNicosData(self):
        while self.topLevelItemCount() > 0:
            self.takeTopLevelItem(0)
        #root directory containing all the setups or subdirectories with setups.
        setupRoot = path.join(getNicosDir(), 'custom')

        #list of directories in */nicos-core/custom/
        setupDirectories = []
        for item in os.listdir(setupRoot):
            if path.isdir(path.join(setupRoot, item)):
                setupDirectories.append(item)

        #list of topLevelItems representing the directories in
        #*/nicos-core/custom: for example instruments, ...
        topLevelItems = []
        for directory in sorted(setupDirectories):
            topLevelItems.append(
                QTreeWidgetItem([directory,
                                 'nicos-core/custom'], ItemTypes.Directory))
        self.addTopLevelItems(topLevelItems)

        #all these directories (may) have setups, find all of them and add them
        #as children, after that, add all their devices as children
        for item in topLevelItems:
            item.setIcon(0, QIcon(path.join(getResDir(), 'folder.png')))
            scriptList = [[]] #list of rows, a row = list of strings
            if path.isdir(path.join(setupRoot, item.text(0), 'setups')):
                self.getSetupsForDir(path.join(setupRoot, item.text(0)),
                                     'setups', scriptList)
                for script in sorted(scriptList):
                    if script:
                        item.addChild(QTreeWidgetItem(script, ItemTypes.Setup))

            #setup for this directory has been loaded, add the devices.
            currentIndex = 0
            while currentIndex < item.childCount():
                currentPath = item.child(currentIndex).text(1)
                setup = self.setupHandler.readSetupReturn(currentPath)
                for device in setup.devices:
                    #read the setup and add all the devices as child tree items
                    item.child(currentIndex).addChild(
                        QTreeWidgetItem([device.name,
                                         'in file: ' + item.child(
                                            currentIndex).text(0)],
                        ItemTypes.Device))
                item.child(currentIndex).setIcon(0, QIcon(
                    path.join(getResDir(), 'setup.png')))

                #icons for all devices
                deviceIndex = 0
                while deviceIndex < item.child(currentIndex).childCount():
                    item.child(currentIndex).child(deviceIndex).setIcon(
                        0, QIcon(path.join(getResDir(), 'device.png')))
                    deviceIndex += 1
                currentIndex += 1
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)


    def getSetupsForDir(self, previousDir, newDir, listOfSetups):
        #gets a root directory: previousDir and a subdirectory in the root
        #walks down every directory starting from newDir and appends every
        #*.py file it finds to the initial listOfSetups which is passed to each
        #level of recursion
        #actually appends a list of strings: first string is filename, second
        #string is the full path.
        for item in os.listdir(path.join(previousDir, newDir)):
            if item.endswith('.py'):
                listOfSetups.append([item,
                                     str(path.join(previousDir, newDir, item))])
            elif path.isdir(path.join(previousDir, newDir, item)):
                self.getSetupsForDir(path.join(
                    previousDir, newDir), item, listOfSetups)


    def markItem(self, item):
        self.markedItem = item
        self.markedItem.setText(0, '*' + self.markedItem.text(0))

    def unmarkItem(self):
        if self.markedItem:
            self.markedItem.setText(0, self.markedItem.text(0)[1:])
        self.markedItem = None


    def contextMenuOnItem(self, item, pos):
        if item is None:
            return #invoked context menu on whitespace

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


    def addSetup(self):
        mw = self.parent().parent().parent()
        if self.setupHandler.unsavedChanges:
            if not mw.msgboxUnsavedChanges():
                return
        newSetup = QInputDialog.getText(self,
                                        'New setup...',
                                        'Enter name of new setup:')
        if not newSetup[1]:
            return #user pressed cancel

        newSetup = str(newSetup[0])

        if not newSetup:
            return #string is empty

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


    def addDevice(self):
        mw = self.parent().parent().parent()

        if self.setupHandler.currentSetup is not None: #a setup was loaded
            if not self.currentItem().text(
                1) == self.setupHandler.currentSetup.path: #the setup, the user
                #wants to add a new device to, is not the currently loaded one
                if self.setupHandler.unsavedChanges:
                    if not mw.msgboxUnsavedChanges():
                        return
                #the user wants to continue. Old setup was saved/discarded
                self.setupHandler.readSetupFile(self.currentItem().text(1))
        else:
            #if no setup has been loaded before, load the one the device is
            #going to be added to.
            self.setupHandler.readSetupFile(self.currentItem().text(1))

        newDevice = QInputDialog.getText(self,
                                        'New device...',
                                        'Enter name of new device:')
        if not newDevice[1]:
            return #user pressed cancel

        newDevice = str(newDevice[0])

        if not newDevice:
            QMessageBox.warning(self,
                                'Error',
                                'No name entered for device.')
            return

        newItem = QTreeWidgetItem(
            [newDevice, 'in file: ' + self.currentItem().text(0)],
            ItemTypes.UnsavedDevice)
        newItem.setIcon(0, QIcon(path.join(getResDir(), 'device.png')))
        self.currentItem().addChild(newItem)
        self.setupHandler.addDevice(newDevice)
        if not self.setupHandler.unsavedChanges:
            self.unmarkItem()
            if not self.setupHandler.isCustomFile:
                self.markItem(self.currentItem())
            if not self.setupHandler.setupDisplayed:
                self.setupHandler.readSetupFile(self.currentItem().text(1))
                mw.setupWidget.loadData(self.setupHandler.currentSetup)
            self.setupHandler.changedSlot()


    def changedSlot(self):
        if not self.markedItem:
            if not self.setupHandler.isCustomFile:
                self.markItem(self.currentItem())
        self.setupHandler.changedSlot()


    def cleanUnsavedDevices(self):
        currentDir = 0
        while self.topLevelItemCount() > currentDir:
            currentSetup = 0
            while self.topLevelItem(currentDir).childCount() > currentSetup:
                currentDevice = 0
                while self.topLevelItem(currentDir).child(
                    currentSetup).childCount() > currentDevice:
                    item = self.topLevelItem(currentDir).child(
                        currentSetup).child(currentDevice)
                    if item.type() == ItemTypes.UnsavedDevice:
                        self.topLevelItem(currentDir).child(
                            currentSetup).removeChild(item)
                    else:
                        currentDevice += 1
                currentSetup += 1
            currentDir += 1


    def setSetupHandler(self, setupHandler):
        self.setupHandler = setupHandler
