#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI user editor window."""

from __future__ import with_statement

__version__ = "$Revision$"

import sys
import time
import subprocess
from os import path
from logging import WARNING

from PyQt4.QtCore import pyqtSignature as qtsig, SIGNAL, Qt, QVariant, \
     QStringList, QFileSystemWatcher
from PyQt4.QtGui import QDialog, QPlainTextEdit, QHeaderView, QHBoxLayout, \
     QTreeWidgetItem, QMessageBox, QTextCursor, QTextDocument, QPen, QColor, \
     QFont, QAction, QPrintDialog, QPrinter, QFileDialog, QMenu, QToolBar, \
     QFileSystemModel

try:
    from PyQt4.Qsci import QsciScintilla, QsciLexerPython, QsciPrinter
except (ImportError, RuntimeError):
    has_scintilla = False
else:
    has_scintilla = True

from nicos.gui.panels import Panel
from nicos.gui.utils import showToolText, loadUi, showTraceback, \
     formatDuration, formatEndtime, setBackgroundColor, importString

COMMENT_STR = '##'


class QScintillaCompatible(QPlainTextEdit):
    """
    Wrapper that lets us use the same methods on the editor as for the
    QScintilla control.
    """
    def __init__(self, parent):
        QPlainTextEdit.__init__(self, parent)
        self.findtext  = ''
        self.findflags = 0

    def text(self):
        return self.toPlainText()

    def setText(self, text):
        self.setPlainText(text)

    def append(self, text):
        self.appendPlainText(text)

    def setCursorPosition(self, line, column):
        cursor = self.textCursor()
        cursor.move(QTextCursor.Start)
        cursor.move(QTextCursor.Down, QTextCursor.MoveAnchor, line)
        cursor.move(QTextCursor.Right, QTextCursor.MoveAnchor, column)
        self.setTextCursor(cursor)

    def findFirst(self, text, regexp, case, wholeword, wrap, forward=True):
        flags = QTextDocument.FindFlag()
        if not forward:
            flags |= QTextDocument.FindBackward
        if wholeword:
            flags |= QTextDocument.FindWholeWords
        if case:
            flags |= QTextDocument.FindCaseSensitively
        self.findtext = text
        self.findflags = flags
        return self.find(text, flags)

    def findNext(self):
        return self.find(self.findtext, self.findflags)

    def replace(self, text):
        self.insertPlainText(text)

    def setModified(self, modified):
        self.document().setModified(modified)

    def isModified(self):
        return self.document().isModified()

    def markerAdd(self, line, marker):
        pass

    def markerDeleteAll(self):
        pass


if has_scintilla:
    class Printer(QsciPrinter):
        """
        Class extending the default QsciPrinter with a header.
        """
        def formatPage(self, painter, drawing, area, pagenr):
            QsciPrinter.formatPage(self, painter, drawing, area, pagenr)

            fn = self.docName()
            header = 'File: %s    page %s    %s' % \
                     (fn, pagenr, time.strftime('%Y-%m-%d %H:%M'))
            painter.save()
            pen = QPen(QColor(30, 30, 30))
            pen.setWidth(1)
            painter.setPen(pen)
            newTop = area.top() + painter.fontMetrics().height() + 15
            area.setLeft(area.left() + 30)
            if drawing:
                painter.drawText(area.left(),
                                 area.top() + painter.fontMetrics().ascent(),
                                 header)
                painter.drawLine(area.left() - 2, newTop - 12,
                                 area.right() + 2, newTop - 12)
            area.setTop(newTop)
            painter.restore()


