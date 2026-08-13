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

"""NICOS GUI sample setup window."""

from os import path

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QDialogButtonBox, pyqtSlot
from nicos.utils import findResource


class SamplePanel(Panel):
    """MLZ sample setup window."""

    panelName = 'MLZ Sample setup'
    uiName = path.join('nicos_mlz', 'gui', 'setup_sample.ui')

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource(self.uiName))
        self.client.connected.connect(self.on_client_connected)
        self.client.disconnected.connect(self.on_client_disconnected)
        self.samples.numberOfEntriesChanged.connect(self.enableDisableApply)

        if client.isconnected:
            self.on_client_connected()
        else:
            self.on_client_disconnected()

    @pyqtSlot()
    def on_client_connected(self):
        sample_dev = self.client.eval('session.experiment.sample', 'Sample')
        paramInfo = self.client.getDeviceParamInfo(sample_dev)
        params = self.client.getDeviceParams(sample_dev)
        self.samples.setSamples(
            [sample for _, sample in sorted(params.get('samples', {}).items())],
            paramInfo)
        self.enableDisableApply(self.samples.count())

    @pyqtSlot()
    def on_client_disconnected(self):
        self.samples.clear()
        self.setViewOnly(True)

    def setViewOnly(self, viewonly):
        btns = self.buttonBox.standardButtons()
        if viewonly:
            btns &= ~QDialogButtonBox.StandardButton.Apply
        else:
            btns |= QDialogButtonBox.StandardButton.Apply
        self.buttonBox.setStandardButtons(btns)

    def applyChanges(self):
        if code := self.samples.generateCode().rstrip():
            if self.client.run(code, noqueue=True) is not None:
                self.showInfo('Samples set.')
            else:
                self.showError("Couldn't set samples")

    def on_buttonBox_clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.ApplyRole:
            self.applyChanges()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.closeWindow()

    @pyqtSlot(int)
    def enableDisableApply(self, rows):
        self.setViewOnly(not rows or self.client.viewonly)
