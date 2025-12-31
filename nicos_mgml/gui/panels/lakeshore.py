# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Petr Cermak <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""Lakeshore panel."""

from nicos.clients.gui.panels.generic import GenericPanel
from nicos.guisupport.qt import pyqtSlot
from nicos.utils import findResource

from nicos_mgml.gui import uipath


class LakeshorePanel(GenericPanel):
    """Better fast control of LS 350 regulator."""

    # this needs to be unique!
    panelName = 'Lakeshore panel'

    def __init__(self, parent, client, options):
        options.update({'uifile': findResource(f'{uipath}/panels/lakeshore.ui')})
        GenericPanel.__init__(self, parent, client, options)

    @pyqtSlot()
    def on_vtiapplyButton_clicked(self):
        self.client.run(f'T_vti.ramp = {self.vtiRamp.getValue()}')
        self.client.run(f'move("T_vti", {self.vtiTarget.getValue()})')
        self.client.run(f'move("range_vti", "{self.vtiRange.getValue()}")')

    @pyqtSlot()
    def on_sampleapplyButton_clicked(self):
        self.client.run(f'T_sample.ramp = {self.sampleRamp.getValue()}')
        self.client.run(f'move("T_sample", {self.sampleTarget.getValue()})')
        self.client.run(f'move("range_sample", "{self.sampleRange.getValue()}")')

    @pyqtSlot()
    def on_mainsorbapplyButton_clicked(self):
        self.client.run(f'T_mainsorb.ramp = {self.mainsorbRamp.getValue()}')
        self.client.run(f'move("T_mainsorb", {self.mainsorbTarget.getValue()})')
        self.client.run(f'move("range_mainsorb", "{self.mainsorbRange.getValue()}")')

    @pyqtSlot()
    def on_minisorbapplyButton_clicked(self):
        self.client.run(f'T_minisorb.ramp = {self.minisorbRamp.getValue()}')
        self.client.run(f'move("T_minisorb", {self.minisorbTarget.getValue()})')
        self.client.run(f'move("range_minisorb", "{self.minisorbRange.getValue()}")')
