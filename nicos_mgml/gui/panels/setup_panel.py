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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Petr Čermák <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""NICOS GUI experiment setup window."""

from nicos.clients.gui.panels import PanelDialog
from nicos.clients.gui.panels.expinfo import \
    ExpInfoPanel as DefaultExpInfoPanel
from nicos.clients.gui.panels.setup_panel import ExpPanel as DefaultExpPanel, \
    splitUsers
from nicos.core import ConfigurationError
from nicos.guisupport.qt import QMessageBox, pyqtSlot
from nicos.utils import decodeAny, findResource

from nicos_mgml.gui import uipath


def combineUsers(users):
    """Combine user info into a string with known format."""
    res = []
    for user in users:
        res.append(user['name'])
    return '; '.join(res)


class ExpPanel(DefaultExpPanel):
    """Provides a panel with several input fields for the experiment settings.

    Options:

    * ``new_exp_panel`` -- class name of the panel which should be opened after
      a new experiment has been started.
    * ``finish_exp_panel`` -- class name of the panel which should be opened
      before an experiment is finished.
    """

    panelName = 'Experiment setup'
    ui = findResource(f'{uipath}/panels/setup_exp.ui')

    def _update_proposal_info(self):
        propinfo, samplename, errorbehavior = self.client.eval(
            'session.experiment.propinfo, '
            'session.experiment.sample.samplename, '
            'session.experiment.errorbehavior',
            (None, None, None),
        )
        if not propinfo:
            self._orig_propinfo = {}
            return
        self._orig_propinfo = propinfo
        self._orig_samplename = samplename
        self._orig_errorbehavior = errorbehavior
        self.proposalNum.setText(propinfo.get('proposal', ''))
        self.expTitle.setText(decodeAny(propinfo.get('title', '')))

        self.users.setText(combineUsers(propinfo.get('users', [])))
        self.localContacts.clear()
        lc = propinfo.get('localcontacts', [])
        if len(lc) > 0:
            if 'id' in lc[0]:
                self.localContacts.addItem(lc[0]['name'], userData=lc[0]['id'])
            elif 'name' in lc[0]:
                self.localContacts.addItem(lc[0]['name'], userData=0)
        self.notifEmails.setPlainText(
            decodeAny('\n'.join(propinfo.get('notif_emails', [])))
        )
        self.dataEmails.setPlainText(
            decodeAny('\n'.join(propinfo.get('data_emails', [])))
        )

        self.sampleName.setText(decodeAny(samplename))
        self.errorAbortBox.setChecked(errorbehavior == 'abort')

    def _getProposalInput(self):
        prop = self.proposalNum.text()
        title = self.expTitle.text()
        try:
            users = splitUsers(self.users.text())
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Invalid email address in users list')
            raise ConfigurationError from None
        try:
            local = [
                {
                    'id': self.localContacts.currentData(),
                    'name': self.localContacts.currentText(),
                }
            ]
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Invalid local contact')
            raise ConfigurationError from None
        sample = self.sampleName.text()
        notifEmails = self.notifEmails.toPlainText().strip()
        notifEmails = notifEmails.split('\n') if notifEmails else []
        dataEmails = self.dataEmails.toPlainText().strip()
        dataEmails = dataEmails.split('\n') if dataEmails else []
        errorbehavior = 'abort' if self.errorAbortBox.isChecked() else 'report'
        return prop, title, users, local, sample, notifEmails, dataEmails, errorbehavior

    def on_client_connected(self):
        # fill proposal
        self._update_proposal_info()
        # check for new or finish
        if self.client.eval('session.experiment.mustFinish', False):
            self.finishBox.setVisible(True)
            self.newBox.setVisible(False)
            self.dataBox.setVisible(False)
            self.startButton.setText('Update Experiment')
        else:
            self.finishBox.setVisible(False)
            self.newBox.setVisible(True)
            self.dataBox.setVisible(True)
            self.proposalNum.setText('')  # do not offer "service"
            self.startButton.setText('Start Experiment')
        # check for capability to ask proposal database
        if self.client.eval('session.experiment._canQueryProposals()', None):
            self.propdbInfo.setVisible(True)
            self.queryDBButton.setVisible(True)
        if self.client.viewonly:
            self.finishButton.setVisible(False)
            self.startButton.setVisible(False)
        else:
            self.finishButton.setVisible(True)
            self.startButton.setVisible(True)
        # fill proposal combo
        try:
            result = self.client.eval('session.experiment._queryProposals()', None)

            if result:
                self.proposalCombo.clear()
                for r in result:
                    self.proposalCombo.addItem(
                        f"{r['proposal']} {r['title']}", userData=r['proposal']
                    )
            else:
                pass
                # self.showError(
                #     'Querying User dashboard failed :('
                #     'Maybe you have no accepted proposals?'
                # )
        except Exception as e:
            self.log.warning('error in proposal query', exc=1)
            self.showError(
                'Querying User dashboard failed for an '
                'unknown reason. Please check logfiles.\n' + repr(e)
            )

    @pyqtSlot()
    def on_startButton_clicked(self):
        self.applyChanges()

    @pyqtSlot()
    def on_queryDBButton_clicked(self):
        try:
            prop = self.proposalCombo.currentData()
        except ConfigurationError:
            return

        # read all values from propdb
        try:
            result = self.client.eval(
                f'session.experiment._queryProposals("{prop}")', None
            )

            if result:
                result = result[0]
                # check for errors/warnings:
                if result.get('errors'):
                    self.showError(
                        'Proposal cannot be performed:\n\n'
                        + '\n'.join(result['errors'])
                    )
                    return
                if result.get('warnings'):
                    self.showError(
                        'Proposal might have problems:\n\n'
                        + '\n'.join(result['warnings'])
                    )
                # now transfer it into gui
                self.proposalNum.setText(decodeAny(result.get('proposal', '')))
                self.expTitle.setText(decodeAny(result.get('title', '')))
                self.users.setText(combineUsers(result.get('users', [])))
                # fill local contacts
                self.localContacts.clear()
                for lc in result.get('localcontacts', []):
                    self.localContacts.addItem(lc['name'], userData=lc['id'])
                self.notifEmails.setPlainText(
                    decodeAny('\n'.join(result.get('notif_emails', [])))
                )
                self.dataEmails.setPlainText(
                    decodeAny('\n'.join(result.get('data_emails', [])))
                )
            else:
                self.showError(
                    'Querying User dashboard failed: '
                    'the proposal might not exist or '
                    'it is not yours!'
                )
        except Exception as e:
            self.log.warning('error in proposal query', exc=1)
            self.showError(
                'Querying User dashboard failed for an '
                'unknown reason. Please check logfiles.\n' + repr(e)
            )


class ExpInfoPanel(DefaultExpInfoPanel):
    @pyqtSlot()
    def on_proposalBtn_clicked(self):
        dlg = PanelDialog(
            self,
            self.client,
            ExpPanel,
            'Proposal info',
            new_exp_panel=self._new_exp_panel,
            finish_exp_panel=self._finish_exp_panel,
        )
        dlg.exec_()
