#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI settings window."""

from PyQt4.QtGui import QDialog, QTreeWidgetItem, QListWidgetItem
from PyQt4.QtCore import pyqtSignature as qtsig

from nicos.clients.base import ConnectionData
from nicos.clients.gui.utils import loadUi, dialogFromUi, DlgUtils


class SettingsDialog(QDialog, DlgUtils):
    def __init__(self, main):
        QDialog.__init__(self, main)
        DlgUtils.__init__(self, 'Settings')
        loadUi(self, 'settings.ui', 'dialogs')
        self.main = main
        self.sgroup = main.sgroup

        genitem = QTreeWidgetItem(self.settingsTree, ['General'], -2)
        QTreeWidgetItem(self.settingsTree, ['Connection presets'], -1)
        self.settingsTree.setCurrentItem(genitem)
        self.stacker.setCurrentIndex(0)

        # general page
        self.instrument.setText(main.instrument)
        self.confirmExit.setChecked(main.confirmexit)
        self.warnWhenAdmin.setChecked(main.warnwhenadmin)
        self.showTrayIcon.setChecked(main.showtrayicon)
        self.autoReconnect.setChecked(main.autoreconnect)
        self.autoSaveLayout.setChecked(main.autosavelayout)
        self.manualSaveLayout.setChecked(not main.autosavelayout)

        # connection data page
        self.connpresets = main.connpresets
        for setting, cdata in main.connpresets.items():
            QListWidgetItem(setting + ' (%s:%s)' % (cdata.host, cdata.port),
                            self.settinglist).setData(32, setting)

    def saveSettings(self):
        self.main.instrument = self.instrument.text()
        self.main.confirmexit = self.confirmExit.isChecked()
        self.main.warnwhenadmin = self.warnWhenAdmin.isChecked()
        self.main.showtrayicon = self.showTrayIcon.isChecked()
        self.main.autoreconnect = self.autoReconnect.isChecked()
        self.main.autosavelayout = self.autoSaveLayout.isChecked()
        with self.sgroup as settings:
            settings.setValue(
                'connpresets_new', dict((k, v.serialize()) for (k, v)
                                        in self.connpresets.items()))
            settings.setValue('instrument', self.main.instrument)
            settings.setValue('confirmexit', self.main.confirmexit)
            settings.setValue('warnwhenadmin', self.main.warnwhenadmin)
            settings.setValue('showtrayicon', self.main.showtrayicon)
            settings.setValue('autoreconnect', self.main.autoreconnect)
            settings.setValue('autosavelayout', self.main.autosavelayout)
        if self.main.showtrayicon:
            self.main.trayIcon.show()
        else:
            self.main.trayIcon.hide()

    @qtsig('')
    def on_saveLayoutBtn_clicked(self):
        self.main.saveWindowLayout()
        for win in self.main.windows.values():
            win.saveWindowLayout()
        self.showInfo('The window layout was saved.')

    @qtsig('')
    def on_settingAdd_clicked(self):
        dlg = dialogFromUi(self, 'settings_conn.ui', 'dialogs')
        if dlg.exec_() != QDialog.Accepted:
            return
        if dlg.name.text() == '':
            return
        name = dlg.name.text()
        while name in self.connpresets:
            name += '_'
        cdata = ConnectionData(dlg.host.text(), dlg.port.value(),
                               dlg.login.text(), None, dlg.viewonly.isChecked())
        self.connpresets[name] = cdata
        QListWidgetItem(name + ' (%s:%s)' % (cdata.host, cdata.port),
                        self.settinglist).setData(32, name)

    @qtsig('')
    def on_settingDel_clicked(self):
        item = self.settinglist.currentItem()
        if item is None:
            return
        del self.connpresets[item.data(32)]
        self.settinglist.takeItem(self.settinglist.row(item))

    @qtsig('')
    def on_settingEdit_clicked(self):
        item = self.settinglist.currentItem()
        if item is None:
            return
        cdata = self.connpresets[item.data(32)]
        dlg = dialogFromUi(self, 'settings_conn.ui', 'dialogs')
        dlg.name.setText(item.data(32))
        dlg.name.setEnabled(False)
        dlg.host.setText(cdata.host)
        dlg.port.setValue(cdata.port)
        dlg.login.setText(cdata.user)
        dlg.viewonly.setChecked(cdata.viewonly)
        if dlg.exec_() != QDialog.Accepted:
            return
        cdata.host = dlg.host.text()
        cdata.port = dlg.port.value()
        cdata.user = dlg.login.text()
        cdata.viewonly = dlg.viewonly.isChecked()
        item.setText('%s (%s:%s)' % (dlg.name.text(), cdata.host, cdata.port))

    def on_settingsTree_itemClicked(self, item, column):
        self.on_settingsTree_itemActivated(item, column)

    def on_settingsTree_itemActivated(self, item, column):
        if self.stacker.count() > 3:
            self.stacker.removeWidget(self.stacker.widget(3))
        if item.type() == -2:
            self.stacker.setCurrentIndex(0)
        elif item.type() == -1:
            self.stacker.setCurrentIndex(1)
        elif item.type() == 0:
            self.stacker.setCurrentIndex(2)
