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
"""NICOS GUI user editor utility classes."""


from PyQt4.QtGui import QDialog, QMessageBox, QStyle
from PyQt4.QtCore import pyqtSlot

from nicos.guisupport.utils import waitCursor
from nicos.clients.gui.utils import loadUi


class SearchDialog(QDialog):
    def __init__(self, parent, editor, has_scintilla):
        QDialog.__init__(self, parent)
        loadUi(self, 'search.ui', 'panels')

        self.editor = editor
        self.found = False
        self.forward = True

        if not has_scintilla:
            # QPlainTextEdit doesn't support some find flags
            self.regexpCheckBox.setEnabled(False)
            self.wrapCheckBox.setEnabled(False)
            self.wrapCheckBox.setChecked(False)

        for box in [self.regexpCheckBox, self.caseCheckBox, self.wordCheckBox,
                    self.wrapCheckBox]:
            box.toggled.connect(self.reset_found)

    @pyqtSlot()
    def on_findNextButton_clicked(self):
        self.findPrevButton.setDefault(False)
        self.findNextButton.setDefault(True)
        if self.found and self.forward:
            return self.editor.findNext()

        ret = self.editor.findFirst(
            self.findText.currentText(),
            self.regexpCheckBox.isChecked(),
            self.caseCheckBox.isChecked(),
            self.wordCheckBox.isChecked(),
            self.wrapCheckBox.isChecked())
        self.found = ret
        self.forward = True
        return ret

    @pyqtSlot()
    def on_findPrevButton_clicked(self):
        self.findNextButton.setDefault(False)
        self.findPrevButton.setDefault(True)
        if self.found and not self.forward:
            return self.editor.findNext()

        ret = self.editor.findFirst(
            self.findText.currentText(),
            self.regexpCheckBox.isChecked(),
            self.caseCheckBox.isChecked(),
            self.wordCheckBox.isChecked(),
            self.wrapCheckBox.isChecked(),
            False)
        self.found = ret
        self.forward = False
        return ret

    def reset_found(self, *args):
        self.found = False

    @pyqtSlot()
    def on_replaceButton_clicked(self):
        if not self.found:
            if not self.on_findNextButton_clicked():
                return
        self.editor.replace(self.replaceText.currentText())
        self.on_findNextButton_clicked()

    @pyqtSlot()
    def on_replaceAllButton_clicked(self):
        found = self.editor.findFirst(
                self.findText.currentText(),
                self.regexpCheckBox.isChecked(),
                self.caseCheckBox.isChecked(),
                self.wordCheckBox.isChecked(),
                False,
                forward=True,
                line=0,
                index=0,
                show=False)
        if not found:
            return
        with waitCursor():
            rtext = self.replaceText.currentText()
            self.editor.replace(rtext)
            while self.editor.findNext():
                self.editor.replace(rtext)

    def setEditor(self, editor):
        self.editor = editor
        self.reset_found()


class OverwriteQuestion(QMessageBox):
    """Special QMessageBox for asking what to do when a script is running."""

    def __init__(self):
        QMessageBox.__init__(self, QMessageBox.Question, 'Code generation',
                             'Do you want to append to or overwrite the '
                             'current code?',
                             QMessageBox.NoButton)
        self.b0 = self.addButton('Append', QMessageBox.YesRole)
        self.b1 = self.addButton('Overwrite', QMessageBox.ApplyRole)
        self.b2 = self.addButton('Cancel', QMessageBox.RejectRole)
        self.b2.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))

    def exec_(self):
        QMessageBox.exec_(self)
        btn = self.clickedButton()
        if btn == self.b0:
            return QMessageBox.Yes    # Append
        if btn == self.b1:
            return QMessageBox.Apply  # Overwrite
        return QMessageBox.Cancel     # Cancel
