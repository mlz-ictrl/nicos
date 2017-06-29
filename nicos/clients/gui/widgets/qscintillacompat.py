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

"""NICOS GUI user editor qscintilla compat edit widget."""


from PyQt4.QtGui import QPlainTextEdit, QTextCursor, QTextDocument, \
    QColor, QTextEdit, QTextFormat, QPainter, QWidget
from PyQt4.QtCore import Qt, QRect, QSize


class LineNumberArea(QWidget):

    codeEditor = None

    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class QScintillaCompatible(QPlainTextEdit):
    """
    Wrapper that lets us use the same methods on the editor as for the
    QScintilla control.
    """
    lineNumberArea = None

    def __init__(self, parent):
        QPlainTextEdit.__init__(self, parent)
        self.findtext = ''
        self.findflags = 0
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).
                  translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(),
                                 self.fontMetrics().height(), Qt.AlignRight,
                                 number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def resizeEvent(self, event):
        QPlainTextEdit.resizeEvent(self, event)

        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                                              self.lineNumberAreaWidth(),
                                              cr.height()))

    def lineNumberAreaWidth(self):
        return 3 + self.fontMetrics().width(str(max(1, self.blockCount())))

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.yellow).lighter(160)

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(),
                                       self.lineNumberArea.width(),
                                       rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def text(self):
        return self.toPlainText()

    def setText(self, text):
        self.setPlainText(text)

    def append(self, text):
        self.appendPlainText(text)

    def insert(self, text):
        self.insertPlainText(text)

    def moveToEnd(self):
        self.moveCursor(QTextCursor.End)

    def beginUndoAction(self):
        pass

    def endUndoAction(self):
        pass

    def setCursorPosition(self, line, column):
        cursor = self.textCursor()
        cursor.move(QTextCursor.Start)
        cursor.move(QTextCursor.Down, QTextCursor.MoveAnchor, line)
        cursor.move(QTextCursor.Right, QTextCursor.MoveAnchor, column)
        self.setTextCursor(cursor)

    def findFirst(self, text, regexp, case, wholeword, wrap, forward=True,
                  line=None, column=None):
        flags = QTextDocument.FindFlag()
        if not forward:
            flags |= QTextDocument.FindBackward
        if wholeword:
            flags |= QTextDocument.FindWholeWords
        if case:
            flags |= QTextDocument.FindCaseSensitively
        self.findtext = text
        self.findflags = flags
        if line is not None:
            if column is not None:
                self.setCursorPosition(line, column)
            else:
                self.setCursorPosition(line, 0)
        return self.find(text, flags)

    def findNext(self):
        return self.find(self.findtext, self.findflags)

    def replace(self, text):
        self.insertPlainText(text)

    def setModified(self, modified):
        self.document().setModified(modified)

    def isModified(self):
        return self.document().isModified()
