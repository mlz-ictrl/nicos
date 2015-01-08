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

"""A line editor control with history stepping."""

import re

from PyQt4.QtGui import QApplication, QKeyEvent, QLineEdit, QCompleter, \
     QStringListModel
from PyQt4.QtCore import Qt, SIGNAL, QEvent

from nicos.pycompat import xrange as range  # pylint: disable=W0622

wordsplit_re = re.compile(r'[ \t\n\"\\\'`@$><=;|&{(\[]')


class HistoryLineEdit(QLineEdit):
    """
    A line editor with history stepping.
    """
    __pyqtSignals__ = ['escapePressed()']

    scrollingKeys = [Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown]

    def __init__(self, parent, history=None):
        QLineEdit.__init__(self, parent)
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
            self.emit(SIGNAL('escapePressed()'))
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

        elif key_code == Qt.Key_Return:
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
