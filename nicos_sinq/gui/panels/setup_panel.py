#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""NICOS GUI experiment setup window."""

from nicos.clients.flowui.panels.setup_panel import ExpPanel as EssExpPanel
from nicos.guisupport.qt import QDialog, QFileDialog

from nicos_sinq.gui import uipath


class ExpPanel(EssExpPanel):
    """
    Extends the EssExpPanel and let the user select the experiment scriptpath
    """

    ui = '%s/panels/setup_exp.ui' % uipath

    def __init__(self, parent, client, options):
        EssExpPanel.__init__(self, parent, client, options)
        self.scriptPathLine.returnPressed.connect(self.on_script_path_changed)
        self.scriptPathButton.clicked.connect(
            self.on_script_path_button_clicked)

    def on_client_connected(self):
        EssExpPanel.on_client_connected(self)
        scriptpath = self.client.eval('session.experiment.scriptpath', '.')
        self.scriptPathLine.setText(scriptpath)

    def on_script_path_changed(self):
        scriptpath = self.scriptPathLine.text()
        self.client.run(f'Exp.scriptpath = "{scriptpath}"')

    def on_script_path_button_clicked(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        if dialog.exec_() == QDialog.Accepted:
            scriptpath = dialog.selectedFiles()[0]
            self.client.run(f'Exp.scriptpath = "{scriptpath}"')
            self.scriptPathLine.setText(scriptpath)
