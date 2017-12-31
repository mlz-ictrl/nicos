#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

from nicos.guisupport.qt import pyqtSlot, QTimer, QDialog, QMessageBox, \
    QPushButton

from nicos.clients.gui.panels import Panel, PanelDialog
from nicos.clients.gui.panels.setup_panel import ExpPanel, SetupsPanel, \
    DetEnvPanel, GenericSamplePanel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.widget import NicosWidget
from nicos.core.utils import ADMIN


class ExpInfoPanel(Panel):
    """Provides a panel with several labels displaying basic experiment info.

    This is for example the experiment title, sample name, and user name.

    It also provides several buttons with which the user can change proposal
    info, sample properties, scan environment and setups.

    Options:

    * ``sample_panel`` -- what to show when the user clicks on the "Sample"
      button.  The value must be a panel configuration, e.g. ``panel('...')``
      or ``tabbed(...)``.

      There are several panels that are useful for this:

      - ``nicos.clients.gui.panels.setup_panel.GenericSamplePanel`` -- a panel
        that only shows a single input box for the sample name.
      - ``nicos.clients.gui.panels.setup_panel.TasSamplePanel`` -- a panel that
        also shows input boxes for triple-axis sample properties (such as
        lattice constants).

    * ``popup_proposal_after`` -- if given, the proposal dialog will be opened
      when the daemon has been idle for more than the specified time interval
      (in hours).
    """

    panelName = 'Experiment Info'
    _viewonly = False

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'expinfo.ui', 'panels')
        for ch in self.findChildren(NicosWidget):
            ch.setClient(client)
        client.setup.connect(self.on_client_setup)
        client.initstatus.connect(self.on_client_initstatus)

        self.detLabel.setFormatCallback(
            lambda value, strvalue: ', '.join(sorted(value)))
        self.envLabel.setFormatCallback(
            lambda value, strvalue: ', '.join(sorted(value)))

        self._sample_panel = None

    def setOptions(self, options):
        Panel.setOptions(self, options)
        self._sample_panel = options.get('sample_panel', GenericSamplePanel)
        self._timeout = options.get('popup_proposal_after', 0)
        if self._timeout:
            self._proposal_popup_timer = QTimer(interval=self._timeout * 3600000)
            self._proposal_popup_timer.setSingleShot(True)
            self._proposal_popup_timer.timeout.connect(
                self.on_proposal_popup_timer_timeout)
        else:
            self._proposal_popup_timer = None

    def hideTitle(self):
        self.titleLbl.setVisible(False)

    def setViewOnly(self, viewonly):
        self._viewonly = viewonly
        if not self._viewonly and self._timeout:
            # ask explicitly for status to restart timer if necessary
            self.client.ask('getstatus')

    def on_client_initstatus(self, initstatus):
        self.setupLabel.setText(', '.join(sorted(initstatus['setups'][1])))

    def on_client_setup(self, data):
        self.setupLabel.setText(', '.join(sorted(data[1])))

    def updateStatus(self, status, exception=False):
        if self._proposal_popup_timer:
            if status == 'idle':
                if not self._viewonly or \
                    (self.client.user_level is not None and
                     self.client.user_level < ADMIN):
                    self._proposal_popup_timer.start()
            else:
                self._proposal_popup_timer.stop()

    def on_proposal_popup_timer_timeout(self):
        if self._viewonly:
            return
        dlg = QMessageBox(self)
        dlg.setText('The experiment has been idle for more than %.1f hours.' %
                    self._timeout)
        contButton = QPushButton('Continue current experiment')
        finishAndNewButton = QPushButton('Finish and start new experiment')
        dlg.addButton(contButton, QMessageBox.RejectRole)
        dlg.addButton(finishAndNewButton, QMessageBox.ActionRole)
        dlg.exec_()
        if dlg.clickedButton() == finishAndNewButton:
            self.on_proposalBtn_clicked()
        elif dlg.clickedButton() == contButton:
            self._proposal_popup_timer.start()

    @pyqtSlot()
    def on_proposalBtn_clicked(self):
        dlg = PanelDialog(self, self.client, ExpPanel, 'Proposal info')
        dlg.exec_()

    @pyqtSlot()
    def on_setupBtn_clicked(self):
        dlg = PanelDialog(self, self.client, SetupsPanel, 'Setups')
        dlg.exec_()

    @pyqtSlot()
    def on_sampleBtn_clicked(self):
        dlg = PanelDialog(self, self.client, self._sample_panel,
                          'Sample information')
        dlg.exec_()

    @pyqtSlot()
    def on_detenvBtn_clicked(self):
        dlg = PanelDialog(self, self.client, DetEnvPanel,
                          'Detectors and environment')
        dlg.exec_()

    @pyqtSlot()
    def on_remarkBtn_clicked(self):
        dlg = QDialog(self)
        loadUi(dlg, 'expinfo_remark.ui', 'panels')

        def callback():
            self.showInfo('The remark will be added to the logbook as a '
                          'heading and will also appear in the data files.')
        dlg.buttonBox.helpRequested.connect(callback)

        for ch in dlg.findChildren(NicosWidget):
            ch.setClient(self.client)
        dlg.remarkEdit.setFocus()
        if not dlg.exec_():
            return
        self.client.run('Remark(%r)' % dlg.remarkEdit.getValue())