class EditorPanel(Panel):
    panelName = 'User editor'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'editor.ui', 'panels')

        self.window = parent

        if has_scintilla:
            self.editor = QsciScintilla(self)
            self.lexer = QsciLexerPython(self.editor)
            self.editor.setUtf8(True)
            self.editor.setLexer(self.lexer)
            self.editor.setAutoIndent(True)
            self.editor.setEolMode(QsciScintilla.EolUnix)
            self.editor.setIndentationsUseTabs(False)
            self.editor.setIndentationGuides(True)
            self.editor.setTabIndents(True)
            self.editor.setBackspaceUnindents(True)
            self.editor.setTabWidth(4)
            self.editor.setIndentationWidth(0)
            self.editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)
            self.editor.setFolding(QsciScintilla.PlainFoldStyle)
            self.editor.setIndentationGuidesForegroundColor(QColor("#CCC"))
            self.editor.setWrapMode(QsciScintilla.WrapCharacter)
            # markers for errors/problems (higher numbers have precedence)
            self.editor.markerDefine(QsciScintilla.RightTriangle, 1)
            self.editor.setMarkerBackgroundColor(QColor("yellow"), 1)
            self.editor.markerDefine(QsciScintilla.Circle, 2)
            self.editor.setMarkerBackgroundColor(QColor("red"), 2)
        else:
            self.editor = QScintillaCompatible(self)
            self.lexer = None
            self.actionComment.setEnabled(False)
            self.actionUncomment.setEnabled(False)

        self.current_status = None
        self.recentf_actions = []
        self.filename = ''
        self.setFilename('', force=True)
        self.window.setWindowTitle('New[*] - %s editor' %
                                   self.mainwindow.instrument)
        self.window.setWindowModified(False)
        self.searchdlg = None
        self.menuRecent = QMenu('Recent files')

        for fn in self.recentf:
            action = QAction(fn, self)
            self.connect(action, SIGNAL('triggered()'), self.openRecentFile)
            self.recentf_actions.append(action)
            self.menuRecent.addAction(action)

        hlayout = QHBoxLayout(self)
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(self.editor)
        self.mainFrame.setLayout(hlayout)
        self.editor.setFrameStyle(0)

        self.fileSystemWatcher = QFileSystemWatcher(self)
        self.connect(self.fileSystemWatcher,
                     SIGNAL('fileChanged(const QString &)'),
                     self.on_fileSystemWatcher_fileChanged)
        self.saving = False  # True while saving
        self.warnWidget.hide()

        self.simRanges.header().setResizeMode(QHeaderView.ResizeToContents)
        self.simPane.hide()

        self.splitter.restoreState(self.splitterstate)
        self.treeModel = QFileSystemModel()
        idx = self.treeModel.setRootPath('/')
        self.treeModel.setNameFilters(['*.py'])
        self.treeModel.setNameFilterDisables(False)  # hide them
        self.fileTree.setModel(self.treeModel)
        self.fileTree.header().hideSection(1)
        self.fileTree.header().hideSection(2)
        self.fileTree.header().hideSection(3)
        self.fileTree.header().hide()
        self.fileTree.setRootIndex(idx)
        self.actionShowScripts.setChecked(True)

        self.connect(self.actionUndo, SIGNAL('triggered()'), self.editor.undo)
        self.connect(self.actionRedo, SIGNAL('triggered()'), self.editor.redo)
        self.connect(self.actionCut, SIGNAL('triggered()'), self.editor.cut)
        self.connect(self.actionCopy, SIGNAL('triggered()'), self.editor.copy)
        self.connect(self.actionPaste, SIGNAL('triggered()'), self.editor.paste)
        self.connect(self.editor, SIGNAL('modificationChanged(bool)'),
                     self.setDirty)

        self.waiting_sim_result = False
        self.connect(self.client, SIGNAL('message'), self.on_client_message)
        self.connect(self.client, SIGNAL('simresult'), self.on_client_simresult)
        if self.client.connected:
            self.on_client_connected()
        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)
        self.connect(self.client, SIGNAL('cache'), self.on_client_cache)

    def setSettings(self, settings):
        self.toolconfig = settings.get('tools', '')

    def getMenus(self):
        menuFile = QMenu('&File', self)
        menuFile.addAction(self.actionNew)
        menuFile.addAction(self.actionOpen)
        menuFile.addAction(self.menuRecent.menuAction())
        menuFile.addAction(self.actionSave)
        menuFile.addAction(self.actionSaveAs)
        menuFile.addAction(self.actionReload)
        menuFile.addAction(self.actionShowScripts)
        menuFile.addSeparator()
        menuFile.addAction(self.actionPrint)

        menuEdit = QMenu('&Edit', self)
        menuEdit.addAction(self.actionUndo)
        menuEdit.addAction(self.actionRedo)
        menuEdit.addSeparator()
        menuEdit.addAction(self.actionCut)
        menuEdit.addAction(self.actionCopy)
        menuEdit.addAction(self.actionPaste)
        menuEdit.addSeparator()
        menuEdit.addAction(self.actionComment)
        menuEdit.addAction(self.actionUncomment)
        menuEdit.addSeparator()
        menuEdit.addAction(self.actionFind)

        menuScript = QMenu('&Script', self)
        menuScript.addSeparator()
        menuScript.addAction(self.actionRun)
        menuScript.addAction(self.actionSimulate)
        menuScript.addAction(self.actionUpdate)
        menuScript.addSeparator()
        menuScript.addAction(self.actionGet)

        ret = [menuFile, menuEdit, menuScript]
        if self.toolconfig:
            menuTools = QMenu('&Tools', self)
            for i, tconfig in enumerate(self.toolconfig):
                action = QAction(tconfig[0], self)
                menuTools.addAction(action)
                def tool_callback(on, i=i):
                    self.runTool(i)
                self.connect(action, SIGNAL('triggered(bool)'), tool_callback)
            ret.append(menuTools)

        return ret

    def runTool(self, ttype):
        tconfig = self.toolconfig[ttype]
        try:
            # either it's a class name
            toolclass = importString(tconfig[1])
        except ImportError:
            raise
            # or it's a system command
            subprocess.Popen(tconfig[1], shell=True)
        else:
            dialog = toolclass(self, **tconfig[2])
            self.connect(dialog, SIGNAL('addCode'), self.editor.append)
            dialog.setWindowModality(Qt.NonModal)
            dialog.show()

    def getToolbars(self):
        bar = QToolBar('Editor')
        bar.addAction(self.actionNew)
        bar.addAction(self.actionOpen)
        bar.addAction(self.actionSave)
        bar.addSeparator()
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionUndo)
        bar.addAction(self.actionRedo)
        bar.addSeparator()
        bar.addAction(self.actionCut)
        bar.addAction(self.actionCopy)
        bar.addAction(self.actionPaste)
        bar.addSeparator()
        bar.addAction(self.actionRun)
        bar.addAction(self.actionSimulate)
        bar.addAction(self.actionGet)
        bar.addAction(self.actionUpdate)
        showToolText(bar, self.actionRun)
        showToolText(bar, self.actionSimulate)
        showToolText(bar, self.actionGet)
        showToolText(bar, self.actionUpdate)
        return [bar]

    def updateStatus(self, status, exception=False):
        self.current_status = status

    def setCustomStyle(self, font, back):
        if has_scintilla:
            self.lexer.setDefaultFont(font)
            for i in range(16):
                self.lexer.setFont(font, i)
            # make keywords bold
            bold = QFont(font)
            bold.setBold(True)
            self.lexer.setFont(bold, 5)
        else:
            self.editor.setFont(font)
        self.simOutView.setFont(font)
        self.simOutViewErrors.setFont(font)
        if has_scintilla:
            self.lexer.setPaper(back)
        else:
            setBackgroundColor(self.editor, back)

    def setDirty(self, dirty):
        self.actionSave.setEnabled(dirty)
        self.actionUndo.setEnabled(dirty)
        self.window.setWindowModified(dirty)

    def loadSettings(self, settings):
        self.recentf = list(settings.value('recentf').toStringList())
        self.splitterstate = settings.value('splitter').toByteArray()

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())

    def requestClose(self):
        return self.checkDirty()

    def on_client_connected(self):
        initialdir = self.client.eval('session.experiment.scriptdir', '')
        if initialdir:
            idx = self.treeModel.setRootPath(initialdir)
            self.fileTree.setRootIndex(idx)

    def on_client_cache(self, (time, key, op, value)):
        if key.endswith('/scriptdir'):
            self.on_client_connected()

    def on_client_message(self, message):
        if message[-1] != '(sim) ':
            return
        if self.waiting_sim_result:
            self.simOutView.addMessage(message)
            if message[2] >= WARNING:
                self.simOutViewErrors.addMessage(message)

    def on_client_simresult(self, (timing, devinfo)):
        if not self.waiting_sim_result:
            return
        self.waiting_sim_result = False

        # show timing
        self.simTotalTime.setText(formatDuration(timing))
        self.simFinished.setText(formatEndtime(timing))

        # device ranges
        for devname, (_, dmin, dmax) in devinfo.iteritems():
            if dmin is not None:
                item = QTreeWidgetItem([devname, dmin, '-', dmax])
                self.simRanges.addTopLevelItem(item)

        self.simPane.show()

    def on_fileTree_doubleClicked(self, idx):
        if not self.checkDirty():
            return
        fpath = str(self.treeModel.filePath(idx))
        self.openFile(fpath)

    def on_actionShowScripts_toggled(self, on):
        if on:
            self.scriptsPane.show()
        else:
            self.scriptsPane.hide()

    def on_scriptsPane_visibilityChanged(self, visible):
        self.actionShowScripts.setChecked(visible)

    @qtsig('')
    def on_actionPrint_triggered(self):
        if has_scintilla:
            printer = Printer()
            printer.setOutputFileName('')
            printer.setDocName(self.filename)
            #printer.setFullPage(True)
            if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
                bgcolor = self.lexer.paper(0)
                # printer prints background color too, so set it to white
                self.lexer.setPaper(Qt.white)
                printer.printRange(self.editor)
                self.lexer.setPaper(bgcolor)
        else:
            printer = QPrinter()
            printer.setOutputFileName('')
            if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
                getattr(self.editor, 'print')(printer)

    def validateScript(self):
        script = str(self.editor.text().toUtf8()) + '\n'
        try:
            compile(script, 'script', 'exec')
        except SyntaxError, err:
            self.showError('Syntax error in script: %s' % err)
            self.editor.setCursorPosition(err.lineno - 1, err.offset)
            return
        return script

    @qtsig('')
    def on_actionRun_triggered(self):
        script = self.validateScript()
        if self.current_status != 'idle':
            if not self.askQuestion('A script is currently running, do you '
                                    'want to queue this script?', True):
                return
        if script is not None:
            self.client.tell('queue', self.filename, script)

    @qtsig('')
    def on_actionSimulate_triggered(self):
        script = self.validateScript()
        if script is None:
            return
        self.client.tell('simulate', self.filename, script)
        self.waiting_sim_result = True
        self.clearSimPane()
        self.simPane.show()

    @qtsig('')
    def on_actionUpdate_triggered(self):
        script = self.validateScript()
        if script is not None:
            self.client.tell('update', script)

    @qtsig('')
    def on_actionGet_triggered(self):
        if not self.checkDirty():
            return
        self.editor.setText(self.client.ask('getscript'))

    def clearSimPane(self):
        self.simOutView.clear()
        self.simOutViewErrors.clear()
        self.simRanges.clear()
        self.simTotalTime.setText('')
        self.simFinished.setText('')

    def on_simPane_visibilityChanged(self, visible):
        if not visible:
            self.editor.markerDeleteAll()

    def on_simErrorsOnly_toggled(self, on):
        self.simOutStack.setCurrentIndex(on)

    def checkDirty(self):
        if not self.editor.isModified():
            return True
        if self.filename:
            message = 'Save changes in %s before continuing?' % self.filename
        else:
            message = 'Save new file before continuing?'
        rc = QMessageBox.question(
            self, 'User Editor', message,
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if rc == QMessageBox.Save:
            return self.on_actionSave_triggered()
        elif rc == QMessageBox.Discard:
            return True
        else:
            return False

    def setFilename(self, newfn, force=False):
        oldfn = self.filename
        self.filename = newfn
        if oldfn == newfn and not force:
            return
        if oldfn:
            self.fileSystemWatcher.removePath(oldfn)
        if newfn:
            self.actionReload.setEnabled(True)
            self.fileSystemWatcher.addPath(newfn)
            self.window.setWindowTitle('%s[*] - %s editor' %
                                       (newfn, self.mainwindow.instrument))
        else:
            self.actionReload.setEnabled(False)
            self.window.setWindowTitle('New[*] - %s editor' %
                                       self.mainwindow.instrument)

    def on_fileSystemWatcher_fileChanged(self, filename):
        if self.saving:
            return
        if self.editor.isModified():
            # warn the user
            self.warnText.setText(
                'The file has changed on disk, but has also been edited'
                ' here.\nPlease use either File-Reload to load the'
                ' version on disk or File-Save to save this version.')
            self.warnWidget.show()
        else:
            # reload without asking
            self.openFile(self.filename)
        # re-add the filename to the watcher if it was deleted
        # (happens for programs that do delete-write on save)
        if self.fileSystemWatcher.files().isEmpty():
            self.fileSystemWatcher.addPath(self.filename)

    @qtsig('')
    def on_actionNew_triggered(self):
        if not self.checkDirty():
            return
        self.editor.clear()
        self.editor.setModified(False)
        self.setFilename('')
        self.clearSimPane()

    @qtsig('')
    def on_actionOpen_triggered(self):
        if not self.checkDirty():
            return
        if not self.filename:
            initialdir = self.client.eval('session.experiment.scriptdir', '')
        else:
            initialdir = path.dirname(self.filename)
        fn = QFileDialog.getOpenFileName(self, 'Open script', initialdir,
                                         'Script files (*.py)')
        if fn.isEmpty():
            return
        self.openFile(unicode(fn).encode(sys.getfilesystemencoding()))
        self.addToRecentf(fn)

    @qtsig('')
    def on_actionReload_triggered(self):
        if not self.checkDirty():
            return
        self.openFile(self.filename)

    def openRecentFile(self):
        fn = unicode(self.sender().text()).encode(sys.getfilesystemencoding())
        self.openFile(fn)

    def openFile(self, fn):
        try:
            with open(fn) as f:
                self.editor.setText(f.read().decode('utf8'))
        except Exception, err:
            return self.showError('Opening file failed: %s' % err)

        self.editor.setModified(False)
        self.setFilename(fn)
        self.clearSimPane()

    def addToRecentf(self, fn):
        new_action = QAction(fn, self)
        self.connect(new_action, SIGNAL('triggered()'), self.openRecentFile)
        if self.recentf_actions:
            self.menuRecent.insertAction(self.recentf_actions[0], new_action)
            self.recentf_actions.insert(0, new_action)
            del self.recentf_actions[10:]
        else:
            self.menuRecent.addAction(new_action)
            self.recentf_actions.append(new_action)
        with self.sgroup as settings:
            settings.setValue('recentf', QVariant(QStringList(
                [a.text() for a in self.recentf_actions])))

    @qtsig('')
    def on_actionSave_triggered(self):
        if not self.filename:
            return self.on_actionSaveAs_triggered()

        try:
            self.saving = True
            try:
                with open(self.filename, 'w') as f:
                    f.write(str(self.editor.text().toUtf8()))
            finally:
                self.saving = False
        except Exception, err:
            self.showError('Writing file failed: %s' % err)
            return False

        self.editor.setModified(False)
        self.setFilename(self.filename)  # now add to file system watcher
        return True

    @qtsig('')
    def on_actionSaveAs_triggered(self):
        if self.filename:
            initialdir = path.dirname(self.filename)
        else:
            initialdir = self.client.eval('session.experiment.scriptdir', '')
        fn = QFileDialog.getSaveFileName(self, 'Save script', initialdir,
                                         'Script files (*.py)')
        fn = unicode(fn).encode(sys.getfilesystemencoding())
        if fn == '':
            return False
        if '.' not in fn:
            fn += '.py'
        self.setFilename(fn)
        self.addToRecentf(fn)
        return self.on_actionSave_triggered()

    @qtsig('')
    def on_actionFind_triggered(self):
        if not self.searchdlg:
            self.searchdlg = SearchDialog(self, self.editor)
        self.searchdlg.found = False
        self.searchdlg.show()

    @qtsig('')
    def on_actionComment_triggered(self):
        if self.editor.hasSelectedText():
            # comment selection

            # get the selection boundaries
            lineFrom, _, lineTo, indexTo = self.editor.getSelection()
            if indexTo == 0:
                endLine = lineTo - 1
            else:
                endLine = lineTo

            self.editor.beginUndoAction()
            # iterate over the lines
            for line in range(lineFrom, endLine+1):
                self.editor.insertAt(COMMENT_STR, line, 0)
            # change the selection accordingly
            self.editor.setSelection(lineFrom, 0, endLine+1, 0)
            self.editor.endUndoAction()
        else:
            # comment line
            line, _ = self.editor.getCursorPosition()
            self.editor.beginUndoAction()
            self.editor.insertAt(COMMENT_STR, line, 0)
            self.editor.endUndoAction()

    @qtsig('')
    def on_actionUncomment_triggered(self):
        if self.editor.hasSelectedText():
            # uncomment selection

            # get the selection boundaries
            lineFrom, indexFrom, lineTo, indexTo = self.editor.getSelection()
            if indexTo == 0:
                endLine = lineTo - 1
            else:
                endLine = lineTo

            self.editor.beginUndoAction()
            # iterate over the lines
            for line in range(lineFrom, endLine+1):
                # check if line starts with our comment string (i.e. was commented
                # by our comment...() slots
                if not self.editor.text(line).startsWith(COMMENT_STR):
                    continue

                self.editor.setSelection(line, 0, line, len(COMMENT_STR))
                self.editor.removeSelectedText()

                # adjust selection start
                if line == lineFrom:
                    indexFrom -= len(COMMENT_STR)
                    if indexFrom < 0:
                        indexFrom = 0

                # adjust selection end
                if line == lineTo:
                    indexTo -= len(COMMENT_STR)
                    if indexTo < 0:
                        indexTo = 0

            # change the selection accordingly
            self.editor.setSelection(lineFrom, indexFrom, lineTo, indexTo)
            self.editor.endUndoAction()
        else:
            # uncomment line
            line, _ = self.editor.getCursorPosition()

            # check if line starts with our comment string (i.e. was commented
            # by our comment...() slots
            if not self.editor.text(line).startsWith(COMMENT_STR):
                return

            # now remove the comment string
            self.editor.beginUndoAction()
            self.editor.setSelection(line, 0, line, len(COMMENT_STR))
            self.editor.removeSelectedText()
            self.editor.endUndoAction()

    def on_simOutView_anchorClicked(self, url):
        url = str(url.toString())
        if url.startswith('trace:'):
            showTraceback(url[6:], self, self.simOutView)

    def on_simOutViewErrors_anchorClicked(self, url):
        self.on_simOutView_anchorClicked(url)


class SearchDialog(QDialog):
    def __init__(self, parent, editor):
        QDialog.__init__(self, parent)
        loadUi(self, 'search.ui', 'panels')

        self.editor  = editor
        self.found   = False
        self.forward = True

        if not has_scintilla:
            # QPlainTextEdit doesn't support some find flags
            self.regexpCheckBox.setEnabled(False)
            self.wrapCheckBox.setEnabled(False)
            self.wrapCheckBox.setChecked(False)

        for box in [self.regexpCheckBox, self.caseCheckBox, self.wordCheckBox,
                    self.wrapCheckBox]:
            self.connect(box, SIGNAL('toggled(bool)'), self.reset_found)

    @qtsig('')
    def on_findNextButton_clicked(self):
        self.findPrevButton.setDefault(False)
        self.findNextButton.setDefault(True)
        if self.found and self.forward:
            return self.editor.findNext()
        else:
            ret = self.editor.findFirst(
                self.findText.currentText(),
                self.regexpCheckBox.isChecked(),
                self.caseCheckBox.isChecked(),
                self.wordCheckBox.isChecked(),
                self.wrapCheckBox.isChecked())
            self.found = ret
            self.forward = True
            return ret

    @qtsig('')
    def on_findPrevButton_clicked(self):
        self.findNextButton.setDefault(False)
        self.findPrevButton.setDefault(True)
        if self.found and not self.forward:
            return self.editor.findNext()
        else:
            ret = self.editor.findFirst(
                self.findText.currentText(),
                self.regexpCheckBox.isChecked(),
                self.caseCheckBox.isChecked(),
                self.wordCheckBox.isChecked(),
                self.wrapCheckBox.isChecked(),
                False)
            self.found = ret
            self.forward = False
            return ret

    def reset_found(self, *args):
        self.found = False

    @qtsig('')
    def on_replaceButton_clicked(self):
        if not self.found:
            if not self.on_findNextButton_clicked():
                return
        self.editor.replace(self.replaceText.currentText())
        self.on_findNextButton_clicked()

    @qtsig('')
    def on_replaceAllButton_clicked(self):
        if not self.found:
            if not self.on_findNextButton_clicked():
                return
        rtext = self.replaceText.currentText()
        self.editor.replace(rtext)
        while self.on_findNextButton_clicked():
            self.editor.replace(rtext)
