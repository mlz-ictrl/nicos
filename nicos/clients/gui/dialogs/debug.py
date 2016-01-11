#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI debug console window."""

import sys
import codeop

# prevent importing the traceback.py from this package
traceback = __import__('traceback')

from PyQt4.QtGui import QMainWindow, QPlainTextEdit, QFont, QTextOption, \
    QTextCursor, QSplitter
from PyQt4.QtCore import Qt, QCoreApplication, SIGNAL

from nicos.protocols.daemon import DAEMON_EVENTS
from nicos.pycompat import exec_, xrange as range  # pylint: disable=W0622


class StdoutProxy(object):
    def __init__(self, write_func):
        self.write_func = write_func
        self.skip = False

    def write(self, text):
        if not self.skip:
            stripped_text = text.rstrip('\n')
            self.write_func(stripped_text)
            QCoreApplication.processEvents()
        self.skip = not self.skip


class ConsoleBox(QPlainTextEdit):
    def __init__(self, ps1='>>> ', ps2='... ', startup_message='', parent=None):
        QPlainTextEdit.__init__(self, parent)
        self.ps1, self.ps2 = ps1, ps2
        self.history = []
        self.namespace = {}
        self.construct = []
        self.compiler = codeop.CommandCompiler()
        self.stdout = StdoutProxy(self.appendPlainText)

        self.setWordWrapMode(QTextOption.WrapAnywhere)
        self.setUndoRedoEnabled(False)
        self.document().setDefaultFont(QFont("monospace", 10, QFont.Normal))
        self.showMessage(startup_message)

    def showMessage(self, message):
        oldcommand = self.getCommand()
        self.appendPlainText(message)
        self.newPrompt()
        if oldcommand:
            self.setCommand(oldcommand)

    def newPrompt(self):
        if self.construct:
            prompt = self.ps2
        else:
            prompt = self.ps1
        self.appendPlainText(prompt)
        self.moveCursor(QTextCursor.End)

    def getCommand(self):
        doc = self.document()
        curr_line = doc.findBlockByLineNumber(doc.lineCount() - 1).text()
        return curr_line[len(self.ps1):]

    def setCommand(self, command):
        if self.getCommand() == command:
            return
        self.moveCursor(QTextCursor.End)
        self.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        for _ in range(len(self.ps1)):
            self.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)
        self.textCursor().removeSelectedText()
        self.textCursor().insertText(command)
        self.moveCursor(QTextCursor.End)

    def getConstruct(self, command):
        res = self.compiler('\n'.join(self.construct + [command]),
                            '<interactive>', 'single')
        if res is not None:
            self.construct = []
        else:
            self.construct.append(command)
        return res

    def addToHistory(self, command):
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.history_index = len(self.history)

    def getPrevHistoryEntry(self):
        if self.history:
            self.history_index = max(0, self.history_index - 1)
            return self.history[self.history_index]
        return ''

    def getNextHistoryEntry(self):
        if self.history:
            hist_len = len(self.history)
            self.history_index = min(hist_len, self.history_index + 1)
            if self.history_index < hist_len:
                return self.history[self.history_index]
        return ''

    def getCursorPosition(self):
        return self.textCursor().columnNumber() - len(self.ps1)

    def setCursorPosition(self, position):
        self.moveCursor(QTextCursor.StartOfLine)
        for _ in range(len(self.ps1) + position):
            self.moveCursor(QTextCursor.Right)

    def runCommand(self):
        command = self.getCommand()
        self.addToHistory(command)

        tmp_stdout = sys.stdout
        sys.stdout = self.stdout
        try:
            command = self.getConstruct(command)
            if not command:
                return
            exec_(command, self.namespace)
        except SystemExit:
            self.emit(SIGNAL('close'))
        except:  # pylint: disable=W0702
            traceback_lines = traceback.format_exc().split('\n')
            # Remove traceback mentioning this file, and a linebreak
            for i in (2, 1, -1):
                traceback_lines.pop(i)
            self.appendPlainText('\n'.join(traceback_lines))
        finally:
            sys.stdout = tmp_stdout
        self.newPrompt()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.runCommand()
            return
        if event.key() == Qt.Key_Home:
            self.setCursorPosition(0)
            return
        if event.key() == Qt.Key_PageUp:
            return
        elif event.key() in (Qt.Key_Left, Qt.Key_Backspace):
            if self.getCursorPosition() == 0:
                return
        elif event.key() == Qt.Key_Up:
            self.setCommand(self.getPrevHistoryEntry())
            return
        elif event.key() == Qt.Key_Down:
            self.setCommand(self.getNextHistoryEntry())
            return
        elif event.key() == Qt.Key_D and event.modifiers() == Qt.ControlModifier:
            self.emit(SIGNAL('close'))
        super(ConsoleBox, self).keyPressEvent(event)


class DebugConsole(QMainWindow):

    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.resize(800, 500)
        self.setWindowTitle('Debug console')

        self.console = ConsoleBox(parent=self, startup_message='-' * 80 + '''
NICOS GUI debug console
Objects in the namespace:
  app             Qt application object
  main            Main window instance
  client          Client connection object
Helper functions:
  watch(*events)  Install a handler for daemon events (all if no arguments)
                  that prints them to this console
''' + '-' * 80)
        self.outbox = QPlainTextEdit(self)
        self.outbox.document().setDefaultFont(
            self.console.document().defaultFont())
        self.mainwidget = QSplitter(Qt.Vertical, self)
        self.mainwidget.addWidget(self.console)
        self.mainwidget.addWidget(self.outbox)
        self.setCentralWidget(self.mainwidget)
        self.connect(self.console, SIGNAL('close'), self.close)

        self.console.namespace.update(dict(
            app    = QCoreApplication.instance(),
            main   = parent,
            client = parent.client,
            watch  = self.install_handlers,
        ))

    def install_handlers(self, *events):
        def make_handler(event):
            def handler(*args):
                self.on_client_signal(event, args)
            return handler
        if not events:
            events = DAEMON_EVENTS.keys()
        for event in events:
            self.connect(self.parent().client, SIGNAL(event),
                         make_handler(event))

    def addLogMsg(self, msg):
        self.outbox.appendPlainText(msg)

    def on_client_signal(self, name, args):
        self.outbox.appendPlainText('event: %s %r' % (name, args))
