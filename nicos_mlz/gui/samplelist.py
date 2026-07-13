# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI sample list widget."""

from os import path

from nicos.clients.gui.panels.setup_panel import GenericSampleWidget
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QAbstractItemView, QDialog, QDialogButtonBox, \
    QFrame, QListWidget, QListWidgetItem, QPushButton, Qt, QVBoxLayout, \
    QWidget, pyqtSignal, pyqtSlot
from nicos.utils import findResource


class SampleItem(QListWidgetItem):

    def __init__(self, parent=None, **params):
        QListWidgetItem.__init__(
            self, parent, QListWidgetItem.ItemType.UserType)
        self.setData(Qt.ItemDataRole.UserRole, params)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)


class SampleItemWidget(QWidget):

    def __init__(self, parent=None, **params):
        QWidget.__init__(self, parent)
        loadUi(self, findResource(path.join('nicos_mlz', 'gui', 'sample.ui')))
        loadUi(self.buttons, path.join('cmdlets', 'buttons.ui'))

        self.samplename.setText(params.get('samplename', ''))


class SampleListWidget(QListWidget):

    numberOfEntriesChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        self.itemDoubleClicked.connect(self.sampleEdit)
        self.paramInfo = None

    def setSamples(self, samples, paramInfo=None):
        self.clear()
        for s in samples:
            item = SampleItem(self, **s)
            self._addItemWidget(item, s)
        self.paramInfo = paramInfo

    def _addItemWidget(self, item, data):
        widget = SampleItemWidget(**data)
        widget.buttons.upBtn.clicked.connect(self.sampleUp)
        widget.buttons.downBtn.clicked.connect(self.sampleDown)
        widget.buttons.delBtn.clicked.connect(self.sampleRemove)
        item.setSizeHint(widget.sizeHint())
        self.setItemWidget(item, widget)

    @pyqtSlot()
    def sampleUp(self):
        if (row := self._findRow(self.sender())) > 0:
            data = self.item(row).data(Qt.ItemDataRole.UserRole)
            data['samplename'] = self.itemWidget(
                self.item(row)).samplename.text()
            item = self.takeItem(row)
            self.insertItem(row - 1, item)
            self._addItemWidget(item, data)

    @pyqtSlot()
    def sampleDown(self):
        if 0 <= (row := self._findRow(self.sender())) < self.count() - 1:
            data = self.item(row).data(Qt.ItemDataRole.UserRole)
            data['samplename'] = self.itemWidget(
                self.item(row)).samplename.text()
            item = self.takeItem(row)
            self.insertItem(row + 1, item)
            self._addItemWidget(item, data)

    @pyqtSlot()
    def sampleRemove(self):
        if (row := self._findRow(self.sender())) != -1:
            self.takeItem(row)
            self.numberOfEntriesChanged.emit(self.count())

    def sampleEdit(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        editor = SampleEditor(self.paramInfo, self, **data)
        if editor.exec() == QDialog.DialogCode.Accepted:
            new_data = editor.getData()
            item.setData(Qt.ItemDataRole.UserRole, new_data)
            self.itemWidget(item).samplename.setText(
                new_data.get('samplename', ''))

    def _findRow(self, button):
        if not button:
            return -1

        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            # Check if this widget contains the clicked button
            if widget and button in widget.findChildren(QPushButton):
                return self.row(item)
        return -1

    def generateCode(self):
        if not self.count():
            return ''
        code = ['ClearSamples()']
        for i in range(self.count()):
            it = self.item(i)
            data = [f'{k}={v!r}' for k, v in
                    it.data(Qt.ItemDataRole.UserRole).items()
                    if k != 'samplename']
            code.append(f'SetSample({i}, '
                        f'{self.itemWidget(it).samplename.text()!r}, '
                        f"{', '.join(data)})")
        return '\n'.join(code).rstrip()


class SampleEditor(QDialog):

    def __init__(self, paramInfo, parent=None, **params):
        QDialog.__init__(self, parent)
        self.setWindowTitle('Modify sample')
        layout = QVBoxLayout(self)

        self.editor = GenericSampleWidget()
        self.editor.setParameters(paramInfo, params)
        layout.addWidget(self.editor)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

    def getData(self):
        return self.editor.getParams()
