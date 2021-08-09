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
from nicos.clients.flowui import uipath
from nicos.clients.gui.panels import Panel, PanelDialog
from nicos.clients.gui.panels.setup_panel import ExpPanel as DefaultExpPanel, \
    SetupsPanel as DefaultSetupsPanel, combineUsers, splitUsers
from nicos.clients.gui.utils import loadUi
from nicos.core import ConfigurationError
from nicos.guisupport.qt import QDialogButtonBox, QMessageBox, Qt, pyqtSlot


class ExpPanel(DefaultExpPanel):
    """Provides a panel with several input fields for the experiment settings.

    Options:

    * ``new_exp_panel`` -- class name of the panel which should be opened after
      a new experiment has been started.
    """

    panelName = 'Experiment setup'
    ui = '%s/panels/ui_files/setup_exp.ui' % uipath

    def __init__(self, parent, client, options):
        self._old_settings = {}
        self._new_settings = {}
        DefaultExpPanel.__init__(self, parent, client, options)

    def initUi(self):
        DefaultExpPanel.initUi(self)
        self._text_controls = (self.expTitle, self.users, self.localContacts,
                               self.proposalNum, self.sampleName)
        self.applyWarningLabel.setStyleSheet('color: red')
        self.applyWarningLabel.setVisible(False)
        self.buttonBox.addButton("Discard Changes", QDialogButtonBox.ResetRole)

    def on_client_connected(self):
        # fill proposal
        self._update_proposal_info()
        self.newBox.setVisible(True)
        # check for capability to ask proposal database
        if self.client.eval('session.experiment._canQueryProposals()', None):
            self.propdbInfo.setVisible(True)
            self.queryDBButton.setVisible(True)
        else:
            self.queryDBButton.setVisible(False)
        self.setViewOnly(self.client.viewonly)

    def on_client_disconnected(self):
        for control in self._text_controls:
            control.setText('')
        self.notifEmails.setPlainText('')
        self.dataEmails.setPlainText('')
        DefaultExpPanel.on_client_disconnected(self)

    def setViewOnly(self, viewonly):
        for control in self._text_controls:
            control.setEnabled(not viewonly)
        self.notifEmails.setEnabled(not viewonly)
        self.dataEmails.setEnabled(not viewonly)
        self.errorAbortBox.setEnabled(not viewonly)
        self.queryDBButton.setEnabled(not viewonly)
        if viewonly:
            self._set_buttons_and_warning_behaviour(False)
        else:
            self._check_for_changes()

    def on_buttonBox_clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self.applyChanges()
        elif role == QDialogButtonBox.ResetRole:
            self.discardChanges()

    def discardChanges(self):
        self._update_proposal_info()

    def _getProposalInput(self):
        prop = self.proposalNum.text().strip()
        title = self.expTitle.text().strip()
        try:
            users = splitUsers(self.users.text())
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Invalid email address in '
                                'users list')
            raise ConfigurationError from None
        try:
            local = splitUsers(self.localContacts.text())
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Invalid email address in '
                                'local contacts list')
            raise ConfigurationError from None
        sample = self.sampleName.text().strip()
        notifEmails = self.notifEmails.toPlainText().strip()
        notifEmails = notifEmails.split('\n') if notifEmails else []
        dataEmails = self.dataEmails.toPlainText().strip()
        dataEmails = dataEmails.split('\n') if dataEmails else []
        errorbehavior = 'abort' if self.errorAbortBox.isChecked() else 'report'
        return prop, title, users, local, sample, notifEmails, dataEmails, \
            errorbehavior

    def _update_proposal_info(self):
        DefaultExpPanel._update_proposal_info(self)
        self._update_settings()
        self._check_for_changes()

    def _update_settings(self):
        self._old_settings['notifications'] = \
            self.notifEmails.toPlainText().strip()
        self._old_settings['data_emails'] = \
            self.dataEmails.toPlainText().strip()
        self._old_settings['local_contact'] = self.localContacts.text().strip()
        self._old_settings['sample'] = self.sampleName.text().strip()
        self._old_settings['users'] = self.users.text().strip()
        self._old_settings['abort'] = 'abort' \
            if self.errorAbortBox.isChecked() else 'report'
        self._old_settings['title'] = self.expTitle.text().strip()
        self._old_settings['proposal'] = self.proposalNum.text().strip()
        self._new_settings = self._old_settings.copy()

    @pyqtSlot()
    def on_queryDBButton_clicked(self):
        try:
            prop, title, _, _, _, _, _, _ = self._getProposalInput()
        except ConfigurationError:
            return

        # read all values from propdb
        try:
            queryprop = prop or None
            result = self.client.eval(
                'session.experiment._queryProposals(%r, {})' % queryprop)

            if result:
                if len(result) != 1:
                    result = self.chooseProposal(result)
                    if not result:
                        return
                else:
                    result = result[0]
                    # check for errors/warnings:
                    if result.get('errors'):
                        self.showError('Proposal cannot be performed:\n\n' +
                                       '\n'.join(result['errors']))
                        return
                if result.get('warnings'):
                    self.showError('Proposal might have problems:\n\n' +
                                   '\n'.join(result['warnings']))
                # now transfer it into gui
                self.proposalNum.setText(result.get('proposal', prop))
                self.expTitle.setText(result.get('title', title))
                self.users.setText(
                    combineUsers(result.get('users', [])))
                self.localContacts.setText(
                    combineUsers(result.get('localcontacts', [])))
            else:
                self.showError('Querying proposal management system failed')
        except Exception as e:
            self.log.warning('error in proposal query', exc=1)
            self.showError('Querying proposal management system failed: '
                           + str(e))

    @pyqtSlot(str)
    def on_proposalNum_textChanged(self, value):
        self._new_settings['proposal'] = value.strip()
        self._check_for_changes()

    @pyqtSlot(str)
    def on_expTitle_textChanged(self, value):
        self._new_settings['title'] = value.strip()
        self._check_for_changes()

    @pyqtSlot(str)
    def on_users_textChanged(self, value):
        self._new_settings['users'] = value.strip()
        self._check_for_changes()

    @pyqtSlot(str)
    def on_localContacts_textChanged(self, value):
        self._new_settings['local_contact'] = value.strip()
        self._check_for_changes()

    @pyqtSlot(str)
    def on_sampleName_textChanged(self, value):
        self._new_settings['sample'] = value.strip()
        self._check_for_changes()

    @pyqtSlot()
    def on_errorAbortBox_clicked(self):
        value = 'abort' if self.errorAbortBox.isChecked() else 'report'
        self._new_settings['abort'] = value
        self._check_for_changes()

    @pyqtSlot()
    def on_notifEmails_textChanged(self):
        value = self.notifEmails.toPlainText().strip()
        self._new_settings['notifications'] = value
        self._check_for_changes()

    @pyqtSlot()
    def on_dataEmails_textChanged(self):
        value = self.dataEmails.toPlainText().strip()
        self._new_settings['data_emails'] = value
        self._check_for_changes()

    def _check_for_changes(self):
        changed = self._old_settings != self._new_settings
        self._set_buttons_and_warning_behaviour(changed)

    def _set_buttons_and_warning_behaviour(self, value):
        for button in self.buttonBox.buttons():
            role = self.buttonBox.buttonRole(button)
            button.setEnabled(value)
            if role == QDialogButtonBox.ResetRole:
                button.setVisible(value)
        self.applyWarningLabel.setVisible(value)


