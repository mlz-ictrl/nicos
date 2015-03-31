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

#icons: https://launchpad.net/elementaryicons

import logging
import os
from os import path

from PyQt4 import uic
from PyQt4.QtGui import QMainWindow, QFileDialog, QTreeWidgetItem, QIcon, QLabel
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import Qt

from nicos.core.sessions.setups import readSetup

from setupfiletool.widgetsetup import WidgetSetup
from setupfiletool.widgetdevice import WidgetDevice
from setupfiletool.utilities.itemtypes import ItemTypes

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'mainwindow.ui'), self)

        self.resDir = path.join(self.getNicosDir(),
                                'tools', 'setupfiletool', 'res')

        #root directory containing all the setups or subdirectories with setups.
        self.setupRoot = path.join(self.getNicosDir(), 'custom')

        # initialize empty dictionary
        # supposed to be a dictionary of Tuples of parsed files
        self.info = {}
        self.currentSetupPath = ''
        self.currentSetup = None

        #signal/slot connections
        self.pushButtonLoadFile.clicked.connect(
            self.loadFile)
        self.treeWidget.itemActivated.connect(self.loadSelection)

        # Initialize a logger required by setups.readSetup()
        self.log = logging.getLogger()

        #list of directories in */nicos-core/custom/
        self.setupDirectories = []
        for item in os.listdir(self.setupRoot):
            if path.isdir(path.join(self.setupRoot, item)):
                self.setupDirectories.append(item)

        #list of topLevelItems representing the directories in
        #*/nicos-core/custom: for example instruments, ...
        topLevelItems = []
        for directory in sorted(self.setupDirectories):
            topLevelItems.append(
                QTreeWidgetItem([directory,
                                 'nicos-core/custom'], ItemTypes.Directory))
        self.treeWidget.addTopLevelItems(topLevelItems)

        #all these directories (may) have setups, find all of them and add them
        #as children, after that, add all their devices as children
        for item in topLevelItems:
            item.setIcon(0, QIcon(path.join(self.resDir, 'folder.png')))
            scriptList = [[]] #list of rows, a row = list of strings
            if path.isdir(path.join(self.setupRoot, item.text(0), 'setups')):
                self.getSetupsForDir(path.join(self.setupRoot, item.text(0)),
                                     'setups', scriptList)
                for script in sorted(scriptList):
                    if script:
                        item.addChild(QTreeWidgetItem(script, ItemTypes.Setup))

            #setup for this directory has been loaded, add the devices.
            currentIndex = 0
            while currentIndex < item.childCount():
                currentPath = item.child(currentIndex).text(1)
                self.readSetupFile(currentPath)
                for key in self.info[currentPath[:-3]]['devices'].keys():
                    #read the setup and add all the devices as child tree items
                    item.child(currentIndex).addChild(
                        QTreeWidgetItem([key,
                                         'in file: ' + item.child(currentIndex).text(0)],
                        ItemTypes.Device))
                item.child(currentIndex).setIcon(0, QIcon(
                    path.join(self.resDir, 'setup.png')))

                #icons for all devices
                deviceIndex = 0
                while deviceIndex < item.child(currentIndex).childCount():
                    item.child(currentIndex).child(deviceIndex).setIcon(
                        0, QIcon(path.join(self.resDir, 'device.png')))
                    deviceIndex += 1
                currentIndex += 1

        #hide the "path" column in treeWidget. May be toggleable later
        self.treeWidget.setColumnCount(1)

        #information of hidden column is still accessible.
        #print(topLevelItems[0].child(0).text(1)) -> path to very first setup

        #GUI setup for working area on the right
        self.widgetSetup = WidgetSetup()

        #setup the tool to recognize changes made to setups
        self.unsavedChanges = False
        self.widgetSetup.editedSetup.connect(self.setupEdited)
        self.treeWidget.editedSetup.connect(self.setupEdited)

        self.widgetDevice = WidgetDevice()
        self.labelHeader = QLabel('Select Setup or device...')
        self.labelHeader.setAlignment(Qt.AlignCenter)
        self.workarea.addWidget(self.widgetSetup)
        self.workarea.addWidget(self.widgetDevice)
        self.workarea.addWidget(self.labelHeader)
        self.workarea.setCurrentIndex(2)


    def msgboxUnsavedChanges(self):
        if self.currentSetup:
            fileStr = self.currentSetup.text(0)
        else:
            fileStr = self.currentSetupPath
        reply = QMessageBox.question(self, 'Unsaved changes',
            'Save changes to ' + fileStr + '?',
            QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            #TODO write saving method
            print('save')


    def setupEdited(self):
        if not self.unsavedChanges:
            self.unsavedChanges = True
            if self.currentSetup:
                self.currentSetup.setText(0, '*' + self.currentSetup.text(0))


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


    def loadSelection(self):
        if self.unsavedChanges:
            self.msgboxUnsavedChanges()
            if self.currentSetup:
                self.currentSetup.setText(0, self.currentSetup.text(0)[1:])
            self.unsavedChanges = False
            self.currentSetup = None

        items = self.treeWidget.selectedItems()
        for item in items: #no multiple selection -> only 1 item
            if item.type() == ItemTypes.Directory:
                self.info.clear()
                self.currentSetupPath = ''
                self.workarea.setCurrentIndex(2)
                return

            elif item.type() == ItemTypes.Setup:
                self.currentSetupPath = item.text(1)
                self.currentSetup = item
                self.readSetupFile(self.currentSetupPath)
                self.updateSetupGui()

            elif item.type() == ItemTypes.Device:
                self.currentSetupPath = item.parent().text(1)
                self.currentSetup = item.parent()
                self.readSetupFile(self.currentSetupPath)
                self.updateDeviceGui()


    def loadFile(self):
        # allows a user specify the setup file to be parsed
        if self.unsavedChanges:
            self.msgboxUnsavedChanges()
            if self.currentSetup:
                self.currentSetup.setText(0, self.currentSetup.text(0)[1:])
            self.unsavedChanges = False
        setupFile = QFileDialog.getOpenFileName(
            self,
            'Open setup file',
            path.expanduser('~'),
            'Python Files (*.py)')

        if setupFile:
            self.readSetupFile(setupFile)
            self.currentSetupPath = setupFile
            self.currentSetup = None #no item for custom files available
            self.updateSetupGui()
        #TODO: Find a way to display devices of a manually loaded setup!!


    def readSetupFile(self, pathToFile):
        # uses nicos.core.sessions.setups.readSetup() to read a setup file and
        # put the information in the self.info dictionary.
        self.info.clear()
        readSetup(self.info,
                  path.dirname(pathToFile),
                  pathToFile,
                  self.log)


    def updateSetupGui(self):
        #selection = setup
        self.widgetSetup.clear()
        self.widgetSetup.loadData(self.info[self.currentSetupPath[:-3]])
        self.workarea.setCurrentIndex(0)


    def updateDeviceGui(self):
        #selection = device
        self.workarea.setCurrentIndex(1)


    def getNicosDir(self):
        # this file should be in */nicos-core/tools/setupfiletool
        return(path.abspath(path.join(path.dirname( __file__ ), '..', '..')))
