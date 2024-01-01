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
#
# *****************************************************************************
from datetime import datetime
from logging import INFO
from os import path

import elog
from elog import LogbookInvalidMessageID, LogbookMessageRejected, \
    LogbookServerProblem

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QAbstractItemView, QLineEdit, QTableWidgetItem
from nicos.utils.loggers import INPUT

from nicos_sinq.gui import uipath


def is_connected(logbook):
    try:
        logbook.post('', attribute_as_param='value')
    except (LogbookInvalidMessageID, LogbookServerProblem):
        return False
    except LogbookMessageRejected:
        return True


class ElogPanel(Panel):
    panelName = 'Console'
    ui = path.join(uipath, 'panels', 'ui_files', 'elog.ui')

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, self.ui)
        self.message_selected = None

        # Populate the options for the message
        options.get('types', ['General'])
        options.get('categories', ['Other'])

        # The table with the list of messages is READ ONLY
        self.messagesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.messagesTable.setHorizontalHeaderLabels(['Id', 'Date', 'Subject'])

        self.loginPassword.setEchoMode(QLineEdit.Password)
        self.logbook = None

        client.message.connect(self.on_client_message)

        self.connectButton.clicked.connect(self.connectToElog)
        self.submitButton.clicked.connect(self.postMessage)
        self.editButton.clicked.connect(self.editMessage)
        self.refreshMessagesButton.clicked.connect(self.updateMessagesTable)
        self.messagesTable.cellClicked.connect(self.onSelectCell)

    def on_client_message(self, message):
        if not self.recordButton.isChecked():
            return
        if message[2] not in (INFO, INPUT):
            return
        message = message[3].strip()
        self.messageText.append(f'|  {message}')

    def _connect(self):
        self.logbook = elog.open(self.logbookAddress.text(),
                                 user=self.loginUser.text(),
                                 password=self.loginPassword.text())
        if is_connected(self.logbook):
            self.logbook.get_last_message_id()
            self.connectionStatus.setText('Connected')
            self.updateMessagesTable()
            self.connectButton.setText('Disconnect')
        else:
            self.connectionStatus.setText('Connection failed')
            self.logbook = None

    def _disconnect(self):
        self.logbook = None
        self.connectButton.setText('Connect')
        self.connectionStatus.setText('Disconnected')
        self.messagesTable.clear()
        self.editButton.setText('Edit')

    def connectToElog(self):
        if self.logbook:
            self._disconnect()
            return
        self._connect()

    def postMessage(self):
        # try to post new message
        try:
            msg_id = self.logbook.post(
                self.messageText.toPlainText(),
                author=self.messageAuthor.text(),
                type=self.messageType.currentText(),
                category=self.messageCategory.currentText(),
                subject=self.messageSubject.text(),
                attribute_as_param='value')
        except LogbookMessageRejected as e:
            self.log.error(e)
            return
        except AttributeError:
            self.log.error('Client not connected')
            return

        self.messageText.clear()

        # Add the message_id, subject to the table
        row_count = self.messagesTable.rowCount()
        self.messagesTable.setRowCount(row_count + 1)
        self.messagesTable.setItem(row_count, 0, QTableWidgetItem(f'{msg_id}'))
        self.messagesTable.setItem(
            row_count, 1, QTableWidgetItem(datetime.now().strftime('%c')))
        self.messagesTable.setItem(
            row_count, 2, QTableWidgetItem(self.messageSubject.text()))

    def editMessage(self):
        try:
            _msg_id = self.logbook.post(
                self.messageText.toPlainText(),
                msg_id=self.message_selected,
                author=self.messageAuthor.text(),
                type=self.messageType.currentText(),
                category=self.messageCategory.currentText(),
                subject=self.messageSubject.text(),
                attribute_as_param='value')
            self.messageText.clear()
        except LogbookMessageRejected as e:
            self.log.error(e)
        except AttributeError:
            self.log.errornt('Client not connected')

    def updateMessagesTable(self):
        self.messagesTable.clear()
        try:
            message_ids = self.logbook.get_message_ids()
        except AttributeError:
            self.log.error('Not connected to a logbook')
            return
        self.messagesTable.setRowCount(len(message_ids))
        for index, message_id in enumerate(reversed(message_ids)):
            message = self.logbook.read(message_id)[1]
            self.messagesTable.setItem(index, 0,
                                       QTableWidgetItem(f'{message_id}'))
            self.messagesTable.setItem(
                index, 1, QTableWidgetItem(message.get('Date', '')))
            self.messagesTable.setItem(
                index, 2, QTableWidgetItem(message.get('Subject', '')))

    def onSelectItem(self, item):
        self.message_selected = int(item.text())
        try:
            message, options, _ = self.logbook.read(self.message_selected)
        except ValueError as e:
            self.log.error('%s: %s', self.__class__.__name__, e)
            return
        self.messageText.setPlainText(message)
        self.messageAuthor.setText(options.get('Author', ''))
        self.messageType.setCurrentText(options.get('Type', ''))
        self.messageCategory.setCurrentText(options.get('Category', ''))
        self.messageSubject.setText(options.get('Subject', ''))
        self.editButton.setText(f'Edit #{item.text()}')

    def onSelectCell(self, row, column):
        try:
            item = self.messagesTable.item(row, 0)
            self.message_selected = int(item.text())
        except AttributeError as e:
            self.log.error('%s: %s', self.__class__.__name__, e)
            return
        try:
            message, options, _ = self.logbook.read(self.message_selected)
        except ValueError as e:
            self.log.error('%s: %s', self.__class__.__name__, e)
            return
        self.messageText.setPlainText(message)
        self.messageAuthor.setText(options.get('Author', ''))
        self.messageType.setCurrentText(options.get('Type', ''))
        self.messageCategory.setCurrentText(options.get('Category', ''))
        self.messageSubject.setText(options.get('Subject', ''))
        self.editButton.setText(f'Edit #{item.text()}')
