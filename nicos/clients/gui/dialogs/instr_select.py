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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Dialog for selecting an instrument guiconfig."""

import os
from os import path

from nicos.guisupport.qt import QDialog, QIcon, QTreeWidgetItem

from nicos import config
from nicos.clients.gui.utils import loadUi, SettingGroup


class InstrSelectDialog(QDialog):
    """A dialog to request connection parameters."""

    def __init__(self, reason, parent=None):
        QDialog.__init__(self, parent)
        loadUi(self, 'instr_select.ui', 'dialogs')
        icon = QIcon(':/appicon-16')
        if reason:
            self.reasonLbl.setText(reason)
        else:
            self.reasonLbl.hide()
            self.saveBox.hide()

        self.confTree.itemDoubleClicked.connect(self.handleDoubleClick)
        for entry in sorted(os.listdir(config.nicos_root)):
            full = path.join(config.nicos_root, entry)
            if not (entry.startswith('nicos_') and path.isdir(full)):
                continue
            pkgitem = QTreeWidgetItem(self.confTree, [entry])
            pkgitem.setIcon(0, icon)
            for subentry in sorted(os.listdir(full)):
                configfile = path.join(full, subentry, 'guiconfig.py')
                if not path.isfile(configfile):
                    continue
                item = QTreeWidgetItem(pkgitem, [subentry])
                item.setData(0, QTreeWidgetItem.UserType, configfile)

    def handleDoubleClick(self, item, _col):
        if item.data(0, QTreeWidgetItem.UserType):
            self.accept()

    @classmethod
    def select(cls, reason='', force=False):
        with SettingGroup('Instrument') as settings:
            configfile = None if force else \
                (settings.value('guiconfig') or None)
            while not (configfile and path.isfile(configfile)):
                dlg = cls(reason)
                result = dlg.exec_()
                if not result:
                    return None
                items = dlg.confTree.selectedItems()
                if items:
                    configfile = items[0].data(0, QTreeWidgetItem.UserType)
                    if force or dlg.saveBox.isChecked():
                        settings.setValue('guiconfig', configfile)
            return configfile
