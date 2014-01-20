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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Dialog for showing information about new plug-and-play events."""

from PyQt4.QtGui import QMessageBox, QStyle
from PyQt4.QtCore import Qt, SIGNAL


class PnPSetupQuestion(QMessageBox):
    """Special QMessageBox for asking what to do a new setup was detected."""

    def __init__(self, parent, data, load_callback):
        self.setup = data[1]
        message = ('<b>New sample environment detected</b><br/>'
                   'A new sample environment <b>%s</b> has been detected:<br/>%s'
                   % (data[1], data[2] or ''))
        QMessageBox.__init__(self, QMessageBox.Information, 'NICOS Plug & Play',
                             message, QMessageBox.NoButton, parent)
        self.setWindowModality(Qt.NonModal)
        self.b0 = self.addButton('Ignore', QMessageBox.RejectRole)
        self.b0.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.b1 = self.addButton('Load setup', QMessageBox.YesRole)
        self.b1.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        self.b0.clicked.connect(self.on_ignore_clicked)
        self.b1.clicked.connect(self.on_load_clicked)
        self.b0.setFocus()
        self.load_callback = load_callback

    def on_ignore_clicked(self):
        self.emit(SIGNAL('closed'), self)
        self.reject()

    def on_load_clicked(self):
        self.load_callback()
        self.emit(SIGNAL('closed'), self)
        self.accept()

    def closeEvent(self, event):
        self.emit(SIGNAL('closed'), self)
        return QMessageBox.closeEvent(self, event)
