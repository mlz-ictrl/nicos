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

"""NICOS GUI panel with most important experiment info."""

from PyQt4.QtGui import QInputDialog
from PyQt4.QtCore import pyqtSignature as qtsig, SIGNAL

from nicos.utils import importString
from nicos.clients.gui.panels import Panel, PanelDialog
from nicos.clients.gui.panels.setup_panel import ExpPanel, SetupsPanel, \
    DetEnvPanel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.widget import NicosWidget


class ExpInfoPanel(Panel):
    panelName = 'Experiment Info'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'expinfo.ui', 'panels')
        for ch in self.findChildren(NicosWidget):
            ch.setClient(self.client)
        self.connect(self.client, SIGNAL('setup'), self.on_client_setup)
        self.connect(self.client, SIGNAL('initstatus'), self.on_client_initstatus)

        self.detLabel.setFormatCallback(lambda value, strvalue: ', '.join(value))
        self.envLabel.setFormatCallback(lambda value, strvalue: ', '.join(value))

        self._sample_panel = None

    def setOptions(self, options):
        self._sample_panel = options.get('sample_panel')

    def hideTitle(self):
        self.titleLbl.setVisible(False)

    def on_client_initstatus(self, initstatus):
        self.setupLabel.setText(', '.join(initstatus['setups'][1]))

    def on_client_setup(self, data):
        self.setupLabel.setText(', '.join(data[1]))

    @qtsig('')
    def on_proposalBtn_clicked(self):
        dlg = PanelDialog(self, self.client, ExpPanel)
        dlg.exec_()

    @qtsig('')
    def on_setupBtn_clicked(self):
        dlg = PanelDialog(self, self.client, SetupsPanel)
        dlg.exec_()

    @qtsig('')
    def on_sampleBtn_clicked(self):
        if self._sample_panel:
            pnlclass = importString(self._sample_panel,
                                    ('nicos.clients.gui.panels.',))
            dlg = PanelDialog(self, self.client, pnlclass)
            dlg.exec_()
            return
        sample, ok = QInputDialog.getText(self, 'New sample',
            'Please enter the sample name.')
        if not ok or not sample:
            return
        sample = unicode(sample)
        self.client.tell('queue', '', 'NewSample(%r)' % sample)

    @qtsig('')
    def on_detenvBtn_clicked(self):
        dlg = PanelDialog(self, self.client, DetEnvPanel)
        dlg.exec_()

    @qtsig('')
    def on_remarkBtn_clicked(self):
        remark, ok = QInputDialog.getText(self, 'New remark',
            'Please enter the remark.  The remark will be added to the logbook '
            'as a heading and will also appear in the data files.')
        if not ok or not remark:
            return
        remark = unicode(remark)
        self.client.tell('queue', '', 'Remark(%r)' % remark)
