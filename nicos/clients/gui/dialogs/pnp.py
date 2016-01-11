#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
from PyQt4.QtCore import Qt, pyqtSignal, SIGNAL


class PnPSetupQuestion(QMessageBox):
    """Special QMessageBox for asking what to do a new setup was detected."""

    closed = pyqtSignal('QMessageBox')

    def __init__(self, parent, client, data):
        self.client = client
        self.connect(client, SIGNAL('setup'), self.on_client_setup)
        self.data = data
        add_mode = data[0] == 'added'
        if add_mode:
            message = (
                '<b>New sample environment detected</b><br/>'
                'A new sample environment <b>%s</b> has been detected:<br/>%s'
                % (data[1], data[2] or ''))
        else:
            message = (
                '<b>Sample environment removed</b><br/>'
                'The sample environment <b>%s</b> has been removed:<br/>%s'
                % (data[1], data[2] or ''))
        QMessageBox.__init__(self, QMessageBox.Information, 'NICOS Plug & Play',
                             message, QMessageBox.NoButton, parent)
        self.setWindowModality(Qt.NonModal)
        self.b0 = self.addButton('Ignore', QMessageBox.RejectRole)
        self.b0.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        if add_mode:
            self.b1 = self.addButton('Load setup', QMessageBox.YesRole)
        else:
            self.b1 = self.addButton('Remove setup', QMessageBox.YesRole)
        self.b1.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        self.b0.clicked.connect(self.on_ignore_clicked)
        self.b1.clicked.connect(self.on_execute_clicked)
        self.b0.setFocus()

    def on_ignore_clicked(self):
        self.closed.emit(self)
        self.reject()

    def on_execute_clicked(self):
        if self.data[0] == 'added':
            self.client.run('AddSetup(%r)' % self.data[1])
        else:
            self.client.run('RemoveSetup(%r)' % self.data[1])
        self.closed.emit(self)
        self.accept()

    def closeEvent(self, event):
        self.closed.emit(self)
        return QMessageBox.closeEvent(self, event)

    def on_client_setup(self, data):
        setupnames = data[0]
        if self.data[0] == 'added' and self.data[1] in setupnames:
            # somebody loaded the setup!
            self.on_ignore_clicked()
        elif self.data[0] == 'removed' and self.data[1] not in setupnames:
            # somebody unloaded the setup!
            self.on_ignore_clicked()
