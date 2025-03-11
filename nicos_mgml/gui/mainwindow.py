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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from nicos.clients.gui.mainwindow import MainWindow as NICOSMainWindow
from nicos.guisupport.qt import QInputDialog, QMessageBox, Qt
from nicos.protocols.daemon import BREAK_NOW


class MainWindow(NICOSMainWindow):

    default_facility_logo = ':/mgml/mgml-logo-auth'
    default_connect_dialog_cls = 'nicos_mgml.gui.panels.auth.ConnectionDialog'

    def on_client_prompt(self, data):
        if self.promptWindow:
            self.promptWindow.close()

        if len(data) == 1:
            # show non-modal dialog box that prompts the user to continue or
            # abort
            prompt_text = data[0]
            dlg = self.promptWindow = QMessageBox(
                QMessageBox.Icon.Information, 'Confirmation required',
                prompt_text,
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                self)
            dlg.setWindowModality(Qt.WindowModality.NonModal)

            # give the buttons better descriptions
            btn = dlg.button(QMessageBox.StandardButton.Cancel)
            btn.setText('Abort script')
            btn.clicked.connect(lambda: self.client.tell_action('stop', BREAK_NOW))
            btn = dlg.button(QMessageBox.StandardButton.Ok)
            btn.setText('Continue script')
            btn.clicked.connect(lambda: self.client.tell_action('continue'))
            btn.setFocus()

            dlg.show()
        else:
            # show non-modal dialog box that prompts the user to continue or abort
            prompt_text = data[0]
            command = data[1]
            text, ok = QInputDialog.getText(self, 'Input requested', prompt_text)

            if ok:
                # execute the command
                self.client.tell('exec', command.format(text))
                self.client.tell_action('continue')
            else:
                self.client.tell_action('stop', BREAK_NOW)
