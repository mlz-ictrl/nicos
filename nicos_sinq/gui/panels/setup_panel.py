#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

from nicos.clients.gui.panels.setup_panel import ExpPanel as MlzExpPanel
from nicos.guisupport.qt import QDialog, QFileDialog, QLineEdit
from nicos.guisupport.widget import NicosWidget, PropDef

from nicos_sinq.gui import uipath


class LineEdit(QLineEdit, NicosWidget):
    key = PropDef('key', str, '', 'Cache key to display (without "nicos/"'
                                  'prefix), set either "dev" or this')

    def __init__(self, parent, designMode=False):
        QLineEdit.__init__(self, parent)
        NicosWidget.__init__(self)

    def registerKeys(self):
        self.registerKey(self.props['key'])

    def on_keyChange(self, key, value, time, expired):
        self.setText(value)


class ExpPanel(MlzExpPanel):
    """
    Extends the MlzExpPanel and let the user select the experiment scriptpath
    """

    ui = '%s/panels/setup_exp.ui' % uipath

    def __init__(self, parent, client, options):
        MlzExpPanel.__init__(self, parent, client, options)
        self.expTitle.key = 'exp/title'
        self.expTitle.setClient(client)
        self.scriptPathLine.returnPressed.connect(self.on_script_path_changed)
        self.scriptPathButton.clicked.connect(
            self.on_script_path_button_clicked)

    def on_client_connected(self):
        # fill proposal
        self._update_proposal_info()
        self.newBox.setVisible(True)
        # check for capability to ask proposal database
        if self.client.eval('session.experiment._canQueryProposals()',
                            None):
            self.propdbInfo.setVisible(True)
            self.queryDBButton.setVisible(True)
        else:
            self.queryDBButton.setVisible(False)
        self.setViewOnly(self.client.viewonly)
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
