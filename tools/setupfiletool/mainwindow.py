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

# icons: https://launchpad.net/elementaryicons

from os import path
import logging

from PyQt4 import uic
from PyQt4.QtGui import QMainWindow, QFileDialog, QLabel, QMessageBox, \
    QApplication
from PyQt4.QtCore import Qt

from setupfiletool.setupwidget import SetupWidget
from setupfiletool.devicewidget import DeviceWidget
from setupfiletool.utilities.utilities import ItemTypes, getNicosDir
from setupfiletool.dialogs.newsetup import NewSetupDialog
from setupfiletool.setup import Setup


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'mainwindow.ui'), self)

        self.log = logging.getLogger()

        # dictionary of setup - setupWidget
        self.setupWidgets = {}
        # dictionary of setup - dict, which is deviceName - deviceWidget
        self.deviceWidgets = {}

        self.labelHeader = QLabel('Select Setup or device...')
        self.labelHeader.setAlignment(Qt.AlignCenter)

        # signal/slot connections
        self.treeWidget.itemActivated.connect(self.loadSelection)
        self.treeWidget.deviceRemoved.connect(self.deviceRemovedSlot)

        # setup the menu bar
        self.actionNewFile.triggered.connect(self.newFile)
        self.actionSave.triggered.connect(self.actionSaveSlot)
        self.actionSaveAs.triggered.connect(self.actionSaveAsSlot)
        self.actionLoadFile.triggered.connect(self.loadFile)
        self.actionExit.triggered.connect(self.close)
        self.menuView.addAction(self.dockWidget.toggleViewAction())
        self.dockWidget.toggleViewAction().setText('Show Tree')
        self.actionAboutSetupFileTool.triggered.connect(
            self.aboutSetupFileTool)
        self.actionAboutQt.triggered.connect(QApplication.aboutQt)

        self.workarea.addWidget(self.labelHeader)

        self.treeWidget.setColumnCount(1)
        self.treeWidget.setLogger(self.log)
        self.treeWidget.loadNicosData()

    def loadSelection(self, curItem, column):
        self.treeWidget.setCurrentItem(curItem)

        if curItem.type() == ItemTypes.Directory:
            self.workarea.setCurrentIndex(0)

        elif curItem.type() == ItemTypes.Setup:
            if curItem.text(1) in self.setupWidgets:
                # if setup was loaded previously:
                self.workarea.setCurrentIndex(
                    self.workarea.indexOf(self.setupWidgets[curItem.text(1)]))
            else:
                # if setup hasn't been loaded before:
                newWidget = SetupWidget()
                newWidget.editedSetup.connect(self.editedSetupSlot)
                newWidget.loadData(Setup(curItem.text(1), self.log, self))
                self.workarea.addWidget(newWidget)
                self.setupWidgets[curItem.text(1)] = newWidget
                self.workarea.setCurrentIndex(self.workarea.indexOf(newWidget))
                # initialize empty dictionary for this setup
                self.deviceWidgets[curItem.text(1)] = {}

        elif curItem.type() == ItemTypes.Device:
            if curItem.parent().text(1) not in self.setupWidgets:
                # if the setup, this device belongs to, hasn't been loaded yet:
                newWidget = SetupWidget()
                newWidget.editedSetup.connect(self.editedSetupSlot)
                newWidget.loadData(Setup(curItem.parent().text(1),
                                         self.log, self))
                self.workarea.addWidget(newWidget)
                self.setupWidgets[curItem.parent().text(1)] = newWidget
                # initialize empty dictionary for this setup
                self.deviceWidgets[curItem.parent().text(1)] = {}

            if curItem.text(0) in self.deviceWidgets[curItem.parent().text(1)]:
                # if device was loaded previously:
                self.workarea.setCurrentIndex(
                    self.workarea.indexOf(self.deviceWidgets[
                        curItem.parent().text(1)][curItem.text(0)]))

            else:
                # device has never been loaded before:
                newWidget = DeviceWidget()
                newWidget.editedDevice.connect(self.editedSetupSlot)
                newWidget.loadDevice(Setup.getDeviceOfSetup(curItem.parent(
                    ).text(1), curItem.text(0), self.log))
                self.workarea.addWidget(newWidget)
                self.deviceWidgets[curItem.parent(
                    ).text(1)][curItem.text(0)] = newWidget
                self.workarea.setCurrentIndex(self.workarea.indexOf(newWidget))

    def loadFile(self):
        setupFile = QFileDialog.getOpenFileName(
            self,
            'Open setup file',
            getNicosDir(),
            'Python Files (*.py)')
        if setupFile:
            self.treeWidget.showManualDirectory()
            self.treeWidget.addManualFile(setupFile)

    def newFile(self):
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
            self.workarea.setCurrentIndex(0)

    def editedSetupSlot(self):
        if self.treeWidget.currentItem().type() == ItemTypes.Setup:
            self.treeWidget.markItem(self.treeWidget.currentItem())
        elif self.treeWidget.currentItem().type() == ItemTypes.Device:
            self.treeWidget.markItem(self.treeWidget.currentItem().parent())

    def deviceRemovedSlot(self, setup, deviceName):
        if setup not in self.setupWidgets.keys():
            # setup was never loaded
            return
        if deviceName not in self.deviceWidgets[setup].keys():
            # device was never loaded
            return

        deviceWidget = self.deviceWidgets[setup][deviceName]
        if self.workarea.currentWidget() == deviceWidget:
            self.workarea.setCurrentIndex(
                self.workarea.indexOf(self.setupWidgets[setup]))
            # when the device's widget was loaded, switch to the setup the
            # device belonged to.
        del self.deviceWidgets[setup][deviceName]

    def aboutSetupFileTool(self):
        QMessageBox.information(
            self,
            'About SetupFileTool', 'A tool designed to optimize \
            editing setup files for NICOS.')

    def closeEvent(self, event):
        if self.treeWidget.markedSetups:
            reply = QMessageBox.question(self, 'Unsaved changes',
                                         'Do you want to save your changes?',
                                         QMessageBox.Yes,
                                         QMessageBox.No,
                                         QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                paths = []
                for setup in self.treeWidget.markedSetups:
                    paths.append(setup.text(1))
                self.saveSetups(paths)
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            elif reply == QMessageBox.Cancel:
                event.ignore()
        else:
            event.accept()

    def getCurrentSetupItem(self):
        # if a setup is loaded, returns the item in the tree to it.
        # if a device is loaded, returns the item of the setup the device
        # belongs to.
        # returns None for directories and the manual directory.
        curItem = self.treeWidget.currentItem()
        if curItem.type() == ItemTypes.Directory:
            return None
        if curItem.type() == ItemTypes.ManualDirectory:
            return None
        if curItem.type() == ItemTypes.Device:
            return curItem.parent()
        elif curItem.type() == ItemTypes.Setup:
            return curItem

    def saveSetups(self, setupsToSave):
        # setupsToSave should be a list of paths to setups.
        # saves all the setups in that list.
        # useful when exiting the application and saving all changed setups.
        for setup in setupsToSave:
            self.save(setup)

    def actionSaveSlot(self):
        # saves the currently selected setup. Or, if a device is loaded,
        # saves the setup the device belongs to.
        if self.getCurrentSetupItem() not in self.treeWidget.markedSetups:
            return  # setup to be saved hasn't been edited
        self.save(self.getCurrentSetupItem().text(1))
        self.treeWidget.unmarkItem(self.getCurrentSetupItem())

    def actionSaveAsSlot(self):
        # asks the user where to save the current setup to.
        if not self.getCurrentSetupItem():
            return
        setup = self.getCurrentSetupItem().text(1)
        filepath = QFileDialog.getSaveFileName(
            self,
            "Save as...",
            getNicosDir(),
            "Python script (*.py)")

        if filepath:
            if not str(filepath).endswith('.py'):
                filepath += '.py'
            self.save(setup, filepath)
            if filepath == setup:
                self.treeWidget.unmarkItem(self.getCurrentSetupItem())

    def save(self, setup, setupPath=None):
        # one may provide a path different from the current file to save to.
        if not setupPath:
            setupPath = setup

        setupData = self.setupWidgets[setup]
        output = []
        add = output.append
        add(self.saveDescription(setupData))
        add(self.saveGroup(setupData))
        add(self.saveIncludes(setupData))
        add(self.saveExcludes(setupData))
        add(self.saveModules(setupData))
        add(self.saveSysconfig(setupData))
        add(self.saveDevices(setup, setupData))
        add(self.saveStartupcode(setupData))

        with open(setupPath, 'w') as outputFile:
            outputFile.write(''.join(output))

    def saveDescription(self, setupData):
        output = []
        output.append('description = ')
        output.append(repr(str(setupData.lineEditDescription.text())) + '\n\n')
        return ''.join(output)

    def saveGroup(self, setupData):
        output = []
        output.append('group = ')
        output.append(repr(str(setupData.comboBoxGroup.currentText())) +
                      '\n\n')
        return ''.join(output)

    def saveIncludes(self, setupData):
        output = []
        includes = []
        includeIndex = 0
        while includeIndex < setupData.listWidgetIncludes.count():
            includes.append(str(setupData.listWidgetIncludes.item(
                includeIndex).text()))
            includeIndex += 1
        output.append('includes = ')
        output.append(repr(includes) + '\n\n')
        return ''.join(output)

    def saveExcludes(self, setupData):
        output = []
        excludes = []
        excludeIndex = 0
        while excludeIndex < setupData.listWidgetExcludes.count():
            excludes.append(str(setupData.listWidgetExcludes.item(
                excludeIndex).text()))
            excludeIndex += 1
        output.append('excludes = ')
        output.append(repr(excludes) + '\n\n')
        return ''.join(output)

    def saveModules(self, setupData):
        output = []
        modules = []
        moduleIndex = 0
        while moduleIndex < setupData.listWidgetModules.count():
            modules.append(str(setupData.listWidgetModules.item(
                moduleIndex).text()))
            moduleIndex += 1
        output.append('modules = ')
        output.append(repr(modules) + '\n\n')
        return ''.join(output)

    def saveSysconfig(self, setupData):
        output = []
        if setupData.treeWidgetSysconfig.topLevelItemCount() > 0:
            output.append('sysconfig = dict(\n')
            for key, value in setupData.treeWidgetSysconfig.getData(
                    ).iteritems():
                output.append('    ' + key + ' = ' + repr(value) + ',\n')
            output.append(')\n\n')

        output.append('devices = dict(\n')
        return ''.join(output)

    def saveDevices(self, setup, setupData):
        output = []
        childIndex = 0
        deviceItems = []
        while childIndex < self.getCurrentSetupItem().childCount():
            deviceItems.append(self.getCurrentSetupItem().child(childIndex))
            childIndex += 1
        for device in deviceItems:
            # makes sure all items have corresponding GUI widgets.
            # if a device was manually added or renamed, it's already in
            # self.deviceWidgets[setup]. If it came with the setup and wasn't
            # loaded, it will be loaded now, so the loop getting all the data
            # to be saved doesn't have to distinguish between loaded and
            # not loaded devices.
            if device.text(0) not in self.deviceWidgets[setup]:
                # device wasn't loaded before
                newWidget = DeviceWidget()
                newWidget.editedDevice.connect(self.editedSetupSlot)
                newWidget.loadDevice(Setup.getDeviceOfSetup(setup,
                                                            device.text(0),
                                                            self.log))
                self.workarea.addWidget(newWidget)
                self.deviceWidgets[setup][device.text(0)] = newWidget

        for name, info in self.deviceWidgets[setup].iteritems():
            output.append('    ' + name + ' = device(')
            indent = len(name) + 14
            for params in info.currentWidgets:
                if isinstance(params.value, basestring):
                    # if parameter is a string
                    if str(params.labelParam.text()) == 'Class:':
                        prepend = ''
                        param = repr(str(
                            params.lineEditParam.text())) + ',\n'
                    else:
                        prepend = indent * ' ' + str(
                            params.labelParam.text())[:-1] + ' = '
                        param = repr(str(params.lineEditParam.text())) + ',\n'
                else:
                    prepend = indent * ' ' + str(
                        params.labelParam.text())[:-1] + ' = '
                    param = str(params.lineEditParam.text()) + ',\n'
                output.append(prepend + param)
            output.append((indent - 1) * ' ' + '),\n')
        output.append(')\n\n')
        return ''.join(output)

    def saveStartupcode(self, setupData):
        output = []
        startupcode = setupData.textEditStartupCode.toPlainText()
        output.append("startupcode = '''\n")
        if startupcode:
            output.append(startupcode + '\n')
        output.append("'''\n")
        return ''.join(output)
