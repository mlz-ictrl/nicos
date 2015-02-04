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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI virtual console panel component."""

import io
import sys
import time

from PyQt4.QtGui import QDialog, QFileDialog, QMessageBox, QMenu, QColor, \
    QPrinter, QPrintDialog, QAbstractPrintDialog
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig, Qt

from nicos.utils import chunks
from nicos.clients.gui.panels import Panel, showPanel
from nicos.clients.gui.utils import loadUi, setBackgroundColor, setForegroundColor, \
    enumerateWithProgress, ScriptExecQuestion
from nicos.clients.gui.dialogs.traceback import TracebackDialog
from nicos.core import SIMULATION, SLAVE, MAINTENANCE


class ConsolePanel(Panel):
    panelName = 'Console'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'console.ui', 'panels')

        self.current_status = None
        self.run_color = QColor('#ffdddd')
        self.idle_color = parent.user_color
        self.commandInput.scrollWidget = self.outView
        self.grepPanel.hide()
        self.grepText.scrollWidget = self.outView
        self.actionLabel.hide()
        self.outView.setActionLabel(self.actionLabel)
        self.commandInput.history = self.cmdhistory
        self.commandInput.completion_callback = self.completeInput
        self.grepNoMatch.setVisible(False)

        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('message'), self.on_client_message)
        self.connect(client, SIGNAL('initstatus'), self.on_client_initstatus)
        self.connect(client, SIGNAL('mode'), self.on_client_mode)
        self.connect(client, SIGNAL('experiment'), self.on_client_experiment)

        self.outView.setContextMenuPolicy(Qt.CustomContextMenu)

        self.menu = QMenu('&Output', self)
        self.menu.addAction(self.actionCopy)
        self.menu.addAction(self.actionGrep)
        self.menu.addSeparator()
        self.menu.addAction(self.actionSave)
        self.menu.addAction(self.actionPrint)

    def on_outView_customContextMenuRequested(self, point):
        self.menu.popup(self.outView.mapToGlobal(point))

    def setOptions(self, options):
        self.hasinput = bool(options.get('hasinput', True))
        self.inputFrame.setVisible(self.hasinput)
        self.hasmenu = bool(options.get('hasmenu', True))

    def setExpertMode(self, expert):
        if not self.hasinput:
            self.inputFrame.setVisible(expert)

    def loadSettings(self, settings):
        self.cmdhistory = settings.value('cmdhistory') or []

    def saveSettings(self, settings):
        # only save 100 entries of the history
        cmdhistory = self.commandInput.history[-100:]
        settings.setValue('cmdhistory', cmdhistory)

    def getMenus(self):
        if self.hasmenu:
            return [self.menu]
        return []

    def setCustomStyle(self, font, back):
        self.idle_color = back
        for widget in (self.outView, self.commandInput):
            widget.setFont(font)
            setBackgroundColor(widget, back)
        self.label.setFont(font)

    def updateStatus(self, status, exception=False):
        self.current_status = status
        if status != 'idle':
            setBackgroundColor(self.commandInput, self.run_color)
        else:
            setBackgroundColor(self.commandInput, self.idle_color)
        self.commandInput.update()
        self.commandInput.setEnabled(status != 'disconnected')

    def completeInput(self, fullstring, lastword):
        try:
            return self.client.ask('complete', fullstring, lastword)
        except Exception:
            return []

    def on_client_connected(self):
        self.outView._currentuser = self.client.login

    def on_client_mode(self, mode):
        if mode == SLAVE:
            self.label.setText('slave >>')
        elif mode == SIMULATION:
            self.label.setText('SIM >>')
        elif mode == MAINTENANCE:
            self.label.setText('maint >>')
        else:
            self.label.setText('>>')

    def on_client_initstatus(self, state):
        self.on_client_mode(state['mode'])
        self.outView.clear()
        messages = self.client.ask('getmessages', '10000')
        if not messages:
            return
        total = len(messages) // 2500 + 1
        for _, batch in enumerateWithProgress(chunks(messages, 2500),
                            text='Synchronizing...', parent=self, total=total):
            self.outView.addMessages(batch)
        self.outView.scrollToBottom()

    def on_client_message(self, message):
        if message[-1] == '(editorsim) ':
            return
        self.outView.addMessage(message)

    def on_client_experiment(self, data):
        (_, proptype) = data
        if proptype == 'user':
            # only clear history and output when switching TO a user experiment
            self.commandInput.history = []
            # clear everything except the last command with output
            self.outView.clearAlmostEverything()

    def on_outView_anchorClicked(self, url):
        """Called when the user clicks a link in the out view."""
        url = url.toString()
        if url.startswith('exec:'):
            # Direct execution is too dangerous. Just insert it in the editor.
            if self.inputFrame.isVisible():
                self.commandInput.setText(url[5:])
                self.commandInput.setFocus()
        elif url.startswith('edit:'):
            if not self.mainwindow.editor_wintype:
                return
            win = self.mainwindow.createWindow(self.mainwindow.editor_wintype)
            panel = win.getPanel('User editor')
            panel.openFile(url[5:])
            showPanel(panel)
        elif url.startswith('trace:'):
            TracebackDialog(self, self.outView, url[6:]).show()
        else:
            self.log.warning('Strange anchor in outView: ' + url)

    @qtsig('')
    def on_actionPrint_triggered(self):
        printer = QPrinter()
        printdlg = QPrintDialog(printer, self)
        printdlg.addEnabledOption(QAbstractPrintDialog.PrintSelection)
        if printdlg.exec_() == QDialog.Accepted:
            self.outView.print_(printer)

    @qtsig('')
    def on_actionSave_triggered(self):
        fn = QFileDialog.getSaveFileName(self, 'Save', '', 'All files (*.*)')
        if not fn:
            return
        try:
            fn = fn.encode(sys.getfilesystemencoding())
            with io.open(fn, 'w', encoding='utf-8') as f:
                f.write(self.outView.getOutputString())
        except Exception as err:
            QMessageBox.warning(self, 'Error', 'Writing file failed: %s' % err)

    @qtsig('')
    def on_actionCopy_triggered(self):
        self.outView.copy()

    @qtsig('')
    def on_actionGrep_triggered(self):
        self.grepPanel.setVisible(True)
        self.grepText.setFocus()

    @qtsig('')
    def on_grepClose_clicked(self):
        self.grepPanel.setVisible(False)
        self.commandInput.setFocus()
        self.outView.scrollToBottom()

    def on_grepText_returnPressed(self):
        self.on_grepSearch_clicked()

    def on_grepText_escapePressed(self):
        self.on_grepClose_clicked()

    @qtsig('')
    def on_grepSearch_clicked(self):
        st = self.grepText.text()
        if not st:
            return
        found = self.outView.findNext(st, self.grepRegex.isChecked())
        self.grepNoMatch.setVisible(not found)

    @qtsig('')
    def on_grepOccur_clicked(self):
        st = self.grepText.text()
        if not st:
            return
        self.outView.occur(st, self.grepRegex.isChecked())

    def on_commandInput_textChanged(self, text):
        try:
            script = self.commandInput.text()
            if not script or script.strip().startswith('#'):
                return
            compile(script+'\n', 'script', 'single')
        except Exception:
            setForegroundColor(self.commandInput, QColor("#ff0000"))
        else:
            setForegroundColor(self.commandInput, QColor("#000000"))

    def on_commandInput_returnPressed(self):
        script = self.commandInput.text().strip()
        if not script:
            return
        # XXX: this does not apply in SPM mode
        # if not (sscript.startswith(('#', '?', '.', ':')) or sscript.endswith('?')):
        #     try:
        #         compile(script+'\n', 'script', 'single')
        #     except SyntaxError as err:
        #         QMessageBox.information(
        #             self, 'Command', 'Syntax error in command: %s' % err.msg)
        #         self.commandInput.setCursorPosition(err.offset)
        #         return
        action = 'queue'
        if self.current_status != 'idle':
            qwindow = ScriptExecQuestion()
            result = qwindow.exec_()
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Apply:
                action = 'execute'
        if action == 'queue':
            self.mainwindow.action_start_time = time.time()
            self.client.tell('queue', '', script)
        else:
            self.client.tell('exec', script)
        self.commandInput.setText('')
