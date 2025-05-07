# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

from nicos.guisupport.colors import colors
from nicos.guisupport.qt import QCheckBox, QDialog, QLineEdit, QMessageBox, \
    QSizePolicy, QSpacerItem, QTimer, pyqtProperty, pyqtSlot, uic
from nicos.guisupport.utils import setBackgroundColor

from nicostools.cacheinspector.editdlg import EntryEditDialog


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


ui_class, base_class = uic.loadUiType(
    path.join(path.dirname(path.abspath(__file__)), 'ui', 'entry.ui'))


class EntryWidget(base_class, ui_class):
    def __init__(self, client, watcher, entry,
                 shortKey, showTimeStamp, showTTL, parent=None):
        base_class.__init__(self, parent)
        self.setupUi(self)
        self.updateTimer = QTimer(self)
        self.updateTimer.setSingleShot(True)
        self.watcher = watcher
        self.client = client
        self.entry = entry
        self.widgetValue = None
        self.setupEvents()
        self.setupWidgetUi(shortKey, showTimeStamp, showTTL)

    def setupEvents(self):
        """Sets up all events."""
        self.buttonSet.clicked.connect(self.setKey)
        self.buttonDel.clicked.connect(self.delKey)
        self.buttonWatch.clicked.connect(self.watchKey)
        self.client.signals.keyUpdated.connect(self.keyUpdated)
        self.updateTimer.timeout.connect(self.updateTimerEvent)

    def setupWidgetUi(self, shortKey, showTimeStamp, showTTL):
        """
        Sets up and generate a UI according to the data type of the value
        and whether time to live or time stamp should be shown.
        """
        entry = self.entry

        fm = self.labelTime.fontMetrics()
        margins = self.labelTime.contentsMargins()
        self.labelTime.setMinimumWidth(fm.horizontalAdvance(entry.convertTime(1.0)) +
                                       margins.left() + margins.right() +
                                       self.labelTime.sizeHint().width())

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
                5, QSpacerItem(56, 20, QSizePolicy.Policy.Expanding))
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
            setBackgroundColor(self, colors.expired_color)
        elif entry.ttl:
            setBackgroundColor(self, colors.ttl_color)

        if isinstance(self.widgetValue, ReadOnlyCheckBox):
            self.widgetValue.setChecked(entry.value == 'True')
        else:
            self.widgetValue.setText(entry.value)

        self.labelTTL.setText(str(entry.ttl or ''))
        self.labelTime.setText(entry.convertTime())

        if entry.ttl:
            # automatically refresh the value if the entry has a ttl (we don't
            # get timestamp updates from the server unless the value changes)
            time_to_update = max((entry.time + entry.ttl) - time.time(), 0)
            self.updateTimer.start(int(time_to_update * 1000))

    def setKey(self):
        """Sets the key locally and on the server."""
        dlg = EntryEditDialog(self)
        dlg.fillEntry(self.entry)
        dlg.valueTime.setText('')  # we want current timestamp by default
        dlg.valueKey.setReadOnly(True)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        entry = dlg.getEntry()
        self.client.put(entry.key, entry)

    def delKey(self):
        if QMessageBox.question(self, 'Delete', 'Really delete?') == \
           QMessageBox.StandardButton.No:
            return
        self.client.delete(self.entry.key)

    def watchKey(self):
        """Adds our key to the watcher window."""
        if not self.watcher:
            return
        widget = EntryWidget(self.client, None, self.entry,
                             False, True, True, self.watcher)
        self.watcher.addWidgetKey(widget)
        self.watcher.show()

    def keyUpdated(self, key, entry):
        if key != self.entry.key:
            return
        self.entry = entry
        self.updateValues()

    def updateTimerEvent(self):
        self.client.update(self.entry.key)
