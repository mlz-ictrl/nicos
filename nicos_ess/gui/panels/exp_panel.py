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
#   Ebad Kamil <Ebad.Kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#   Kenan Muric <kenan.muric@ess.eu>
#   AÜC Hardal <umit.hardal@ess.eu>
#
# *****************************************************************************

"""NICOS GUI experiment setup window."""
from copy import deepcopy

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.panels.setup_panel import ProposalDelegate, \
    combineUsers, splitUsers
from nicos.clients.gui.utils import dialogFromUi, loadUi
from nicos.core import ConfigurationError
from nicos.guisupport.qt import QAbstractTableModel, QDialogButtonBox, \
    QHeaderView, QListWidgetItem, QMessageBox, Qt, pyqtSignal, pyqtSlot
from nicos.utils import decodeAny, findResource


class TableModel(QAbstractTableModel):
    data_updated = pyqtSignal()

    def __init__(self, headings, mappings=None, transposed=False):
        """ Constructor.

        :param headings: the column headings.
        :param mappings: maps the keys in the underlying data to the headings.
        :param transposed: whether to display the data rotated (headings on the
                           left side).
        """
        super().__init__()
        self._transposed = transposed
        self._headings = headings
        self._mappings = mappings if mappings else {}
        # raw_data is the underlying NICOS data
        self._raw_data = []
        self._table_data = []

    @property
    def raw_data(self):
        """
        :return: list of dictionaries containing the underlying data.
        """
        return self._raw_data

    @raw_data.setter
    def raw_data(self, data):
        """
        Sets the underlying data for the table.

        If the keys in the data don't match the fields then they are ignored.

        :param data: list of dictionaries containing the data.
        """
        self._raw_data = data

        new_table = self._empty_table(len(self._headings),
                                      len(self._raw_data))

        for i, item in enumerate(self._raw_data):
            for j, heading in enumerate(self._headings):
                key = self._mappings.get(heading, heading)
                new_table[i][j] = item.get(key, '')

        self._table_data = new_table
        self.layoutChanged.emit()
        self.data_updated.emit()

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            row, column = self._get_row_and_column(index)
            return self._table_data[row][column]

    def setData(self, index, value, role):
        if role != Qt.EditRole:
            return False

        row, column = self._get_row_and_column(index)

        self._table_data[row][column] = value
        col_name = self._headings[column]
        self._raw_data[row][self._mappings.get(col_name, col_name)] = value
        self.data_updated.emit()
        return True

    def _get_row_and_column(self, index):
        if self._transposed:
            return index.column(), index.row()
        return index.row(), index.column()

    def columnCount(self, index):
        return len(self._raw_data) if self._transposed else len(self._headings)

    def rowCount(self, index):
        return len(self._headings) if self._transposed else len(self._raw_data)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return section + 1 if self._transposed else self._headings[section]
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return self._headings[section] if self._transposed else section + 1

    def _empty_table(self, columns, rows):
        return [[''] * columns for _ in range(rows)]


class ProposalSettings:
    def __init__(self, proposal_id='', title='', users=None, local_contacts='',
                 abort_on_error='', notifications=None, samples=None):
        self.proposal_id = proposal_id
        self.title = title
        self.users = users if users else []
        self.local_contacts = local_contacts
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


