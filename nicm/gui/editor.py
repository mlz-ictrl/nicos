#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
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
# *****************************************************************************

"""NICM GUI user editor window."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import re
import time
from os import path

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import pyqtSignature as qtsig

try:
    from PyQt4.Qsci import QsciScintilla, QsciLexerPython, QsciPrinter
except (ImportError, RuntimeError):
    has_scintilla = False
else:
    has_scintilla = True

try:
    from scipy.optimize import fmin
except:
    fmin = None

from nicm.gui.util import SettingGroup, showToolText, loadUi, DlgUtils, \
     format_duration, format_endtime
from nicm.gui.analyzer import AnalyzerError, AnalyzerResult, Analyzer, \
     analyze, compile_ast, get_global_names
from nicm.gui.toolsupport import editor_tools, HasTools

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


class EditorWindow(QMainWindow, HasTools, DlgUtils):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        DlgUtils.__init__(self, 'User editor')
        loadUi(self, 'editor.ui')

        self.client = parent.client

        if has_scintilla:
            self.editor = QsciScintilla(self)
            self.lexer = QsciLexerPython(self.editor)
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

        self.setCentralWidget(self.editor)
        self.editor.setFrameStyle(0)

        self.fileSystemWatcher = QFileSystemWatcher(self)
        self.connect(self.fileSystemWatcher,
                     SIGNAL('fileChanged(const QString &)'),
                     self.on_fileSystemWatcher_fileChanged)
        self.saving = False  # True while saving
        self.warnWidget.hide()

        self.analysisErrors.header().setResizeMode(QHeaderView.ResizeToContents)
        self.analysisRanges.header().setResizeMode(QHeaderView.ResizeToContents)
        self.analysisTimingProblems.header().setResizeMode(
            QHeaderView.ResizeToContents)
        self.analysisWidget.hide()
        # auto-check feature
        self.checkTimer = QTimer(self)
        self.checkTimer.setSingleShot(True)
        self.connect(self.checkTimer, SIGNAL('timeout()'), self.autoCheck)
        self.connect(self.editor, SIGNAL('textChanged()'),
                     self.on_editor_textChanged)

        self.connect(self.actionUndo, SIGNAL('triggered()'), self.editor.undo)
        self.connect(self.actionRedo, SIGNAL('triggered()'), self.editor.redo)
        self.connect(self.actionCut, SIGNAL('triggered()'), self.editor.cut)
        self.connect(self.actionCopy, SIGNAL('triggered()'), self.editor.copy)
        self.connect(self.actionPaste, SIGNAL('triggered()'), self.editor.paste)
        self.connect(self.editor, SIGNAL('modificationChanged(bool)'),
                     self.setDirty)
        showToolText(self.toolBar, self.actionRun)
        showToolText(self.toolBar, self.actionGet)
        showToolText(self.toolBar, self.actionUpdate)

        self.recentf_actions = []
        self.filename = ''
        self.setFilename('', force=True)
        self.setWindowModified(False)
        self.searchdlg = None

        self.last_goal_time = None
        self.last_goal_var = None

        self.sgroup = SettingGroup('EditorWindow')
        self.loadSettings()

        self.addTools(editor_tools, self.menuTools, self.editor.append)

    def setFont(self, font):
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

    def setDirty(self, dirty):
        self.actionSave.setEnabled(dirty)
        self.actionUndo.setEnabled(dirty)
        self.setWindowModified(dirty)

    def loadSettings(self):
        with self.sgroup as settings:
            geometry = settings.value('geometry').toByteArray()
            font     = QFont(settings.value('font'))
            color    = QColor(settings.value('color'))
            recentf  = list(settings.value('recentf').toStringList())
        self.restoreGeometry(geometry)
        self.setFont(font)
        if color.isValid():
            if has_scintilla:
                self.lexer.setDefaultPaper(color)
            else:
                self.editor.palette().setColor(QPalette.Base, color)
                self.editor.setBackgroundRole(QPalette.Base)
        for fn in recentf:
            action = QAction(fn, self)
            self.connect(action, SIGNAL('triggered()'), self.openRecentFile)
            self.recentf_actions.append(action)
            self.menuRecent.addAction(action)
        self.update()

    def closeEvent(self, event):
        if not self.checkDirty():
            event.ignore()
            return
        with self.sgroup as settings:
            settings.setValue('geometry', QVariant(self.saveGeometry()))
        event.accept()
        self.emit(SIGNAL('closed'), self)

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
        try:
            script = str(self.editor.text()) + '\n'
        except UnicodeError:
            return self.showError('Unicode error in script.')
        try:
            compile(script, 'script', 'exec')
        except SyntaxError, err:
            self.showError(self.tr('Syntax error in script: %1').arg(str(err)))
            self.editor.setCursorPosition(err.lineno - 1, err.offset)
            return
        return script

    @qtsig('')
    def on_actionRun_triggered(self):
        script = self.validateScript()
        if self.parent().current_status != 'idle':
            if not self.askQuestion('A script is currently running, do you '
                                    'want to queue this script?', True):
                return
        if script is not None:
            self.parent().run_script(self.filename, script)

    @qtsig('')
    def on_actionUpdate_triggered(self):
        script = self.validateScript()
        if script is not None:
            self.client.send_commands('update_prg', script)

    @qtsig('')
    def on_actionGet_triggered(self):
        if not self.checkDirty():
            return
        self.editor.setText(self.parent().current_request.get('script', ''))

    def on_editor_textChanged(self):
        if self.analysisAutoCheck.isChecked():
            self.checkTimer.stop()
            self.checkTimer.start(1000)

    def on_analysisAutoCheck_stateChanged(self, state):
        if state == Qt.Checked:
            self.autoCheck()

    def autoCheck(self):
        self.on_actionEstimate_triggered()

    def clearAnalysis(self):
        self.analysisErrors.clear()
        self.analysisTimingProblems.clear()
        self.analysisRanges.clear()
        self.editor.markerDeleteAll()
        self.analysisCountingTime.setText('')
        self.analysisMovingTime.setText('')
        self.analysisOtherTime.setText('')
        self.analysisTotalTime.setText('')
        self.analysisFinished.setText('')

    @qtsig('')
    def on_actionEstimate_triggered(self):
        self.analysisAutoCheck.setChecked(True)
        try:
            result = analyze(str(self.editor.text()))
        except AnalyzerError, err:
            self.showWarning(str(err))
            return

        # clear analysis results
        self.clearAnalysis()

        # show analysis results: timings
        self.analysisCountingTime.setText(format_duration(result.count_time))
        self.analysisMovingTime.setText(format_duration(result.move_time))
        self.analysisOtherTime.setText(format_duration(result.other_time))
        self.analysisTotalTime.setText(format_duration(result.total_time))
        self.analysisFinished.setText(format_endtime(result.total_time))

        for line, message in sorted(result.timing_problems):
            item = QTreeWidgetItem([str(line), message], line - 1)
            self.analysisTimingProblems.addTopLevelItem(item)
            self.editor.markerAdd(line - 1, 1)

        # errors
        for line, message in sorted(result.errors):
            item = QTreeWidgetItem([str(line), message], line - 1)
            self.analysisErrors.addTopLevelItem(item)
            self.editor.markerAdd(line - 1, 2)

        # device ranges
        for devname, (dmin, dmax) in result.device_ranges.iteritems():
            item = QTreeWidgetItem([devname, str(dmin), '-', str(dmax)])
            self.analysisRanges.addTopLevelItem(item)

        self.analysisWidget.show()

    def on_analysisErrors_itemClicked(self, item, column):
        self.editor.setCursorPosition(item.type(), 0)
        self.editor.setFocus()

    def on_analysisTimingProblems_itemClicked(self, item, column):
        self.editor.setCursorPosition(item.type(), 0)
        self.editor.setFocus()

    def on_analysisWidget_visibilityChanged(self, visible):
        if not visible:
            self.analysisAutoCheck.setCheckState(Qt.Unchecked)
            self.editor.markerDeleteAll()

    @qtsig('')
    def on_actionGoalTime_triggered(self):
        # goal time estimation only works when scipy is installed
        if fmin is None:
            return self.showError('scipy is not available.')
        script = str(self.editor.text())
        try:
            names = get_global_names(script)
        except SyntaxError, err:
            self.showError('Syntax error in script.')
            self.editor.setCursorPosition(err.lineno - 1, err.offset)
            return
        # display the goal parameter dialog, and fill the "Variable" entry
        # with all globally assigned variables
        dlg = QDialog(self)
        loadUi(dlg, 'goalinput.ui')
        if self.last_goal_time is not None:
            dlg.goalTime.setText(str(self.last_goal_time))
        for i, name in enumerate(names):
            dlg.goalVar.addItem(name)
            # pre-select names that look like preset times
            if name.startswith('t') or name.startswith('messzeit') or \
                   name.startswith('preset'):
                dlg.goalVar.setCurrentIndex(i)
        if self.last_goal_var is not None:
            dlg.goalVar.setEditText(self.last_goal_var)
        if dlg.exec_() != QDialog.Accepted:
            return

        units = {'seconds': 1, 'hours': 3600, 'days': 3600*24}
        goal_var = str(dlg.goalVar.currentText())
        self.last_goal_var = goal_var
        if not goal_var:
            return self.showError('You must enter a variable name.')
        goal_time, ok = dlg.goalTime.text().toDouble()
        if not ok:
            return self.showError('You must enter a valid goal time.')
        self.last_goal_time = goal_time
        goal_time *= units[str(dlg.goalTimeUnit.currentText())]

        # minimize the difference between total and goal time
        mod = compile_ast(script)
        def minfunc(x):
            result = AnalyzerResult()
            analyzer = Analyzer(result)
            analyzer.set_local_override(goal_var, abs(x[0]))
            analyzer.do_suite(mod.body)
            return abs(result.total_time - goal_time)
        initial = 0.9999
        opt_val, _, _, _, err = fmin(minfunc, [initial], full_output=True)
        if err != 0 or opt_val[0] == initial:
            return self.showError('Minimizing total time failed.')

        # display result
        if self.askQuestion(
            self.tr('Optimum value for %1: %2\nAdd/replace assignment?').
            arg(goal_var).arg(opt_val[0])):

            # if wanted, add or replace an assignment of the goal variable
            goal_assign = '%s = %s' % (goal_var, QString('%1').arg(opt_val[0]))
            lines = script.splitlines()
            insert_point = -2
            for i, line in enumerate(lines):
                # ignore leading empty and comment lines
                if not line.strip() or line.lstrip().startswith('#'):
                    continue
                if re.match(r'%s\s*=' % goal_var, line):
                    # it's already there, replace it  (loses line comments!)
                    lines[i] = goal_assign
                    insert_point = -1
                if insert_point == -2:
                    # if we don't find an assignment, insert it here
                    # (after initial comment lines)
                    insert_point = i
            if insert_point == -2:
                # no insertion point found (should be impossible if script is
                # non-empty), append assignment at the end anyway
                lines.append(goal_assign)
            elif insert_point >= 0:
                # not replaced, insert assignment at the insertion point
                lines.insert(insert_point, goal_assign)
            # XXX no undo possible when using setText
            self.editor.setText('\n'.join(lines))

        self.on_actionEstimate_triggered()

    @qtsig('')
    def on_actionFont_triggered(self):
        font, ok = QFontDialog.getFont(self.editor.font(), self)
        if not ok:
            return
        self.setFont(font)
        with self.sgroup as settings:
            settings.setValue('font', QVariant(font))

    @qtsig('')
    def on_actionColor_triggered(self):
        color = QColorDialog.getColor(Qt.white, self)
        if not color.isValid():
            return
        if has_scintilla:
            self.lexer.setPaper(color)
        else:
            self.editor.palette().setColor(QPalette.Base, color)
            self.editor.setBackgroundRole(QPalette.Base)
        with self.sgroup as settings:
            settings.setValue('color', QVariant(color))

    def checkDirty(self):
        if not self.editor.isModified():
            return True
        rc = QMessageBox.question(
            self, self.tr('User Editor'),
            self.tr('Save changes in %1 before continuing?').arg(self.filename),
            QMessageBox.Save | QMessageBox.Discard |
            QMessageBox.Cancel)
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
            self.setWindowTitle(self.tr('%1[*] - %2 editor')
                                .arg(newfn).arg(self.parent().instrument))
        else:
            self.actionReload.setEnabled(False)
            self.setWindowTitle(self.tr('New[*] - %1 editor')
                                .arg(self.parent().instrument))

    def on_fileSystemWatcher_fileChanged(self, filename):
        if self.saving:
            return
        if self.editor.isModified():
            # warn the user
            self.warnText.setText(
                self.tr('The file has changed on disk, but has also been edited'
                        ' here.\nPlease use either File-Reload to load the'
                        ' version on disk or File-Save to save this version.'))
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
        self.clearAnalysis()

    @qtsig('')
    def on_actionOpen_triggered(self):
        if not self.checkDirty():
            return
        initialdir = self.filename and path.dirname(self.filename) or \
                     self.parent().tcspath
        fn = QFileDialog.getOpenFileName(self, self.tr('Open script'),
                                         initialdir,
                                         self.tr('Script files (*.tcs)'))
        if fn.isEmpty():
            return
        self.openFile(str(fn))
        self.addToRecentf(fn)

    @qtsig('')
    def on_actionReload_triggered(self):
        if not self.checkDirty():
            return
        self.openFile(self.filename)

    def openRecentFile(self):
        self.openFile(str(self.sender().text()))

    def openFile(self, fn):
        try:
            with open(fn) as f:
                self.editor.setText(f.read())
        except Exception, err:
            return self.showError(
                self.tr('Opening file failed: %1').arg(str(err)))

        self.editor.setModified(False)
        self.setFilename(fn)
        self.clearAnalysis()

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
                    f.write(str(self.editor.text()))
            finally:
                self.saving = False
        except Exception, err:
            return self.showError(
                self.tr('Writing file failed: %1').arg(str(err)))
            return False

        self.editor.setModified(False)
        self.setFilename(self.filename)  # now add to file system watcher
        return True

    @qtsig('')
    def on_actionSaveAs_triggered(self):
        if self.filename:
            initialdir = path.dirname(self.filename)
        else:
            initialdir = self.parent().tcspath
        fn = str(QFileDialog.getSaveFileName(self, self.tr('Save script'),
            initialdir, self.tr('Script files (*.tcs)')))
        if fn == '':
            return False
        if '.' not in fn:
            fn += '.tcs'
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
            lineFrom, indexFrom, lineTo, indexTo = self.editor.getSelection()
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
            line, index = self.editor.getCursorPosition()
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
            line, index = self.editor.getCursorPosition()

            # check if line starts with our comment string (i.e. was commented
            # by our comment...() slots
            if not self.editor.text(line).startsWith(COMMENT_STR):
                return

            # now remove the comment string
            self.editor.beginUndoAction()
            self.editor.setSelection(line, 0, line, len(COMMENT_STR))
            self.editor.removeSelectedText()
            self.editor.endUndoAction()


class SearchDialog(QDialog):
    def __init__(self, parent, editor):
        QDialog.__init__(self, parent)
        loadUi(self, 'search.ui')

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
