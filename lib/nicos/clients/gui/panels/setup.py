#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI experiment setup window."""

from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QDialogButtonBox, QListWidgetItem

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, DlgUtils


class SetupPanel(Panel, DlgUtils):
    panelName = 'Experiment setup'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        DlgUtils.__init__(self, 'Setup')
        loadUi(self, 'setup.ui', 'panels')

        if self.client.connected:
            self.on_client_connected()
        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)

    def on_client_connected(self):
        self._setupinfo = self.client.eval('session.getSetupInfo()', None)
        self.basicSetup.clear()
        self.optSetups.clear()
        keep = QListWidgetItem('<keep current>', self.basicSetup)
        if self._setupinfo is not None:
            for name, info in sorted(self._setupinfo.items()):
                if info is None:
                    continue
                if info['group'] == 'basic':
                    QListWidgetItem(name, self.basicSetup)
                elif info['group'] == 'optional':
                    item = QListWidgetItem(name, self.optSetups)
                    item.setFlags(Qt.ItemIsUserCheckable |
                                  Qt.ItemIsSelectable |
                                  Qt.ItemIsEnabled)
                    item.setCheckState(Qt.Unchecked)
        self.basicSetup.setCurrentItem(keep)

    def on_basicSetup_itemClicked(self, item):
        if item.text() != '<keep current>':
            self.showSetupInfo(item.text())

    def on_optSetups_itemClicked(self, item):
        self.showSetupInfo(item.text())

    def showSetupInfo(self, setup):
        info = self._setupinfo[str(setup)]
        devs = []
        for devname, devconfig in info['devices'].iteritems():
            if not devconfig[1].get('lowlevel'):
                devs.append(devname)
        devs = ', '.join(sorted(devs))
        self.setupDescription.setText(
            '<b>%s</b><br/>%s<br/><br/>'
            'Devices: %s<br/>' % (setup, info['description'], devs))

    def on_buttonBox_clicked(self, button):
        if self.buttonBox.buttonRole(button) == QDialogButtonBox.ApplyRole:
            self.applyChanges()
        else:
            self.parentwindow.close()

    def applyChanges(self):
        done = []
        prop = str(self.proposalNum.text())
        title = unicode(self.expTitle.text())
        users = unicode(self.users.text())
        local = unicode(self.localContact.text())
        if prop:
            args = {'proposal': prop}
            if local:
                args['localcontact'] = local
            if title:
                args['title'] = title
            if users:
                args['user'] = users
            code = 'NewExperiment(%s)\n' % ', '.join('%s=%r' % i
                                                     for i in args.items())
            self.client.tell('queue', '', code)
            done.append('New experiment started.')
        setups = []
        cmd = 'NewSetup'
        basic = str(self.basicSetup.currentItem().text())
        if basic == '<keep current>':
            cmd = 'AddSetup'
        else:
            setups.append(basic)
        for i in range(self.optSetups.count()):
            item = self.optSetups.item(i)
            if item.checkState() == Qt.Checked:
                setups.append(str(item.text()))
        if setups:
            self.client.tell('queue', '',
                             '%s(%s)\n' % (cmd, ', '.join(map(repr, setups))))
            done.append('New setups loaded.')
        if done:
            self.showInfo('\n'.join(done))
