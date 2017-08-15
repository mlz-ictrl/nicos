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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""
NICOS GUI LED class.
"""

import ast

from nicos.guisupport.qt import Qt, QSize, QLabel, QWidget, QPixmap

from nicos.core.status import OK, BUSY
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.pycompat import string_types


ledColors = set(["blue", "green", "red", "yellow", "orange"])


class BaseLed(QLabel, NicosWidget):

    designer_icon = ':/leds/green_on'

    _ledPatternName = ':/leds/{color}_{status}'

    ledStatus = PropDef('ledStatus', bool, True, 'Status to display the '
                        '"On color" (bright)')
    ledInverted = PropDef('ledInverted', bool, False, 'Status to display the '
                          '"Off color" (dark)')
    ledColor = PropDef('ledColor', str, 'green', 'Color of the LED (default '
                       'is green)')

    def __init__(self, parent=None, designMode=False):
        QLabel.__init__(self, parent)
        NicosWidget.__init__(self)
        self._refresh()

    def sizeHint(self):
        if self.layout() is None:
            return QSize(24, 24)
        return QLabel.sizeHint(self)

    def minimumSizeHint(self):
        return QSize(8, 8)

    def _refresh(self):
        status = self.props['ledStatus']
        inverted = self.props['ledInverted']
        color = self.props['ledColor']
        if inverted:
            status = not status
        status = status and "on" or "off"
        ledName = self._ledPatternName.format(color=color, status=status)
        pixmap = QPixmap(ledName).scaled(self.size(), Qt.KeepAspectRatio,
                                         Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event):
        self._refresh()
        return QWidget.resizeEvent(self, event)

    def registerKeys(self):
        self.registerKey(self.props['key'])

    def propertyUpdated(self, pname, value):
        self._refresh()
        NicosWidget.propertyUpdated(self, pname, value)


class ValueLed(BaseLed):
    designer_description = 'LED showing if the selected value is true'

    dev = PropDef('dev', str, '', 'NICOS device to use the value')
    key = PropDef('key', str, '', 'Key to use as the value')
    goal = PropDef('goal', str, '', 'Comparison value (by default the LED is '
                   'green if value is true/nonzero)')

    _goalval = None

    def propertyUpdated(self, pname, value):
        if pname == 'dev':
            if value:
                self.key = value + '.value'
        elif pname == 'goal':
            self._goalval = ast.literal_eval(value) if value else None
        BaseLed.propertyUpdated(self, pname, value)

    def on_keyChange(self, key, value, time, expired):
        if expired:
            self.ledStatus = False
        else:
            self.ledStatus = True
        if self._goalval is not None:
            green = value == self._goalval
        else:
            green = value
        if green:
            self.ledColor = 'green'
        else:
            self.ledColor = 'red'


class StatusLed(BaseLed):
    designer_description = 'LED showing the status of the device'
    designer_icon = ':/leds/yellow_on'

    dev = PropDef('dev', str, '', 'Device name')
    key = PropDef('key', str, '', 'Key name of the device')

    def propertyUpdated(self, pname, value):
        if pname == 'dev':
            if value:
                self.key = value + '.status'
        BaseLed.propertyUpdated(self, pname, value)

    def on_keyChange(self, key, value, time, expired):
        if value is None:
            expired = True
            value = (OK, '')
        if expired:
            self.ledStatus = False
        else:
            self.ledStatus = True
        if value[0] == OK:
            self.ledColor = 'green'
        elif value[0] == BUSY:
            self.ledColor = 'yellow'
        else:
            self.ledColor = 'red'


class ClickableOutputLed(ValueLed):
    designer_description = 'Digital Output Led that changes device state on click'
    designer_icon = ':/leds/orange_on'

    ledColor = PropDef('ledColor', str, 'orange', 'Default led color')
    stateActive = PropDef('stateActive', str, '1', 'Target for active LED '
                          'state (green)')
    stateInactive = PropDef('stateInactive', str, '0', 'Target for inactive '
                            'LED state (red)')

    def __init__(self, parent=None, designMode=False):
        self.current = None
        self._stateActive = 1
        self._stateInactive = 0
        ValueLed.__init__(self, parent, designMode)

    def on_keyChange(self, key, value, time, expired):
        ValueLed.on_keyChange(self, key, value, time, expired)
        self.current = value

    def propertyUpdated(self, pname, value):
        ValueLed.propertyUpdated(self, pname, value)

        if pname == 'stateInactive':
            if isinstance(value, string_types):
                self._stateInactive = value
            else:
                self._stateInactive = ast.literal_eval(value) if value else 0
        if pname == 'stateActive':
            if isinstance(value, string_types):
                self._stateActive = value
            else:
                self._stateActive = ast.literal_eval(value) if value else 1

    def mousePressEvent(self, event):
        self.ledColor = 'orange'

        if event.button() == Qt.LeftButton:
            if self.current == self._stateActive:
                self._client.run('move(%s, %r)' % (self.dev, self._stateInactive))
            else:
                self._client.run('move(%s, %r)' % (self.dev, self._stateActive))

        event.accept()
