#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2026 by the NICOS contributors (see AUTHORS)
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
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************
'''
A panel to enter sample names for every position of the SampleSwitcher device.
'''
from nicos.clients.gui.panels import Panel
from nicos.guisupport.qt import QWidget, QVBoxLayout,  QLabel,  QHBoxLayout, QLineEdit, QPushButton, QSizePolicy, QScrollArea
from nicos.protocols.cache import cache_load, OP_TELL, cache_dump


class SampleChangerPanel(Panel):
    _devinfo = {}

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self._active_sample = 0
        self._target = -1
        self._sample_entries = []

        self.build_fixed_entries()

        client.cache.connect(self.on_client_cache)
        client.connected.connect(self.on_client_connected)

    def build_fixed_entries(self):
        vbox = self.layout()
        vbox.addWidget(QLabel('<h1>Sample Changer - Name your samples</h1>'), stretch=0)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Installed Device:"), stretch=0)
        self._installed_devices = QLabel()
        hbox.addWidget(self._installed_devices, stretch=1)
        vbox.addLayout(hbox, stretch=0)

        self.sample_lines = QScrollArea(self)
        self.sample_lines.setWidgetResizable(True)
        vbox.addWidget(self.sample_lines, stretch=0)

        vbox.addSpacing(10)
        btn = QPushButton('Apply')
        btn.pressed.connect(self.apply_names)
        vbox.addWidget(btn, stretch=0)

    def apply_names(self):
        names = []
        for entry in self._sample_entries:
            names.append(str(entry.text()))
        self.client.tell('exec', f'schanger.sample_names = {names!r};schanger(schanger.read())')

    def build_sample_lines(self, name_list):
        self.layout().removeWidget(self.sample_lines)
        self.sample_lines.deleteLater()
        self.sample_lines = QScrollArea(self)
        sw = QWidget()
        self.sample_lines.setWidget(sw)
        # self.sample_lines.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.sample_lines.setWidgetResizable(True)
        self.sample_lines.setWidgetResizable(True)
        self.layout().insertWidget(2, self.sample_lines, stretch=1)

        vbox = QVBoxLayout()
        sw.setLayout(vbox)
        self._sample_entries=[]
        for i,name in enumerate(name_list):
            hbox = QHBoxLayout()
            btn = QPushButton('Move to ')
            btn.pressed.connect(lambda idx=i: self.move_to_sample(idx))
            hbox.addWidget(btn, stretch=0)
            hbox.addWidget(QLabel(f'{i}:'))
            entry = QLineEdit()
            entry.setText(name)
            entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self._sample_entries.append(entry)
            hbox.addWidget(entry)
            vbox.addLayout(hbox, stretch=0)
        vbox.addStretch(1)
        self.active_sample()

    def move_to_sample(self, index):
        self.client.tell('exec', f'schanger({index})')
        self._target = index

    def active_sample(self):
        for entry in self._sample_entries:
            entry.setStyleSheet("QLineEdit{background: white;}")
        if self._active_sample>=0 and len(self._sample_entries)>0:
            self._sample_entries[self._active_sample].setStyleSheet("QLineEdit{background: lightgreen;}")
            self._target = -1
        elif self._target>=0:
            self._sample_entries[self._target].setStyleSheet("QLineEdit{background: lightyellow;}")

    def on_client_cache(self, data):
        (_time, key, _op, value) = data
        if '/' not in key:
            return
        ldevname, subkey = key.rsplit('/', 1)

        if ldevname == 'schanger':
            if subkey == 'status':
                value = cache_load(value)
            elif subkey == 'value':
                value = cache_load(value)
                self._active_sample = value
                self.active_sample()
            elif subkey == 'sample_names':
                value = cache_load(value)
                self.build_sample_lines(value)
            elif subkey == 'current_holder':
                value = cache_load(value)
                self._installed_devices.setText(value)

    def on_client_connected(self):
        state = self.client.ask('getstatus')
        if not state:
            return
        devlist = ['schanger']

        for devname in devlist:
            self._create_device_item(devname)

    def _create_device_item(self, devname):
        ldevname = devname.lower()
        # get all cache keys pertaining to the device
        params = self.client.getDeviceParams(devname)
        if not params:
            return
        # let the cache handler process all properties
        for key, value in params.items():
            self.on_client_cache((1, ldevname + '/' + key, OP_TELL, cache_dump(value)))
