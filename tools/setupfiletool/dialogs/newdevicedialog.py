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

from os import path

from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog, QMenu

from setupfiletool import classparser


class NewDeviceDialog(QDialog):
    def __init__(self, classesList, parent=None):
        super(NewDeviceDialog, self).__init__(parent)
        uic.loadUi(path.abspath(path.join(path.dirname(__file__),
                                          '..',
                                          'ui',
                                          'dialogs',
                                          'newdevicedialog.ui')), self)
        self.menu = QMenu('Select class')
        self.pushButtonSelectClass.setMenu(self.menu)
        for _class in sorted([str(__class)[14:-2] for __class in classesList]):
            self.recursiveMenu(_class, self.menu)

        self.menuCustom = QMenu('Select class')
        for _class in sorted([str(__class)[14:-2] for __class in
                              classparser.getDeviceClasses(None)]):
            self.recursiveMenu(_class, self.menuCustom)

        self.checkBoxCustomClasses.stateChanged.connect(
            self.stateChangedHandler)

    def stateChangedHandler(self, state):
        if state == Qt.Checked:
            self.pushButtonSelectClass.setMenu(self.menuCustom)
        else:
            self.pushButtonSelectClass.setMenu(self.menu)

    def recursiveMenu(self, partialString, parentMenu):
        if len(partialString.split('.')) == 1:
            action = parentMenu.addAction(partialString)
            action.triggered.connect(self.classSelectedSlot)
        else:
            uncombinedNextPartialString = partialString.split('.')
            menus = parentMenu.findChildren(QMenu)

            submenuIsPresent = False
            submenu = None
            for menu in menus:
                if menu.title() == uncombinedNextPartialString[0]:
                    submenu = menu
                    uncombinedNextPartialString.pop(0)
                    submenuIsPresent = True

            if not submenuIsPresent:
                submenu = QMenu(uncombinedNextPartialString.pop(0), parentMenu)
                parentMenu.addMenu(submenu)

            nextPartialString = '.'.join(uncombinedNextPartialString)
            self.recursiveMenu(nextPartialString, submenu)

    def classSelectedSlot(self):
        stringList = []
        self.recursiveActionParent(self.sender(), stringList)
        stringList.append(self.sender().text())
        self.labelSelectedClass.setText('.'.join(stringList))

    def recursiveActionParent(self, action, partialStringList):
        if action.parent() == self.menu:
            return
        elif action.parent() == self.menuCustom:
            return
        partialStringList.insert(0, action.parent().title())
        self.recursiveActionParent(action.parent(), partialStringList)
