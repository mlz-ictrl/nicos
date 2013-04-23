#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

from PyQt4.QtCore import Qt, pyqtProperty, QSize
from PyQt4.QtGui import QLabel, QWidget, QPixmap

from nicos.core.status import OK, BUSY, PAUSED
from nicos.guisupport.widget import DisplayWidget


ledColors = set(["blue", "green", "red", "yellow", "orange"])


class BaseLed(QLabel, DisplayWidget):

    designer_description = 'LED'
    designer_icon = ':/leds/green_on'

    defaultLedPattern = ":leds/{color}_{status}"
    defaultLedColor = "green"
    defaultLedStatus = True
    defaultLedInverted = False

    def __init__(self, parent=None, designMode=False):
        self._key = ''
        self._device = ''
        self._ledStatus = self.defaultLedStatus
        self._ledColor = self.defaultLedColor
        self._ledPatternName = self.defaultLedPattern
        self._ledInverted = self.defaultLedInverted
        self._ledName = self.toLedName()
        QLabel.__init__(self, parent)
        DisplayWidget.__init__(self)
        self._refresh()

    def sizeHint(self):
        if self.layout() is None:
            return QSize(24, 24)
        return QLabel.sizeHint(self)

    def minimumSizeHint(self):
        return QSize(8, 8)

    def toLedName(self, status=None, color=None, inverted=None):
        if status is None: status = self._ledStatus
        if color is None: color = self._ledColor
        if inverted is None: inverted = self._ledInverted
        if inverted:
            status = not status
        status = status and "on" or "off"
        return self._ledPatternName.format(color=color, status=status)

    def _refresh(self):
        self._ledName = self.toLedName()
        pixmap = QPixmap(self._ledName).scaled(self.size(), Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        return self.update()

    def resizeEvent(self, event):
        self._refresh()
        return QWidget.resizeEvent(self, event)

    def registerKeys(self):
        self._skey = self._source.register(self, self._key)

    def getLedPatternName(self):
        return self._ledPatternName
    def setLedPatternName(self, name):
        self._ledPatternName = str(name)
        self._refresh()
    def resetLedPatternName(self):
        self.setLedPatternName(self.defaultLedPattern)
    ledPattern = pyqtProperty("QString", getLedPatternName, setLedPatternName,
                              resetLedPatternName, doc="led pattern name")

    def getLedStatus(self):
        return self._ledStatus
    def setLedStatus(self, status):
        self._ledStatus = bool(status)
        self._refresh()
    def resetLedStatus(self):
        self.setLedStatus(self.defaultLedStatus)
    ledStatus = pyqtProperty("bool", getLedStatus, setLedStatus,
                             resetLedStatus, doc="led status")

    def getLedInverted(self):
        return self._ledInverted
    def setLedInverted(self, inverted):
        self._ledInverted = bool(inverted)
        self._refresh()
    def resetLedInverted(self):
        self.setLedInverted(self.defaultLedInverted)
    ledInverted = pyqtProperty("bool", getLedInverted, setLedInverted,
                               resetLedInverted, doc="led inverted mode")

    def getLedColor(self):
        return self._ledColor
    def setLedColor(self, color):
        color = str(color).lower()
        if color.lower() not in ledColors:
            raise Exception("Invalid color '%s'" % color)
        self._ledColor = color
        self._refresh()
    def resetLedColor(self):
        self.setLedColor(self.defaultLedColor)
    ledColor = pyqtProperty("QString", getLedColor, setLedColor,
                            resetLedColor, doc="led color")


class ValueLed(BaseLed):
    designer_description = 'LED showing if the selected value is true'

    def get_device(self):
        return self._device
    def set_device(self, value):
        self._device = str(value)
        if value:
            self._key = str(value + '.value')
    def reset_device(self):
        self._device = ''
    device = pyqtProperty(str, get_device, set_device, reset_device)

    def get_key(self):
        return self._key
    def set_key(self, value):
        self._key = str(value)
    def reset_key(self):
        self._key = ''
    key = pyqtProperty(str, get_key, set_key, reset_key)

    def on_keyChange(self, key, value, time, expired):
        if expired:
            self.setLedStatus(False)
        else:
            self.setLedStatus(True)
        if value:
            self.setLedColor('green')
        else:
            self.setLedColor('red')


class StatusLed(BaseLed):
    designer_description = 'LED showing the status of the device'
    designer_icon = ':/leds/yellow_on'

    def get_device(self):
        return self._device
    def set_device(self, value):
        self._device = str(value)
        if value:
            self._key = str(value + '.status')
    def reset_device(self):
        self._device = ''
    device = pyqtProperty(str, get_device, set_device, reset_device)

    def get_key(self):
        return self._key
    def set_key(self, value):
        self._key = str(value)
    def reset_key(self):
        self._key = ''
    key = pyqtProperty(str, get_key, set_key, reset_key)

    def on_keyChange(self, key, value, time, expired):
        if value is None:
            expired = True
            value = (OK, '')
        if expired:
            self.setLedStatus(False)
        else:
            self.setLedStatus(True)
        if value[0] == OK:
            self.setLedColor('green')
        elif value[0] in (BUSY, PAUSED):
            self.setLedColor('yellow')
        else:
            self.setLedColor('red')
