#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#   Pascal Neubert <pascal.neubert@frm2.tum.de>
#
# *****************************************************************************

import time
from os import path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot, pyqtProperty
from PyQt4.QtGui import QWidget, QLineEdit, QCheckBox, QSpacerItem, \
    QSizePolicy, QColor

from nicos.guisupport.utils import setBackgroundColor


class ReadOnlyCheckBox(QCheckBox):

    def __init__(self, *args):
        QCheckBox.__init__(self, *args)
        self._readOnly = True

    def isReadOnly(self):
        return self._readOnly

    def mousePressEvent(self, event):
        if self.isReadOnly():
            event.accept()
        else:
            QCheckBox.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.isReadOnly():
            event.accept()
        else:
            QCheckBox.mouseReleaseEvent(self, event)

    @pyqtSlot(bool)
    def setReadOnly(self, state):
        self._readOnly = state

    readOnly = pyqtProperty(bool, isReadOnly, setReadOnly)


class WidgetKeyEntry(QWidget):
    def __init__(self, cacheaccess, entry, showTimeStamp, showTTL, parent=None):
        QWidget.__init__(self, parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)), 'ui',
                             'WidgetKeyEntry.ui'), self)
        self.cacheAccess = cacheaccess
        self.entry = entry
        self.widgetValue = None
        self.setupWidgetUi(showTimeStamp, showTTL)
        self.setupEvents()
        cacheaccess.signals.keyUpdated.connect(self.keyUpdated)

    def setupEvents(self):
        """ Sets up all events. """
        self.buttonSet.clicked.connect(self.setKey)

    def setupWidgetUi(self, showTimeStamp, showTTL):
        """
        Sets up and generate a UI according to the data type of the value
        and whether or not time to live or time stamp should be shown.
        """
        entry = self.entry

        self.buttonSet.setVisible(False)
        self.labelKey.setText(entry.key.rpartition('/')[2])
        self.labelKey.setToolTip(entry.key)

        if entry.value in ('True', 'False'):
            self.widgetValue = ReadOnlyCheckBox()
            self.layoutWidget.insertWidget(4, self.widgetValue)
            self.layoutWidget.insertSpacerItem(
                5, QSpacerItem(56, 20, QSizePolicy.Expanding))
        else:
            self.widgetValue = QLineEdit()
            self.layoutWidget.insertWidget(4, self.widgetValue)
        self.widgetValue.setReadOnly(True)
        self.widgetValue.setToolTip(entry.key)

        if not showTTL:
            self.labelTTL.hide()
        if not showTimeStamp:
            self.labelTime.hide()

        self.updateValues()

    def updateValues(self):
        entry = self.entry

        if entry.expired:
            color = QColor(0xce, 0x9b, 0x9b)
            setBackgroundColor(self, color)
        elif entry.ttl:
            color = QColor(0xff, 0xfa, 0x66)
            setBackgroundColor(self, color)

        if isinstance(self.widgetValue, ReadOnlyCheckBox):
            self.widgetValue.setChecked(entry.value == 'True')
        else:
            self.widgetValue.setText(entry.value)

        self.labelTTL.setText(entry.ttl or '')
        self.labelTime.setText(self.convertTime(entry.time))

    def setKey(self):
        """ Sets the key locally and on the server. """
        # if isinstance(self.widgetValue, QCheckBox):
        #     if self.fullKey.find('!') == -1 \
        #         or self.fullKey.find('=') >= 0 \
        #         and self.fullKey.find('=') < self.fullKey.find('!'):
        #         self.cacheAccess.setKeyValue(self.fullKey[:self.fullKey.find('=')],
        #                                      self.widgetValue.isChecked())
        #     else:
        #         self.cacheAccess.setKeyValue(self.fullKey[:self.fullKey.find('!')],
        #                                      self.widgetValue.isChecked())
        #     for i in range(len(self.cacheAccess.entries)):
        #         if self.cacheAccess.entries[i] == (self.fullKey):
        #             self.cacheAccess.entries[i] = \
        #                     self.fullKey[:self.fullKey.find('=')] + '='
        #             self.cacheAccess.entries[i] += \
        #                     str(self.widgetValue.isChecked()) + '\n'
        # else:
        #     if self.fullKey.find('!') == -1 \
        #         or self.fullKey.find('=') >= 0 \
        #         and self.fullKey.find('=') < self.fullKey.find('!'):
        #         self.cacheAccess.setKeyValue(self.fullKey[:self.fullKey.find('=')],
        #                                      self.widgetValue.text())
        #     else:
        #         self.cacheAccess.setKeyValue(self.fullKey[:self.fullKey.find('!')],
        #                                      self.widgetValue.text())
        #     for i in range(len(self.cacheAccess.entries)):
        #         if self.cacheAccess.entries[i] == (self.fullKey):
        #             self.cacheAccess.entries[i] = \
        #                     self.fullKey[:self.fullKey.find('=')] + '='
        #             self.cacheAccess.entries[i] += \
        #                     str(self.widgetValue.text() + '\n')
        # self.updateValues()

    def keyUpdated(self, key, entry):
        if key != self.entry.key:
            return
        self.entry = entry
        self.updateValues()

    def convertTime(self, unixTimeStamp):
        """ Converts the unix time stamp to a readable time stamp. """
        ttup = time.localtime(unixTimeStamp)
        if ttup[:3] == time.localtime()[:3]:
            return time.strftime('%H:%M:%S', ttup)
        else:
            return time.strftime('%Y-%m-%d %H:%M:%S', ttup)
