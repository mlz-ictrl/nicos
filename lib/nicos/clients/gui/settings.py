#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

from __future__ import with_statement

__version__ = "$Revision$"

import uuid

from PyQt4.QtCore import Qt, QVariant, pyqtSignature as qtsig
from PyQt4.QtGui import QDialog, QTreeWidgetItem, QInputDialog, \
     QWidget, QListWidgetItem

from nicos.clients.gui.utils import loadUi, dialogFromUi, DlgUtils


class SettingsDialog(QDialog, DlgUtils):
    def __init__(self, main):
        QDialog.__init__(self, main)
        DlgUtils.__init__(self, 'Settings')
        loadUi(self, 'settings.ui')
        self.main = main
        self.sgroup = main.sgroup
        self.pgroup = main.pgroup
        self.local_profiles = main.profiles.copy()

        genitem = QTreeWidgetItem(self.settingsTree, ['General'], -2)
        QTreeWidgetItem(self.settingsTree, ['Connection presets'], -1)
        #self.pitem = QTreeWidgetItem(self.settingsTree, ['Layout profiles'], 0)
        #self.pitem.setExpanded(True)
        self.settingsTree.setCurrentItem(genitem)
        self.stacker.setCurrentIndex(0)

        # general page
        self.instrument.setText(main.instrument)
        self.confirmExit.setChecked(main.confirmexit)
        self.showTrayIcon.setChecked(main.showtrayicon)
        self.autoReconnect.setChecked(main.autoreconnect)

        # connection data page
        self.connpresets = main.connpresets
        for setting, cdata in main.connpresets.iteritems():
            QListWidgetItem(setting + ' (%s:%s)' % (cdata[0], cdata[1]),
                            self.settinglist).setData(32, setting)

        # profiles page
        #for (uid, (name, wconfig, tconfig)) in self.local_profiles.iteritems():
        #    QTreeWidgetItem(self.pitem, [name], 1).setData(0, 32, uid)
        #    QListWidgetItem(name, self.profileList).setData(32, uid)
        #    self.profileCombo.addItem(name)

    def saveSettings(self):
        self.main.instrument = self.instrument.text()
        self.main.confirmexit = self.confirmExit.isChecked()
        self.main.showtrayicon = self.showTrayIcon.isChecked()
        self.main.autoreconnect = self.autoReconnect.isChecked()
        with self.sgroup as settings:
            settings.setValue('connpresets', self.connpresets)
            settings.setValue('instrument', QVariant(self.main.instrument))
            settings.setValue('confirmexit', QVariant(self.main.confirmexit))
            settings.setValue('showtrayicon', QVariant(self.main.showtrayicon))
            settings.setValue('autoreconnect', QVariant(self.main.autoreconnect))
        if self.main.showtrayicon:
            self.main.trayIcon.show()
        else:
            self.main.trayIcon.hide()

    @qtsig('')
    def on_settingAdd_clicked(self):
        dlg = dialogFromUi(self, 'settings_conn.ui')
        if dlg.exec_() != QDialog.Accepted:
            return
        if dlg.name.text() == '':
            return
        name = str(dlg.name.text())
        while name in self.connpresets:
            name += '_'
        cdata = [dlg.host.text(), dlg.port.value(), dlg.login.text()]
        self.connpresets[name] = cdata
        QListWidgetItem(name + ' (%s:%s)' % (cdata[0], cdata[1]),
                        self.settinglist).setData(32, name)

    @qtsig('')
    def on_settingDel_clicked(self):
        item = self.settinglist.currentItem()
        if item is None:
            return
        del self.connpresets[str(item.data(32).toString())]
        self.settinglist.takeItem(self.settinglist.row(item))

    @qtsig('')
    def on_settingEdit_clicked(self):
        item = self.settinglist.currentItem()
        if item is None:
            return
        cdata = self.connpresets[str(item.data(32).toString())]
        dlg = dialogFromUi(self, 'settings_conn.ui')
        dlg.name.setText(item.data(32).toString())
        dlg.name.setEnabled(False)
        dlg.host.setText(cdata[0])
        dlg.port.setValue(cdata[1])
        dlg.login.setText(cdata[2])
        if dlg.exec_() != QDialog.Accepted:
            return
        cdata[0] = dlg.host.text()
        cdata[1] = dlg.port.value()
        cdata[2] = dlg.login.text()
        item.setText('%s (%s:%s)' % (dlg.name.text(), cdata[0], cdata[1]))

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
        else:
            widget = QWidget(self)
            loadUi(widget, 'profile.ui')
            uid = str(item.data(0, 32).toString())
            name = self.local_profiles[uid][0]
            widget.groupBox.setTitle('Profile configuration (%s)' % name)
            # XXX populate widget
            self.stacker.addWidget(widget)
            self.stacker.setCurrentWidget(widget)

    def on_createProfile_released(self):
        name, ok = QInputDialog.getText(self, 'Add profile', 'Profile name:')
        if not ok:
            return
        newname = str(name)
        if any(newname == v[0] for v in self.local_profiles.values()):
            return self.showError('Profile already exists')
        uid = str(uuid.uuid1())
        QListWidgetItem(newname, self.profileList).setData(32, uid)
        self.profileCombo.addItem(newname)
        newitem = QTreeWidgetItem(self.pitem, [newname], 1)
        newitem.setData(0, 32, uid)
        self.local_profiles[uid] = [newname, []]
        self.settingsTree.setCurrentItem(newitem)
        self.on_settingsTree_itemActivated(newitem, 0)

    def on_deleteProfile_released(self):
        item = self.profileList.currentItem()
        if item is None:
            return
        uid = str(item.data(32).toString())
        if not self.askQuestion('Really delete this profile?', True):
            return
        name = self.local_profiles.pop(uid)[0]
        self.profileCombo.removeItem(self.profileCombo.findText(name))
        for item in self.settingsTree.findItems(
                        name, Qt.MatchExactly|Qt.MatchRecursive):
            self.pitem.removeChild(item)
        for item in self.profileList.findItems(name, Qt.MatchExactly):
            self.profileList.takeItem(self.profileList.row(item))

    def on_editProfile_released(self):
        item = self.profileList.currentItem()
        if item is None:
            return
        uid = str(item.data(32).toString())
        name = self.local_profiles[uid][0]
        for item in self.settingsTree.findItems(
                        name, Qt.MatchExactly|Qt.MatchRecursive):
            self.settingsTree.setCurrentItem(item)
            self.on_settingsTree_itemActivated(item, 0)
            return
