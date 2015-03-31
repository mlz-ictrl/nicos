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

from PyQt4.QtGui import QTreeWidgetItem, QMenu, QIcon
from PyQt4.QtCore import pyqtSignal

from setupfiletool.utilities.treewidgetcontextmenu import TreeWidgetContextMenu
from setupfiletool.utilities.itemtypes import ItemTypes

class TreeWidget(TreeWidgetContextMenu):
    editedSetup = pyqtSignal()


    def __init__(self, parent=None):
        TreeWidgetContextMenu.__init__(self, parent)


    def contextMenuOnItem(self, item, pos):
        if item.type() == ItemTypes.Setup:
            menu = QMenu(self)
            addDeviceAction = menu.addAction('Add device...')
            addDeviceAction.triggered.connect(self.addDevice)
            menu.popup(pos)


    def addDevice(self):
        #self->dockWidgetContents->dockWidget->MainWindow
        nicosDir = (self.parent().parent().parent().getNicosDir())
        resDir = path.join(nicosDir, 'tools', 'setupfiletool', 'res')
        newItem = QTreeWidgetItem(
            ['<New Device>', 'in file: ' + self.currentItem().text(0)],
            ItemTypes.Device)
        newItem.setIcon(0, QIcon(path.join(resDir, 'device.png')))
        self.currentItem().addChild(newItem)
        self.editedSetup.emit()
