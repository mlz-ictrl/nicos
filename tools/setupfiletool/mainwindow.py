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

from setupfiletool.widgetsetup import WidgetSetup
from setupfiletool.widgetdevice import WidgetDevice
from setupfiletool.utilities.utilities import ItemTypes
from setupfiletool.setuphandler import SetupHandler

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'mainwindow.ui'), self)

        self.setupHandler = SetupHandler()

        #GUI setup for working area on the right
        self.widgetSetup = WidgetSetup()
        self.widgetDevice = WidgetDevice()
        self.labelHeader = QLabel('Select Setup or device...')
        self.labelHeader.setAlignment(Qt.AlignCenter)

        #signal/slot connections
        self.treeWidget.itemActivated.connect(self.loadSelection)
        self.widgetSetup.editedSetup.connect(self.treeWidget.changedSlot)
        self.actionExit.triggered.connect(QCoreApplication.instance().quit)
        self.actionLoadFile.triggered.connect(self.loadFile)
        self.actionAboutSetupFileTool.triggered.connect(self.aboutSetupFileTool)
        self.actionAboutQt.triggered.connect(QApplication.aboutQt)

        self.workarea.addWidget(self.widgetSetup)
        self.workarea.addWidget(self.widgetDevice)
        self.workarea.addWidget(self.labelHeader)
        self.workarea.setCurrentIndex(2)

        self.treeWidget.setSetupHandler(self.setupHandler)
        self.widgetSetup.setSetupHandler(self.setupHandler)
        self.treeWidget.setColumnCount(1)
        self.treeWidget.loadNicosData()


    def msgboxUnsavedChanges(self):
        fileStr = self.setupHandler.currentSetupPath
        reply = QMessageBox.question(self, 'Unsaved changes',
            'Save changes to ' + fileStr + '?',
            QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
        return reply


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
            reply = self.msgboxUnsavedChanges()
            if reply == QMessageBox.Yes:
                self.setupHandler.save()
                self.treeWidget.unmarkItem()
            elif reply == QMessageBox.No:
                self.treeWidget.cleanUnsavedDevices()
                self.setupHandler.clear()
                self.treeWidget.unmarkItem()
            elif reply ==  QMessageBox.Cancel:
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
            reply = self.msgboxUnsavedChanges()
            if reply == QMessageBox.Yes:
                self.setupHandler.save()
                self.treeWidget.unmarkItem()
            elif reply == QMessageBox.No:
                self.treeWidget.cleanUnsavedDevices()
                self.setupHandler.clear()
                self.treeWidget.unmarkItem()
            elif reply ==  QMessageBox.Cancel:
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


    def updateSetupGui(self):
        #selection = setup
        self.widgetSetup.clear()
        self.widgetSetup.loadData(self.setupHandler.info[
            self.setupHandler.currentSetupPath[:-3]])
        self.workarea.setCurrentIndex(0)


    def updateDeviceGui(self):
        #selection = device
        self.widgetDevice.label.setText(
            'you loaded: ' + self.treeWidget.currentItem().text(0))
        self.workarea.setCurrentIndex(1)


    def aboutSetupFileTool(self):
        QMessageBox.information(self,
            'About SetupFileTool', 'A tool designed to optimize ' +
            'editing setup files for NICOS.')
