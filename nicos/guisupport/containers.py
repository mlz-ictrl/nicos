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
Custom container widgets.
"""

from nicos.guisupport.qt import pyqtSignal, uic, QHBoxLayout, QSizePolicy, \
    QSpacerItem, QToolButton, QVBoxLayout, QWidget

from nicos.guisupport.widget import NicosWidget, PropDef


class MultiEntry(QWidget):
    addOrRemove = pyqtSignal()

    def __init__(self, parent, client, uifile):
        QWidget.__init__(self, parent)
        new_layout = QHBoxLayout()
        self.subwidget = QWidget(self)
        if uifile:
            uic.loadUi(uifile, self.subwidget)
        self.button = QToolButton(self)
        self.setButton('+')
        self.button.clicked.connect(self.on_button_click)
        new_layout.addWidget(self.subwidget)
        new_layout.addSpacerItem(QSpacerItem(15, 1, QSizePolicy.Fixed))
        new_layout.addWidget(self.button)
        new_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(new_layout)
        for ch in self.subwidget.findChildren(NicosWidget):
            ch.setClient(client)

    def setButton(self, plusminus):
        self.button.setText(plusminus)
        if plusminus == '+':
            self.button.setToolTip('Add another')
        else:
            self.button.setToolTip('Remove this')

    def on_button_click(self):
        self.addOrRemove.emit()


class MultiList(NicosWidget, QWidget):
    """A list of entries, where each entry is a frame loaded from a UI file."""

    designer_description = 'A list (with add/remove controls) of .ui entries'

    properties = {
        'uifile': PropDef(str, '', 'UI file to use for the entries'),
    }

    entryAdded = pyqtSignal(object)
    entryRemoved = pyqtSignal(object)

    def __init__(self, parent, designMode=False, **kwds):
        QWidget.__init__(self, parent, **kwds)
        NicosWidget.__init__(self)
        self._entries = []
        self._vlayout = QVBoxLayout()
        self._vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._vlayout)
        self._add()
        self._designer = designMode

    def registerKeys(self):
        pass

    def propertyUpdated(self, pname, value):
        if pname == 'uifile':
            self.clear()
        NicosWidget.propertyUpdated(self, pname, value)

    def entry(self, i):
        return self._entries[i].subwidget

    def entries(self):
        return [e.subwidget for e in self._entries]

    def count(self):
        return len(self._entries)

    def clear(self):
        for entry in self._entries[::-1]:
            self._remove(entry)
        self._add()

    def _remove(self, entry):
        self._entries.remove(entry)
        self._vlayout.removeWidget(entry)
        self.entryRemoved.emit(entry.subwidget)
        entry.deleteLater()
        if self._entries:
            self._entries[-1].setButton('+')

    def _add(self):
        new_frame = MultiEntry(self, self._client, self.props['uifile'])
        new_frame.addOrRemove.connect(self._addRemove)
        if self._entries:
            self._entries[-1].setButton('-')
        self._entries.append(new_frame)
        self._vlayout.addWidget(new_frame)
        self.entryAdded.emit(self._entries[-1].subwidget)

    def _addRemove(self):
        if not self._entries or self.sender() is self._entries[-1]:
            self._add()
        else:
            self._remove(self.sender())
