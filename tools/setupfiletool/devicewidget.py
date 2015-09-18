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
from PyQt4.QtGui import QWidget, QSpacerItem
from PyQt4.QtCore import pyqtSignal

from setupfiletool.deviceparam import DeviceParam

from nicos.guisupport.typedvalue import create
from nicos.pycompat import string_types


class DeviceWidget(QWidget):
    editedDevice = pyqtSignal()

    def __init__(self, parent=None):
        super(DeviceWidget, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'devicewidget.ui'), self)
        self.currentWidgets = []

    def clear(self):
        self.currentWidgets = []
        for index in reversed(range(self.paramList.count())):
            if not isinstance(self.paramList.itemAt(index), QSpacerItem):
                self.paramList.itemAt(index).widget().setParent(None)
            else:
                self.paramList.takeAt(index)

    def getClassOfDevice(self, device):
        # this method gets a device and parses it's classString
        # building two modules: one for nicos devices and one for
        # instrument specific devices. it then tries to get the class in those
        # modules. If it doesn't find the class, it returns None.
        mods = self.parent().deviceModules
        myClass = device.classString.split(".")[-1]
        myMod = device.classString.split(".")
        myMod.pop()
        myMod1 = "nicos." + ".".join(myMod)
        myMod2 = "custom." + ".".join(myMod)
        myMods = [myMod1, myMod2]
        for mod in myMods:
            if mod in mods:
                myClass = getattr(mods[mod], myClass)
                return myClass
        return None

    def loadDevice(self, device):
        self.clear()

        myClass = self.getClassOfDevice(device)
        classParam = DeviceParam('Class:', create(
            self, str, device.classString))
        classParam.pushButtonRemove.setEnabled(False)
        self.paramList.addWidget(classParam)
        self.currentWidgets.append(classParam)

        for param, value in device.parameters.items():
            isUnkownValue = False
            try:
                typ = myClass.parameters[param].type
            except (AttributeError, KeyError):
                if isinstance(value, string_types):
                    # this is why can't have nice things
                    isUnkownValue = False
                else:
                    isUnkownValue = True
                typ = str
            try:
                myUnit = myClass.parameters[param].unit
            except (AttributeError, KeyError):
                myUnit = ''
            newParam = DeviceParam(param + ':', create(self,
                                                       typ,
                                                       value,
                                                       unit=myUnit))
            newParam.isUnknownValue = isUnkownValue
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
        # Planned for redesign: Only allow optional parameters to be removed
        param = self.sender().parent()
        self.currentWidgets.remove(param)
        param.setParent(None)
        self.editedDevice.emit()
