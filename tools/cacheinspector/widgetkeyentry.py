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

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot, pyqtProperty
from PyQt4.QtGui import QWidget, QLineEdit, QCheckBox, QSpacerItem, QDialog, \
    QSizePolicy, QColor, QMessageBox

from nicos.guisupport.utils import setBackgroundColor

from .windowaddkey import WindowAddKey  # pylint: disable=F0401


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
    def __init__(self, cacheaccess, watcher, entry,
                 shortKey, showTimeStamp, showTTL, parent=None):
        QWidget.__init__(self, parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)), 'ui',
                             'WidgetKeyEntry.ui'), self)
        self.watcher = watcher
        self.cacheAccess = cacheaccess
        self.entry = entry
        self.widgetValue = None
        self.setupWidgetUi(shortKey, showTimeStamp, showTTL)
        self.setupEvents()
        cacheaccess.signals.keyUpdated.connect(self.keyUpdated)

    def setupEvents(self):
        """ Sets up all events. """
        self.buttonSet.clicked.connect(self.setKey)
        self.buttonDel.clicked.connect(self.delKey)
        self.buttonWatch.clicked.connect(self.watchKey)

    def setupWidgetUi(self, shortKey, showTimeStamp, showTTL):
        """
        Sets up and generate a UI according to the data type of the value
        and whether or not time to live or time stamp should be shown.
        """
        entry = self.entry

        if self.watcher is None:  # widget is already in watcher
            self.buttonWatch.hide()

        if shortKey:
            self.labelKey.setText(entry.key.rpartition('/')[2])
            self.labelKey.setToolTip(entry.key)
        else:
            self.labelKey.setText(entry.key)

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
        self.labelTime.setText(entry.convertTime())

    def setKey(self):
        """ Sets the key locally and on the server. """
        dlg = WindowAddKey(self)
        dlg.fillEntry(self.entry)
        dlg.valueTime.setText('')  # we want current timestamp by default
        dlg.valueKey.setReadOnly(True)
        if dlg.exec_() != QDialog.Accepted:
            return
        entry = dlg.getEntry()
        self.cacheAccess.put(entry.key, entry)

    def delKey(self):
        if QMessageBox.question(
                self, 'Delete', 'Really delete?',
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        self.cacheAccess.delete(self.entry.key)

    def watchKey(self):
        """Adds our key to the watcher window."""
        if not self.watcher:
            return
        widget = WidgetKeyEntry(self.cacheAccess, None, self.entry,
                                False, True, True, self.watcher)
        self.watcher.addWidgetKey(widget)
        self.watcher.show()

    def keyUpdated(self, key, entry):
        if key != self.entry.key:
            return
        self.entry = entry
        self.updateValues()
