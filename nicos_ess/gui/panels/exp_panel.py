#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Ebad Kamil <Ebad.Kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#   Kenan Muric <kenan.muric@ess.eu>
#   AÜC Hardal <umit.hardal@ess.eu>
#
# *****************************************************************************
"""NICOS GUI experiment setup window."""
from copy import deepcopy

from nicos.clients.gui.panels.setup_panel import ProposalDelegate, combineUsers
from nicos.clients.gui.utils import dialogFromUi, loadUi
from nicos.core import ADMIN
from nicos.guisupport.qt import QDialogButtonBox, QHeaderView, QIntValidator, \
    QListWidgetItem, Qt, pyqtSlot
from nicos.guisupport.tablemodel import TableModel
from nicos.utils import decodeAny, findResource

from nicos_ess.gui.panels.panel import PanelBase


class ProposalSettings:

    def __init__(self,
                 proposal_id='',
                 title='',
                 users=None,
                 local_contacts=None,
                 abort_on_error='',
                 notifications=None,
                 samples=None):
        self.proposal_id = proposal_id
        self.title = title
        self.users = users if users else []
        self.local_contacts = local_contacts if local_contacts else [{}]
        self.samples = samples if samples else []
        self.notifications = notifications if notifications else []
        self.abort_on_error = abort_on_error

    def __eq__(self, other):
        if self.proposal_id != other.proposal_id \
                or self.title != other.title \
                or self.users != other.users \
                or self.local_contacts != other.local_contacts \
                or self.notifications != other.notifications \
                or self.abort_on_error != other.abort_on_error\
                or self.samples != other.samples:
            return False
        return True


