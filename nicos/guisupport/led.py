#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

from PyQt4.QtGui import QLabel, QWidget, QPixmap
from PyQt4.QtCore import Qt, QSize

from nicos.core.status import OK, BUSY, PAUSED
from nicos.guisupport.widget import NicosWidget, PropDef


ledColors = set(["blue", "green", "red", "yellow", "orange"])


class BaseLed(QLabel, NicosWidget):

    designer_icon = ':/leds/green_on'

    _ledPatternName = ':/leds/{color}_{status}'

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

    def resizeEvent(self, event):
        self._refresh()
        return QWidget.resizeEvent(self, event)

    def registerKeys(self):
        self._skey = self._source.register(self, self.props['key'])

    properties = {
        'ledStatus':   PropDef(bool, True),
        'ledInverted': PropDef(bool, False),
        'ledColor':    PropDef(str, 'green'),
    }

    def propertyUpdated(self, pname, value):
        self._refresh()
        NicosWidget.propertyUpdated(self, pname, value)


class ValueLed(BaseLed):
    designer_description = 'LED showing if the selected value is true'

    properties = {
        'dev':   PropDef(str, ''),
        'key':   PropDef(str, ''),
    }

    def propertyUpdated(self, pname, value):
        if pname == 'dev':
            if value:
                self.key = value + '.value'
        BaseLed.propertyUpdated(self, pname, value)

    def on_keyChange(self, key, value, time, expired):
        if expired:
            self.ledStatus = False
        else:
            self.ledStatus = True
        if value:
            self.ledColor = 'green'
        else:
            self.ledColor = 'red'


class StatusLed(BaseLed):
    designer_description = 'LED showing the status of the device'
    designer_icon = ':/leds/yellow_on'

    properties = {
        'dev':   PropDef(str, ''),
        'key':   PropDef(str, ''),
    }

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
        elif value[0] in (BUSY, PAUSED):
            self.ledColor = 'yellow'
        else:
            self.ledColor = 'red'
