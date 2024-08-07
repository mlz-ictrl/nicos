# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

from logging import WARNING

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.utils import findResource

from nicos_sinq.amor.devices.selene import ACTIVE, INACTIVE, NARROW, WIDE


class SelenePanel(Panel):

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource(
            'nicos_sinq/amor/gui/panels/ui_files/selene.ui')
        )

        self._client = client

        for index in range(1, 37):
            getattr(self, f'pushButton_{index}').setClient(client)

        self.pitchIndexLabel.key = 'selene/_pitch'
        self.pitchIndexLabel.offset = 1

        self.motorPositionLabel.key = 'selene/value'

        self.positionLabel.key = 'selene/position'

        self.rangeLabel.key = 'selene/range'
        self.rangeLabel.zname = 'wide'
        self.rangeLabel.oname = 'narrow'

        self.stateLabel.key = 'selene/enabled'
        self.stateLabel.zname = 'disabled'
        self.stateLabel.oname = 'enabled'

        self.HLMWideLabel.key = 'selene/high_limit_wide'
        self.HLMNarrowLabel.key = 'selene/high_limit_narrow'
        self.workingPositionLabel.key = 'selene/working_position'
        self.LLMWideLabel.key = 'selene/low_limit_wide'
        self.LLMNarrowLabel.key = 'selene/low_limit_narrow'

        for name in ['position', 'range', 'state', 'pitchIndex', 'HLMWide',
                     'HLMNarrow', 'LLMWide', 'LLMNarrow', 'workingPosition',
                     'motorPosition']:
            getattr(self, f'{name}Label').setClient(client)

        self.enableGroup.setId(self.enableButton, ACTIVE)
        self.enableGroup.setId(self.disableButton, INACTIVE)
        self.enableGroup.buttonClicked['int'].connect(self.on_state_group)

        self.rangeGroup.setId(self.wideButton, WIDE)
        self.rangeGroup.setId(self.narrowButton, NARROW)
        self.rangeGroup.buttonClicked['int'].connect(self.on_range_group)

        self.driveToEdit.returnPressed.connect(self.on_drive_to)

        self.toWorkingPositionButton.clicked.connect(
            self.on_to_working_position)
        self.setWorkingPositionButton.clicked.connect(
            self.on_set_working_position)
        self.toParkButton.clicked.connect(self.on_to_parking_position)
        self.offFocusButton.clicked.connect(self.on_move_off_focus)

        self._client.message.connect(self.on_client_message)

    def on_client_message(self, message):
        if message[2] < WARNING:
            self.textStatus.setText('')
            return
        self.textStatus.setText(f'{message[0]}: {message[3].strip()}')

    def on_range_group(self, value):
        self._client.run(f'selene.range = {value}')

    def on_state_group(self, value):
        self._client.run(f'selene.'
                         f'{"enable" if value == ACTIVE else "disable"}()')

    def on_drive_to(self):
        self._client.run(f'maw(selene, {self.driveToEdit.text()})')

    def on_to_working_position(self):
        self._client.run('selene.move_to_working_position()')

    def on_set_working_position(self):
        self._client.run('selene.set_present_as_working_position()')

    def on_to_parking_position(self):
        self._client.run('selene.doPark()')

    def on_move_off_focus(self):
        self._client.run('selene.move_off_focus()')
