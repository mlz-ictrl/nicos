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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""NICOS GUI scan plot window -- SINQ flavour."""

from nicos.clients.flowui.panels import get_icon
from nicos.clients.flowui.panels.scans import ScansPanel as FlowuiScansPanel
from nicos.clients.gui.dialogs.filesystem import FileFilterDialog
from nicos.devices.datasinks.scan import AsciiScanfileReader
from nicos.guisupport.qt import QDialog, QToolBar, pyqtSlot

from nicos_sinq.devices.illasciisink import ILLAsciiScanfileReader


class ScansPanel(FlowuiScansPanel):

    def set_icons(self):
        FlowuiScansPanel.set_icons(self)
        self.actionOpen.setIcon(get_icon('folder_open-24px.svg'))

    def createPanelToolbar(self):
        default_bar, fitbar = FlowuiScansPanel.createPanelToolbar(self)
        bar = QToolBar('Scans')
        bar.addAction(self.actionOpen)
        for action in default_bar.actions():
            bar.addAction(action)
        return bar, fitbar

    @pyqtSlot()
    def on_actionOpen_triggered(self):
        """Open image file using registered reader classes."""
        ffilters = {
            'Scan files (*.dat)': AsciiScanfileReader,
            'SINQ TAS files (*.dat *.scn)': ILLAsciiScanfileReader,
        }
        fdialog = FileFilterDialog(self, "Open data files", "",
                                   ";;".join(ffilters.keys()))
        if self._fileopen_filter:
            fdialog.selectNameFilter(self._fileopen_filter)
        if fdialog.exec() != QDialog.DialogCode.Accepted:
            return
        files = fdialog.selectedFiles()
        if not files:
            return
        self._fileopen_filter = fdialog.selectedNameFilter()
        for f in files:
            try:
                self.data.on_client_dataset(
                    ffilters[self._fileopen_filter](f).scandata
                )
            except Exception as err:
                self.showError("Can't load scan file: %s (%s)" % (f, err))
