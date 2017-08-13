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
#   Jens Krüger <jens.kruege@tum.de>
#
# *****************************************************************************

"""NICOS GUI panel with information about the TOFTOF safety status."""

from PyQt4.QtGui import QTableWidgetItem
from PyQt4.QtCore import QByteArray

from nicos.utils import findResource

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi

from nicos.protocols.cache import cache_load
from nicos_mlz.toftof.devices.safety_desc import bit_description


class SafetyPanel(Panel):
    panelName = 'Safety'
    devname = 'saf'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, findResource('nicos_mlz/toftof/gui/safety.ui'))

        self.table.horizontalHeader().restoreState(self._headerstate)
        self.clear()

        if client.isconnected:
            self.on_client_connected()
        client.connected.connect(self.on_client_connected)
        client.setup.connect(self.on_client_connected)
        client.disconnected.connect(self.on_client_disconnected)
        client.cache.connect(self.on_client_cache)

    def saveSettings(self, settings):
        settings.setValue('headers', self.table.horizontalHeader().saveState())

    def loadSettings(self, settings):
        self._headerstate = settings.value('headers', '', QByteArray)

    def clear(self):
        self.table.clearContents()

    def on_client_connected(self):
        self.clear()
        self.table.setRowCount(len(bit_description))
        for m in range(len(bit_description)):
            for n in [0, 1]:
                newitem = QTableWidgetItem()
                self.table.setItem(m, n, newitem)
            self.table.item(m, 1).setText(bit_description[m])
        params = self.client.getDeviceParams(self.devname)
        if params:
            value = params.get('value')
            if value:
                self._update_table(value)

    def on_client_disconnected(self):
        self.clear()

    def _update_table(self, value):
        for n, bit in enumerate('{0:048b}'.format(value)[::-1]):
            self.table.item(n, 0).setText(bit)
        self.table.resizeRowsToContents()

    def on_client_cache(self, data):
        (_time, key, _op, value) = data
        ldevname, subkey = key.split('/')
        if ldevname == self.devname:
            if subkey == 'value':
                if not value:
                    fvalue = 0
                else:
                    fvalue = cache_load(value)
                self._update_table(fvalue)
