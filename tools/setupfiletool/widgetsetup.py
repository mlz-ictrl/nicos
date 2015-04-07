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

from PyQt4 import uic
from PyQt4.QtGui import QWidget, QTreeWidgetItem
from PyQt4.QtCore import pyqtSignal, pyqtSlot

from setupfiletool.dialogs.addincludedialog import AddIncludeDialog
from setupfiletool.dialogs.addexcludedialog import AddExcludeDialog
from setupfiletool.dialogs.addmoduledialog import AddModuleDialog
from setupfiletool.dialogs.addsysconfigdialog import AddSysconfigDialog

class WidgetSetup(QWidget):
    editedSetup = pyqtSignal()


    def __init__(self, parent = None):
        super(WidgetSetup, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'widgetsetup.ui'), self)

        #keys taken from */nicos-core/custom/skeleton/setups/system.py
        self.sysconfigKeys = ['cache',
                              'instrument',
                              'experiment',
                              'datasinks',
                              'notifiers']

        self.lineEditDescription.textEdited.connect(self.editedSetup.emit)
        self.comboBoxGroup.activated.connect(self.editedSetup.emit)


    def on_listWidgetIncludes_itemSelectionChanged(self):
        if self.listWidgetIncludes.currentRow() > -1:
            self.pushButtonRemoveInclude.setEnabled(True)
        else:
            self.pushButtonRemoveInclude.setEnabled(False)


    def on_listWidgetExcludes_itemSelectionChanged(self):
        if self.listWidgetExcludes.currentRow() > -1:
            self.pushButtonRemoveExclude.setEnabled(True)
        else:
            self.pushButtonRemoveExclude.setEnabled(False)


    def on_listWidgetModules_itemSelectionChanged(self):
        if self.listWidgetModules.currentRow() > -1:
            self.pushButtonRemoveModule.setEnabled(True)
        else:
            self.pushButtonRemoveModule.setEnabled(False)


    def on_treeWidgetSysconfig_itemSelectionChanged(self):
        if len(self.treeWidgetSysconfig.selectedItems()) == 0:
            self.pushButtonRemoveSysconfig.setEnabled(False)
        else:
            self.pushButtonRemoveSysconfig.setEnabled(True)


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
            self.sysconfigKeys): #can't add any unknown keys
            self.pushButtonAddSysconfig.setEnabled(False)
        else:
            self.pushButtonAddSysconfig.setEnabled(True)
        self.editedSetup.emit()

    @pyqtSlot()
    def on_pushButtonAddInclude_clicked(self):
        dlg = AddIncludeDialog()
        if dlg.exec_():
            newInclude = dlg.lineEditNewInclude.text()
            if newInclude:
                self.listWidgetIncludes.addItem(newInclude)
                self.editedSetup.emit()


    @pyqtSlot()
    def on_pushButtonAddExclude_clicked(self):
        dlg = AddExcludeDialog()
        if dlg.exec_():
            newExclude = dlg.lineEditNewExclude.text()
            if newExclude:
                self.listWidgetExcludes.addItem(newExclude)
                self.editedSetup.emit()


    @pyqtSlot()
    def on_pushButtonAddModule_clicked(self):
        dlg = AddModuleDialog()
        if dlg.exec_():
            newModule = dlg.lineEditNewModule.text()
            if newModule:
                self.listWidgetModules.addItem(newModule)
                self.editedSetup.emit()


    @pyqtSlot()
    def on_pushButtonAddSysconfig_clicked(self):
        dlg = AddSysconfigDialog()
        i = 0
        topLevelItems = []
        while i < self.treeWidgetSysconfig.topLevelItemCount():
            #apparently, text() returns a unicode string..? Therefore str()
            topLevelItems.append(str(self.treeWidgetSysconfig.topLevelItem(
                i).text(0)))
            i += 1

        for key in self.sysconfigKeys:
            if not key in topLevelItems:
                dlg.comboBoxNewSysconfig.addItem(key)

        if dlg.exec_():
            key = dlg.comboBoxNewSysconfig.currentText()
            value = dlg.lineEditValue.text()

            self.treeWidgetSysconfig.addTopLevelItem(QTreeWidgetItem([key]))
            if value:
                currentIndex = 0
                while currentIndex < self.treeWidgetSysconfig.topLevelItemCount(
                    ):
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
        #Because I'm blocking the textEdit's signals when clearing it and when
        #loading data from a setup, textChagned will only be emitted when the
        #user himself changes the text.
        #Comparable to QLineEdit's textEdited signal. Sadly, QTextEdit does not
        #implement this.
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


    def loadData(self, info):
        self.lineEditDescription.setText(info['description'])
        self.comboBoxGroup.setCurrentIndex(
            self.comboBoxGroup.findText(info['group']))
        for includeItem in info['includes']:
            self.listWidgetIncludes.addItem(includeItem)
        for excludeItem in info['excludes']:
            self.listWidgetExcludes.addItem(excludeItem)
        for moduleItem in info['modules']:
            self.listWidgetModules.addItem(moduleItem)

        topLevelItems = []
        for key in self.sysconfigKeys:
            if key in info['sysconfig']:
                topLevelItems.append(QTreeWidgetItem([key]))
        self.treeWidgetSysconfig.addTopLevelItems(topLevelItems)

        for item in topLevelItems:
            if isinstance(info['sysconfig'][item.text(0)], list):
                for listItem in info['sysconfig'][item.text(0)]:
                    item.addChild(QTreeWidgetItem([listItem]))
            else:
                item.addChild(QTreeWidgetItem(
                    [info['sysconfig'][item.text(0)]]))

        if self.treeWidgetSysconfig.topLevelItemCount() == len(
            self.sysconfigKeys): #can't add any unknown keys
            self.pushButtonAddSysconfig.setEnabled(False)
        else:
            self.pushButtonAddSysconfig.setEnabled(True)
        self.textEditStartupCode.blockSignals(True)
        self.textEditStartupCode.setPlainText(info['startupcode'][1:-1])
        self.textEditStartupCode.blockSignals(False)
        self.setupHandler.setupDisplayed = True


    def setSetupHandler(self, setupHandler):
        self.setupHandler = setupHandler
