#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""Simplified interface to report a ticket to the NICOS Redmine tracker."""

from cgi import escape

from PyQt4.QtCore import QSettings, QUrl
from PyQt4.QtGui import QDesktopServices, QDialog, QDialogButtonBox, \
    QGridLayout, QLabel, QLineEdit


try:
    import redmine  # pylint: disable=F0401
except ImportError:
    redmine = None

from nicos.clients.gui.panels import DlgUtils
from nicos.clients.gui.utils import loadUi


TRACKER_URL = 'http://forge.frm2.tum.de/redmine'
TICKET_URL = 'http://forge.frm2.tum.de/issues/%d'
PROJECT_ID = 'NICOS'
CREATE_TICKET_URL = 'http://forge.frm2.tum.de/projects/nicos/issues/new'


class BugreportTool(QDialog, DlgUtils):
    toolName = 'BugreportTool'

    def __init__(self, parent, client, **kwds):
        QDialog.__init__(self, parent)
        DlgUtils.__init__(self, self.toolName)
        loadUi(self, 'bugreport.ui', 'tools')

        settings = QSettings('nicos', 'secrets')
        settings.beginGroup('Redmine')
        self.instrument = settings.value('instrument', 'not specified')
        self.apikey = settings.value('apikey')
        self.username = settings.value('username')

        self.traceback = kwds.get('traceback')
        self.log_excerpt = kwds.get('log_excerpt', '')
        if not self.traceback:
            self.tbLabel.hide()
            self.scriptBox.hide()
        else:
            self.ticketType.setEnabled(False)  # always bug
            self.scriptBox.setChecked(True)
            self.subject.setText(self.traceback.splitlines()[-1].strip())

        self.stacker.setCurrentIndex(0)
        self.subject.setFocus()
        btn = self.buttonBox.addButton('Login details', QDialogButtonBox.ResetRole)
        btn.clicked.connect(self._queryDetails)

        if not redmine:
            self.showError('Reporting is not possible since the python-redmine '
                           'module is not installed.')
            return  # don't add Submit button
        elif not self.instrument or not self.apikey:
            if not self._queryDetails():
                return

        self.buttonBox.addButton('Submit', QDialogButtonBox.AcceptRole)

        self.titleLabel.setText(
            'Submit a ticket for instrument "%s" (as user %s)'
            % (self.instrument, self.username))

    def _queryDetails(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('Login details for ticket tracker required')
        layout = QGridLayout()
        layout.addWidget(QLabel('Please enter details for the ticket tracker. '
                                'You can contact the instrument control group '
                                'for help.', dlg))
        layout.addWidget(QLabel('Instrument name:', dlg))
        instrBox = QLineEdit(self.instrument, dlg)
        layout.addWidget(instrBox)
        layout.addWidget(QLabel('Username:', dlg))
        userBox = QLineEdit(self.username, dlg)
        layout.addWidget(userBox)
        layout.addWidget(QLabel('Password:', dlg))
        passwdBox = QLineEdit(dlg)
        passwdBox.setEchoMode(QLineEdit.Password)
        layout.addWidget(passwdBox)
        buttonbox = QDialogButtonBox(dlg)
        buttonbox.addButton(QDialogButtonBox.Ok)
        buttonbox.addButton(QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(dlg.accept)
        buttonbox.rejected.connect(dlg.reject)
        layout.addWidget(buttonbox)
        dlg.setLayout(layout)
        if dlg.exec_() == QDialog.Accepted:
            rm = redmine.Redmine(TRACKER_URL, username=userBox.text(),
                                 password=passwdBox.text())
            try:
                apikey = rm.auth().api_key
            except Exception as err:
                self.showError(str(err))
                return False
            self.showInfo('Login successful.  Your API key has been stored '
                          'for further reports.')
            settings = QSettings('nicos', 'secrets')
            settings.beginGroup('Redmine')
            self.instrument = instrBox.text()
            self.apikey = apikey
            self.username = userBox.text()
            settings.setValue('instrument', self.instrument)
            settings.setValue('apikey', self.apikey)
            settings.setValue('username', self.username)
            if not self.instrument or not self.apikey:
                return False
            self.titleLabel.setText(
                'Submit a ticket for instrument "%s" (as user %s)'
                % (self.instrument, self.username))
            return True

    def on_buttonBox_accepted(self):
        ticket_type = self.ticketType.currentText()
        is_critical = self.highPrio.isChecked()
        subject = self.subject.text().strip()
        description = self.descText.toPlainText().strip()
        reproduction = self.reproText.toPlainText().strip()
        add_log = self.scriptBox.isChecked()

        if not subject or not description:
            self.showError('Please enter a ticket subject and description.')
            return

        try:
            ticket_num = self.submitIssue(ticket_type, is_critical, subject,
                                          description, reproduction, add_log)
        except Exception as e:
            self.showError('Unfortunately, something went wrong submitting the '
                           'ticket (%s). The tracker page will now be opened, '
                           'please enter the ticket there.' % e)
            QDesktopServices.openUrl(QUrl(CREATE_TICKET_URL))
            return

        # switch to "thank you" display
        self.stacker.setCurrentIndex(1)
        self.buttonBox.clear()
        self.buttonBox.addButton(QDialogButtonBox.Close)
        self.ticketUrl.setText(TICKET_URL % ticket_num)

    def on_ticketUrl_released(self):
        QDesktopServices.openUrl(QUrl(self.ticketUrl.text()))

    def submitIssue(self, ticket_type, is_critical, subject, description,
                    reproduction, add_log):

        def wrap(text):
            return escape(text).replace('\n\n', '</p><p>'). \
                replace('\n', '<br/>')

        full_desc = '<p>' + wrap(description) + '</p>'
        if reproduction:
            full_desc += '\n\n<p><b>Reproduction:</b></p>' + \
                         '<p>' + wrap(reproduction) + '</p>'
        if self.traceback:
            full_desc += '\n\n<p><b>Traceback:</b></p>\n' + \
                         '<pre>' + self.traceback + '</pre>'
        if add_log and self.log_excerpt:
            full_desc += '\n\n<p><b>Log excerpt:</b></p>\n' + \
                         '<pre>' + self.log_excerpt + '</pre>'

        rm = redmine.Redmine(TRACKER_URL, key=self.apikey)
        issue = rm.issue.new()
        issue.project_id = PROJECT_ID
        issue.subject = subject
        trackers = rm.tracker.all()
        tracker_id = [t.id for t in trackers if t.name == ticket_type][0]
        issue.tracker_id = tracker_id
        issue.description = full_desc
        if is_critical:
            prios = rm.enumeration.filter(resource='issue_priorities')
            prio_id = [p.id for p in prios if p.name == 'Urgent'][0]
            issue.priority_id = prio_id
        issue.custom_fields = [{'id': 1, 'value': self.instrument}]
        issue.save()
        return issue.id
