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
from nicos.guisupport.qt import QDialogButtonBox, QMessageBox, Qt, \
    pyqtSignal, pyqtSlot


class ExpPanel(DefaultExpPanel):
    """Provides a panel with several input fields for the experiment settings.

    Options:

    * ``new_exp_panel`` -- class name of the panel which should be opened after
      a new experiment has been started.
    """

    panelName = 'Experiment setup'
    ui = '%s/panels/ui_files/setup_exp.ui' % uipath
    exp_proposal_activated = pyqtSignal()

    def __init__(self, parent, client, options):
        DefaultExpPanel.__init__(self, parent, client, options)
        # Setting up warning label so user remembers to press apply button.
        self._defined_emails = self.notifEmails.toPlainText().strip()
        self._defined_data_emails = self.dataEmails.toPlainText().strip()
        self.num_experiment_props_opts = len(self._getProposalInput()) + 1
        self.is_exp_props_edited = [False] * self.num_experiment_props_opts
        self.applyWarningLabel.setStyleSheet('color: red')
        self.applyWarningLabel.setVisible(False)

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
        ExpPanel.on_client_connected(self)
        self.applyWarningLabel.setVisible(False)

    def setViewOnly(self, viewonly):
        self.buttonBox.setEnabled(not viewonly)
        self.queryDBButton.setEnabled(not viewonly)

    def _getProposalInput(self):
        prop = self.proposalNum.text()
        title = self.expTitle.text()
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
        sample = self.sampleName.text()
        notifEmails = self.notifEmails.toPlainText().strip()
        notifEmails = notifEmails.split('\n') if notifEmails else []
        dataEmails = self.dataEmails.toPlainText().strip()
        dataEmails = dataEmails.split('\n') if dataEmails else []
        errorbehavior = 'abort' if self.errorAbortBox.isChecked() else 'report'
        return prop, title, users, local, sample, notifEmails, dataEmails, \
            errorbehavior

    def applyChanges(self):
        done = []

        # proposal settings
        try:
            prop, title, users, local, sample, notifEmails, _, \
                errorbehavior = self._getProposalInput()
        except ConfigurationError:
            return
        notifEmails = [_f for _f in notifEmails if _f]  # remove empty lines

        # check conditions
        if self.client.eval('session.experiment.serviceexp', True) and \
           self.client.eval('session.experiment.proptype', 'user') == 'user' and \
           self.client.eval('session.experiment.proposal', '') != prop:
            self.showError('Can not directly switch experiments, please use '
                           'FinishExperiment first!')
            return

        # do some work
        if prop and prop != self._orig_propinfo.get('proposal'):
            args = {'proposal': prop}
            if local:
                args['localcontact'] = local
            if title:
                args['title'] = title
            if users:
                args['user'] = users
            code = 'NewExperiment(%s)' % ', '.join('%s=%r' % i
                                                   for i in args.items())
            if self.client.run(code, noqueue=False) is None:
                self.showError('Could not start new experiment, a script is '
                               'still running.')
                return
            done.append('New experiment started.')
            if self._new_exp_panel:
                dlg = PanelDialog(self, self.client, self._new_exp_panel,
                                  'New experiment')
                dlg.exec_()
        else:
            if title != self._orig_propinfo.get('title'):
                self.client.run('Exp.update(title=%r)' % title)
                done.append('New experiment title set.')
            if users != self._orig_propinfo.get('users'):
                self.client.run('Exp.update(users=%r)' % users)
                done.append('New users set.')
            if local != self._orig_propinfo.get('localcontacts'):
                self.client.run('Exp.update(localcontacts=%r)' % local)
                done.append('New local contact set.')
        if sample != self._orig_samplename:
            self.client.run('NewSample(%r)' % sample)
            done.append('New sample name set.')
        if notifEmails != self._orig_propinfo.get('notif_emails'):
            self.client.run('SetMailReceivers(%s)' %
                            ', '.join(map(repr, notifEmails)))
            done.append('New mail receivers set.')
        if errorbehavior != self._orig_errorbehavior:
            self.client.run('SetErrorAbort(%s)' % (errorbehavior == 'abort'))
            done.append('New error behavior set.')

        # tell user about everything we did
        if done:
            self.showInfo('\n'.join(done))
        self._update_proposal_info()
        self._defined_emails = self.notifEmails.toPlainText().strip()
        self._defined_data_emails = self.dataEmails.toPlainText().strip()
        self.applyWarningLabel.setVisible(False)
        self.is_exp_props_edited = [False] * self.num_experiment_props_opts
        self.exp_proposal_activated.emit()

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
        curr_val = self._get_proposal_data('proposal')
        self._apply_warning_status(value, 0, curr_val)

    @pyqtSlot(str)
    def on_expTitle_textChanged(self, value):
        curr_val = self._get_proposal_data('title')
        self._apply_warning_status(value, 1, curr_val)

    @pyqtSlot(str)
    def on_users_textChanged(self, value):
        users = self._get_proposal_data('users', [])
        if users:
            curr_val = combineUsers(users)
            self._apply_warning_status(value, 2, curr_val)

    @pyqtSlot(str)
    def on_localContacts_textChanged(self, value):
        self.is_exp_props_edited[3] = value != self._defined_data_emails
        self._set_warning_visibility()

    @pyqtSlot(str)
    def on_sampleName_textChanged(self, value):
        curr_val = self._orig_samplename
        if curr_val is None:
            curr_val = ""
        self._apply_warning_status(value, 4, curr_val)

    @pyqtSlot()
    def on_errorAbortBox_clicked(self):
        value = 'abort' if self.errorAbortBox.isChecked() else 'report'
        self.is_exp_props_edited[5] = value != self._orig_errorbehavior
        self._set_warning_visibility()

    @pyqtSlot()
    def on_notifEmails_textChanged(self):
        value = self.notifEmails.toPlainText().strip()
        self.is_exp_props_edited[6] = value != self._defined_emails
        self._set_warning_visibility()

    @pyqtSlot()
    def on_dataEmails_textChanged(self):
        value = self.dataEmails.toPlainText().strip()
        self.is_exp_props_edited[7] = value != self._defined_data_emails
        self._set_warning_visibility()

    def _get_proposal_data(self, props_key, default=''):
        return self._orig_propinfo.get(props_key, default) or default

    def _apply_warning_status(self, value, index, props_curr_val):
        self.is_exp_props_edited[index] = \
            value != props_curr_val
        self._set_warning_visibility()

    def _set_warning_visibility(self):
        self.applyWarningLabel.setVisible(any(self.is_exp_props_edited))


