# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2019 by the NICOS contributors (see AUTHORS)
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
#   Edward Wall <edward.wall@psi.ch>
#
# *****************************************************************************

from nicos.clients.gui.panels import Panel
from nicos.guisupport.qt import QHBoxLayout, QLabel, QPushButton, \
    QScrollArea, QVBoxLayout, QWidget
from nicos.protocols.cache import cache_load


class TableViewPanel(Panel):

    _TABLES = ['Table2', 'Table3', 'Table4', 'Table5', 'Table6']

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)

        self._table_devices = dict()
        self._table_setups = dict()
        self._unassigned = []

        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self._build_fixed_layout()
        self._update_table_display()

        client.cache.connect(self.on_client_cache)
        client.connected.connect(self.on_client_connected)

    def _build_fixed_layout(self):
        vbox = self.layout()
        vbox.addWidget(QLabel('<h1>Device Assigned Tables</h1>'), stretch=0)

        vbox.addSpacing(10)

        self.tables = QScrollArea(self)
        self.tables_view = QWidget()
        self.tables_view.setLayout(QVBoxLayout())
        self.tables.setWidget(self.tables_view)
        self.tables.setWidgetResizable(True)
        vbox.addWidget(self.tables, stretch=0)

        vbox.addSpacing(10)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox, stretch=0)

        discover_button = QPushButton('Auto-Discover')
        discover_button.pressed.connect(self._discover)
        hbox.addWidget(discover_button, stretch=0)

        clear_button = QPushButton('Reset Configuration')
        clear_button.pressed.connect(self._clear)
        hbox.addWidget(clear_button, stretch=0)

    def _update_table_display(self):
        self.unassigned = []
        if self.client.isconnected:
            self.unassigned = self.client.ask('eval', 'find_unassigned(False)', False)

        self.layout().removeWidget(self.tables_view)
        self.tables_view.deleteLater()

        self.tables_view = QWidget()
        vbox = QVBoxLayout()
        self.tables_view.setLayout(vbox)
        self.tables.setWidget(self.tables_view)

        if self.unassigned:
            vbox.addWidget(QLabel('<h3>Unassigned Setups</h3>'), stretch=0)

            for setup in self.unassigned:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(f'<h4>{setup}: </h4>'), stretch=0)

                for table in self._TABLES:
                    table_button = QPushButton(table)
                    table_button.pressed.connect(lambda setup=setup, table=table: self._assign_to_table(setup, table))
                    hbox.addWidget(table_button, stretch=0)

                vbox.addLayout(hbox, stretch=0)

            vbox.addSpacing(10)

        for table in self._TABLES:
            vbox.addWidget(QLabel(f'<h3>{table}</h3>'), stretch=0)
            vbox.addWidget(QLabel(f'Setups: {self._table_setups.get(table.lower(), [])}'), stretch=0)
            vbox.addWidget(QLabel(f'Devices: {self._table_devices.get(table.lower(), [])}'), stretch=0)

    def _assign_to_table(self, dev, table):
        self.client.tell('queue', '', f'{table}.attach("{dev}")')

    def _discover(self):
        self.client.tell('queue', '', 'boadiscover()')

    def _clear(self):
        for devname in self._TABLES:
            self.client.tell('queue', '', f'{devname}.empty()')

    def on_client_cache(self, data):
        (_, key, _, value) = data
        if '/' not in key:
            return

        devname, subkey = key.rsplit('/', 1)
        if devname.startswith("table"):
            if subkey == 'additional_devices':
                self._table_devices[devname] = cache_load(value)
                self._update_table_display()
            elif subkey == 'setups':
                self._table_setups[devname] = cache_load(value)
                self._update_table_display()

    def on_client_connected(self):
        if not self.client.isconnected:
            return

        for devname in self._TABLES:
            params = self.client.getDeviceParams(devname)
            if params:
                for key, value in params.items():
                    if key == 'additional_devices':
                        self._table_devices[devname.lower()] = value
                        self._update_table_display()
                    elif key == 'setups':
                        self._table_setups[devname.lower()] = value
                        self._update_table_display()
