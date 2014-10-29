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

from os import path
from os.path import join
import datetime
from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QLineEdit, QLabel, QCheckBox, QSpacerItem,\
    QSizePolicy, QPalette, QColor #, QSpinBox

class WidgetKeyEntry(QWidget):
    def __init__(self, cacheaccess, fullKey, key, value, showTimeStamp, showTTL,
                 parent = None):
        QWidget.__init__(self)
        uic.loadUi(join(path.dirname(path.abspath(__file__)), 'ui',
                        'WidgetKeyEntry.ui'), self)
        self.cacheAccess = cacheaccess
        self.fullKey = fullKey
        self.widgetValue = None
        self.setupWidgetUi(key, value, showTimeStamp, showTTL)
        self.setupEvents()

    def setupWidgetUi(self, key, value, showTimeStamp, showTTL):
        """
            Sets up and generate a UI according to the data type of the value
            and whether or not time to live or time stamp should be shown.
        """
        self.labelTTL = QLabel()
        self.labelTimeStamp = QLabel()
        widgetValuePal = QPalette()
        widgetPal = QPalette()
        self.buttonSet.setVisible(False)
        self.labelKey.setText(key[str(key).rfind('/') + 1:])
        t, ttl, value = value
        self.labelKey.setToolTip(self.fullKey)
        if ttl:
            color = QColor(0xce, 0x9b, 0x9b)
            widgetValuePal.setColor(QPalette.Base, color)
            widgetPal.setColor(QPalette.Background, color)
            self.setAutoFillBackground(True)
            self.setPalette(widgetPal)

        if isinstance(value, bool) or value in ('True', 'False'):
            self.widgetValue = QCheckBox()
            if value in (True, 'True'):
                self.widgetValue.setCheckState(Qt.Checked)
            else:
                self.widgetValue.setCheckState(Qt.Unchecked)
            self.layoutWidget.insertSpacerItem(1, QSpacerItem(56, 20,
                                                        QSizePolicy.Expanding))
            self.widgetValue.setDisabled(True)
        else:
            self.widgetValue = QLineEdit()
            self.widgetValue.setText(str(value))
            self.widgetValue.setReadOnly(True)
        self.widgetValue.setToolTip(key)
        self.layoutWidget.insertWidget(1, self.widgetValue)
        self.widgetValue.setPalette(widgetValuePal)
        if showTTL:
            self.labelTTL.setText(self.cacheAccess.getTTL(self.fullKey))
            self.labelTTL.setToolTip('Time to Live')
            self.layoutWidget.insertWidget(0, self.labelTTL)
        if showTimeStamp:
            self.labelTimeStamp.setText(self.convertToUTC(
                self.cacheAccess.getTimeStamp(self.fullKey)))
            self.labelTimeStamp.setToolTip('Time Stamp')
            self.layoutWidget.insertWidget(0, self.labelTimeStamp)

    def setupEvents(self):
        """ Sets up all events. """
        self.buttonSet.clicked.connect(self.setKey)

    def setKey(self):
        """ Sets the key locally and on the server. """
        if isinstance(self.widgetValue, QCheckBox):
            if self.fullKey.find('!') == -1 \
                or self.fullKey.find('=') >= 0 \
                and self.fullKey.find('=') < self.fullKey.find('!'):
                self.cacheAccess.setKeyValue(self.fullKey[:self.fullKey.find('=')],
                                             self.widgetValue.isChecked())
            else:
                self.cacheAccess.setKeyValue(self.fullKey[:self.fullKey.find('!')],
                                             self.widgetValue.isChecked())
            for i in range(len(self.cacheAccess.entries)):
                if self.cacheAccess.entries[i] == (self.fullKey):
                    self.cacheAccess.entries[i] = \
                            self.fullKey[:self.fullKey.find('=')] + '='
                    self.cacheAccess.entries[i] += \
                            str(self.widgetValue.isChecked()) + '\n'
        else:
            if self.fullKey.find('!') == -1 \
                or self.fullKey.find('=') >= 0 \
                and self.fullKey.find('=') < self.fullKey.find('!'):
                self.cacheAccess.setKeyValue(self.fullKey[:self.fullKey.find('=')],
                                             self.widgetValue.text())
            else:
                self.cacheAccess.setKeyValue(self.fullKey[:self.fullKey.find('!')],
                                             self.widgetValue.text())
            for i in range(len(self.cacheAccess.entries)):
                if self.cacheAccess.entries[i] == (self.fullKey):
                    self.cacheAccess.entries[i] = \
                            self.fullKey[:self.fullKey.find('=')] + '='
                    self.cacheAccess.entries[i] += \
                            str(self.widgetValue.text() + '\n')
        self.updateValues()

    def updateValues(self, local=True):
        """
        Updates all information shown by the widget to the information in the
        local data.
        """
        #if not local:
        #    if self.fullKey.find('!') == -1
        #       or self.fullKey.find('=') >= 0
        #       and self.fullKey.find('=') < self.fullKey.find('!'):
        #        self.fullKey = self.cacheAccess.getKeyValue(self.fullKey[
        #               self.fullKey.find('@') + 1:self.fullKey.find('=')], True)
        #    else:
        #        self.fullKey = self.cacheAccess.getKeyValue(self.fullKey[
        #               self.fullKey.find('@') + 1:self.fullKey.find('!')], True)
        #    self.cacheAccess.entries


    def convertToUTC(self, unixTimeStamp):
        """ Converts the unix time stamp to a readable time stamp. """
        try:
            timeStamp = float(unixTimeStamp)
            return datetime.datetime.fromtimestamp(timeStamp).strftime(
                    '%d-%m-%Y %H:%M:%S')
        except ValueError:
            return '01-01-1970 00:00:00'
