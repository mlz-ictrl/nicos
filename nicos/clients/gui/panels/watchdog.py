#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI watchdog reconfiguration panel."""

from __future__ import absolute_import, division, print_function

from time import time as currenttime

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QT_VER, QByteArray, QDialogButtonBox, \
    QHeaderView, Qt, QTreeWidgetItem
from nicos.pycompat import iteritems


class WatchdogPanel(Panel):
    """Provides a way to reconfigure the watchdog service on the fly."""

    panelName = 'Watchdog'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, 'panels/watchdog.ui')

        self._preconf_entries = {}
        self._preconf_enable = {}
        self._user_entries = {}

        # don't expose user defined conditions for now
        self.userWidget.hide()

        for tree in (self.preconfTree, self.userTree):
            tree.setColumnCount(11)
            tree.setHeaderLabels([
                'Enabled', 'Message', 'Condition', 'Only for setup',
                'Grace time', 'Precondition', 'Precondition time',
                'OK message', 'Script action', 'Warn action', 'OK action'
            ])

            if QT_VER == 4:
                tree.header().setResizeMode(QHeaderView.Interactive)
            else:
                tree.header().setSectionResizeMode(QHeaderView.Interactive)

        self.preconfTree.header().restoreState(self._preconf_headerstate)
        self.userTree.header().restoreState(self._user_headerstate)

        if client.isconnected:
            self.on_client_connected()
        client.connected.connect(self.on_client_connected)
        client.experiment.connect(self.on_client_experiment)
        client.setup.connect(self.on_client_setup)

    def saveSettings(self, settings):
        settings.setValue('preconf_headers',
                          self.preconfTree.header().saveState())
        settings.setValue('user_headers',
                          self.userTree.header().saveState())

    def loadSettings(self, settings):
        self._preconf_headerstate = settings.value('preconf_headers', '',
                                                   QByteArray)
        self._user_headerstate = settings.value('user_headers', '', QByteArray)

    def on_client_connected(self):
        self._update()

    def on_client_experiment(self):
        self._update()

    def on_client_setup(self):
        self._update()

    def _update(self):
        self.preconfTree.clear()
        self._preconf_enable = {}
        self._preconf_entries = {}
        self._user_entries = {}

        cf = self.client.eval('session.cache.get_raw("watchdog/configured")',
                              Ellipsis)
        if cf is Ellipsis:
            self.showError('Could not query watchdog configuration; '
                           'are you connected to a daemon?')
            return
        cf = sorted(cf, key=lambda entry: entry['id'])
        for entry in cf:
            eid = entry['id']
            item = QTreeWidgetItem(self.preconfTree, [
                '', entry['message'], entry['condition'], entry['setup'],
                str(entry['gracetime']), entry['precondition'],
                str(entry['precondtime']), entry['okmessage'],
                entry['scriptaction'], entry['action'], entry['okaction']
            ])
            item.setCheckState(0, Qt.Checked if entry['enabled']
                               else Qt.Unchecked)
            self._preconf_enable[eid] = entry['enabled']
            self._preconf_entries[eid] = entry
            item.setData(0, 32, eid)

    def on_preconfTree_itemChanged(self, item, col):
        eid = item.data(0, 32)
        if col == 0 and eid is not None:
            self._preconf_enable[eid] = item.checkState(0) == Qt.Checked

    def on_buttonBox_clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            updates = []
            for (eid, enabled) in iteritems(self._preconf_enable):
                if enabled != self._preconf_entries[eid]['enabled']:
                    updates.append((eid, enabled))

            if updates:
                msg = [currenttime(), updates]
                self.client.eval(
                    'session.cache.put_raw("watchdog/enable", %r)' % msg)
                self.showInfo('Updates applied.')
                self._update()
        elif role == QDialogButtonBox.ResetRole:
            self._update()
