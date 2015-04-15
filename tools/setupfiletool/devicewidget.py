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
from PyQt4.QtGui import QWidget, QSpacerItem, QInputDialog, QMessageBox
from PyQt4.QtCore import pyqtSignal

from setupfiletool.deviceparam import DeviceParam


class DeviceWidget(QWidget):
    editedDevice = pyqtSignal()

    def __init__(self, parent=None):
        super(DeviceWidget, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'devicewidget.ui'), self)

        self.pushButtonAdd.clicked.connect(self.addParam)
        self.currentWidgets = []

    def clear(self):
        self.currentWidgets = []
        for index in reversed(range(self.paramList.count())):
            if not isinstance(self.paramList.itemAt(index), QSpacerItem):
                self.paramList.itemAt(index).widget().setParent(None)
            else:
                self.paramList.takeAt(index)

    def loadDevice(self, device):
        self.clear()
        classParam = DeviceParam(self, 'Class:', device.classString)
        classParam.pushButtonRemove.setEnabled(False)
        self.paramList.addWidget(classParam)

        self.currentWidgets.append(classParam)
        for key, value in device.parameters.iteritems():
            newParam = DeviceParam(self, key + ':', value)
            self.paramList.addWidget(newParam)
            self.currentWidgets.append(newParam)
        self.paramList.addStretch()

        for widget in self.currentWidgets:
            widget.pushButtonRemove.clicked.connect(self.removeParam)
            widget.pushButtonRemove.clicked.connect(self.editedDevice.emit)
            widget.editedParam.connect(self.editedDevice.emit)
        self.setOptimalWidth()

    def setOptimalWidth(self):
        # get necessary width to align labels
        maxWidth = 100  # default minimum 100
        for widget in self.currentWidgets:
            labelWidth = widget.labelParam.sizeHint().width()

            if labelWidth > maxWidth:
                maxWidth = labelWidth
        for widget in self.currentWidgets:
            widget.labelParam.setMinimumWidth(maxWidth)

    def removeParam(self):
        # removes the widget calling this function
        param = self.sender().parent()
        self.currentWidgets.remove(param)
        param.setParent(None)
        self.editedDevice.emit()

    def addParam(self):
        newParam = QInputDialog.getText(self,
                                        'New parameter...',
                                        'Enter a new parameter:')
        if not newParam[1]:
            return  # user pressed cancel

        newParam = str(newParam[0])

        if not newParam:
            QMessageBox.warning(self,
                                'Error',
                                'No name entered for parameter.')
            return
        newParam = newParam + ':'
        self.paramList.takeAt(self.paramList.count() - 1)  # remove stretch
        newParamWidget = DeviceParam(self, newParam, '')
        newParamWidget.pushButtonRemove.clicked.connect(self.removeParam)
        newParamWidget.pushButtonRemove.clicked.connect(self.editedDevice.emit)
        newParamWidget.editedParam.connect(self.editedDevice.emit)
        self.paramList.addWidget(newParamWidget)
        self.currentWidgets.append(newParamWidget)
        self.setOptimalWidth()
        self.paramList.addStretch()
        self.editedDevice.emit()
