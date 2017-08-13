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

from nicos.guisupport.qt import pyqtSignal, QMenu, QMessageBox, QTreeWidgetItem

from setupfiletool.utilities.treewidgetcontextmenu import TreeWidgetContextMenu
from setupfiletool.dialogs import NewValueDialog


class SysconfigWidget(TreeWidgetContextMenu):
    editedSetup = pyqtSignal()

    def __init__(self, parent=None):
        TreeWidgetContextMenu.__init__(self, parent)
        # a list of items of a sysconfig that allow only one value.
        # the others, 'datasinks' and 'notifiers', allow mulitple values.
        # this information was taken from
        # nicos-core/nicos_demo/skeleton/setups/system.py
        self.nonListItems = ['cache', 'instrument', 'experiment']

    def contextMenuOnItem(self, item, pos):
        if item is None:
            return  # invoked context menu on whitespace

        topLevelItems = []
        currentIndex = 0
        while currentIndex < self.topLevelItemCount():
            topLevelItems.append(self.topLevelItem(currentIndex))
            currentIndex += 1
        if self.currentItem() in topLevelItems:
            if self.currentItem().text(0) in self.nonListItems:
                if self.currentItem().childCount() > 0:
                    return  # value is already set, can't add multiple values
            menu = QMenu(self)
            addValueAction = menu.addAction('Add value...')
            addValueAction.triggered.connect(self.addValue)
            menu.popup(pos)

    def addValue(self):
        dlg = NewValueDialog()
        if dlg.exec_():
            value = dlg.getValue()
            if not value:
                QMessageBox.warning(self, 'Error', 'No value entered.')
                return
            self.currentItem().addChild(QTreeWidgetItem([value]))
            self.editedSetup.emit()

    def getData(self):
        # returns the sysconfig as a dict. the items on self.nonListItems
        # have strings as values, the others ('datasinks' and 'notifiers')
        # have a list of strings as value.
        # if the item exists but there is no value in the tree, the value
        # in the dict will be set to 'None'.
        info = {}
        index = 0
        while index < self.topLevelItemCount():
            curItem = self.topLevelItem(index)
            if curItem.childCount() > 0:
                if curItem.text(0) in self.nonListItems:
                    info[str(curItem.text(0))] = str(curItem.child(0).text(0))
                else:
                    childIndex = 0
                    values = []
                    while childIndex < curItem.childCount():
                        values.append(str(curItem.child(childIndex).text(0)))
                        childIndex += 1
                    info[str(curItem.text(0))] = values
            else:
                info[curItem.text(0)] = None
            index += 1
        return info
