#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI experiment setup window."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels import Panel, PanelDialog
from nicos.clients.gui.utils import loadUi
from nicos.core import ConfigurationError
from nicos.core.params import mailaddress
from nicos.guisupport.qt import QDialogButtonBox, QMessageBox, pyqtSlot
from nicos.utils import decodeAny, findResource


class ExpPanel(Panel):
    """Provides a panel with several input fields for the experiment settings.

    Options:

    * ``new_exp_panel`` -- class name of the panel which should be opened after
      a new experiment has been started.
    * ``finish_exp_panel`` -- class name of the panel which should be opened
      before an experiment is finished.
    """

    panelName = 'Experiment setup'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_ess/loki/gui/ui_files/setup_exp.ui'))

        self._orig_proposal = None
        self._new_exp_panel = None
        self._finish_exp_panel = None

        # Setting up warning label so user remembers to press apply button.
        self._defined_emails = self.notifEmails.toPlainText().strip()
        self.num_experiment_props_opts = len(self._getProposalInput())
        self.is_exp_props_edited = [False] * self.num_experiment_props_opts
        self.applyWarningLabel.setStyleSheet('color: red')
        self.applyWarningLabel.setVisible(False)

        # Additional dialog panels to pop up after NewExperiment() and before
        # FinishExperiment() respectively.
        self._new_exp_panel = options.get('new_exp_panel')
        self._finish_exp_panel = options.get('finish_exp_panel')

        self._text_controls = (self.queryDBButton, self.proposalNum,
                               self.expTitle, self.users, self.localContact,)

        # Hide proposal retrieval until available
        self.propdbInfo.setVisible(False)
        self.queryDBButton.setVisible(False)

        if client.isconnected:
            self.on_client_connected()
        else:
            self.on_client_disconnected()

        client.connected.connect(self.on_client_connected)
        client.disconnected.connect(self.on_client_disconnected)
        client.setup.connect(self.on_client_setup)
        client.experiment.connect(self.on_client_experiment)

    def _update_proposal_info(self):
        values = self.client.eval('session.experiment.proposal, '
                                  'session.experiment.title, '
                                  'session.experiment.users, '
                                  'session.experiment.localcontact, '
                                  'session.experiment.errorbehavior', None)
        if values:
            self._orig_proposal_info = values
            self.proposalNum.setText(values[0])
            self.proposalID.setText(decodeAny(values[0]))
            self.expTitle.setText(decodeAny(values[1]))
            self.users.setText(decodeAny(values[2]))
            self.localContact.setText(decodeAny(values[3]))
            self.errorAbortBox.setChecked(values[4] == 'abort')
        receiverinfo = self.client.eval(
            '__import__("nicos").commands.basic._listReceivers('
            '"nicos.devices.notifiers.Mailer")', {})
        emails = []
        for data in receiverinfo.values():
            for (addr, what) in data:
                if what == 'receiver' and addr not in emails:
                    emails.append(addr)
        self._orig_email = emails
        self.notifEmails.setPlainText(decodeAny('\n'.join(self._orig_email)))
        propinfo = self.client.eval('session.experiment.propinfo', {})
        self._orig_datamails = propinfo.get('user_email', '')
        if not isinstance(self._orig_datamails, list):
            self._orig_datamails = self._orig_datamails.splitlines()

    def on_client_connected(self):
        # fill proposal
        self._update_proposal_info()
        # check for new or finish
        if self.client.eval('session.experiment.mustFinish', False):
            self.newBox.setVisible(False)
        else:
            self.newBox.setVisible(True)
        # check for capability to ask proposal database
        if self.client.eval('getattr(session.experiment, "propdb", "")', None):
            self.propdbInfo.setVisible(True)
            self.queryDBButton.setVisible(True)
        else:
            self.queryDBButton.setVisible(False)
            self.propLabel.setText('Enter a proposal number:')
        self.setViewOnly(self.client.viewonly)

    def on_client_disconnected(self):
        for control in self._text_controls:
            control.setText("")
        self.notifEmails.setPlainText("")
        self.proposalNum.setText('')  # do not offer "service"
        self.proposalID.setText('')
        self.setViewOnly(True)
        self.applyWarningLabel.setVisible(False)

    def setViewOnly(self, is_view_only):
        for control in self._text_controls:
            control.setEnabled(not is_view_only)

        self.notifEmails.setEnabled(not is_view_only)
        self.errorAbortBox.setEnabled(not is_view_only)
        self.queryDBButton.setEnabled(not is_view_only)
        self.applyBtn.setEnabled(not is_view_only)

    def on_client_experiment(self, data):
        # just reinitialize
        self.on_client_connected()

    def on_client_setup(self, data):
        # just reinitialize
        self.on_client_connected()

    def _getProposalInput(self):
        prop = self.proposalNum.text()
        title = self.expTitle.text()
        users = self.users.text()
        try:
            local = mailaddress(self.localContact.text())
        except ValueError:
            QMessageBox.critical(self, 'Error', 'The local contact entry is '
                                                'not  a valid email address')
            raise ConfigurationError('')
        emails = self.notifEmails.toPlainText().strip()
        emails = emails.split('\n') if emails else []
        if local and local not in emails:
            emails.append(local)
        errorbehavior = 'abort' if self.errorAbortBox.isChecked() else 'report'
        return prop, title, users, local, emails, errorbehavior

    @pyqtSlot()
    def on_queryDBButton_clicked(self):
        try:
            prop, title, users, _, emails, _ = self._getProposalInput()
        except ConfigurationError:
            return

        # read all values from propdb
        try:
            result = self.client.eval(
                'session.experiment._fillProposal(%s, {})' % prop, None)

            if result:
                if result['wrong_instrument']:
                    self.showError('Proposal is not for this instrument, '
                                   'please check the proposal number!')
                # now transfer it into gui
                # XXX check: is the result bytes or str on Python 3?
                self.expTitle.setText(decodeAny(result.get('title', title)))
                self.users.setText(decodeAny(result.get('user', users)))
                # XXX: local contact must be email, but proposal db returns
                # only a name
                # self.localContact.setText(decodeAny(result.get('localcontact',
                #                                                local)))
                self.notifEmails.setPlainText(
                    decodeAny(result.get('user_email', emails)))
                # check permissions:
                failed = []
                yes = 'yes'
                no = 'no'
                if result.get('permission_security', no) != yes:
                    failed.append('* Security (Tel. 12699)')
                if result.get('permission_radiation_protection', no) != yes:
                    failed.append('* Radiation protection (Tel. 14955)')
                if failed and not result['wrong_instrument']:
                    self.showError('Proposal lacks sufficient permissions '
                                   'to be performed!\n\n' + '\n'.join(failed))
            else:
                self.showInfo('Reading proposaldb failed for an unknown '
                              'reason. Please check logfiles for hints.')
        except Exception as e:
            self.log.warning(e, exc=1)
            self.showInfo('Reading proposaldb failed for an unknown reason. '
                          'Please check logfiles....\n' + repr(e))

    @pyqtSlot()
    def on_applyBtn_clicked(self):
        done = []

        # proposal settings
        try:
            prop, title, users, local, email, errorbehavior = \
                self._getProposalInput()
        except ConfigurationError:
            return
        email = [_f for _f in email if _f]  # remove empty lines

        # check conditions
        if self.client.eval('session.experiment.serviceexp', True) and \
                self.client.eval('session.experiment.proptype',
                                 'user') == 'user' and \
                self.client.eval('session.experiment.proposal', '') != prop:
            self.showError('Can not directly switch experiments, please use '
                           'FinishExperiment first!')
            return

        script_running = self.mainwindow.current_status != 'idle'

        # do some work
        if prop and prop != self._orig_proposal_info[0]:
            args = {'proposal': prop}
            if local:
                args['localcontact'] = local
            if title:
                args['title'] = title
            if users:
                args['user'] = users
            code = 'NewExperiment(%s)' % ', '.join('%s=%r' % i
                                                   for i in args.items())
            if self.client.run(code, noqueue=True) is None:
                self.showError('Could not start new experiment, a script is '
                               'still running.')
                return
            done.append('New experiment started.')
            if self._new_exp_panel:
                dlg = PanelDialog(self, self.client, self._new_exp_panel,
                                  'New experiment')
                dlg.exec_()
        else:
            if title != self._orig_proposal_info[1]:
                self.client.run('Exp.title = %r' % title)
                done.append('New experiment title set.')
            if users != self._orig_proposal_info[2]:
                self.client.run('Exp.users = %r' % users)
                done.append('New users set.')
            if local != self._orig_proposal_info[3]:
                self.client.run('Exp.localcontact = %r' % local)
                done.append('New local contact set.')
        if email != self._orig_email:
            self.client.run('SetMailReceivers(%s)' %
                            ', '.join(map(repr, email)))
            done.append('New mail receivers set.')
        if errorbehavior != self._orig_proposal_info[4]:
            self.client.run('SetErrorAbort(%s)' % (errorbehavior == 'abort'))
            done.append('New error behavior set.')

        # tell user about everything we did
        if done:
            if script_running:
                done.append('')
                done.append('The changes have been queued since a script '
                            'is currently running.')
            self.showInfo('\n'.join(done))
        self._update_proposal_info()
        self._defined_emails = self.notifEmails.toPlainText().strip()
        self.is_exp_props_edited = [False] * self.num_experiment_props_opts
        self.applyWarningLabel.setVisible(False)

    @pyqtSlot(str)
    def on_proposalNum_textChanged(self, value):
        self._apply_warning_status(value, 0)

    @pyqtSlot(str)
    def on_expTitle_textChanged(self, value):
        self._apply_warning_status(value, 1)

    @pyqtSlot(str)
    def on_users_textChanged(self, value):
        self._apply_warning_status(value, 2)

    @pyqtSlot(str)
    def on_localContact_textChanged(self, value):
        self._apply_warning_status(value, 3)

    @pyqtSlot()
    def on_errorAbortBox_clicked(self):
        value = 'abort' if self.errorAbortBox.isChecked() else 'report'
        self._apply_warning_status(value, 4)

    @pyqtSlot()
    def on_notifEmails_textChanged(self):
        value = self.notifEmails.toPlainText().strip()
        self.is_exp_props_edited[5] = value != self._defined_emails
        self._set_warning_visibility()

    def _apply_warning_status(self, value, index):
        self.is_exp_props_edited[index] = \
            value != decodeAny(self._orig_proposal_info[index])
        self._set_warning_visibility()

    def _set_warning_visibility(self):
        self.applyWarningLabel. \
            setVisible(any(self.is_exp_props_edited))
