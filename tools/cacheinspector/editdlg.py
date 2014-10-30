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

from PyQt4 import uic
from PyQt4.QtGui import QDialog, QMessageBox

from nicos.protocols.cache import cache_load

from .cacheclient import Entry  # pylint: disable=F0401


class EntryEditDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(join(path.dirname(path.abspath(__file__)), 'ui',
                        'entryedit.ui'), self)
        self.setupEvents()

    def setupEvents(self):
        """Set up the events."""
        self.buttonBox.accepted.connect(self.okPressed)

    def okPressed(self):
        try:
            cache_load(self.valueValue.text())
        except ValueError:
            if QMessageBox.question(
                    self, 'Really?', 'The value you entered for key %s '
                    'does not conform to the serialization format used by NICOS'
                    ' and therefore cannot be used by NICOS cache clients.\n\n'
                    'Really set this value?' % self.valueKey.text(),
                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return
        self.accept()

    def fillEntry(self, entry):
        self.valueKey.setText(entry.key)
        self.valueValue.setText(entry.value)
        self.valueTTL.setText(str(entry.ttl or ''))
        self.valueTime.setText(entry.convertTime())

    def getEntry(self):
        entry = Entry(self.valueKey.text(), self.valueValue.text(),
                      Entry.parseTime(self.valueTime.text()),
                      float(self.valueTTL.text() or '0') or None, False)
        return entry
