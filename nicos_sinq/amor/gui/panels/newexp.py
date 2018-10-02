#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import

import os

from nicos.clients.gui.panels.generic import GenericPanel
from nicos.core import ConfigurationError
from nicos.core.params import mailaddress
from nicos.guisupport.qt import QDialogButtonBox, QMessageBox, pyqtSlot
from nicos.utils import decodeAny


class AmorNewExpPanel(GenericPanel):
    """Provides a panel with several input fields for the experiment settings.
    """

    panelName = 'Experiment Edit'

    def __init__(self, parent, client, options):
        GenericPanel.__init__(self, parent, client, options)
        self._orig_proposal = None

        client.connected.connect(self.on_client_connected)
        client.setup.connect(self.on_client_connected)
        client.experiment.connect(self.on_client_experiment)

    def _update_proposal_info(self):
        values = self.client.eval('session.experiment.proposal, '
                                  'session.experiment.title, '
                                  'session.experiment.users, '
                                  'session.experiment.proposalpath, '
                                  'session.experiment.remark', None)
        if values:
            usersplit = decodeAny(values[2]).split('<')
            username = usersplit[0].strip()
            useremail = usersplit[1][:-1] if len(usersplit) > 1 else ''
            values = (values[0], values[1], username, useremail, values[3],
                      values[4])
            self._orig_proposal_info = values
            self.proposalNum.setText(values[0])
            self.expTitle.setText(decodeAny(values[1]))
            self.userName.setText(values[2])
            self.userEmail.setText(values[3])
            self.proposalDir.setText(decodeAny(values[4]))
            self.remark.setText(decodeAny(values[5]))

    def on_client_connected(self):
        # fill proposal
        self._update_proposal_info()
        # check for new or finish
        if self.client.eval('session.experiment.mustFinish', False):
            self.finishBox.setVisible(True)
            self.proposalNum.setEnabled(False)
            self.proposalDir.setEnabled(False)
        else:
            self.finishBox.setVisible(False)
            self.proposalNum.setEnabled(True)
            self.proposalDir.setEnabled(True)
            self.proposalNum.setText('')  # do not offer "service"
            self.proposalDir.setText('')

        if self.client.viewonly:
            self.finishButton.setVisible(False)
            self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        else:
            self.finishButton.setVisible(True)
            self.buttonBox.setStandardButtons(QDialogButtonBox.Apply |
                                              QDialogButtonBox.Close)

    def on_client_experiment(self, data):
        # just reinitialize
        self.on_client_connected()

    def _getProposalInput(self):
        prop = self.proposalNum.text()
        title = self.expTitle.text().encode('utf-8')
        username = self.userName.text().encode('utf-8')
        remark = self.remark.text().encode('utf-8')
        proposaldir = self.proposalDir.text().encode('utf-8')
        if proposaldir and not os.path.isdir(proposaldir):
            QMessageBox.critical(self, 'Error', 'The provided proposal path '
                                 'does not exist!')
            raise ConfigurationError('')
        if not os.access(proposaldir, os.W_OK):
            QMessageBox.critical(self, 'Error', 'Don\'t have permission to '
                                 'write in the proposal path! Please choose '
                                 'a different one!')
            raise ConfigurationError('')
        try:
            useremail = mailaddress(self.userEmail.text().encode('utf-8'))
        except ValueError:
            QMessageBox.critical(self, 'Error', 'The user email entry is '
                                 'not  a valid email address')
            raise ConfigurationError('')
        return prop, title, username, useremail, proposaldir, remark

    @pyqtSlot()
    def on_finishButton_clicked(self):
        code = 'Exp.proposalpath = "/home/amor/nicos/service"'
        code += '\n'
        code = 'FinishExperiment()'
        if self.client.run(code, noqueue=True) is None:
            self.showError('Could not finish experiment, a script '
                           'is still running.')

    def on_buttonBox_clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self.applyChanges()
        elif role == QDialogButtonBox.RejectRole:
            self.closeWindow()

    def applyChanges(self):
        done = []

        # proposal settings
        try:
            prop, title, username, useremail, proposaldir, remark = \
                self._getProposalInput()
        except ConfigurationError:
            return

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
            if title:
                args['title'] = title
            args['user'] = ''
            if username:
                args['user'] = username
            if useremail:
                args['user'] += ' <' + useremail + '>'
            code = ''
            if proposaldir:
                code += 'Exp.proposalpath = %r' % proposaldir
                code += '\n'

            code += 'NewExperiment(%s)' % ', '.join('%s=%r' % i
                                                    for i in args.items())

            if remark:
                code += '\n'
                code += 'Exp.remark = %r' % remark

            if self.client.run(code, noqueue=False) is None:
                self.showError('Could not start new experiment, a script is '
                               'still running.')
                return
            done.append('New experiment started.')
        else:
            if title != self._orig_proposal_info[1]:
                self.client.run('Exp.title = %r' % title)
                done.append('New experiment title set.')
            if username != self._orig_proposal_info[2] or \
               useremail != self._orig_proposal_info[3]:
                users = username
                if useremail:
                    users += ' <' + useremail + '>'
                self.client.run('Exp.users = %r' % users)
                done.append('New user set.')

            if proposaldir and proposaldir != self._orig_proposal_info[4]:
                self.client.run('Exp.proposalpath = %r' % proposaldir)
                done.append('Proposal directory updated')

            if remark and remark != self._orig_proposal_info[5]:
                self.client.run('Exp.remark = %r' % remark)
                done.append('Remark updated.')

        # tell user about everything we did
        if done:
            self.showInfo('\n'.join(done))
        self._update_proposal_info()
