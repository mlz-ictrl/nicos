#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2020 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels import PanelDialog
from nicos.clients.gui.panels.generic import GenericPanel
from nicos.clients.gui.panels.setup_panel import DetEnvPanel, \
    GenericSamplePanel, SetupsPanel
from nicos.guisupport.qt import pyqtSlot
from nicos.guisupport.widget import NicosWidget

from nicos_sinq.amor.gui.panels.newexp import AmorNewExpPanel


class AmorExpPanel(GenericPanel):

    def __init__(self, parent, client, options):
        GenericPanel.__init__(self, parent, client, options)
        for ch in self.findChildren(NicosWidget):
            ch.setClient(client)
        client.setup.connect(self.on_client_setup)
        client.initstatus.connect(self.on_client_initstatus)

        self.detLabel.setFormatCallback(
            lambda value, strvalue: ', '.join(sorted(value)))
        self.envLabel.setFormatCallback(
            lambda value, strvalue: ', '.join(sorted(value)))

    def on_client_initstatus(self, initstatus):
        self.setupLabel.setText(', '.join(sorted(initstatus['setups'][1])))

    def on_client_setup(self, data):
        self.setupLabel.setText(', '.join(sorted(data[1])))

    @pyqtSlot()
    def on_proposalBtn_clicked(self):
        dlg = PanelDialog(self, self.client, AmorNewExpPanel, 'Proposal info',
                          uifile='nicos_sinq/amor/gui/panels/newexp.ui')
        dlg.exec_()

    @pyqtSlot()
    def on_setupBtn_clicked(self):
        dlg = PanelDialog(self, self.client, SetupsPanel, 'Setups')
        dlg.exec_()

    @pyqtSlot()
    def on_sampleBtn_clicked(self):
        dlg = PanelDialog(self, self.client, GenericSamplePanel,
                          'Sample information')
        dlg.exec_()

    @pyqtSlot()
    def on_detenvBtn_clicked(self):
        dlg = PanelDialog(self, self.client, DetEnvPanel,
                          'Detectors and environment')
        dlg.exec_()