class SetupsPanel(DefaultSetupsPanel):
    def finishUi(self):
        self.buttonBox.setLayoutDirection(Qt.RightToLeft)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply)
        self.buttonBox.addButton(self._reload_btn, QDialogButtonBox.ResetRole)

    def setViewOnly(self, value):
        for button in self.buttonBox.buttons():
            button.setEnabled(not value)


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

        # Additional dialog panels to pop up after FinishExperiment().
        self._finish_exp_panel = options.get('finish_exp_panel')
        self.finishButton.setEnabled(False)

        client.connected.connect(self.on_client_connected)
        client.disconnected.connect(self.on_client_disconnected)
        client.setup.connect(self.on_client_connected)

    def on_client_connected(self):
        if not self.client.viewonly:
            self.finishButton.setEnabled(True)

    def on_client_disconnected(self):
        self.finishButton.setEnabled(False)

    def setViewOnly(self, value):
        self.finishButton.setEnabled(self.client.isconnected and not value)

    def on_new_experiment_proposal(self):
        if not self.client.viewonly:
            self.finishButton.setEnabled(True)

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
            self.finishButton.setEnabled(False)
            self.show_finish_message()

    def show_finish_message(self):
        msg_box = QMessageBox()
        msg_box.setText('Experiment successfully finished.')
        return msg_box.exec_()
