# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI experiment setup window."""

from os import path

from nicos.clients.gui.panels.setup_panel import ExpPanel as BaseExpPanel
from nicos.core.errors import ConfigurationError
from nicos.guisupport.qt import QMessageBox, pyqtSlot
from nicos.utils import findResource
from nicos.utils.user import combineUsers, splitUsers


class ExpPanel(BaseExpPanel):

    ui = findResource(path.join('nicos_mlz', 'gui', 'setup_exp.ui'))

    def on_client_disconnected(self):
        self.proposalNum.clear()
        self.expTitle.clear()
        self.users.clear()
        self.notifEmails.clear()
        self.dataEmails.clear()
        self.localContacts.clear()
        self.samples.clear()
        BaseExpPanel.on_client_disconnected(self)

    def _getProposalInput(self):
        prop = self.proposalNum.text()
        title = self.expTitle.text()
        try:
            users = splitUsers(self.users.text())
        except ValueError:
            QMessageBox.warning(
                self, 'Error', 'Invalid users list, please specify as\n\n'
                'First Name <first@email.com>; Second Name <second@email.com>'
            )
            raise ConfigurationError from None
        try:
            local = splitUsers(self.localContacts.text())
        except ValueError:
            QMessageBox.warning(
                self, 'Error', 'Invalid local contacts, please specify as\n\n'
                'First Name <first@email.com>; Second Name <second@email.com>'
            )
            raise ConfigurationError from None
        sample = ''
        notifEmails = self.notifEmails.toPlainText().strip()
        notifEmails = notifEmails.split('\n') if notifEmails else []
        dataEmails = self.dataEmails.toPlainText().strip()
        dataEmails = dataEmails.split('\n') if dataEmails else []
        errorbehavior = 'abort' if self.errorAbortBox.isChecked() else 'report'
        return prop, title, users, local, sample, notifEmails, dataEmails, \
            errorbehavior

    def _update_proposal_info(self):
        propinfo, samplename, errorbehavior = \
            self.client.eval('session.experiment.propinfo, '
                             'session.experiment.sample.samplename, '
                             'session.experiment.errorbehavior',
                             ({}, None, None))
        self._orig_propinfo = propinfo
        self._orig_samplename = samplename
        self._orig_errorbehavior = errorbehavior
        if not propinfo:
            return
        self.proposalNum.setText(propinfo.get('proposal', ''))
        self.expTitle.setText(propinfo.get('title', ''))

        self.users.setText(combineUsers(propinfo.get('users', [])))
        self.localContacts.setText(
            combineUsers(propinfo.get('localcontacts', [])))
        self.notifEmails.setPlainText(
            '\n'.join(propinfo.get('notif_emails', [])))
        self.dataEmails.setPlainText(
            '\n'.join(propinfo.get('data_emails', [])))

        self.errorAbortBox.setChecked(errorbehavior == 'abort')

        samples = self.client.eval('session.experiment.sample.samples', {})
        if len(samples) > 1:
            self.samples.setSamples(samples.values())

    @pyqtSlot()
    def on_finishButton_clicked(self):
        BaseExpPanel.on_finishButton_clicked(self)
        self.samples.clear()

    @pyqtSlot()
    def on_queryDBButton_clicked(self):
        try:
            prop, title, _, _, _sample, notifEmails, dataEmails, \
                _ = self._getProposalInput()
        except ConfigurationError:
            return

        # read all values from propdb
        try:
            queryprop = prop or None
            result = self.client.eval(
                'session.experiment._queryProposals(%r, {})' % queryprop, None)

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

                # TODO Sync sample parameters from Ghost with NICOS !!!!
                sample_dev = self.client.eval(
                    'session.experiment.sample', 'Sample')
                paramInfo = self.client.getDeviceParamInfo(sample_dev)
                samples = result.get('samples', [])
                for sample in samples:
                    sample['samplename'] = sample.pop('name', '')
                    # The next lines are a little bit of hacking to overcome
                    # the mismatch between NICOS and GhOST keys
                    if 'spacegroup' in paramInfo:
                        sample['spacegroup'] = sample.pop('spgr', '')
                    if all(k in paramInfo for k in ['lattice', 'angles']):
                        cell = [float(x) for x in
                                sample.pop('cell', '0 0 0 0 0 0').split()]
                        if lc := (6 - len(cell)):
                            cell.extend([0] * lc)
                        sample['lattice'] = cell[:3]
                        sample['angles'] = cell[3:]
                self.samples.setSamples(samples, paramInfo)

                self.notifEmails.setPlainText(
                    '\n'.join(result.get('notif_emails', notifEmails)))
                self.dataEmails.setPlainText(
                    '\n'.join(result.get('data_emails', dataEmails)))
            else:
                self.showError('Querying proposal management system failed: '
                               'the proposal might not exist or be for '
                               'another instrument.')
        except Exception as e:
            self.log.warning('error in proposal query', exc=1)
            self.showError('Querying proposal management system failed for an '
                           'unknown reason. Please check logfiles.\n' + repr(e))

    def _sample_hook(self, sample):
        if code := self.samples.generateCode().rstrip():
            if self.client.run(code, noqueue=True) is not None:
                return 'Samples set.'
            return "Couldn't set samples. A script is still running"
        return None
