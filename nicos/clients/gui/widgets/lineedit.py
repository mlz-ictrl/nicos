#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""A line editor control with history stepping."""

import re

from nicos.guisupport.qt import pyqtSignal, Qt, QEvent, QRegExp, QColor, \
    QApplication, QCompleter, QKeyEvent, QLineEdit, QMessageBox, QPalette, \
    QStringListModel, QRegExpValidator

from nicos.clients.gui.utils import ScriptExecQuestion
from nicos.guisupport.utils import setBackgroundColor, setForegroundColor
from nicos.pycompat import xrange as range  # pylint: disable=W0622


wordsplit_re = re.compile(r'[ \t\n\"\\\'`@$><=;|&{(\[]')


class HistoryLineEdit(QLineEdit):
    """
    A line edit with history stepping.
    """

    escapePressed = pyqtSignal()

    scrollingKeys = [Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown]

    def __init__(self, parent, history=None):
        QLineEdit.__init__(self, parent)
        self.run_color = QColor('#ffdddd')
        self.idle_color = self.palette().color(QPalette.Base)
        self.active_fgcolor = QColor('#000000')
        self.inactive_fgcolor = QColor('#c9c9c9')
        self.error_fgcolor = QColor("#ff0000")
        self.history = history or []
        self.scrollWidget = None
        self.completion_callback = lambda text: []
        self._start_text = ''
        self._current = -1
        self._completer = QCompleter([], self)
        self.setCompleter(self._completer)

    def event(self, event):
        # need to reimplement the general event handler to enable catching Tab
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            fullstring = self.text()
            lastword = wordsplit_re.split(fullstring)[-1]
            # pylint: disable=E1121
            matches = self.completion_callback(fullstring, lastword)
            if matches is None:
                return True
            if lastword:
                startstring = fullstring[:-len(lastword)]
            else:
                startstring = fullstring
            fullmatches = [startstring + m for m in matches]
            if len(fullmatches) == 1:
                self.setText(fullmatches[0])
            else:
                self._completer.setModel(QStringListModel(fullmatches, self))
                self._completer.complete()
            return True
        return QLineEdit.event(self, event)

    def keyPressEvent(self, kev):
        key_code = kev.key()

        # if it's a shifted scroll key...
        if kev.modifiers() & Qt.ShiftModifier and \
                self.scrollWidget and \
                key_code in self.scrollingKeys:
            # create a new, unshifted key event and send it to the
            # scrolling widget
            nev = QKeyEvent(kev.type(), kev.key(), Qt.NoModifier)
            QApplication.sendEvent(self.scrollWidget, nev)
            return

        if key_code == Qt.Key_Escape:
            # abort history search
            self.setText(self._start_text)
            self._current = -1
            self.escapePressed.emit()
            QLineEdit.keyPressEvent(self, kev)

        elif key_code == Qt.Key_Up:
            # go earlier
            if self._current == -1:
                self._start_text = self.text()
                self._current = len(self.history)
            self.stepHistory(-1)
        elif key_code == Qt.Key_Down:
            # go later
            if self._current == -1:
                return
            self.stepHistory(1)

        elif key_code == Qt.Key_PageUp:
            # go earlier with prefix
            if self._current == -1:
                self._current = len(self.history)
                self._start_text = self.text()
            prefix = self.text()[:self.cursorPosition()]
            self.stepHistoryUntil(prefix, 'up')

        elif key_code == Qt.Key_PageDown:
            # go later with prefix
            if self._current == -1:
                return
            prefix = self.text()[:self.cursorPosition()]
            self.stepHistoryUntil(prefix, 'down')

        elif key_code == Qt.Key_Return or key_code == Qt.Key_Enter:
            # accept - add to history and do normal processing
            self._current = -1
            text = self.text()
            if text and (not self.history or self.history[-1] != text):
                # append to history, but only if it isn't equal to the last
                self.history.append(text)
            self._completer.setCompletionPrefix('')
            self._completer.setModel(QStringListModel([], self))
            QLineEdit.keyPressEvent(self, kev)

        else:
            # process normally
            QLineEdit.keyPressEvent(self, kev)

    def stepHistory(self, num):
        self._current += num
        if self._current <= -1:
            # no further
            self._current = 0
            return
        if self._current >= len(self.history):
            # back to start
            self._current = -1
            self.setText(self._start_text)
            return
        self.setText(self.history[self._current])

    def stepHistoryUntil(self, prefix, direction):
        if direction == 'up':
            lookrange = range(self._current - 1, -1, -1)
        else:
            lookrange = range(self._current + 1, len(self.history))
        for i in lookrange:
            if self.history[i].startswith(prefix):
                self._current = i
                self.setText(self.history[i])
                self.setCursorPosition(len(prefix))
                return
        if direction == 'down':
            # nothing found: go back to start
            self._current = -1
            self.setText(self._start_text)
            self.setCursorPosition(len(prefix))


