#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""A text control to display logging messages of the daemon."""

import re
from logging import DEBUG, ERROR, FATAL, INFO, WARNING
from time import localtime, strftime

from PyQt4.QtCore import QRect, QRegExp, QSize, Qt
from PyQt4.QtGui import QBrush, QColor, QFont, QMainWindow, QPainter, \
    QPixmap, QTextBrowser, QTextCharFormat, QTextCursor, QTextEdit

from nicos.pycompat import from_maybe_utf8, xrange as range  # pylint: disable=W0622
from nicos.utils.loggers import ACTION, INPUT


levels = {DEBUG: 'DEBUG', INFO: 'INFO', WARNING: 'WARNING',
          ERROR: 'ERROR', FATAL: 'FATAL'}

# text formats for the output view

std = QTextCharFormat()

grey = QTextCharFormat()
grey.setForeground(QBrush(QColor('grey')))

red = QTextCharFormat()
red.setForeground(QBrush(QColor('red')))

magenta = QTextCharFormat()
magenta.setForeground(QBrush(QColor('#C000C0')))

bold = QTextCharFormat()
bold.setFontWeight(QFont.Bold)

redbold = QTextCharFormat()
redbold.setForeground(QBrush(QColor('red')))
redbold.setFontWeight(QFont.Bold)

# REs for hyperlinks

command_re = re.compile(r'>>> \[([^ ]+) .*?\]  (.*?)\n')
script_re = re.compile(r'>>> \[([^ ]+) .*?\] -{20} ?(.*?)\n')
update_re = re.compile(r'UPDATE (?:\(.*?\) )?\[([^ ]+) .*?\] -{20} ?(.*?)\n')


# time formatter

def format_time_full(timeval):
    return strftime('[%Y-%m-%d %H:%M:%S] ', localtime(timeval))


def format_time(timeval):
    return strftime('[%H:%M:%S] ', localtime(timeval))


