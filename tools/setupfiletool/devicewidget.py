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

from setupfiletool.deviceparam import DeviceParam

class DeviceWidget(QWidget):
    def __init__(self, parent=None):
        super(DeviceWidget, self).__init__(parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'devicewidget.ui'), self)
        self.info = {}

    def on_listWidgetParameters_itemSelectionChanged(self):
        items = self.listWidgetParameters.selectedItems()
        for item in items: #no more than one item can be selected
            itm = item.text()
        self.textEditValues.setPlainText(repr(self.info[itm]))


    def clear(self):
        self.currentDevice = None
        for index in reversed(range(self.paramList.count())):
            if not isinstance(self.paramList.itemAt(index), QSpacerItem):
                self.paramList.itemAt(index).widget().setParent(None)
            else:
                self.paramList.takeAt(index)


    def loadDevice(self, device):
        self.clear()
        self.currentDevice = device
        classParam = DeviceParam(self, 'Class:', device.classString)
        self.paramList.addWidget(classParam)

        currentWidgets = []
        currentWidgets.append(classParam)
        for key, value in device.parameters.iteritems():
            newParam = DeviceParam(self, key + ':', repr(value))
            self.paramList.addWidget(newParam)
            currentWidgets.append(newParam)
        self.paramList.addStretch()

        #get necessary width to align labels
        maxWidth = 100 #default minimum 100
        for widget in currentWidgets:
            labelWidth = widget.labelParam.sizeHint().width()

            if labelWidth > maxWidth:
                maxWidth = labelWidth
        for widget in currentWidgets:
            widget.labelParam.setMinimumWidth(maxWidth)
