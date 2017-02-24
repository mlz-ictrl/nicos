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
"""Classes to handle the devices."""

from os import path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QMessageBox, QSpacerItem, QWidget

from nicos.guisupport.typedvalue import create
from nicos.pycompat import string_types

from setupfiletool import classparser
from setupfiletool.deviceparam import DeviceParam
from setupfiletool.dialogs import AddParameterDialog


class DeviceWidget(QWidget):
    editedDevice = pyqtSignal()

    def __init__(self, parent=None):
        super(DeviceWidget, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'devicewidget.ui'), self)
        self.parameters = {}
        self.pushButtonAdd.clicked.connect(self.addParameter)

    def addParameter(self):
        dlg = AddParameterDialog(self.myClass.parameters, self.parameters)

        if dlg.exec_():
            param = dlg.getValue()
            if not param:
                QMessageBox.warning(self, 'Error',
                                    'No name parameter name entered.')
            if param in self.parameters.keys():
                QMessageBox.warning(self, 'Error', 'Parameter already exists.')
                return
            self.parametersLayout.takeAt(self.parametersLayout.count() - 1)
            newParam = self.createParameterWidget(param, '')
            self.parametersLayout.addWidget(newParam)
            self.parameters[param] = newParam
            self.parametersLayout.addStretch()
            self.setOptimalWidth()
            self.editedDevice.emit()

    def clear(self):
        self.parameters.clear()
        for index in reversed(range(self.parametersLayout.count())):
            if not isinstance(
                    self.parametersLayout.itemAt(index), QSpacerItem):
                self.parametersLayout.itemAt(index).widget().setParent(None)
            else:
                self.parametersLayout.takeAt(index)

    def getClassOfDevice(self, device):
        myClass = device.classString.split('.')[-1]
        mod = device.classString.split('.')
        mod.pop()
        mod = '.'.join(mod)
        return getattr(classparser.modules[mod], myClass)

    def loadDevice(self, device):
        self.clear()
        errors = []
        try:
            self.myClass = self.getClassOfDevice(device)
        except KeyError as e:
            errors.append('Failed to load class ' + str(e))
        if errors:
            QMessageBox.warning(self,
                                'Errors',
                                '\n'.join(errors))
            self.pushButtonAdd.setEnabled(False)
            return

        classParam = DeviceParam('Class', create(
            self, str, device.classString))
        classParam.pushButtonRemove.setVisible(False)
        classParam.placeholder.setVisible(True)
        classParam.valueWidget.setEnabled(False)
        self.parametersLayout.addWidget(classParam)
        self.parameters['Class'] = classParam

        mandatoryParams = []
        optionalParams = []
        for param in sorted(device.parameters):
            try:
                mandatory = self.myClass.parameters[param].mandatory
            except (AttributeError, KeyError):
                mandatory = False
            if mandatory:
                mandatoryParams.append(param)
            else:
                optionalParams.append(param)

        for param in mandatoryParams:
            value = device.parameters[param]
            newParam = self.createParameterWidget(param, value)
            self.parametersLayout.addWidget(newParam)
            self.parameters[param] = newParam
        for param in optionalParams:
            value = device.parameters[param]
            newParam = self.createParameterWidget(param, value)
            self.parametersLayout.addWidget(newParam)
            self.parameters[param] = newParam

        self.parametersLayout.addStretch()
        self.setOptimalWidth()

    def createParameterWidget(self, param, value):
        isUnkownValue = False
        try:
            typ = self.myClass.parameters[param].type
        except (AttributeError, KeyError):
            if isinstance(value, string_types):
                isUnkownValue = False
            else:
                isUnkownValue = True
            typ = type(value)
            if typ is None:
                typ = str
        try:
            myUnit = self.myClass.parameters[param].unit
        except (AttributeError, KeyError):
            myUnit = ''
        newParam = DeviceParam(param, create(self,
                                             typ,
                                             value,
                                             unit=myUnit))
        newParam.isUnknownValue = isUnkownValue
        try:
            newParam.labelParam.setToolTip(self.myClass.parameters[
                param].description)
        except:  # pylint: disable=bare-except
            newParam.labelParam.setToolTip('No info found.')
        try:
            mandatory = self.myClass.parameters[param].mandatory
        except (AttributeError, KeyError):
            mandatory = False
        if mandatory:
            newParam.pushButtonRemove.setVisible(False)
            newParam.placeholder.setVisible(True)
        newParam.editedParam.connect(self.editedDevice.emit)
        newParam.clickedRemoveButton.connect(self.removeParam)
        return newParam

    def setOptimalWidth(self):
        # get necessary width to align labels
        maxWidth = 100  # default minimum 100
        for _, widget in self.parameters.iteritems():
            labelWidth = widget.labelParam.sizeHint().width()

            if labelWidth > maxWidth:
                maxWidth = labelWidth
        for _, widget in self.parameters.iteritems():
            widget.labelParam.setMinimumWidth(maxWidth)

    def removeParam(self, param):
        # param is a parameter's name, which works as a key for self.parameters
        self.parameters[param].setParent(None)
        del self.parameters[param]
        self.editedDevice.emit()
