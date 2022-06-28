#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

from nicos.guisupport.qt import QDialog, QDialogButtonBox, QMenu, \
    QRegularExpression, QRegularExpressionValidator, Qt, uic

from .. import classparser
from ..utilities.utilities import getClass


class NewDeviceDialog(QDialog):
    def __init__(self, classesList, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(path.abspath(path.join(path.dirname(__file__),
                                          '..',
                                          'ui',
                                          'dialogs',
                                          'newdevicedialog.ui')), self)
        self.menu = QMenu('Select class')
        self.menuCustom = QMenu('Select class')

        for _class in sorted([getClass(__class) for __class in classesList]):
            self.recursiveMenu(_class, self.menu)

        for _class in sorted([getClass(__class) for __class in
                              classparser.getDeviceClasses(None)]):
            if _class.startswith('nicos.'):
                self.recursiveMenu(_class, self.menu)
            else:
                self.recursiveMenu(_class, self.menuCustom)

        self.checkBoxCustomClasses.stateChanged.connect(
            self.stateChangedHandler)

        self.lineEditDeviceName.setValidator(QRegularExpressionValidator(
            QRegularExpression('[A-Za-z0-9_]*')))
        self.pushButtonSelectClass.setMenu(self.menu)
        self.buttonBox.button(QDialogButtonBox.Ok).setDisabled(True)
        self.lineEditDeviceName.textChanged['const QString &'].connect(
            self.devChanged)

    def devChanged(self, text):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            bool(text) and bool(self.labelSelectedClass.text()))

    def stateChangedHandler(self, state):
        if state == Qt.Checked:
            self.pushButtonSelectClass.setMenu(self.menuCustom)
        else:
            self.pushButtonSelectClass.setMenu(self.menu)

    def recursiveMenu(self, partialString, parentMenu):
        if not partialString.count('.'):
            action = parentMenu.addAction(partialString)
            action.triggered.connect(self.classSelectedSlot)
        else:
            uncombinedNextPartialString = partialString.split('.')
            submenu = None
            for menu in parentMenu.findChildren(
                QMenu, options=Qt.FindDirectChildrenOnly):
                if menu.title() == uncombinedNextPartialString[0]:
                    submenu = menu
                    uncombinedNextPartialString.pop(0)
                    break

            if not submenu:
                submenu = QMenu(uncombinedNextPartialString.pop(0), parentMenu)
                parentMenu.addMenu(submenu)

            nextPartialString = '.'.join(uncombinedNextPartialString)
            self.recursiveMenu(nextPartialString, submenu)

    def classSelectedSlot(self):
        stringList = []
        self.recursiveActionParent(self.sender(), stringList)
        stringList.append(self.sender().text())
        self.labelSelectedClass.setText('.'.join(stringList))
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            bool(self.lineEditDeviceName.text()) and bool(stringList))

    def recursiveActionParent(self, action, partialStringList):
        if action.parent() in [self.menu, self.menuCustom]:
            return
        partialStringList.insert(0, action.parent().title())
        self.recursiveActionParent(action.parent(), partialStringList)
