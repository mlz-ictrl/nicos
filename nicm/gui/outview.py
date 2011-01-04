#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   A text control to display output
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""A text control to display output."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import re
import time
from logging import DEBUG, INFO, WARNING, ERROR, FATAL

from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, QRegExp

from nicm.gui.util import dialogFromUi


# additional levels used by nicm

OUTPUT = INFO + 5
INPUT  = INFO + 6

levels = {DEBUG: 'DEBUG', INFO: 'INFO', WARNING: 'WARNING',
          ERROR: 'ERROR', FATAL: 'FATAL'}

# text formats for the output view

std = QTextCharFormat()

grey = QTextCharFormat()
grey.setForeground(QBrush(QColor('grey')))

red = QTextCharFormat()
red.setForeground(QBrush(QColor('red')))

bold = QTextCharFormat()
bold.setFontWeight(QFont.Bold)

redbold = QTextCharFormat()
redbold.setForeground(QBrush(QColor('red')))
redbold.setFontWeight(QFont.Bold)

# REs for hyperlinks

script_re = re.compile(r'>>> \[.*?\] -{20} (.*?)\n')
command_re = re.compile(r'>>> \[.*?\]  (.*?)\n')

# time formatter

def format_time(timeval):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeval))


class OutputView(QTextBrowser):

    def __init__(self, parent):
        QTextBrowser.__init__(self, parent)
        self._messages = []
        self._inview = False
        self._errview = None
        self.openErrorWindow()

    def openErrorWindow(self):
        dlg = dialogFromUi(self.parent(), 'errwin.ui')
        self._errview = dlg.outView
        dlg.show()

    def clear(self):
        QTextBrowser.clear(self)
        self._messages = []
        self._inview = False

    def scrollToBottom(self):
        bar = self.verticalScrollBar()
        bar.setValue(bar.maximum())

    def formatMessage(self, message):
        # message is a sequence: (logger, time, levelno, message, exc_text)
        fmt = None
        levelno = message[2]
        if message[0] == 'nicos':
            name = ''
        else:
            name = message[0] + ': '
        if levelno <= DEBUG:
            text = name + message[3]
            fmt = grey
        elif levelno <= OUTPUT:
            text = name + message[3]
        elif levelno == INPUT:
            m = script_re.match(message[3])
            if m:
                fmt = QTextCharFormat()
                fmt.setAnchor(True)
                fmt.setAnchorHref('edit:' + m.group(1))
                fmt.setFontWeight(QFont.Bold)
                return message[3], fmt
            m = command_re.match(message[3])
            if m:
                fmt = QTextCharFormat()
                fmt.setAnchor(True)
                fmt.setAnchorHref('exec:' + m.group(1))
                fmt.setFontWeight(QFont.Bold)
                return message[3], fmt
            return message[3], bold
        elif levelno <= WARNING:
            text = levels[levelno] + ': ' + name + message[3]
            fmt = red
        else:
            text = '%s [%s] %s%s' % (levels[levelno], format_time(message[1]),
                                    name, message[3])
            fmt = redbold
        if message[4]:
            # don't show traceback info by default, but on click
            fmt.setAnchor(True)
            fmt.setAnchorHref('trace:' + message[4])

        # XXX very crude error view window for demonstration
        if levelno >= WARNING and self._errview:
            tc = self._errview.textCursor()
            tc.movePosition(QTextCursor.End)
            tc.setCharFormat(fmt or std)
            tc.insertText(text)
            bar = self._errview.verticalScrollBar()
            bar.setValue(bar.maximum())
        return text, fmt

    def addText(self, text, fmt=None):
        textcursor = self.textCursor()
        textcursor.movePosition(QTextCursor.End)
        textcursor.setCharFormat(fmt or std)
        textcursor.insertText(text)

    def addMessage(self, message):
        bar = self.verticalScrollBar()
        prevmax = bar.maximum()
        prevval = bar.value()

        text, fmt = self.formatMessage(message)
        self.addText(text, fmt)
        self._messages.append(message)

        # only scroll to bottom if we were there already
        if prevval >= prevmax - 5:
            self.scrollToBottom()

    def addMessages(self, messages):
        textcursor = self.textCursor()
        textcursor.movePosition(QTextCursor.End)
        format = self.formatMessage
        # insert text with the same format in one batch; this can save
        # quite a lot of time with text mainly in one format (info)
        lastfmt = None
        lasttext = ''
        for message in messages:
            text, fmt = format(message)
            if fmt is lastfmt:
                lasttext += text
            else:
                textcursor.setCharFormat(lastfmt or std)
                textcursor.insertText(lasttext)
                lastfmt = fmt
                lasttext = text
            self._messages.append(message)
        textcursor.setCharFormat(lastfmt or std)
        textcursor.insertText(lasttext)

    def getOutputString(self):
        return self.toPlainText()

    def findNext(self, what, regex=False):
        self.viewAll()
        cursor = self.textCursor()
        if regex:
            rx = QRegExp(what, Qt.CaseInsensitive)
            newcurs = self.document().find(rx, cursor)
        else:
            newcurs = self.document().find(what, cursor)
        self.setTextCursor(newcurs)

    # XXX needs to be fixed

    def viewOnly(self, match):
        newlines = []
        for line in self._lines:
            if match(line):
                newlines.append(line)
        self.setPlainText(''.join(newlines))
        self.scrollToBottom()
        self._inview = True

    def viewAll(self):
        if self._inview:
            self.setPlainText(''.join(self._lines))
            self._inview = False
