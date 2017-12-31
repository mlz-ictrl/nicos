#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************

from os import path

from nicos.guisupport.qt import uic, QRegExp, QDialog, QRegExpValidator


class NewSetupDialog(QDialog):
    def __init__(self, instruments, instrument=None, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(path.abspath(path.join(path.dirname(__file__),
                                          '..',
                                          'ui',
                                          'dialogs',
                                          'newsetupdialog.ui')), self)
        self.setInstruments(instruments)
        if instrument:
            self.setCurrentInstrument(instrument)
            self.comboBoxInstrument.setDisabled(True)
        self.lineEditFileName.setValidator(QRegExpValidator(
            QRegExp('[A-Za-z_]{1}[A-Za-z0-9_]*')))

    def setInstruments(self, instruments):
        self.comboBoxInstrument.addItems(sorted(instruments))

    def setCurrentInstrument(self, instrument):
        self.comboBoxInstrument.setCurrentIndex(
            self.comboBoxInstrument.findText(instrument))

    def currentInstrument(self):
        return self.comboBoxInstrument.currentText()

    def isSpecialSetup(self):
        return self.checkBoxSpecial.isChecked()

    def getValue(self):
        return self.lineEditFileName.text()
