#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels import Panel, PanelDialog
from nicos.clients.gui.panels.setup_panel import ExpPanel as DefaultExpPanel, \
    SetupsPanel as DefaultSetupsPanel
from nicos.clients.gui.utils import loadUi
from nicos.core import ConfigurationError, mailaddress
from nicos.guisupport.qt import QDialogButtonBox, QMessageBox, pyqtSlot
from nicos.pycompat import to_utf8
from nicos.utils import decodeAny

from nicos_ess.gui import uipath


def maybe_encode(s):
    if isinstance(s, str):
        return s
    return to_utf8(s)


class ExpPanel(DefaultExpPanel):
    """Provides a panel with several input fields for the experiment settings.

    Options:

    * ``new_exp_panel`` -- class name of the panel which should be opened after
      a new experiment has been started.
    """

    panelName = 'Experiment setup'
    ui = '%s/panels/setup_exp.ui' % uipath

    def __init__(self, parent, client, options):
        DefaultExpPanel.__init__(self, parent, client, options)
        delattr(self, '_finish_exp_panel')

    def on_client_connected(self):
        # fill proposal
        self._update_proposal_info()
        self.newBox.setVisible(True)
        self.proposalNum.setText('')  # do not offer "service"
        # check for capability to ask proposal database
        if self.client.eval('getattr(session.experiment, "propdb", "")', None):
            self.propdbInfo.setVisible(True)
            self.queryDBButton.setVisible(True)
        else:
            self.queryDBButton.setVisible(False)
        if self.client.viewonly:
            self.buttonBox.removeButton(QDialogButtonBox.Apply)
        else:
            self.buttonBox.setStandardButtons(QDialogButtonBox.Apply)

    def _getProposalInput(self):
        prop = self.proposalNum.text()
        title = maybe_encode(self.expTitle.text())
        users = maybe_encode(self.users.text())
        try:
            local = mailaddress(maybe_encode(self.localContact.text()))
        except ValueError:
            QMessageBox.critical(self, 'Error', 'The local contact entry is '
                                 'not  a valid email address')
            raise ConfigurationError('')
        emails = maybe_encode(self.notifEmails.toPlainText()).strip()
        emails = emails.split(b'\n') if emails else []
        if local and local not in emails:
            emails.append(local)
        dataEmails = maybe_encode(self.dataEmails.toPlainText()).strip()
        dataEmails = dataEmails.split(b'\n') if dataEmails else []
        errorbehavior = 'abort' if self.errorAbortBox.isChecked() else 'report'
        return prop, title, users, local, emails, dataEmails, errorbehavior

    def applyChanges(self):
        done = []

        # proposal settings
        try:
            prop, title, users, local, email, dataEmails, errorbehavior = \
                self._getProposalInput()
        except ConfigurationError:
            return
        email = [_f for _f in email if _f]  # remove empty lines

        # check conditions
        if self.client.eval('session.experiment.serviceexp', True) and \
           self.client.eval('session.experiment.proptype', 'user') == 'user' and \
           self.client.eval('session.experiment.proposal', '') != prop:
            self.showError('Can not directly switch experiments, please use '
                           'FinishExperiment first!')
            return

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
            if title != self._orig_proposal_info[1]:
                self.client.run('Exp.title = %r' % title)
                done.append('New experiment title set.')
            if users != self._orig_proposal_info[2]:
                self.client.run('Exp.users = %r' % users)
                done.append('New users set.')
            if local != self._orig_proposal_info[3]:
                self.client.run('Exp.localcontact = %r' % local)
                done.append('New local contact set.')
        sample = maybe_encode(self.sampleName.text())
        if sample != self._orig_proposal_info[4]:
            self.client.run('NewSample(%r)' % sample)
            done.append('New sample name set.')
        if email != self._orig_email:
            self.client.run('SetMailReceivers(%s)' %
                            ', '.join(map(repr, email)))
            done.append('New mail receivers set.')
        if dataEmails != self._orig_datamails:
            self.client.run('SetDataReceivers(%s)' %
                            ', '.join(map(repr, dataEmails)))
            done.append('New data mail receivers set.')
        if errorbehavior != self._orig_proposal_info[5]:
            self.client.run('SetErrorAbort(%s)' % (errorbehavior == 'abort'))
            done.append('New error behavior set.')

        # tell user about everything we did
        if done:
            self.showInfo('\n'.join(done))
        self._update_proposal_info()

    @pyqtSlot()
    def on_queryDBButton_clicked(self):
        try:
            prop, title, users, _, emails, dataEmails, \
                _ = self._getProposalInput()
        except ConfigurationError:
            return
        sample = maybe_encode(self.sampleName.text())

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
                self.sampleName.setText(decodeAny(result.get('sample',
                                                             sample)))
                self.notifEmails.setPlainText(
                    decodeAny(result.get('user_email', emails)))
                self.dataEmails.setPlainText(
                    '\n'.join(decodeAny(addr) for addr in dataEmails))
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


class SetupsPanel(DefaultSetupsPanel):
    def on_client_connected(self):
        DefaultSetupsPanel.on_client_connected(self)
        if self.client.viewonly:
            self.buttonBox.removeButton(QDialogButtonBox.Apply)
            self.buttonBox.removeButton(self._reload_btn)
        else:
            self.buttonBox.setStandardButtons(QDialogButtonBox.Apply)
            self.buttonBox.addButton(self._reload_btn,
                                     QDialogButtonBox.ResetRole)


class FinishPanel(Panel):
    """Provides a panel to finish the experiment.

    Options:

    * ``finish_exp_panel`` -- class name of the panel which should be opened
      before an experiment is finished.
    """

    panelName = 'Finish experiment'
    ui = '%s/panels/finish_exp.ui' % uipath

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, self.ui)
        self._finish_exp_panel = None

        # Additional dialog panels to pop up after FinishExperiment().
        self._finish_exp_panel = options.get('finish_exp_panel')

        client.connected.connect(self.on_client_connected)
        client.setup.connect(self.on_client_connected)

    def on_client_connected(self):
        # check for new or finish
        self.finishBox.setVisible(True)
        if self.client.viewonly:
            self.finishButton.setVisible(False)
        else:
            self.finishButton.setVisible(True)

    @pyqtSlot()
    def on_finishButton_clicked(self):
        if self._finish_exp_panel:
            dlg = PanelDialog(self, self.client, self._finish_exp_panel,
                              'Finish experiment')
            dlg.exec_()
        if self.client.run('FinishExperiment()', noqueue=True) is None:
            self.showError('Could not finish experiment, a script '
                           'is still running.')