class MessageView(QTextBrowser):

    def __init__(self, parent):
        QTextBrowser.__init__(self, parent)
        self._messages = []
        self._actionlabel = None
        self._currentuser = None
        self.setFullTimestamps(False)
        self._background_image = None
        self._background_image_area = None

    def setFullTimestamps(self, on):
        if on:
            self.formatTime = format_time_full
            self.formatImportantTime = lambda timeval: ': '
        else:
            self.formatTime = format_time
            self.formatImportantTime = \
                lambda timeval: ' ' + format_time_full(timeval)

    def setActionLabel(self, label):
        self._actionlabel = label

    def clear(self):
        QTextBrowser.clear(self)
        self._messages = []

    def clearAlmostEverything(self):
        # Clears all messages, except the last input command with its output.
        # This is used for clearing output on NewExperiment, because the event
        # that clears the messages arrives *after* the command has run.
        msgs = self._messages[:]
        self.clear()
        i = 0
        for i in range(len(msgs) - 1, -1, -1):
            if msgs[i][2] == INPUT:
                break
        self.addMessages(msgs[i:])

    def scrollToBottom(self):
        bar = self.verticalScrollBar()
        bar.setValue(bar.maximum())

    def getLatest(self, n=5):
        # Return latest n commands together with warning/error output.
        inputcount = 0
        retmsgs = []
        for i in range(len(self._messages) - 1, -1, -1):
            if self._messages[i][2] == INPUT:
                retmsgs.append(self._messages[i])
                inputcount += 1
                if inputcount == n:
                    break
            elif self._messages[i][2] >= WARNING:
                retmsgs.append(self._messages[i])
        return retmsgs[::-1]

    def formatMessage(self, message, actions=True):
        # message is a sequence:
        # (logger, time, levelno, message, exc_text, reqid)
        fmt = None
        levelno = message[2]
        if message[0] == 'nicos':
            name = ''
        else:
            name = '%-10s: ' % message[0]
        if message[5] == '0':  # simulation result started by console
            name = '(sim) ' + name
        if levelno == ACTION:
            if actions and self._actionlabel:
                action = message[3].strip()
                if action:
                    self._actionlabel.setText('Status: ' + action)
                    self._actionlabel.show()
                else:
                    self._actionlabel.hide()
            return '', None
        elif levelno <= DEBUG:
            text = name + message[3]
            fmt = grey
        elif levelno <= INFO:
            if message[3].startswith('  > '):
                fmt = QTextCharFormat(bold)
                fmt.setAnchor(True)
                fmt.setAnchorHref('exec:' + message[3][4:].strip())
                return name + message[3], fmt
            text = name + message[3]
        elif levelno == INPUT:
            m = command_re.match(message[3])
            if m:
                fmt = QTextCharFormat(bold)
                fmt.setAnchor(True)
                fmt.setAnchorHref('exec:' + m.group(2))
                if m.group(1) != self._currentuser:
                    fmt.setForeground(QBrush(QColor('#0000C0')))
                return message[3], fmt
            m = script_re.match(message[3])
            if m:
                fmt = QTextCharFormat(bold)
                if m.group(2):
                    fmt.setAnchor(True)
                    fmt.setAnchorHref('edit:' + m.group(2))
                if m.group(1) != self._currentuser:
                    fmt.setForeground(QBrush(QColor('#0000C0')))
                return message[3], fmt
            m = update_re.match(message[3])
            if m:
                fmt = QTextCharFormat(bold)
                if m.group(2):
                    fmt.setAnchor(True)
                    fmt.setAnchorHref('edit:' + m.group(2))
                if m.group(1) != self._currentuser:
                    fmt.setForeground(QBrush(QColor('#006090')))
                else:
                    fmt.setForeground(QBrush(QColor('#00A000')))
                return message[3], fmt
            return message[3], bold
        elif levelno <= WARNING:
            text = levels[levelno] + ': ' + name + message[3]
            fmt = magenta
        else:
            text = levels[levelno] + self.formatImportantTime(message[1]) + \
                name + message[3]
            fmt = redbold
        if message[4] and fmt:
            # need to construct a new unique object for this
            fmt = QTextCharFormat(fmt)
            # show traceback info on click
            fmt.setAnchor(True)
            fmt.setAnchorHref('trace:' + message[4])
        return text, fmt

    def addText(self, text, fmt=None):
        textcursor = self.textCursor()
        textcursor.movePosition(QTextCursor.End)
        textcursor.setCharFormat(fmt or std)
        textcursor.insertText(from_maybe_utf8(text))

    def addMessage(self, message):
        bar = self.verticalScrollBar()
        prevmax = bar.maximum()
        prevval = bar.value()

        text, fmt = self.formatMessage(message)
        if text:  # not for ACTIONs
            self.addText(self.formatTime(message[1]), grey)
            self.addText(text, fmt)
            self._messages.append(message)

        # only scroll to bottom if we were there already
        if prevval >= prevmax - 5:
            self.scrollToBottom()

    def addMessages(self, messages):
        textcursor = self.textCursor()
        textcursor.movePosition(QTextCursor.End)
        formatter = self.formatMessage
        for message in messages:
            text, fmt = formatter(message, actions=False)
            if text:
                textcursor.setCharFormat(grey)
                textcursor.insertText(self.formatTime(message[1]))
                textcursor.setCharFormat(fmt or std)
                textcursor.insertText(text)
                self._messages.append(message)

    def getOutputString(self):
        return self.toPlainText()

    def findNext(self, what, regex=False):
        cursor = self.textCursor()
        if regex:
            rx = QRegExp(what, Qt.CaseInsensitive)
            newcurs = self.document().find(rx, cursor)
        else:
            newcurs = self.document().find(what, cursor)
        self.setTextCursor(newcurs)
        return not newcurs.isNull()

    def occur(self, what, regex=False):
        content = self.toPlainText().split('\n')
        if regex:
            regexp = QRegExp(what, Qt.CaseInsensitive)
            content = [line for line in content if regexp.indexIn(line) >= 0]
        else:
            what = what.lower()
            content = [line for line in content if what in line.lower()]
        content = '\n'.join(content)
        window = QMainWindow(self)
        window.resize(600, 800)
        window.setWindowTitle('Lines matching %r' % what)
        widget = QTextEdit(window)
        widget.setFont(self.font())
        window.setCentralWidget(widget)
        widget.setText(content)
        window.show()

    def setBackgroundImage(self, filepath):
        self._background_image = QPixmap(filepath)
        self.recalculateBackgroundArea()

    def recalculateBackgroundArea(self):
        if self._background_image is None:
            return
        # recalculate the rect to draw the background image into
        size = self._background_image.size()

        # scale to viewport size and add some margin
        size.scale(self.viewport().size() - QSize(30, 30), Qt.KeepAspectRatio)

        # center background image
        p = (self.viewport().size() - size) / 2

        self._background_image_area = QRect(p.width(), p.height(),
                                            size.width(), size.height())

    def scrollContentsBy(self, x, y):
        QTextBrowser.scrollContentsBy(self, x, y)
        if self._background_image:
            # repaint viewport on scoll to preserve the background image.
            # Using 'update' to let qt optimize the process (speed/flickering)
            self.viewport().update()

    def resizeEvent(self, ev):
        # recalculate the background area only if necessary
        self.recalculateBackgroundArea()
        QTextBrowser.resizeEvent(self, ev)

    def paintEvent(self, ev):
        if self._background_image:
            # draw background image if any (should be mostly transparent!)
            painter = QPainter()
            painter.begin(self.viewport())
            painter.drawPixmap(self._background_image_area,
                               self._background_image)
            painter.end()
        QTextBrowser.paintEvent(self, ev)
