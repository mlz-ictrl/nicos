#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
"""Widget to display the setups and devices in the tree."""

from copy import deepcopy
from os import path

from nicos.guisupport.qt import pyqtSignal, Qt, QIcon, QMenu, QMessageBox, \
    QTreeWidgetItem

from nicos.guisupport.utils import waitCursor

from setupfiletool import classparser, setupcontroller
from setupfiletool.dialogs import NewDeviceDialog, NewSetupDialog
from setupfiletool.utilities.treewidgetcontextmenu import TreeWidgetContextMenu
from setupfiletool.utilities.utilities import ItemTypes, getNicosDir, getResDir


class TreeWidget(TreeWidgetContextMenu):
    # Signal to be emitted when deleting a device.
    # QTreeWidgetItem = Item of device's setup, str = device's name
    deviceRemoved = pyqtSignal(QTreeWidgetItem, str)
    # Signal to be emitted when creating new device.
    # QTreeWidgetItem = Item of device's setup, str = device's name
    deviceAdded = pyqtSignal(QTreeWidgetItem, str)
    newDeviceAdded = pyqtSignal(str, str)

    def __init__(self, parent=None):
        TreeWidgetContextMenu.__init__(self, parent)
        self.dragItem = None

        # don't allow dropping items in root
        root = self.invisibleRootItem()
        root.setFlags(root.flags() & ~Qt.ItemIsDropEnabled)

    def loadNicosData(self):
        while self.topLevelItemCount() > 0:
            self.takeTopLevelItem(0)

        # list of topLevelItems representing the directories in
        # */nicos-core/custom: for example instruments, ...
        self.topLevelItems = []
        for directory in setupcontroller.setup_directories:
            self.topLevelItems.append(
                QTreeWidgetItem([directory], ItemTypes.Directory))
        self.addTopLevelItems(self.topLevelItems)

        # ask the controller to return the setups for current directory
        # add the setups as childitems
        for setup_directory in self.topLevelItems:
            # directories can neither be dragged nor have something dropped on
            setup_directory.setFlags(setup_directory.flags() &
                                     ~Qt.ItemIsDragEnabled &
                                     ~Qt.ItemIsDropEnabled)
            setup_directory.setIcon(0, QIcon(path.join(getResDir(),
                                    'folder.png')))
            for setup in setupcontroller.setup_directories[
                    setup_directory.text(0)]:
                treeWidgetItem = QTreeWidgetItem([setup.name],
                                                 ItemTypes.Setup)
                # scripts cannot be dragged, but they can have
                # something dropped on them (a device).
                treeWidgetItem.setFlags(treeWidgetItem.flags() &
                                        ~Qt.ItemIsDragEnabled)
                treeWidgetItem.setIcon(0, QIcon(
                    path.join(getResDir(), 'setup.png')))
                treeWidgetItem.setup = setup
                setup_directory.addChild(treeWidgetItem)

            # setup for this directory has been loaded, add the devices.
            currentIndex = 0
            while currentIndex < setup_directory.childCount():
                currentItem = setup_directory.child(currentIndex)
                setup = currentItem.setup
                devices = setup.devices.keys()
                for device in devices:
                    # read setup and add all the devices as child tree items
                    deviceItem = QTreeWidgetItem([device],
                                                 ItemTypes.Device)
                    # devices can be dragged, but they can't have something
                    # dropped on them.
                    deviceItem.setFlags(deviceItem.flags() &
                                        ~Qt.ItemIsDropEnabled)
                    deviceItem.device = setup.devices[device]
                    currentItem.addChild(deviceItem)

                # icons for all devices
                deviceIndex = 0
                while deviceIndex < currentItem.childCount():
                    currentItem.child(deviceIndex).setIcon(
                        0, QIcon(path.join(getResDir(), 'device.png')))
                    deviceIndex += 1
                currentIndex += 1

        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)

    def dragEnterEvent(self, event):
        TreeWidgetContextMenu.dragEnterEvent(self, event)
        self.dragItem = self.currentItem()

    def dragMoveEvent(self, event):
        TreeWidgetContextMenu.dragMoveEvent(self, event)

    def dropEvent(self, event):
        """
        To satisfy Qt, a call to TreeWidgetContextMenu.dropEvent is neccessary.

        Else, the animation would look really gross and suggest the object
        might actually not have been copied.
        But after the call, the newly appended child item seems to be
        completely useless: It carries neither data nor does it emit the
        treeWidget's itemActivated signal.
        This may be a bug or my inability to find what's wrong.
        Because of that, I need to construct my own item, find the old one and
        replace it with my new one.
        """
        target = self.getSetupOfDropPos(event.pos())
        if self.dragItem.device.name in target.setup.devices.keys():
            QMessageBox.warning(self, 'Error', 'The target setup already '
                                'contains a device with that name!')
            self.dragItem = None
            event.ignore()
            return
        count = 0
        previousItems = []
        while count < target.childCount():
            previousItems.append(target.child(count))
            count += 1
        TreeWidgetContextMenu.dropEvent(self, event)
        count = 0
        afterDropItems = []
        while count < target.childCount():
            afterDropItems.append(target.child(count))
            count += 1
        newItem = None
        for child in afterDropItems:
            if child not in previousItems:
                newItem = child
        index = target.indexOfChild(newItem)
        target.takeChild(index)
        deviceName = self.dragItem.device.name
        target.setup.devices[deviceName] = deepcopy(self.dragItem.device)
        deviceItem = QTreeWidgetItem([deviceName], ItemTypes.Device)
        deviceItem.setFlags(deviceItem.flags() & ~Qt.ItemIsDropEnabled)
        deviceItem.device = target.setup.devices[deviceName]
        deviceItem.setIcon(0, QIcon(path.join(getResDir(), 'device.png')))
        target.insertChild(index, deviceItem)
        self.deviceAdded.emit(target, deviceName)
        self.itemActivated.emit(deviceItem, 0)

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
            found = directory.text(0) == instrument
            directory.setHidden(not found)
            directory.setExpanded(found)

    def setAllInstrumentsVisible(self):
        for directory in self.topLevelItems:
            directory.setHidden(False)
            directory.setExpanded(False)

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

    def removeDevice(self):
        # It's neccessary to connect this signal in mainwindow,
        # because if the user currently views this device's widget,
        # mainwindow has to switch to a different widget.
        deviceItem = self.currentItem()
        setupItem = deviceItem.parent()
        del setupItem.setup.devices[deviceItem.device.name]
        indexOfDevice = setupItem.indexOfChild(deviceItem)

        setupItem.takeChild(indexOfDevice)
        self.deviceRemoved.emit(setupItem,
                                deviceItem.device.name)

    def getCurrentInstrument(self):
        if self.currentItem().type() == ItemTypes.Directory:
            return self.currentItem()
        elif self.currentItem().type() == ItemTypes.Setup:
            return self.currentItem().parent()
        elif self.currentItem().type() == ItemTypes.Device:
            return self.currentItem().parent().parent()
        return None

    def newSetup(self):
        treeWidgetItem, instrument = self._newSetup(None)
        if not treeWidgetItem:
            return
        for item in self.topLevelItems:
            if item.text(0) == instrument:
                item.addChild(treeWidgetItem)
                self.itemActivated.emit(treeWidgetItem, 0)

    def addSetup(self):
        instrument = self.getCurrentInstrument()
        treeWidgetItem, _ = self._newSetup(instrument.text(0))
        if not treeWidgetItem:
            return
        instrument.addChild(treeWidgetItem)
        self.itemActivated.emit(treeWidgetItem, 0)

    def _newSetup(self, instrument=None):
        dlg = NewSetupDialog([item.text(0) for item in self.topLevelItems
                              if item.type() == ItemTypes.Directory],
                             instrument)
        if dlg.exec_():
            fileName = dlg.getValue()
            if not fileName:
                QMessageBox.warning(self, 'Error', 'No setup name entered.')
                return None, None

            if not fileName.endswith('.py'):
                fileName += '.py'
            if dlg.isSpecialSetup():
                abspath = path.join(getNicosDir(),
                                    'nicos_mlz',
                                    dlg.currentInstrument(),
                                    'setups',
                                    'special',
                                    fileName)
            else:
                abspath = path.join(getNicosDir(),
                                    'nicos_mlz',
                                    dlg.currentInstrument(),
                                    'setups',
                                    fileName)
            try:
                open(abspath, 'w').close()
            except IOError:
                QMessageBox.warning(self, 'Error', 'Could not create new '
                                    'setup!')
                return None, None

            setupcontroller.addSetup(dlg.currentInstrument(), abspath)
            newSetup = None
            for setup in setupcontroller.setup_directories[
                dlg.currentInstrument()]:
                if setup.abspath == abspath:
                    newSetup = setup
            treeWidgetItem = QTreeWidgetItem(['*' + newSetup.name],
                                             ItemTypes.Setup)
            treeWidgetItem.setFlags(treeWidgetItem.flags() &
                                    ~Qt.ItemIsDragEnabled)
            treeWidgetItem.setIcon(0, QIcon(
                path.join(getResDir(), 'setup.png')))
            treeWidgetItem.setup = newSetup
            treeWidgetItem.setup.edited = True
            return treeWidgetItem, dlg.currentInstrument()
        return None, None

    def addDevice(self):
        with waitCursor():
            dlg = NewDeviceDialog(classparser.getDeviceClasses
                                  (self.getCurrentInstrument().text(0)), self)

        if dlg.exec_():
            if not dlg.labelSelectedClass.text():
                QMessageBox.warning(self, 'Error', 'No class selected.')
                return
            if not dlg.lineEditDeviceName.text():
                QMessageBox.warning(self, 'Error', 'No name entered.')
                return
            if dlg.lineEditDeviceName.text() in\
                    self.currentItem().setup.devices.keys():
                QMessageBox.warning(self, 'Error', 'Setup already contains a '
                                    'device with that name!')
                return
            self.newDeviceAdded.emit(dlg.lineEditDeviceName.text(),
                                     dlg.labelSelectedClass.text())
