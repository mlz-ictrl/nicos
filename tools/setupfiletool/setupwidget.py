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
"""Dialog for the setup file without the devices."""

from os import path

from nicos.guisupport.qt import uic, pyqtSignal, pyqtSlot, Qt, QWidget, \
    QTreeWidgetItem

from setupfiletool.dialogs import AddExcludeDialog, AddIncludeDialog, \
    AddModuleDialog, AddSysconfigDialog


class SetupWidget(QWidget):
    editedSetup = pyqtSignal()

    def __init__(self, setup, availablesetups, parent=None):
        QWidget.__init__(self, parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'setupwidget.ui'), self)

        # keys taken from */nicos-core/nicos_demo/skeleton/setups/system.py
        self.sysconfigKeys = ['cache',
                              'instrument',
                              'experiment',
                              'datasinks',
                              'notifiers']

        self.lineEditDescription.textEdited.connect(self.editedSetup.emit)
        self.treeWidgetSysconfig.editedSetup.connect(self.editedSetup.emit)
        self.comboBoxGroup.activated.connect(self.editedSetup.emit)

        self.lineEditDescription.setText(setup.description)
        self.comboBoxGroup.setCurrentIndex(
            self.comboBoxGroup.findText(setup.group))
        for includeItem in setup.includes:
            self.listWidgetIncludes.addItem(includeItem)
        for excludeItem in setup.excludes:
            self.listWidgetExcludes.addItem(excludeItem)
        for moduleItem in setup.modules:
            self.listWidgetModules.addItem(moduleItem)

        topLevelItems = []
        for key in self.sysconfigKeys:
            if key in setup.sysconfig:
                topLevelItems.append(QTreeWidgetItem([key]))
        self.treeWidgetSysconfig.addTopLevelItems(topLevelItems)

        for item in topLevelItems:
            if isinstance(setup.sysconfig[item.text(0)], list):
                for listItem in setup.sysconfig[item.text(0)]:
                    item.addChild(QTreeWidgetItem([listItem]))
            else:
                item.addChild(QTreeWidgetItem(
                    [setup.sysconfig[item.text(0)]]))

        if self.treeWidgetSysconfig.topLevelItemCount() == len(
                self.sysconfigKeys):  # can't add any unknown keys
            self.pushButtonAddSysconfig.setEnabled(False)
        else:
            self.pushButtonAddSysconfig.setEnabled(True)
        self.textEditStartupCode.blockSignals(True)
        self.textEditStartupCode.setPlainText(setup.startupcode[1:-1])
        self.textEditStartupCode.blockSignals(False)
        self.availablesetups = availablesetups

    def on_listWidgetIncludes_itemSelectionChanged(self):
        self.pushButtonRemoveInclude.setEnabled(
            self.listWidgetIncludes.currentRow() > -1)

    def on_listWidgetExcludes_itemSelectionChanged(self):
        self.pushButtonRemoveExclude.setEnabled(
            self.listWidgetExcludes.currentRow() > -1)

    def on_listWidgetModules_itemSelectionChanged(self):
        self.pushButtonRemoveModule.setEnabled(
            self.listWidgetModules.currentRow() > -1)

    def on_treeWidgetSysconfig_itemSelectionChanged(self):
        self.pushButtonRemoveSysconfig.setEnabled(
            len(self.treeWidgetSysconfig.selectedItems()) > 0)

    @pyqtSlot()
    def on_pushButtonRemoveInclude_clicked(self):
        self.listWidgetIncludes.takeItem(self.listWidgetIncludes.currentRow())
        self.editedSetup.emit()

    @pyqtSlot()
    def on_pushButtonRemoveExclude_clicked(self):
        self.listWidgetExcludes.takeItem(self.listWidgetExcludes.currentRow())
        self.editedSetup.emit()

    @pyqtSlot()
    def on_pushButtonRemoveModule_clicked(self):
        self.listWidgetModules.takeItem(self.listWidgetModules.currentRow())
        self.editedSetup.emit()

    @pyqtSlot()
    def on_pushButtonRemoveSysconfig_clicked(self):
        root = self.treeWidgetSysconfig.invisibleRootItem()
        cur = self.treeWidgetSysconfig.currentItem()
        (cur.parent() or root).removeChild(cur)

        if self.treeWidgetSysconfig.topLevelItemCount() == len(
                self.sysconfigKeys):  # can't add any unknown keys
            self.pushButtonAddSysconfig.setEnabled(False)
        else:
            self.pushButtonAddSysconfig.setEnabled(True)
        self.editedSetup.emit()

    def _get_unused_setups(self):
        _in = [i.text() for i in self.listWidgetIncludes.findItems(
               '', Qt.MatchContains)]
        _ex = [i.text() for i in self.listWidgetExcludes.findItems(
               '', Qt.MatchContains)]
        return list(set(self.availablesetups) - set(_in + _ex))

    @pyqtSlot()
    def on_pushButtonAddInclude_clicked(self):
        dlg = AddIncludeDialog(self._get_unused_setups())
        if dlg.exec_():
            newIncludes = dlg.getValue()
            if newIncludes:
                for include in newIncludes:
                    self.listWidgetIncludes.addItem(include)
                    self.editedSetup.emit()

    @pyqtSlot()
    def on_pushButtonAddExclude_clicked(self):
        dlg = AddExcludeDialog(self._get_unused_setups())
        if dlg.exec_():
            newExcludes = dlg.getValue()
            if newExcludes:
                for exclude in newExcludes:
                    self.listWidgetExcludes.addItem(exclude)
                    self.editedSetup.emit()

    @pyqtSlot()
    def on_pushButtonAddModule_clicked(self):
        dlg = AddModuleDialog()
        if dlg.exec_():
            newModule = dlg.getValue()
            if newModule:
                self.listWidgetModules.addItem(newModule)
                self.editedSetup.emit()

    @pyqtSlot()
    def on_pushButtonAddSysconfig_clicked(self):
        dlg = AddSysconfigDialog()
        i = 0
        topLevelItems = []
        while i < self.treeWidgetSysconfig.topLevelItemCount():
            # apparently, text() returns a unicode string..? Therefore str()
            topLevelItems.append(
                str(self.treeWidgetSysconfig.topLevelItem(i).text(0)))
            i += 1

        for key in self.sysconfigKeys:
            if key not in topLevelItems:
                dlg.comboBoxNewSysconfig.addItem(key)

        if dlg.exec_():
            key = dlg.comboBoxNewSysconfig.currentText()
            value = dlg.lineEditValue.text()

            self.treeWidgetSysconfig.addTopLevelItem(QTreeWidgetItem([key]))
            if value:
                currentIndex = 0
                while currentIndex < self.treeWidgetSysconfig.\
                        topLevelItemCount():
                    if self.treeWidgetSysconfig.topLevelItem(
                            currentIndex).text(0) == key:
                        self.treeWidgetSysconfig.topLevelItem(currentIndex
                                                              ).addChild(
                            QTreeWidgetItem([value]))
                    currentIndex += 1
            if self.treeWidgetSysconfig.topLevelItemCount() == len(
                    self.sysconfigKeys):
                self.pushButtonAddSysconfig.setEnabled(False)
            self.editedSetup.emit()

    @pyqtSlot()
    def on_textEditStartupCode_textChanged(self):
        # Because I'm blocking the textEdit's signals when clearing it and when
        # loading data from a setup, textChagned will only be emitted when the
        # user himself changes the text.
        # Comparable to QLineEdit's textEdited signal. Sadly, QTextEdit does
        # not implement this.
        self.editedSetup.emit()

    def clear(self):
        self.lineEditDescription.clear()
        self.comboBoxGroup.setCurrentIndex(0)
        while self.listWidgetIncludes.count() > 0:
            self.listWidgetIncludes.takeItem(0)
        while self.listWidgetExcludes.count() > 0:
            self.listWidgetExcludes.takeItem(0)
        while self.listWidgetModules.count() > 0:
            self.listWidgetModules.takeItem(0)
        self.treeWidgetSysconfig.clear()
        self.textEditStartupCode.blockSignals(True)
        self.textEditStartupCode.clear()
        self.textEditStartupCode.blockSignals(False)
