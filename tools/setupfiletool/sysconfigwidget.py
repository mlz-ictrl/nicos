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

from PyQt4.QtGui import QMenu, QTreeWidgetItem

from setupfiletool.utilities.treewidgetcontextmenu import TreeWidgetContextMenu

class SysconfigWidget(TreeWidgetContextMenu):
    def __init__(self, parent=None):
        TreeWidgetContextMenu.__init__(self, parent)


    def contextMenuOnItem(self, item, pos):
        if item is None:
            return #invoked context menu on whitespace

        topLevelItems = []
        currentIndex = 0
        while currentIndex < self.topLevelItemCount():
            topLevelItems.append(self.topLevelItem(currentIndex))
            currentIndex += 1
        if self.currentItem() in topLevelItems:
            menu = QMenu(self)
            addValueAction = menu.addAction('Add value...')
            addValueAction.triggered.connect(self.addValue)
            menu.popup(pos)


    def addValue(self):
        self.currentItem().addChild(QTreeWidgetItem(['<New value>']))
