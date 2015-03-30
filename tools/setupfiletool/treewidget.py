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

from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QMenu, QIcon

class TreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            pos = event.globalPos()
            item = self.itemAt(event.pos())
        else:
            pos = None
            selection = self.selectedItems()
            if selection:
                item = selection[0]
            else:
                item = self.currentItem()
                if item is None:
                    item = self.invisibleRootItem().child(0)
            if item is not None:
                parent = item.parent()
                while parent is not None:
                    parent.setExpanded(True)
                    parent = parent.parent()
                itemrect = self.visualItemRect(item)
                portrect = self.viewport().rect()
                if not portrect.contains(itemrect.topLeft()):
                    self.scrollToItem(
                        item, QTreeWidget.PositionAtCenter)
                    itemrect = self.visualItemRect(item)
                itemrect.setLeft(portrect.left())
                itemrect.setWidth(portrect.width())
                pos = self.mapToGlobal(itemrect.center())
        if pos is not None:
            if item.text(1):
                menu = QMenu(self)
                addDeviceAction = menu.addAction('Add device...')
                addDeviceAction.triggered.connect(self.addDevice)
                menu.popup(pos)
        event.accept()

    def addDevice(self):
        #self->dockWidgetContents->dockWidget->MainWindow
        nicosDir = (self.parent().parent().parent().getNicosDir())
        resDir = path.join(nicosDir, 'tools', 'setupfiletool', 'res')
        newItem = QTreeWidgetItem(['<New Device>'])
        newItem.setIcon(0, QIcon(path.join(resDir, 'device.png')))
        self.currentItem().addChild(newItem)
