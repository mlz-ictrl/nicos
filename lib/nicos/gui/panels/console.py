#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

__version__ = "$Revision$"

import re
import time
import codecs

from PyQt4.QtCore import QVariant, QStringList, SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig
from PyQt4.QtGui import QDialog, QFileDialog, QMessageBox, QMenu, \
     QColor, QPrinter, QPrintDialog, QAbstractPrintDialog

from nicos.gui.panels import Panel
from nicos.gui.utils import loadUi, setBackgroundColor, setForegroundColor, \
     chunks, enumerateWithProgress, showTraceback


class ConsolePanel(Panel):
    panelName = 'Console'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'console.ui')

        self.current_status = None
        self.run_color = QColor('#ffdddd')
        self.idle_color = parent.user_color
        self.commandInput.scrollWidget = self.outView
        self.grepPanel.hide()
        self.grepText.scrollWidget = self.outView
        self.actionLabel.hide()
        self.outView.setActionLabel(self.actionLabel)
        if not self.hasinput:
            self.inputFrame.setVisible(False)
        self.commandInput.history = self.cmdhistory

        self.connect(client, SIGNAL('message'), self.on_client_message)
        self.connect(client, SIGNAL('initstatus'), self.on_client_initstatus)

    def loadSettings(self, settings):
        self.hasinput = not settings.value('noinput').toBool()
        self.cmdhistory = map(str, settings.value('cmdhistory').toStringList())

    def saveSettings(self, settings):
        settings.setValue('noinput', not self.hasinput)
        # only save 100 entries of the history
        cmdhistory = self.commandInput.history[-100:]
        settings.setValue('cmdhistory', QVariant(QStringList(cmdhistory)))

    def getMenus(self):
        menu = QMenu('&Output', self)
        menu.addAction(self.actionGrep)
        menu.addSeparator()
        menu.addAction(self.actionSave)
        menu.addAction(self.actionPrint)
        return [menu]

    def setCustomStyle(self, font, back):
        self.idle_color = back
        for widget in (self.outView, self.commandInput):
            widget.setFont(font)
            setBackgroundColor(widget, back)

    def updateStatus(self, status, exception=False):
        self.current_status = status
        if status != 'idle':
            setBackgroundColor(self.commandInput, self.run_color)
        else:
            setBackgroundColor(self.commandInput, self.idle_color)
        self.commandInput.update()
        self.commandInput.setEnabled(status != 'disconnected')

    def on_client_initstatus(self, state):
        messages = state[2]
        self.outView.clear()
        total = len(messages) // 2500 + 1
        for i, batch in enumerateWithProgress(chunks(messages, 2500),
                            text='Synchronizing...', parent=self, total=total):
            self.outView.addMessages(batch)
        self.outView.scrollToBottom()

    def on_client_message(self, message):
        if message[-1] == '(sim) ':
            return
        self.outView.addMessage(message)

    def on_outView_anchorClicked(self, url):
        """Called when the user clicks a link in the out view."""
        url = str(url.toString())
        if url.startswith('exec:'):
            self.client.tell('queue', '', url[5:])
            self.mainwindow.action_start_time = time.time()
        elif url.startswith('edit:'):
            # XXX implement this? (also check if file is already open)
            # editor = self.on_actionUserEditor_triggered()
            # editor.openFile(url[5:])
            pass
        elif url.startswith('trace:'):
            showTraceback(url[6:], self, self.outView)
        else:
            print 'Strange anchor in outView: ' + url

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
        if fn.isEmpty():
            return
        try:
            with codecs.open(str(fn), 'w', 'utf-8') as f:
                f.write(unicode(self.outView.getOutputString()))
        except Exception, err:
            QMessageBox.warning(self, 'Error', 'Writing file failed: %s' % err)

    @qtsig('')
    def on_actionGrep_triggered(self):
        self.grepPanel.setVisible(True)
        self.grepText.setFocus()

    @qtsig('')
    def on_grepClose_clicked(self):
        self.outView.viewAll()
        self.grepPanel.setVisible(False)
        self.commandInput.setFocus()
        self.outView.scrollToBottom()

    def on_grepText_returnPressed(self):
        self.on_grepSearch_clicked()

    def on_grepText_escapePressed(self):
        self.on_grepClose_clicked()

    @qtsig('')
    def on_grepSearch_clicked(self):
        st = str(self.grepText.text())
        if not st:
            return
        if self.grepHideRest.isChecked():
            if self.grepRegex.isChecked():
                try:
                    st = re.compile(st, re.I)
                except Exception:
                    QMessageBox.information(self, 'Error',
                                            'Not a valid regex.')
                    return
                match = st.search
            else:
                match = lambda line: st in line
            self.outView.viewOnly(match)
        else:
            self.outView.findNext(st, self.grepRegex.isChecked())

    @qtsig('bool')
    def on_grepHideRest_clicked(self, ischecked):
        if not ischecked:
            self.outView.viewAll()
        else:
            self.on_grepSearch_clicked()

    def on_commandInput_textChanged(self, text):
        try:
            script = str(self.commandInput.text())
            if not script or script.strip().startswith('#'):
                return
            compile(script+'\n', 'script', 'single')
        except Exception:
            setForegroundColor(self.commandInput, QColor("#ff0000"))
        else:
            setForegroundColor(self.commandInput, QColor("#000000"))

    def on_commandInput_returnPressed(self):
        script = str(self.commandInput.text())
        if not script:
            return
        if not script.strip().startswith('#'):
            try:
                compile(script+'\n', 'script', 'single')
            except SyntaxError, err:
                QMessageBox.information(
                    self, 'Command', 'Syntax error in command: %s' % err.msg)
                self.commandInput.setCursorPosition(err.offset)
                return
        if self.current_status != 'idle':
            if QMessageBox.question(
                self, 'Queue?', 'A script is currently running, do you want '
                'to queue this command?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) \
                == QMessageBox.No:
                return
        self.client.tell('queue', '', script)
        self.mainwindow.action_start_time = time.time()
        self.commandInput.setText('')
