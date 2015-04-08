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

from os import path

from PyQt4 import uic
from PyQt4.QtGui import QMainWindow, QFileDialog, QLabel, QMessageBox, \
                        QApplication
from PyQt4.QtCore import Qt, QCoreApplication

from setupfiletool.setupwidget import SetupWidget
from setupfiletool.devicewidget import DeviceWidget
from setupfiletool.utilities.utilities import ItemTypes
from setupfiletool.setuphandler import SetupHandler
from setupfiletool.dialogs.newsetup import NewSetupDialog

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'mainwindow.ui'), self)

        self.setupHandler = SetupHandler()

        #GUI setup for working area on the right
        self.setupWidget = SetupWidget()
        self.deviceWidget = DeviceWidget()
        self.labelHeader = QLabel('Select Setup or device...')
        self.labelHeader.setAlignment(Qt.AlignCenter)

        #signal/slot connections
        self.treeWidget.itemActivated.connect(self.loadSelection)
        self.setupWidget.editedSetup.connect(self.treeWidget.changedSlot)

        #setup the menu bar
        self.actionNewFile.triggered.connect(self.newFile)
        self.actionLoadFile.triggered.connect(self.loadFile)
        self.actionExit.triggered.connect(QCoreApplication.instance().quit)
        self.menuView.addAction(self.dockWidget.toggleViewAction())
        self.dockWidget.toggleViewAction().setText('Show Tree')
        self.actionAboutSetupFileTool.triggered.connect(self.aboutSetupFileTool)
        self.actionAboutQt.triggered.connect(QApplication.aboutQt)

        self.workarea.addWidget(self.setupWidget)
        self.workarea.addWidget(self.deviceWidget)
        self.workarea.addWidget(self.labelHeader)
        self.workarea.setCurrentIndex(2)

        self.treeWidget.setSetupHandler(self.setupHandler)
        self.setupWidget.setSetupHandler(self.setupHandler)
        self.treeWidget.setColumnCount(1)
        self.treeWidget.loadNicosData()


    def msgboxUnsavedChanges(self):
        #asks the user wether to save or discard his changes, or to abort the
        #triggered action. Saving and Discarding return true, while cancelling
        #returns false.
        fileStr = self.setupHandler.currentSetupPath
        reply = QMessageBox.question(self, 'Unsaved changes',
            'Save changes to ' + fileStr + '?',
            QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            self.setupHandler.save()
            self.treeWidget.unmarkItem()
            return True
        elif reply == QMessageBox.No:
            self.treeWidget.cleanUnsavedDevices()
            self.setupHandler.clear()
            self.treeWidget.unmarkItem()
            return True
        elif reply == QMessageBox.Cancel:
            return False


    def loadSelection(self):
        if not self.treeWidget.currentItem().type() == ItemTypes.Directory:
            if self.treeWidget.currentItem().text(
                1) == self.setupHandler.currentSetupPath:
                self.workarea.setCurrentIndex(0)
                return
            elif self.treeWidget.currentItem().parent(
                ).text(1) == self.setupHandler.currentSetupPath:
                #is device of current setup
                self.updateDeviceGui()
                return

        if self.setupHandler.unsavedChanges:
            if not self.msgboxUnsavedChanges():
                return
        self.setupHandler.clear()
        items = self.treeWidget.selectedItems()
        for item in items: #no multiple selection -> only 1 item
            if item.type() == ItemTypes.Directory:
                self.workarea.setCurrentIndex(2)

            elif item.type() == ItemTypes.Setup:
                self.setupHandler.readSetupFile(item.text(1))
                self.updateSetupGui()

            elif item.type() == ItemTypes.Device:
                self.setupHandler.readSetupFile(item.parent().text(1))
                self.updateDeviceGui()


    def loadFile(self):
        if self.setupHandler.unsavedChanges:
            if not self.msgboxUnsavedChanges():
                return

        setupFile = QFileDialog.getOpenFileName(
            self,
            'Open setup file',
            path.expanduser('~'),
            'Python Files (*.py)')
        if setupFile:
            self.setupHandler.readSetupFile(setupFile)
            self.setupHandler.isCustomFile = True
            self.updateSetupGui()
        else:
            self.workarea.setCurrentIndex(2)


    def newFile(self):
        if self.setupHandler.unsavedChanges:
            if not self.msgboxUnsavedChanges():
                return

        dlg = NewSetupDialog()
        if dlg.exec_():
            newFile = dlg.lineEditPath.text()
            if not newFile:
                QMessageBox.warning(self,
                                    'Error',
                                    'No path specified.')
                return

            try:
                open(newFile, 'w').close()
            except IOError:
                QMessageBox.warning(self,
                                    'Error',
                                    'Could not create new setup!')
                return

            if dlg.checkBoxReload.isChecked():
                self.treeWidget.loadNicosData()
            self.workarea.setCurrentIndex(2)


    def updateSetupGui(self):
        #selection = setup
        self.setupWidget.clear()
        self.setupWidget.loadData(self.setupHandler.info[
            self.setupHandler.currentSetupPath[:-3]])
        self.workarea.setCurrentIndex(0)


    def updateDeviceGui(self):
        #selection = device
        currentDevice = self.treeWidget.currentItem().text(0)
        currentSetup = self.setupHandler.currentSetupPath[:-3]
        info = self.setupHandler.info[currentSetup]['devices'][currentDevice]
        self.deviceWidget.loadDevice(info[0], info[1])
        self.workarea.setCurrentIndex(1)


    def aboutSetupFileTool(self):
        QMessageBox.information(self,
            'About SetupFileTool', 'A tool designed to optimize ' +
            'editing setup files for NICOS.')
