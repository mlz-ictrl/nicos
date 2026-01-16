# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

from nicos.guisupport.qt import QLabel, QPushButton
from nicos.guisupport.widget import NicosWidget, PropDef


class PitchButton(QPushButton, NicosWidget):
    enabled = PropDef('enabled', int, 0, 'Pitch̵ is active')
    selected = PropDef('selected', int, 0, 'Pitch is selected')
    low = PropDef('low', float, 0, 'Low limit narrow for the pitch')
    high = PropDef('high', float, 0, 'High limit narrow for the pitch')
    position = PropDef('position', float, 0, 'Position of the segment')

    def __init__(self, parent, designMode=False):
        QPushButton.__init__(self, parent)
        NicosWidget.__init__(self)
        self.index = self.text()
        self.clicked.connect(self.on_click)

    def setClient(self, client):
        NicosWidget.setClient(self, client)
        self._client.connected.connect(self.on_connected)

    def on_connected(self):
        # This protects against selene not being loaded ....
        if not self._client.getDeviceParam('selene', 'low_limit_narrow'):
            return
        self.low = self._client.getDeviceParam('selene', 'low_limit_narrow')[
            int(self.text()) - 1]
        self.high = self._client.getDeviceParam('selene', 'high_limit_narrow')[
            int(self.text()) - 1]
        self.position = self._client.getDeviceParam('selene', 'position')[
            int(self.text()) - 1]

    def registerKeys(self):
        self._source.register(self, f'p{self.text()}/value')
        self._source.register(self, 'selene/_pitch')
        self._source.register(self, 'selene/low_limit_narrow')
        self._source.register(self, 'selene/high_limit_narrow')
        self._source.register(self, 'selene/position')

    def _color_map(self):
        if self.enabled:
            return '#34db77'
        if self.selected:
            return '#db7734'
        if self.low <= self.position <= self.high:
            return '#3498db'
        return '#db3498'

    def on_keyChange(self, key, value, time, expired):
        if key == f'p{self.text()}/value':
            self.enabled = value
        if key == 'selene/_pitch':
            self.selected = (value + 1) == int(self.text())
        if key == 'selene/high_limit_narrow':
            self.high = value[int(self.text()) - 1]
        if key == 'selene/low_limit_narrow':
            self.low = value[int(self.text()) - 1]
        if key == 'selene/position':
            self.position = value[int(self.text()) - 1]
        self.setStyleSheet(
            f'background-color: {self._color_map()};')

    def on_click(self):
        self._client.run(f'selene.pitch = {self.text()}')


class ValueLabel(QLabel, NicosWidget):
    key = PropDef('key', str, '', 'Cache key to display (without "nicos/"'
                                  'prefix), set either "dev" or this')
    value_index = PropDef('value_index', int, -1, 'Index in the value if its '
                                                  'length is > 1')
    offset = PropDef('offset', int, 0, 'Offset to add to the value')
    zname = PropDef('zname', str, '',
                    'Value to display instead of raw value 0')
    oname = PropDef('oname', str, '',
                    'Value to display instead of raw value 1')

    def __init__(self, parent, designMode=False):
        QLabel.__init__(self, parent)
        NicosWidget.__init__(self)

    def registerKeys(self):
        self.registerKey(self.props['key'])

    def on_keyChange(self, key, value, time, expired):
        if isinstance(value, bool):
            value = int(value)
        if isinstance(value, int) and value == 0 and self.zname:
            value = self.zname
        if isinstance(value, int) and value == 1 and self.oname:
            value = self.oname
        if isinstance(value, str):
            self.setText(value)
            return
        if isinstance(value, int):
            self.setText(f'{value + self.offset}')
            return
        if isinstance(value, float):
            self.setText(f'{value + self.offset:.3f}')
            return
        if hasattr(value, '__len__'):
            self.setText(f'{value[self.value_index] + self.offset:.3f}')
            return


class ListEntryLabel(ValueLabel):
    value = PropDef('value', float, 0.0, 'value')
    _values = []

    def setClient(self, client):
        ValueLabel.setClient(self, client)
        self._client.connected.connect(self.on_connected)

    def on_connected(self):
        self._values = self._client.getDeviceParam('selene',
                                                  self.props['key'].split('/')[
                                                      1])
        self.value = self._values[self.value_index]

    def registerKeys(self):
        ValueLabel.registerKeys(self)
        self.registerKey('selene/_pitch')

    def on_keyChange(self, key, value, time, expired):
        if key == 'selene/_pitch':
            self.value_index = value
        if key == self.props['key']:
            self._values = value
            self.value = self._values[self.value_index]

        if self.value_index >= 0 and self._values:
            self.setText(f'{self._values[self.value_index]:.3f}')
        else:
            self.setText(':(')