class ExpPanel(PanelBase):
    """Provides a panel with several input fields for the experiment settings.
    """

    panelName = 'Experiment setup'

    def __init__(self, parent, client, options):
        PanelBase.__init__(self, parent, client, options)
        loadUi(self,
               findResource('nicos_ess/gui/panels/ui_files/exp_panel.ui'))

        self.old_settings = ProposalSettings()
        self.new_settings = ProposalSettings()

        self._user_fields = ['name', 'email', 'affiliation']
        self.to_monitor = ['sample/samples', 'exp/propinfo']
        self.users_model = TableModel(self._user_fields)
        self.users_model.data_updated.connect(self._check_for_changes)
        self.userTable.setModel(self.users_model)
        self.userTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive)

        self.contacts_model = TableModel(['name', 'email', 'affiliation'])
        self.contacts_model.insert_row(0)
        self.contacts_model.data_updated.connect(self._check_for_changes)
        self.contactsTable.setModel(self.contacts_model)
        self.contactsTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.samples_model = TableModel(
            ['name', 'formula', 'number of', 'mass/volume', 'density'],
            mappings={
                'number of': 'number_of',
                'mass/volume': 'mass_volume'
            },
            transposed=True)
        self.samples_model.data_updated.connect(self._check_for_changes)
        self.sampleTable.setModel(self.samples_model)
        self.sampleTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive)

        self.proposalNum.setValidator(QIntValidator(0, 999999999))

        self._text_controls = (self.propTitle, self.proposalNum)
        self._tables = (self.sampleTable, self.contactsTable, self.userTable)

        self.hide_samples = options.get('hide_sample', False)
        if self.hide_samples:
            self._hide_sample_info()
        self._setup_button_box_and_warn_label()
        self.initialise_connection_status_listeners()

    def _setup_button_box_and_warn_label(self):
        self.buttonBox.setLayoutDirection(Qt.RightToLeft)
        self.buttonBox.addButton('Discard Changes', QDialogButtonBox.ResetRole)

        self.applyWarningLabel.setStyleSheet('color: red')
        self.applyWarningLabel.setVisible(False)

    def on_buttonBox_clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self.applyChanges()
        elif role == QDialogButtonBox.ResetRole:
            self.discardChanges()

    def _set_buttons_and_warning_behaviour(self, value):
        for button in self.buttonBox.buttons():
            role = self.buttonBox.buttonRole(button)
            button.setEnabled(value)
            if role == QDialogButtonBox.ResetRole:
                button.setVisible(value)
        self.applyWarningLabel.setVisible(value)

    def _hide_sample_info(self):
        self.sampleTable.hide()
        self.sampleLabel.hide()
        self.sampleLine.hide()
        self.addSampleButton.hide()
        self.deleteSampleButton.hide()

    def initialise_connection_status_listeners(self):
        PanelBase.initialise_connection_status_listeners(self)
        self.client.experiment.connect(self.on_experiment_finished)
        self.client.setup.connect(self.on_client_setup)
        for monitor in self.to_monitor:
            self.client.register(self, monitor)

    def on_keyChange(self, key, value, time, expired):
        if key in self.to_monitor:
            self._update_proposal_info()

    def _update_proposal_info(self):
        values = self.client.eval(
            'session.experiment.proposal, '
            'session.experiment.title, '
            'session.experiment.users, '
            'session.experiment.localcontact, '
            'session.experiment.errorbehavior', None)
        notif_emails = self.client.eval(
            'session.experiment.propinfo["notif_emails"]', [])

        samples = self.client.eval('session.experiment.get_samples()', {})

        if values:
            users = [dict(user) for user in values[2]]
            contacts = [dict(contact) for contact in values[3]]
            self.old_settings = \
                ProposalSettings(decodeAny(values[0]), decodeAny(values[1]),
                                 users, contacts, values[4] == 'abort',
                                 notif_emails, samples)
            self.new_settings = deepcopy(self.old_settings)
            self._update_panel()

    def _update_panel(self):
        self.proposalNum.setText(self.old_settings.proposal_id)
        self.propTitle.setText(self.old_settings.title)
        self.errorAbortBox.setChecked(self.old_settings.abort_on_error)
        self.notifEmails.setPlainText('\n'.join(
            self.old_settings.notifications))
        self._update_samples_model(self.old_settings.samples)
        self._update_users_model(self.old_settings.users)
        self._update_contacts_model(self.old_settings.local_contacts)
        self._format_sample_table()
        self._format_user_table()

    def _format_sample_table(self):
        self._format_table(self.sampleTable, self.samples_model)

    def _format_user_table(self):
        self._format_table(self.userTable, self.users_model)

    def _format_table(self, table, model):
        width = table.width() - table.verticalHeader().width()
        num_cols = model.columnCount(0)
        for i in range(num_cols):
            table.setColumnWidth(i, width // num_cols)

    def on_client_connected(self):
        PanelBase.on_client_connected(self)
        self._update_proposal_info()
        self._is_proposal_system_available()

    def _is_proposal_system_available(self):
        available = self.client.eval('session.experiment._canQueryProposals()',
                                     False)
        self.queryDBButton.setEnabled(available)
        self.proposalNum.setReadOnly(available)
        self.propTitle.setReadOnly(available)
        self.userTable.setEnabled(not available)
        self.addUserButton.setVisible(not available)
        self.deleteUserButton.setVisible(not available)

    def on_client_disconnected(self):
        for control in self._text_controls:
            control.setText('')
        self._update_samples_model([])
        self._update_users_model([])
        self._update_contacts_model([])
        self.notifEmails.setPlainText('')
        self.old_settings = ProposalSettings()
        self.new_settings = ProposalSettings()
        PanelBase.on_client_disconnected(self)

    def on_client_setup(self, data):
        if 'system' in data[0]:
            self._is_proposal_system_available()
            self._update_proposal_info()

    def setViewOnly(self, viewonly):
        for control in self._text_controls:
            control.setEnabled(not viewonly)
        for table in self._tables:
            table.setEnabled(not viewonly)
        self.notifEmails.setEnabled(not viewonly)
        self.errorAbortBox.setEnabled(not viewonly)
        self.queryDBButton.setEnabled(not viewonly)
        self.addUserButton.setEnabled(not viewonly)
        self.queryDBButton.setEnabled(not viewonly)
        self.deleteUserButton.setEnabled(not viewonly)
        self.addSampleButton.setEnabled(not viewonly)
        self.deleteSampleButton.setEnabled(not viewonly)
        if viewonly:
            self._set_buttons_and_warning_behaviour(False)
        else:
            self._check_for_changes()
            self._is_proposal_system_available()

    def applyChanges(self):
        self.queryDBButton.setFocus(True)
        if self.mainwindow.current_status != 'idle':
            self.showInfo('Cannot change settings while a script is running!')
            return
        try:
            self._set_experiment()
            self._set_samples()
            self._set_notification_receivers()
            self._set_abort_on_error()
            self._update_proposal_info()
        except Exception as error:
            self.showError(str(error))

    def _set_experiment(self):
        local_contacts = [
            contact for contact in self.contacts_model.raw_data
            if contact.get('name', None)
        ]

        users = [
            user for user in self.users_model.raw_data
            if any((user.get(field) for field in self._user_fields))
        ]

        exp_args = {
            'title': self.new_settings.title,
            'localcontacts': local_contacts,
            'users': users
        }

        if self.new_settings.proposal_id != self.old_settings.proposal_id:
            exp_args['proposal'] = self.new_settings.proposal_id
            command = 'Exp.new(%s)'
        else:
            command = 'Exp.update(%s)'
        code = command % ', '.join('%s=%r' % i for i in exp_args.items())
        self.client.eval(code)

    def _set_samples(self):
        if self.hide_samples or \
                self.samples_model.raw_data == self.old_settings.samples:
            return

        samples = {}
        for index, sample in enumerate(self.samples_model.raw_data):
            if not sample.get('name', ''):
                sample['name'] = f'sample {index + 1}'
            samples[index] = sample
        self.client.run(f'Exp.sample.set_samples({dict(samples)})')

    def _set_abort_on_error(self):
        abort_on_error = self.new_settings.abort_on_error
        if abort_on_error != self.old_settings.abort_on_error:
            self.client.run('SetErrorAbort(%s)' % abort_on_error)

    def _set_notification_receivers(self):
        notifications = self.new_settings.notifications
        if notifications != self.old_settings.notifications:
            self.client.run('SetMailReceivers(%s)' %
                            ', '.join(map(repr, notifications)))

    @pyqtSlot()
    def on_addUserButton_clicked(self):
        self.users_model.insert_row(self.users_model.num_entries)

    @pyqtSlot()
    def on_deleteUserButton_clicked(self):
        to_remove = {
            index.row()
            for index in self.userTable.selectedIndexes()
            if index.isValid() and index.row() < self.users_model.num_entries
        }
        self.users_model.remove_rows(to_remove)

    @pyqtSlot()
    def on_queryDBButton_clicked(self):
        try:
            kwds = {
                'fed_id': self.parentwindow.client.login,
                'admin': self.parentwindow.client.user_level == ADMIN,
            }
            result = self.client.eval(
                f'session.experiment._queryProposals(kwds={kwds})')

            if result:
                if len(result) > 1:
                    result = self.choose_proposal(result)
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
                self.proposalNum.setText(result.get('proposal', ''))
                self.propTitle.setText(result.get('title', ''))
                self._update_users_model(result.get('users', []))
                self._update_contacts_model(result.get('localcontacts', []))
                self._update_samples_model(result['samples'])
                self._format_user_table()
                self._format_sample_table()
            else:
                self.showError('No proposals found')
        except Exception as e:
            self.log.warning('error in proposal query', exc=1)
            self.showError(f'Querying proposal management system failed: {e}')

    def _update_users_model(self, users):
        self.users_model.raw_data = deepcopy(users)

    def _update_contacts_model(self, contacts):
        self.contacts_model.raw_data = deepcopy(contacts or [{}])

    def choose_proposal(self, proposals):
        dlg = dialogFromUi(self, 'panels/setup_exp_proposal.ui')
        dlg.list.setItemDelegate(ProposalDelegate(dlg))
        for prop in proposals:
            prop_copy = deepcopy(prop)
            prop_copy['users'] = [{'name': combineUsers(prop['users'])}]
            item = QListWidgetItem('', dlg.list)
            item.setData(Qt.UserRole, prop_copy)
        if not dlg.exec():
            return
        sel = dlg.list.currentRow()
        return proposals[sel]

    def _update_samples_model(self, samples):
        if not self.hide_samples:
            self.samples_model.raw_data = deepcopy(samples)

    @pyqtSlot(str)
    def on_proposalNum_textChanged(self, value):
        self.new_settings.proposal_id = value.strip()
        self._check_for_changes()

    @pyqtSlot(str)
    def on_propTitle_textChanged(self, value):
        self.new_settings.title = value.strip()
        self._check_for_changes()

    @pyqtSlot()
    def on_errorAbortBox_clicked(self):
        self.new_settings.abort_on_error = self.errorAbortBox.isChecked()
        self._check_for_changes()

    @pyqtSlot()
    def on_notifEmails_textChanged(self):
        self.new_settings.notifications = \
            self.notifEmails.toPlainText().strip().splitlines()
        self._check_for_changes()

    def _check_for_changes(self):
        has_changed = self.new_settings != self.old_settings
        has_changed |= self.users_model.raw_data != self.old_settings.users
        has_changed |= self.contacts_model.raw_data != \
                       self.old_settings.local_contacts
        if not self.hide_samples:
            has_changed |= \
                self.samples_model.raw_data != self.old_settings.samples
        self._set_buttons_and_warning_behaviour(has_changed)

    def discardChanges(self):
        self._update_proposal_info()
        self._check_for_changes()

    def on_experiment_finished(self):
        self._update_proposal_info()
        self._check_for_changes()

    @pyqtSlot()
    def on_addSampleButton_clicked(self):
        self.samples_model.insert_row(self.samples_model.num_entries)
        self._format_sample_table()

    @pyqtSlot()
    def on_deleteSampleButton_clicked(self):
        to_remove = {
            index.column()
            for index in self.sampleTable.selectedIndexes() if index.isValid()
            and index.column() < self.samples_model.num_entries
        }
        self.samples_model.remove_rows(to_remove)
        self._format_sample_table()
