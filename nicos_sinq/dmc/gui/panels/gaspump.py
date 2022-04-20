#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2022 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QIntValidator, QLabel
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.utils import findResource


def is_about_gaspump(message):
    return any(ch in message[0] for ch in ['ch1_', 'ch2', 'gaspump_command'])


class ValueLabel(QLabel, NicosWidget):
    key = PropDef('key', str, '', 'Cache key to display (without "nicos/"'
                                  'prefix), set either "dev" or this')

    def __init__(self, parent, designMode=False):
        QLabel.__init__(self, parent)
        NicosWidget.__init__(self)

    def registerKeys(self):
        self.registerKey(self.props['key'])

    def on_keyChange(self, key, value, time, expired):
        if isinstance(value, str):
            self.setText(value)
            return
        if isinstance(value, bool):
            value = int(value)
        if isinstance(value, int):
            self.setText(f'{value}')
            return
        if isinstance(value, float):
            self.setText(f'{value:.3f}')
            return


class DmcGaspumpPanel(Panel):
    """Provides a panel with several input fields for the experiment settings.
    """

    panelName = 'Gaspump panel'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_sinq/dmc/gui/panels/ui_files/gaspump.ui'))
        self.load_button.setToolTip('Load parameters from EEPROM')
        self.store_button.setToolTip('Store parameters into EEPROM')
        self.reset_button.setToolTip('Reset the device')

        for channel in [1, 2]:
            for param in ['amplitude', 'frequency', 'phase', 'mode', 'error',
                          'feedback']:
                getattr(self,
                        f'{param}{channel}').key = f'ch{channel}_{param}/value'
                getattr(self, f'{param}{channel}').setClient(client)

        for param in ['amplitude', 'frequency', 'phase']:
            getattr(self, f'set_{param}').setValidator(QIntValidator())

        self.set_amplitude.returnPressed.connect(
            lambda: self.on_set('amplitude'))
        self.set_frequency.returnPressed.connect(
            lambda: self.on_set('frequency'))
        self.set_phase.returnPressed.connect(lambda: self.on_set('phase'))

        self.load_button.clicked.connect(self.on_load)
        self.store_button.clicked.connect(self.on_store)
        self.reset_button.clicked.connect(self.on_reset)

        client.message.connect(self.on_client_message)
        client.simmessage.connect(self.on_client_simmessage)
        client.initstatus.connect(self.on_client_initstatus)

    def on_set(self, parameter):
        button = self.channel_group.checkedButton()
        if not button:
            return
        channel = int(button.text()[-1])
        target = getattr(self, f'set_{parameter}').text()
        self.client.run(f'maw(ch{channel}_{parameter}, {target})')
        getattr(self, f'set_{parameter}').clear()

    def on_load(self):
        button = self.channel_group.checkedButton()
        if not button:
            return
        channel = int(button.text()[-1])
        self.client.run(f'maw(gaspump_command, "load ch{channel}")')

    def on_store(self):
        button = self.channel_group.checkedButton()
        if not button:
            return
        channel = int(button.text()[-1])
        self.client.run(f'maw(gaspump_command, "store ch{channel}")')

    def on_reset(self):
        self.client.run('maw(gaspump_command, reset)')

    def on_client_initstatus(self, state):
        self.outView.clear()
        self.outView.scrollToBottom()

    def on_client_message(self, message):
        if is_about_gaspump(message):
            self.outView.addMessage(message)

    def on_client_simmessage(self, simmessage):
        if simmessage[-1] == '0' and is_about_gaspump(simmessage):
            self.outView.addMessage(simmessage)
