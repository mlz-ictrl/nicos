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
     QFileSystemModel, QTabWidget

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
        self.custom_font = None
        self.custom_back = None

        if not has_scintilla:
            self.actionComment.setEnabled(False)
            self.actionUncomment.setEnabled(False)

        self.current_status = None
        self.recentf_actions = []
        self.searchdlg = None
        self.menuRecent = QMenu('Recent files')

        for fn in self.recentf:
            action = QAction(fn, self)
            self.connect(action, SIGNAL('triggered()'), self.openRecentFile)
            self.recentf_actions.append(action)
            self.menuRecent.addAction(action)

        self.tabber = QTabWidget(self)
        self.tabber.setTabsClosable(True)
        self.tabber.setDocumentMode(True)
        self.connect(self.tabber, SIGNAL('currentChanged(int)'),
                     self.on_tabber_currentChanged)
        self.connect(self.tabber, SIGNAL('tabCloseRequested(int)'),
                     self.on_tabber_tabCloseRequested)

        hlayout = QHBoxLayout(self)
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(self.tabber)
        self.mainFrame.setLayout(hlayout)

        self.editors = []    # tab index -> editor
        self.lexers = {}     # editor -> lexer
        self.filenames = {}  # editor -> filename
        self.watchers = {}   # editor -> QFileSystemWatcher
        self.currentEditor = None

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

        self.waiting_sim_result = False
        self.connect(self.client, SIGNAL('message'), self.on_client_message)
        self.connect(self.client, SIGNAL('simresult'), self.on_client_simresult)
        if self.client.connected:
            self.on_client_connected()
        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)
        self.connect(self.client, SIGNAL('cache'), self.on_client_cache)

        if self.openfiles:
            for fn in self.openfiles:
                self.openFile(str(fn), quiet=True)
        else:
            self.newFile()

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
            self.connect(dialog, SIGNAL('addCode'), self.currentEditor.append)
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
        self.custom_font = font
        self.custom_back = back
        self.simOutView.setFont(font)
        self.simOutViewErrors.setFont(font)
        for editor in self.editors:
            self._updateStyle(editor, self.lexers[editor])

    def _updateStyle(self, editor, lexer):
        if self.custom_font is None:
            return
        bold = QFont(self.custom_font)
        bold.setBold(True)
        if has_scintilla:
            lexer.setDefaultFont(self.custom_font)
            for i in range(16):
                lexer.setFont(self.custom_font, i)
            # make keywords bold
            lexer.setFont(bold, 5)
        else:
            editor.setFont(self.custom_font)
        if has_scintilla:
            lexer.setPaper(self.custom_back)
        else:
            setBackgroundColor(editor, self.custom_back)

    def enableFileActions(self, on):
        for action in [
            self.actionSave, self.actionSaveAs, self.actionReload,
            self.actionPrint, self.actionUndo, self.actionRedo, self.actionCut,
            self.actionCopy, self.actionPaste, self.actionFind, self.actionRun,
            self.actionSimulate, self.actionUpdate
        ]:
            action.setEnabled(on)
        for action in [self.actionComment, self.actionUncomment]:
            action.setEnabled(on and has_scintilla)

    def on_tabber_currentChanged(self, index):
        self.enableFileActions(index >= 0)
        if index == -1:
            self.currentEditor = None
            self.window.setWindowTitle('%s editor' % self.mainwindow.instrument)
            return
        editor = self.editors[index]
        fn = self.filenames[editor]
        if fn:
            self.window.setWindowTitle('%s[*] - %s editor' %
                                       (fn, self.mainwindow.instrument))
        else:
            self.window.setWindowTitle('New[*] - %s editor' %
                                       self.mainwindow.instrument)
        self.window.setWindowModified(editor.isModified())
        self.actionSave.setEnabled(editor.isModified())
        self.actionUndo.setEnabled(editor.isModified())
        self.currentEditor = editor

    def on_tabber_tabCloseRequested(self, index):
        editor = self.editors[index]
        self._close(editor)

    def _close(self, editor):
        if not self.checkDirty(editor):
            return
        index = self.editors.index(editor)
        del self.editors[index]
        del self.lexers[editor]
        del self.filenames[editor]
        del self.watchers[editor]
        self.tabber.removeTab(index)

    def setDirty(self, dirty):
        if self.sender() is self.currentEditor:
            self.actionSave.setEnabled(dirty)
            self.actionUndo.setEnabled(dirty)
            self.window.setWindowModified(dirty)
            index = self.tabber.currentIndex()
            tt = str(self.tabber.tabText(index)).rstrip('*')
            self.tabber.setTabText(index, tt + (dirty and '*' or ''))

    def loadSettings(self, settings):
        self.recentf = list(settings.value('recentf').toStringList())
        self.splitterstate = settings.value('splitter').toByteArray()
        self.openfiles = list(settings.value('openfiles').toStringList())

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.setValue('openfiles', QVariant(QStringList(
            [self.filenames[e] for e in self.editors if self.filenames[e]]
        )))

    def requestClose(self):
        for editor in self.editors:
            if not self.checkDirty(editor):
                return False
        return True

    def createEditor(self):
        if has_scintilla:
            editor = QsciScintilla(self)
            lexer = QsciLexerPython(editor)
            editor.setUtf8(True)
            editor.setLexer(lexer)
            editor.setAutoIndent(True)
            editor.setEolMode(QsciScintilla.EolUnix)
            editor.setIndentationsUseTabs(False)
            editor.setIndentationGuides(True)
            editor.setTabIndents(True)
            editor.setBackspaceUnindents(True)
            editor.setTabWidth(4)
            editor.setIndentationWidth(0)
            editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)
            editor.setFolding(QsciScintilla.PlainFoldStyle)
            editor.setIndentationGuidesForegroundColor(QColor("#CCC"))
            editor.setWrapMode(QsciScintilla.WrapCharacter)
        else:
            editor = QScintillaCompatible(self)
            lexer = None
        editor.setFrameStyle(0)
        self.connect(editor, SIGNAL('modificationChanged(bool)'), self.setDirty)
        self._updateStyle(editor, lexer)
        return editor, lexer

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
        fpath = str(self.treeModel.filePath(idx))
        for i, editor in enumerate(self.editors):
            if self.filenames[editor] == fpath:
                self.tabber.setCurrentIndex(i)
                return
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
            printer.setDocName(self.filenames[self.currentEditor])
            #printer.setFullPage(True)
            if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
                bgcolor = self.lexer.paper(0)
                # printer prints background color too, so set it to white
                self.lexer.setPaper(Qt.white)
                printer.printRange(self.currentEditor)
                self.lexer.setPaper(bgcolor)
        else:
            printer = QPrinter()
            printer.setOutputFileName('')
            if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
                getattr(self.currentEditor, 'print')(printer)

    def validateScript(self):
        script = str(self.currentEditor.text().toUtf8()) + '\n'
        try:
            compile(script, 'script', 'exec')
        except SyntaxError, err:
            self.showError('Syntax error in script: %s' % err)
            self.currentEditor.setCursorPosition(err.lineno - 1, err.offset)
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
            self.client.tell('queue', self.filenames[self.currentEditor], script)

    @qtsig('')
    def on_actionSimulate_triggered(self):
        script = self.validateScript()
        if script is None:
            return
        self.client.tell('simulate', self.filenames[self.currentEditor], script)
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
        script = self.client.ask('getscript')
        if script is not None:
            editor = self.newFile()
            editor.setText(script)

    def clearSimPane(self):
        self.simOutView.clear()
        self.simOutViewErrors.clear()
        self.simRanges.clear()
        self.simTotalTime.setText('')
        self.simFinished.setText('')

    def on_simErrorsOnly_toggled(self, on):
        self.simOutStack.setCurrentIndex(on)

    def checkDirty(self, editor):
        if not editor.isModified():
            return True
        if self.filenames[editor]:
            message = 'Save changes in %s before continuing?' % self.filenames[editor]
        else:
            message = 'Save new file before continuing?'
        rc = QMessageBox.question(
            self, 'User Editor', message,
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if rc == QMessageBox.Save:
            return self.saveFile(editor)
        elif rc == QMessageBox.Discard:
            return True
        else:
            return False

    def on_fileSystemWatcher_fileChanged(self, filename):
        if self.saving:
            return
        for editor, watcher in self.watchers.iteritems():
            if watcher is self.sender():
                break
        else:
            return
        if editor.isModified():
            # warn the user
            self.warnText.setText(
                'The file %r has changed on disk, but has also been edited'
                ' here.\nPlease use either File-Reload to load the'
                ' version on disk or File-Save to save this version.'
                % self.filenames[editor])
            self.warnWidget.show()
        else:
            # reload without asking
            try:
                with open(self.filenames[editor]) as f:
                    text = f.read().decode('utf8')
            except Exception:
                return
            editor.setText(text)
            editor.setModified(False)
        # re-add the filename to the watcher if it was deleted
        # (happens for programs that do delete-write on save)
        if watcher.files().isEmpty():
            watcher.addPath(self.filenames[editor])

    @qtsig('')
    def on_actionNew_triggered(self):
        self.newFile()

    def newFile(self):
        editor, lexer = self.createEditor()
        editor.setModified(False)
        self.editors.append(editor)
        self.lexers[editor] = lexer
        self.filenames[editor] = ''
        self.watchers[editor] = QFileSystemWatcher(self)
        self.connect(self.watchers[editor],
                     SIGNAL('fileChanged(const QString &)'),
                     self.on_fileSystemWatcher_fileChanged)
        self.tabber.addTab(editor, '(New script)')
        self.tabber.setCurrentWidget(editor)
        self.clearSimPane()
        editor.setFocus()
        return editor

    @qtsig('')
    def on_actionOpen_triggered(self):
        if self.currentEditor is not None and self.filenames[self.currentEditor]:
            initialdir = path.dirname(self.filenames[self.currentEditor])
        else:
            initialdir = self.client.eval('session.experiment.scriptdir', '')
        fn = QFileDialog.getOpenFileName(self, 'Open script', initialdir,
                                         'Script files (*.py)')
        if fn.isEmpty():
            return
        self.openFile(unicode(fn).encode(sys.getfilesystemencoding()))
        self.addToRecentf(fn)

    @qtsig('')
    def on_actionReload_triggered(self):
        fn = self.filenames[self.currentEditor]
        if not fn:
            return
        if not self.checkDirty(self.currentEditor):
            return
        try:
            with open(fn) as f:
                text = f.read().decode('utf8')
        except Exception, err:
            return self.showError('Opening file failed: %s' % err)
        self.editor.setText(text)
        self.clearSimPane()

    def openRecentFile(self):
        fn = unicode(self.sender().text()).encode(sys.getfilesystemencoding())
        self.openFile(fn)

    def openFile(self, fn, quiet=False):
        try:
            with open(fn) as f:
                text = f.read().decode('utf8')
        except Exception, err:
            if quiet:
                return
            return self.showError('Opening file failed: %s' % err)

        editor, lexer = self.createEditor()
        editor.setText(text)
        editor.setModified(False)

        # replace tab if it's a single new file
        if len(self.editors) == 1 and not self.filenames[self.editors[0]] and \
            not self.editors[0].isModified():
            self._close(self.editors[0])

        self.editors.append(editor)
        self.lexers[editor] = lexer
        self.filenames[editor] = fn
        self.watchers[editor] = QFileSystemWatcher(self)
        self.connect(self.watchers[editor],
                     SIGNAL('fileChanged(const QString &)'),
                     self.on_fileSystemWatcher_fileChanged)
        self.watchers[editor].addPath(fn)
        self.tabber.addTab(editor, path.basename(fn))
        self.tabber.setCurrentWidget(editor)
        self.clearSimPane()
        editor.setFocus()

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
        self.saveFile(self.currentEditor)
        self.window.setWindowTitle('%s[*] - %s editor' %
            (self.filenames[self.currentEditor], self.mainwindow.instrument))
 
    @qtsig('')
    def on_actionSaveAs_triggered(self):
        self.saveFileAs(self.currentEditor)
        self.window.setWindowTitle('%s[*] - %s editor' %
            (self.filenames[self.currentEditor], self.mainwindow.instrument))

    def saveFile(self, editor):
        if not self.filenames[editor]:
            return self.saveFileAs(editor)

        try:
            self.saving = True
            try:
                with open(self.filenames[editor], 'w') as f:
                    f.write(str(editor.text().toUtf8()))
            finally:
                self.saving = False
        except Exception, err:
            self.showError('Writing file failed: %s' % err)
            return False

        self.watchers[editor].addPath(self.filenames[editor])
        editor.setModified(False)
        return True

    def saveFileAs(self, editor):
        if self.filenames[editor]:
            initialdir = path.dirname(self.filenames[editor])
        else:
            initialdir = self.client.eval('session.experiment.scriptdir', '')
        fn = QFileDialog.getSaveFileName(self, 'Save script', initialdir,
                                         'Script files (*.py)')
        fn = unicode(fn).encode(sys.getfilesystemencoding())
        if fn == '':
            return False
        if '.' not in fn:
            fn += '.py'
        self.addToRecentf(fn)
        self.watchers[editor].removePath(self.filenames[editor])
        self.filenames[editor] = fn
        self.tabber.setTabText(self.editors.index(editor), path.basename(fn))
        return self.saveFile(editor)

    @qtsig('')
    def on_actionFind_triggered(self):
        if not self.searchdlg:
            self.searchdlg = SearchDialog(self, self.currentEditor)
        self.searchdlg.found = False
        self.searchdlg.show()

    @qtsig('')
    def on_actionUndo_triggered(self):
        self.currentEditor.undo()

    @qtsig('')
    def on_actionRedo_triggered(self):
        self.currentEditor.redo()

    @qtsig('')
    def on_actionCut_triggered(self):
        self.currentEditor.cut()

    @qtsig('')
    def on_actionCopy_triggered(self):
        self.currentEditor.copy()

    @qtsig('')
    def on_actionPaste_triggered(self):
        self.currentEditor.paste()

    @qtsig('')
    def on_actionComment_triggered(self):
        if self.currentEditor.hasSelectedText():
            # comment selection

            # get the selection boundaries
            lineFrom, _, lineTo, indexTo = self.currentEditor.getSelection()
            if indexTo == 0:
                endLine = lineTo - 1
            else:
                endLine = lineTo

            self.currentEditor.beginUndoAction()
            # iterate over the lines
            for line in range(lineFrom, endLine+1):
                self.currentEditor.insertAt(COMMENT_STR, line, 0)
            # change the selection accordingly
            self.currentEditor.setSelection(lineFrom, 0, endLine+1, 0)
            self.currentEditor.endUndoAction()
        else:
            # comment line
            line, _ = self.currentEditor.getCursorPosition()
            self.currentEditor.beginUndoAction()
            self.currentEditor.insertAt(COMMENT_STR, line, 0)
            self.currentEditor.endUndoAction()

    @qtsig('')
    def on_actionUncomment_triggered(self):
        if self.currentEditor.hasSelectedText():
            # uncomment selection

            # get the selection boundaries
            lineFrom, indexFrom, lineTo, indexTo = self.currentEditor.getSelection()
            if indexTo == 0:
                endLine = lineTo - 1
            else:
                endLine = lineTo

            self.currentEditor.beginUndoAction()
            # iterate over the lines
            for line in range(lineFrom, endLine+1):
                # check if line starts with our comment string (i.e. was commented
                # by our comment...() slots
                if not self.currentEditor.text(line).startsWith(COMMENT_STR):
                    continue

                self.currentEditor.setSelection(line, 0, line, len(COMMENT_STR))
                self.currentEditor.removeSelectedText()

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
            self.currentEditor.setSelection(lineFrom, indexFrom, lineTo, indexTo)
            self.currentEditor.endUndoAction()
        else:
            # uncomment line
            line, _ = self.currentEditor.getCursorPosition()

            # check if line starts with our comment string (i.e. was commented
            # by our comment...() slots
            if not self.currentEditor.text(line).startsWith(COMMENT_STR):
                return

            # now remove the comment string
            self.currentEditor.beginUndoAction()
            self.currentEditor.setSelection(line, 0, line, len(COMMENT_STR))
            self.currentEditor.removeSelectedText()
            self.currentEditor.endUndoAction()

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