class CommandLineEdit(HistoryLineEdit):
    """
    A NICOS command input line with history stepping.
    """

    def __init__(self, parent, history=None):
        HistoryLineEdit.__init__(self, parent, history)
        self.textChanged.connect(self.on_textChanged)
        self.returnPressed.connect(self.on_returnPressed)
        self.setValidator(QRegExpValidator(QRegExp(r"^\S.*"), self))
        self.current_status = None
        self.error_status = None

    execRequested = pyqtSignal(str, str)

    def setStatus(self, status):
        """Update with the daemon status."""
        self.current_status = status
        if status != 'idle':
            setBackgroundColor(self, self.run_color)
            if not self.error_status:
                setForegroundColor(self, self.inactive_fgcolor)
        else:
            setBackgroundColor(self, self.idle_color)
            if not self.error_status:
                setForegroundColor(self, self.active_fgcolor)
        self.update()
        self.setEnabled(status != 'disconnected')

    def on_textChanged(self):
        setForegroundColor(self, self.active_fgcolor)
        try:
            script = self.text()
            if not script or script.strip().startswith('#'):
                return
            compile(script + '\n', 'script', 'single')
        except Exception:
            self.error_status = True
            setForegroundColor(self, self.error_fgcolor)
            self.update()
        else:
            self.error_status = False
            setForegroundColor(self, self.active_fgcolor)

    def on_returnPressed(self):
        script = self.text()
        if not script:
            return
        # XXX: this does not apply in SPM mode
        # sscript = script.strip()
        # if not (sscript.startswith(('#', '?', '.', ':')) or sscript.endswith('?')):
        #     try:
        #         compile(script+'\n', 'script', 'single')
        #     except SyntaxError as err:
        #         QMessageBox.information(
        #             self, 'Command', 'Syntax error in command: %s' % err.msg)
        #         self.setCursorPosition(err.offset)
        #         return
        action = 'queue'
        if self.current_status != 'idle':
            qwindow = ScriptExecQuestion()
            result = qwindow.exec_()
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Apply:
                if self.current_status != 'idle':
                    # if still busy try immediate execution, may raise,
                    # else just queue it
                    action = 'execute'
        self.execRequested.emit(script, action)


class ShadowTextLineEdit(QLineEdit):

    def __init__(self, *args):
        QLineEdit.__init__(self, *args)
        self._textcolor = self.palette().color(QPalette.Text)
        self._shadowcolor = self.palette().color(QPalette.Dark)
        self._shadowed = True
        self.setShadowText('')

    def setShadowText(self, text):
        self.shadowText = text
        if self._shadowed:
            self._setShadow()

    def focusInEvent(self, event):
        if self._shadowed:
            self.setText('')
        return QLineEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        if not self.text():
            self._setShadow()
        return QLineEdit.focusOutEvent(self, event)

    def setText(self, text):
        self._shadowed = False
        QLineEdit.setText(self, text)
        setForegroundColor(self, self._textcolor)

    def _setShadow(self):
        self._shadowed = True
        QLineEdit.setText(self, self.shadowText)
        setForegroundColor(self, self._shadowcolor)

    def text(self):
        if self._shadowed:
            return ''
        return QLineEdit.text(self)