class SetupsPanel(DefaultSetupsPanel):
    def finishUi(self):
        self.buttonBox.setLayoutDirection(Qt.RightToLeft)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply)
        self.buttonBox.addButton(self._reload_btn, QDialogButtonBox.ResetRole)

    def setViewOnly(self, viewonly):
        for button in self.buttonBox.buttons():
            button.setEnabled(not viewonly)


class FinishPanel(Panel):
    """Provides a panel to finish the experiment.

    Options:

    * ``finish_exp_panel`` -- class name of the panel which should be opened
      before an experiment is finished.
    """

    panelName = 'Finish experiment'
    ui = '%s/panels/ui_files/finish_exp.ui' % uipath
    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, self.ui)
        self._finish_exp_panel = None

        # Additional dialog panel to pop up after FinishExperiment().
        self._finish_exp_panel = options.get('finish_exp_panel')

        self.finishButton.setEnabled(False)
        client.connected.connect(self.on_client_connected)
        client.disconnected.connect(self.on_client_disconnected)
        client.experiment.connect(self.on_experiment_changed)

    def on_experiment_changed(self, a):
        self._enable_finishing()

    def _enable_finishing(self):
        if not self.client.viewonly and self._is_user_experiment():
            self.finishButton.setEnabled(True)
        else:
            self.finishButton.setEnabled(False)

    def _is_user_experiment(self):
        return self.client.eval('session.experiment.proptype', '') == 'user'

    def on_client_connected(self):
        self._enable_finishing()

    def on_client_disconnected(self):
        self.finishButton.setEnabled(False)

    def setViewOnly(self, viewonly):
        self._enable_finishing()

    @pyqtSlot()
    def on_finishButton_clicked(self):
        if self._finish_exp_panel:
            dlg = PanelDialog(self, self.client, self._finish_exp_panel,
                              'Finish experiment')
            dlg.exec_()
        if self.client.run('FinishExperiment()', noqueue=True) is None:
            self.showError('Could not finish experiment, a script '
                           'is still running.')
        else:
            self.show_finish_message()

    def show_finish_message(self):
        msg_box = QMessageBox()
        msg_box.setText('Experiment successfully finished.')
        return msg_box.exec_()