class ExpPanel(Panel):
    """Provides a panel with several input fields for the experiment settings.
    """

    panelName = 'Experiment setup'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_ess/gui/panels/ui_files/exp_panel.ui'))

        self.old_proposal_settings = ProposalSettings()
        self.new_proposal_settings = deepcopy(self.old_proposal_settings)

        self.users_model = TableModel(['name', 'email', 'affiliation'])
        self.users_model.data_updated.connect(self.on_users_changed)
        self.userTable.setModel(self.users_model)
        self.userTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive)

        self.samples_model = TableModel(['name', 'formula', 'number of',
                                         'mass/volume', 'density'],
                                        mappings={'number of': 'number_of',
                                                  'mass/volume': 'mass_volume'},
                                        transposed=True)
        self.samples_model.data_updated.connect(self.on_samples_changed)
        self.sampleTable.setModel(self.samples_model)
        self.sampleTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive)

        self._text_controls = (self.expTitle, self.localContacts,
                               self.proposalNum, self.proposalQuery)

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

    def initialise_connection_status_listeners(self):
        if self.client.isconnected:
            self.on_client_connected()
        else:
            self.on_client_disconnected()
        self.client.connected.connect(self.on_client_connected)
        self.client.disconnected.connect(self.on_client_disconnected)
        self.client.experiment.connect(self.on_experiment_finished)
        self.client.register(self, 'Exp/title')
        self.client.register(self, 'Exp/users')
        self.client.register(self, 'Exp/localcontact')
        self.client.register(self, 'Exp/propinfo')
        self.client.register(self, 'Sample/samples')

    def on_keyChange(self, key, value, time, expired):
        # Value of any registered key changes,
        # update the proposal panel of all clients.
        self._update_proposal_info()

    def _update_proposal_info(self):
        values = self.client.eval('session.experiment.proposal, '
                                  'session.experiment.title, '
                                  'session.experiment.users, '
                                  'session.experiment.localcontact, '
                                  'session.experiment.errorbehavior', None)
        notif_emails = self.client.eval(
            'session.experiment.propinfo["notif_emails"]', [])

        samples = self.client.eval('session.experiment.get_samples()', {})

        if values:
            users = [dict(user) for user in values[2]]
            self.old_proposal_settings = \
                ProposalSettings(decodeAny(values[0]), decodeAny(values[1]),
                                 users, decodeAny(values[3]),
                                 values[4] == 'abort', notif_emails, samples)
            self.new_proposal_settings = deepcopy(self.old_proposal_settings)
            self._update_panel()

    def _update_panel(self):
        self.proposalNum.setText(self.old_proposal_settings.proposal_id)
        self.expTitle.setText(self.old_proposal_settings.title)
        self.localContacts.setText(
            self.old_proposal_settings.local_contacts)
        self.errorAbortBox.setChecked(
            self.old_proposal_settings.abort_on_error)
        self.notifEmails.setPlainText(
            '\n'.join(self.old_proposal_settings.notifications))
        self._update_samples_model(self.old_proposal_settings.samples)
        self._update_users_model(self.old_proposal_settings.users)
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
            table.setColumnWidth(i, width / num_cols)

    def on_client_connected(self):
        self._update_proposal_info()
        self._is_proposal_system_available()
        self.setViewOnly(self.client.viewonly)

    def _is_proposal_system_available(self):
        if self.client.eval('session.experiment._canQueryProposals()', None):
            self.findProposalBox.setVisible(True)
            self.proposalNum.setReadOnly(True)
        else:
            self.findProposalBox.setVisible(False)
            self.proposalNum.setReadOnly(False)

    def on_client_disconnected(self):
        for control in self._text_controls:
            control.setText('')
        self._update_samples_model([])
        self._update_users_model([])
        self.notifEmails.setPlainText('')
        self.setViewOnly(True)

    def setViewOnly(self, viewonly):
        for control in self._text_controls:
            control.setEnabled(not viewonly)
        self.notifEmails.setEnabled(not viewonly)
        self.errorAbortBox.setEnabled(not viewonly)
        self.queryDBButton.setEnabled(not viewonly)
        self.sampleTable.setEnabled(not viewonly)
        self.userTable.setEnabled(not viewonly)
        self.addUserButton.setEnabled(not viewonly)
        self.deleteUserButton.setEnabled(not viewonly)
        if viewonly:
            self._set_buttons_and_warning_behaviour(False)
        else:
            self._check_for_changes()

    def _format_local_contacts(self, local_contacts):
        if local_contacts:
            try:
                return splitUsers(local_contacts)
            except ValueError:
                QMessageBox.warning(self, 'Error', 'Invalid email address in '
                                    'local contacts list')
                raise ConfigurationError from None
        return []

    def applyChanges(self):
        if self.mainwindow.current_status != 'idle':
            self.showInfo('Cannot change settings while a script is running!')
            return

        changes = []

        proposal_id = self.new_proposal_settings.proposal_id
        local_contacts = self._format_local_contacts(
            self.new_proposal_settings.local_contacts)

        # do some work
        if proposal_id != self.old_proposal_settings.proposal_id:
            self.client.run('FinishExperiment()', noqueue=True)
            args = {'proposal': proposal_id,
                    'title': self.new_proposal_settings.title,
                    'localcontact': local_contacts}
            code = 'NewExperiment(%s)' % ', '.join('%s=%r' % i
                                                   for i in args.items())
            if self.client.run(code, noqueue=False) is None:
                self.showError('Could not start new experiment, a script is '
                               'still running.')
                return
            changes.append('New experiment started.')
        else:
            self._set_title(changes)
            self._set_local_contacts(local_contacts, changes)
        self._set_users(changes)
        self._set_samples(changes)
        self._set_notification_receivers(changes)
        self._set_abort_on_error(changes)

        # tell user about everything we did
        if changes:
            self.showInfo('\n'.join(changes))
        self._update_proposal_info()

    def _set_samples(self, changes):
        if self.hide_samples:
            return

        if self.samples_model.raw_data != self.old_proposal_settings.samples:
            for index, sample in enumerate(self.samples_model.raw_data):
                set_sample_cmd = self._create_set_sample_command(index, sample)
                self.client.run(set_sample_cmd)
            changes.append('Samples updated.')

    def _create_set_sample_command(self, index, sample):
        name = sample.get('name', '')
        name = name if name else f'sample {index + 1}'
        return f'SetSample({index}, \'{name}\', ' \
               f'formula=\'{sample["formula"]}\', ' \
               f'number_of={sample["number_of"]}, ' \
               f'mass_volume=\'{sample["mass_volume"]}\', ' \
               f'density=\'{sample["density"]}\')'

    def _set_title(self, changes):
        if self.new_proposal_settings.title != self.old_proposal_settings.title:
            self.client.run('Exp.update(title=%r)' %
                            self.new_proposal_settings.title)
            changes.append('New experiment title set.')

    def _set_users(self, changes):
        if self.users_model.raw_data != self.old_proposal_settings.users:
            users = [user for user in self.users_model.raw_data
                     if any(user.values())]
            self.client.run('Exp.update(users=%r)' % users)
            changes.append('New users set.')

    def _set_local_contacts(self, local_contacts, changes):
        if self.new_proposal_settings.local_contacts != \
                    self.old_proposal_settings.local_contacts:
            self.client.run('Exp.update(localcontacts=%r)' % local_contacts)
            changes.append('New local contact(s) set.')

    def _set_abort_on_error(self, changes):
        abort_on_error = self.new_proposal_settings.abort_on_error
        if abort_on_error != self.old_proposal_settings.abort_on_error:
            self.client.run('SetErrorAbort(%s)' % abort_on_error)
            changes.append('New error behavior set.')

    def _set_notification_receivers(self, changes):
        notifications = self.new_proposal_settings.notifications
        if notifications != self.old_proposal_settings.notifications:
            self.client.run('SetMailReceivers(%s)' %
                            ', '.join(map(repr, notifications)))
            changes.append('New mail receivers set.')

    @pyqtSlot()
    def on_addUserButton_clicked(self):
        users = self.users_model.raw_data
        users.append({})
        self.users_model.raw_data = users

    @pyqtSlot()
    def on_deleteUserButton_clicked(self):
        users = self.users_model.raw_data
        rows = set(index.row() for index in self.userTable.selectedIndexes())
        for row in sorted(rows, reverse=True):
            users.pop(row)
        self.users_model.raw_data = users

    @pyqtSlot()
    def on_queryDBButton_clicked(self):
        try:
            proposal = self.proposalQuery.text()
            result = self.client.eval(
                'session.experiment._queryProposals(%r, {})' % proposal)

            if result:
                if len(result) != 1:
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
                self.proposalNum.setText(result.get('proposal', proposal))
                self.expTitle.setText(result.get('title', ''))
                self._update_users_model(result.get('users', []))
                self._format_user_table()
                self.localContacts.setText(
                    combineUsers(result.get('localcontacts', [])))
                self._update_samples_model(result['samples'])
                self._format_sample_table()
            else:
                self.showError('Querying proposal management system failed')
        except Exception as e:
            self.log.warning('error in proposal query', exc=1)
            self.showError('Querying proposal management system failed: '
                           + str(e))

    def _update_users_model(self, users):
        self.users_model.raw_data = deepcopy(users)

    def choose_proposal(self, proposals):
        dlg = dialogFromUi(self, 'panels/setup_exp_proposal.ui')
        dlg.list.setItemDelegate(ProposalDelegate(dlg))
        for prop in proposals:
            prop_copy = deepcopy(prop)
            prop_copy['users'] = [{'name': combineUsers(prop['users'])}]
            item = QListWidgetItem('', dlg.list)
            item.setData(Qt.UserRole, prop_copy)
        if not dlg.exec_():
            return
        sel = dlg.list.currentRow()
        return proposals[sel]

    def _update_samples_model(self, samples):
        if not self.hide_samples:
            self.samples_model.raw_data = deepcopy(samples)

    @pyqtSlot(str)
    def on_proposalNum_textChanged(self, value):
        self.new_proposal_settings.proposal_id = value.strip()
        self._check_for_changes()

    @pyqtSlot(str)
    def on_expTitle_textChanged(self, value):
        self.new_proposal_settings.title = value.strip()
        self._check_for_changes()

    def on_samples_changed(self):
        self._check_for_changes()

    def on_users_changed(self):
        self._check_for_changes()

    @pyqtSlot(str)
    def on_localContacts_textChanged(self, value):
        self.new_proposal_settings.local_contacts = value.strip()
        self._check_for_changes()

    @pyqtSlot()
    def on_errorAbortBox_clicked(self):
        self.new_proposal_settings.abort_on_error = \
            self.errorAbortBox.isChecked()
        self._check_for_changes()

    @pyqtSlot()
    def on_notifEmails_textChanged(self):
        self.new_proposal_settings.notifications = \
            self.notifEmails.toPlainText().strip().splitlines()
        self._check_for_changes()

    def _check_for_changes(self):
        has_changed = self.new_proposal_settings != self.old_proposal_settings
        has_changed |= \
            self.samples_model.raw_data != self.old_proposal_settings.samples
        has_changed |= \
            self.users_model.raw_data != self.old_proposal_settings.users
        self._set_buttons_and_warning_behaviour(has_changed)

    def discardChanges(self):
        self._update_proposal_info()
        self._check_for_changes()

    def on_experiment_finished(self):
        self._update_proposal_info()
        self._check_for_changes()
        self.proposalQuery.setText('')

    @pyqtSlot()
    def on_proposalQuery_returnPressed(self):
        self.on_queryDBButton_clicked()
