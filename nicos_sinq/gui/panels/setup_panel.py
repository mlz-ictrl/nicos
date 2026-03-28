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
#   Michele Brambilla <michele.brambilla@psi.ch>
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

"""NICOS GUI experiment setup window."""

from nicos.clients.flowui.panels.setup_panel import FinishPanel as CoreFinishPanel
from nicos.clients.gui.panels.setup_panel import ExpPanel as CoreExpPanel
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


class ExpPanel(CoreExpPanel):
    """
    Extends the CoreExpPanel and let the user select the experiment scriptpath
    """

    ui = '%s/panels/setup_exp.ui' % uipath

    def __init__(self, parent, client, options):
        CoreExpPanel.__init__(self, parent, client, options)
        self.expTitle.key = 'exp/title'
        self.expTitle.setClient(client)
        self.scriptPathLine.returnPressed.connect(self.on_script_path_changed)
        self.scriptPathButton.clicked.connect(
            self.on_script_path_button_clicked)

        # Hide widgets we don't use at SINQ. Simply removing them is not so
        # easy, because they are used in some methods of the base MlzExpPanel
        # (e.g. nicos.clients.gui.panels.setup_panel.ExpPanel._update_proposal_info).
        # Overloading all these methods would be tedious and error-prone.
        self.notifEmails.setVisible(False)
        self.notifEmailsLabel.setVisible(False)
        self.dataEmails.setVisible(False)
        self.dataEmailsLabel.setVisible(False)
        self.errorAbortBox.setVisible(False)

    def on_client_connected(self):
        # fill proposal
        self._update_proposal_info()
        self.newBox.setVisible(True)
        # check for capability to ask proposal database
        if self.client.eval('session.experiment._canQueryProposals()', False):
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
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            scriptpath = dialog.selectedFiles()[0]
            self.client.run(f'Exp.scriptpath = "{scriptpath}"')
            self.scriptPathLine.setText(scriptpath)

class FinishPanel(CoreFinishPanel):
    """
    A FinishPanel with an interface for providing instrument-specific
    information on the effect of the "Finish Experiment" button via the
    _finish_text method.
    """

    def _enable_finishing(self):
        exp_name = self.client.eval('session.experiment.title', 'Service')
        if self._is_user_experiment():
            if self.client.viewonly:
                self.finishText.setText(f'Experiment "{exp_name}" is currently '
                                        'running. It cannot be finished from this '
                                        'view-only client instance')
                self.finishButton.setEnabled(False)
            else:
                self.finishText.setText(self._finish_text())
                self.finishButton.setEnabled(True)
        else:
            self.finishText.setText(
                'Instrument is currently in service mode, therefore there is '\
                'no experiment to finish.'
            )
            self.finishButton.setEnabled(False)

    def _finish_text(self) -> str:
        """
        The string returned by this method is shown next to the "Finish Button"
        on the FinishPanel. To provide instrument-specific information, just
        derive a custom FinishPanel and overload this method to return a
        different string.
        """
        exp_name = self.client.eval('session.experiment.title', 'Service')
        return (
            f'Experiment "{exp_name}" is currently running. Finishing it '
            'has the following effects:\n\n'
            '- Switch into service mode\n'
            '- Upload data into SciCat\n'
            '\nIf the proposal is still valid, it is always possible to '
            'start the experiment again.'
        )
