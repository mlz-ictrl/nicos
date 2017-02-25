#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
"""Application main window."""

# icons: https://launchpad.net/elementaryicons

import inspect
import logging

from os import path

from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QFileDialog, QIcon, QLabel, QMainWindow,\
    QMessageBox, QTreeWidgetItem

from nicos.configmod import config
from nicos.pycompat import string_types

from setupfiletool import classparser, setupcontroller
from setupfiletool.devicewidget import DeviceWidget
from setupfiletool.setupwidget import SetupWidget
from setupfiletool.utilities.utilities import ItemTypes, getNicosDir, getResDir


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'mainwindow.ui'), self)

        logging.basicConfig()
        self.log = logging.getLogger()

        setupcontroller.init(self.log)
        classparser.init(self.log)

        # dictionary of absolute path to a setup - setupWidget
        self.setupWidgets = {}
        # dictionary of absolute path to setup - dict
        # which is deviceName - deviceWidget
        self.deviceWidgets = {}

        self.labelHeader = QLabel('Select Setup or device...')
        self.labelHeader.setAlignment(Qt.AlignCenter)

        # signal/slot connections
        self.treeWidget.itemActivated.connect(self.loadSelection)
        self.treeWidget.deviceRemoved.connect(self.deviceRemovedSlot)
        self.treeWidget.deviceAdded.connect(self.deviceAddedSlot)
        self.treeWidget.newDeviceAdded.connect(self.newDeviceAddedSlot)

        # setup the menu bar
        self.actionNewFile.triggered.connect(self.treeWidget.addSetup)
        self.actionSave.triggered.connect(self.actionSaveSlot)
        self.actionSaveAs.triggered.connect(self.actionSaveAsSlot)
        self.actionExit.triggered.connect(self.close)
        self.instrumentMenu = self.menuView.addMenu('Instrument')
        self.actionShowAllInstrument = self.menuView.addAction(
            'Show all instruments')
        self.actionShowAllInstrument.triggered.connect(
            self.treeWidget.setAllInstrumentsVisible)
        self.menuView.addAction(self.dockWidget.toggleViewAction())
        self.dockWidget.toggleViewAction().setText('Show Tree')
        self.actionAboutSetupFileTool.triggered.connect(
            self.aboutSetupFileTool)
        self.actionAboutQt.triggered.connect(QApplication.aboutQt)

        self.workarea.addWidget(self.labelHeader)

        self.treeWidget.loadNicosData()
        for directory in sorted(setupcontroller.setup_directories):
            instrumentAction = self.instrumentMenu.addAction(directory)
            instrumentAction.triggered.connect(
                self.treeWidget.setInstrumentMode)
        if config.instrument and config.instrument not in ('jcns', 'demo'):
            self.treeWidget.setSingleInstrument(config.instrument)

    def loadSetup(self, setup):
        # load a previously not loaded setup's data and initialize their
        # dict in self.setupWidgets.
        # returns index of the setup's widget in self.workarea.
        setupWidget = SetupWidget(setup)
        setupWidget.editedSetup.connect(self.editedSetupSlot)
        self.workarea.addWidget(setupWidget)
        self.setupWidgets[setup.abspath] = setupWidget
        # initialize device widgets dictionary for this setup
        self.deviceWidgets[setup.abspath] = {}
        for deviceName, device in setup.devices.iteritems():
            deviceWidget = DeviceWidget(setupWidget)
            deviceWidget.editedDevice.connect(self.editedSetupSlot)
            deviceWidget.loadDevice(device)
            self.workarea.addWidget(deviceWidget)
            self.deviceWidgets[setup.abspath][deviceName] = deviceWidget
        return self.workarea.indexOf(setupWidget)

    def loadSelection(self, curItem, column):
        self.treeWidget.setCurrentItem(curItem)

        if curItem.type() == ItemTypes.Directory:
            self.workarea.setCurrentIndex(0)

        elif curItem.type() == ItemTypes.Setup:
            if curItem.setup.abspath in self.setupWidgets:
                # if setup was loaded previously:
                self.workarea.setCurrentIndex(
                    self.workarea.indexOf(
                        self.setupWidgets[curItem.setup.abspath]))
            else:
                # if setup hasn't been loaded before:
                i = self.loadSetup(curItem.setup)
                self.workarea.setCurrentIndex(i)

        elif curItem.type() == ItemTypes.Device:
            setup = curItem.parent().setup
            if setup.abspath not in self.setupWidgets:
                # if the setup, this device belongs to, hasn't been loaded yet:
                self.loadSetup(setup)

            self.workarea.setCurrentIndex(
                self.workarea.indexOf(self.deviceWidgets[setup.abspath]
                                      [curItem.device.name]))

    def editedSetupSlot(self):
        setupItem = self.getCurrentSetupItem()
        if setupItem is None:
            return
        if not setupItem.setup.edited:
            setupItem.setText(0, '*' + setupItem.text(0))
            setupItem.setup.edited = True

    def newDeviceAddedSlot(self, deviceName, _classString):
        setupItem = self.getCurrentSetupItem()
        if setupItem.setup.abspath not in self.setupWidgets.keys():
            self.loadSetup(setupItem.setup)

        uncombinedModule = _classString.split('.')
        classname = uncombinedModule.pop()
        module = '.'.join(uncombinedModule)
        classes = inspect.getmembers(classparser.modules[module],
                                     predicate=inspect.isclass)
        _class = [_class[1] for _class in classes if _class[0] == classname][0]
        parameters = {key: '' for key in _class.parameters.keys()
                      if _class.parameters[key].mandatory is True}
        device = setupcontroller.Device(deviceName,
                                        _classString,
                                        parameters=parameters)
        setupItem.setup.devices[deviceName] = device
        deviceWidget = DeviceWidget(self.setupWidgets[
            setupItem.setup.abspath])
        deviceWidget.editedDevice.connect(self.editedSetupSlot)
        deviceWidget.loadDevice(device)
        self.workarea.addWidget(deviceWidget)
        self.deviceWidgets[setupItem.setup.abspath][deviceName] = deviceWidget
        deviceItem = QTreeWidgetItem([deviceName], ItemTypes.Device)
        deviceItem.setFlags(deviceItem.flags() & ~Qt.ItemIsDropEnabled)
        deviceItem.device = setupItem.setup.devices[deviceName]
        deviceItem.setIcon(0, QIcon(path.join(getResDir(), 'device.png')))
        setupItem.insertChild(0, deviceItem)
        self.treeWidget.itemActivated.emit(deviceItem, 0)

        if not setupItem.setup.edited:
            setupItem.setText(0, '*' + setupItem.text(0))
            setupItem.setup.edited = True

    def deviceRemovedSlot(self, setupItem, deviceName):
        if setupItem.setup.abspath not in self.setupWidgets.keys():
            self.loadSetup(setupItem.setup)

        try:
            deviceWidget = self.deviceWidgets[setupItem.setup.abspath][
                deviceName]
            if self.workarea.currentWidget() == deviceWidget:
                self.workarea.setCurrentIndex(
                    self.workarea.indexOf(self.setupWidgets[
                        setupItem.setup.abspath]))
                self.treeWidget.setCurrentItem(setupItem)
                # when the device's widget was loaded, switch to the setup the
                # device belonged to.
            del self.deviceWidgets[setupItem.setup.abspath][deviceName]
        except KeyError:
            # setup was never loaded
            pass
        if not setupItem.setup.edited:
            setupItem.setText(0, '*' + setupItem.text(0))
            setupItem.setup.edited = True

    def deviceAddedSlot(self, setupItem, newDeviceName):
        if setupItem.setup.abspath not in self.setupWidgets.keys():
            self.loadSetup(setupItem.setup)
        else:
            for deviceName, device in setupItem.setup.devices.iteritems():
                if deviceName == newDeviceName:
                    deviceWidget = DeviceWidget(self.setupWidgets[
                        setupItem.setup.abspath])
                    deviceWidget.editedDevice.connect(self.editedSetupSlot)
                    deviceWidget.loadDevice(device)
                    self.workarea.addWidget(deviceWidget)
                    self.deviceWidgets[setupItem.setup.abspath][
                        deviceName] = deviceWidget
        if not setupItem.setup.edited:
            setupItem.setText(0, '*' + setupItem.text(0))
            setupItem.setup.edited = True

    def aboutSetupFileTool(self):
        QMessageBox.information(
            self,
            'About SetupFileTool', 'A tool designed to optimize editing' +
            ' setup files for NICOS.')

    def closeEvent(self, event):
        # Find all setups that have been edited
        setupItemsToBeSaved = []
        for item in self.treeWidget.topLevelItems:
            for index in range(item.childCount()):
                if item.child(index).setup.edited:
                    setupItemsToBeSaved.append(item.child(index))
        if setupItemsToBeSaved:
            reply = QMessageBox.question(self, 'Unsaved changes',
                                         'Do you want to save your changes?',
                                         QMessageBox.Yes,
                                         QMessageBox.No,
                                         QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.saveSetups(setupItemsToBeSaved)
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
        if curItem.type() == ItemTypes.Device:
            return curItem.parent()
        elif curItem.type() == ItemTypes.Setup:
            return curItem

    def saveSetups(self, setupsToSave):
        # setupsToSave should be a list of QTreeWidgetItems.
        # saves all the setups in that list.
        # useful when exiting the application and saving all changed setups.
        for setup in setupsToSave:
            self.save(setup)

    def actionSaveSlot(self):
        # saves the currently selected setup. Or, if a device is loaded,
        # saves the setup the device belongs to.
        if self.getCurrentSetupItem() is None:
            return
        if not self.getCurrentSetupItem().setup.edited:
            return  # setup to be saved hasn't been edited
        self.save(self.getCurrentSetupItem())

    def actionSaveAsSlot(self):
        # asks the user where to save the current setup to.
        if self.getCurrentSetupItem() is None:
            return
        filepath = QFileDialog.getSaveFileName(
            self,
            'Save as...',
            getNicosDir(),
            'Python script (*.py)')

        if filepath:
            if not str(filepath).endswith('.py'):
                filepath += '.py'
            self.save(self.getCurrentSetupItem(), filepath)

    def save(self, setupItem, setupPath=None):
        # one may provide a path different from the current file to save to.
        if not setupPath:
            setupPath = setupItem.setup.abspath

        setupData = self.setupWidgets[setupItem.setup.abspath]
        output = []
        add = output.append
        add(self.saveDescription(setupData))
        add(self.saveGroup(setupData))
        add(self.saveIncludes(setupData))
        add(self.saveExcludes(setupData))
        add(self.saveModules(setupData))
        add(self.saveSysconfig(setupData))
        add(self.saveDevices(setupItem))
        add(self.saveStartupcode(setupData))

        with open(setupPath, 'w') as outputFile:
            outputStringWithNewlines = ''.join(output)
            outputStringListWithNewLines = \
                outputStringWithNewlines.splitlines()
            while True:
                try:
                    outputStringListWithNewLines.remove('')
                except:  # pylint: disable=bare-except
                    break
            output = '\n'.join(outputStringListWithNewLines) + '\n'
            outputFile.write(output)

        if setupItem.setup.abspath == setupPath:
            # saved setup with same name as before; can unmark it
            setupItem.setText(0, setupItem.text(0)[1:])
            setupItem.setup.edited = False

    def saveDescription(self, setupData):
        output = []
        descriptionString = repr(str(setupData.lineEditDescription.text()))
        if not descriptionString:
            return ''
        output.append('description = ')
        output.append(descriptionString + '\n\n')
        return ''.join(output)

    def saveGroup(self, setupData):
        output = []
        groupString = repr(str(setupData.comboBoxGroup.currentText()))
        if not groupString:
            return ''
        output.append('group = ')
        output.append(groupString + '\n\n')
        return ''.join(output)

    def saveIncludes(self, setupData):
        output = []
        includes = []
        includeIndex = 0
        while includeIndex < setupData.listWidgetIncludes.count():
            includes.append(str(setupData.listWidgetIncludes.item(
                includeIndex).text()))
            includeIndex += 1
        if not includes:
            return ''
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
        if not excludes:
            return ''
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
        if not modules:
            return ''
        output.append('modules = ')
        output.append(repr(modules) + '\n\n')
        return ''.join(output)

    def saveSysconfig(self, setupData):
        output = []
        if setupData.treeWidgetSysconfig.topLevelItemCount() > 0:
            output.append('sysconfig = dict(\n')
            for key, value in setupData.treeWidgetSysconfig.getData().items():
                output.append('    ' + key + ' = ' + repr(value) + ',\n')
            output.append(')\n\n')
            return ''.join(output)
        return ''

    def saveDevices(self, setupItem):
        output = []
        childIndex = 0
        deviceItems = []
        while childIndex < setupItem.childCount():
            deviceItems.append(setupItem.child(childIndex))
            childIndex += 1

        if not deviceItems:
            return ''

        output.append('devices = dict(\n')
        for name, info in self.deviceWidgets[setupItem.setup.abspath].items():
            output.append('    ' + name + ' = device(')
            # class string must be first parameter. Also mustn't have a key.
            output.append(repr(info.parameters['Class'].getValue()) + ',\n')
            indent = len(name) + 14
            for _, params in info.parameters.iteritems():
                # skip class as it has already been added
                if not params.param == 'Class':
                    if isinstance(params.getValue(), string_types):
                        prepend = indent * ' ' + str(params.param) + ' = '
                        if params.isUnknownValue:
                            param = str(params.getValue()) + ',\n'
                        else:
                            param = repr(str(params.getValue())) + ',\n'
                    else:
                        prepend = indent * ' ' + str(params.param) + ' = '
                        param = str(params.getValue()) + ',\n'
                    output.append(prepend + param)
            output.append((indent - 1) * ' ' + '),\n')
        output.append(')\n\n')
        return ''.join(output)

    def saveStartupcode(self, setupData):
        output = []
        startupcode = setupData.textEditStartupCode.toPlainText()
        if startupcode:
            output.append("startupcode = '''\n")
            output.append(startupcode + '\n')
            output.append("'''\n")
            return ''.join(output)
        return ''
