#  -*- coding: utf-8 -*-
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

"""NICOS GUI main window."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import re
import time
import codecs
from os import path

from PyQt4.QtCore import *
from PyQt4.QtCore import pyqtSignature as qtsig
from PyQt4.QtGui import *

from nicos import nicos_version
from nicos.gui.data import DataHandler, DataError
from nicos.gui.utils import DlgUtils, SettingGroup, loadUi, dialogFromUi, \
     chunks, get_display, parse_conndata, enumerateWithProgress, \
     setForegroundColor, setBackgroundColor
from nicos.gui.client import NicosClient, STATUS_INBREAK, STATUS_IDLE
from nicos.gui.editor import EditorWindow
from nicos.gui.toolsupport import main_tools, HasTools

from nicos.gui.custom import has_customization, list_customizations

try:
    # needs Qwt5, which may not be available, so make it optional
    from nicos.gui.analysis import AnalysisWindow
except (ImportError, RuntimeError):
    AnalysisWindow = None


class NicosGuiClient(NicosClient, QObject):
    siglist = ['connected', 'disconnected', 'error', 'message',
               'new_request', 'processing_request', 'new_script',
               'new_status', 'new_values', 'new_output',
               'new_dataset', 'new_curve', 'new_point', 'new_points']

    def __init__(self, parent):
        QObject.__init__(self, parent)
        NicosClient.__init__(self)

    def signal(self, type, *args):
        self.emit(SIGNAL(type), *args)


class MainWindow(QMainWindow, HasTools, DlgUtils):
    def __init__(self):
        QMainWindow.__init__(self)
        DlgUtils.__init__(self, 'NICOS')
        loadUi(self, 'main.ui')

        # child window references
        self.editorWindows = set()
        self.analysisWindow = None
        self.errorWindow = None

        # data handling setup
        self.data = DataHandler()

        # log messages sent by the server
        self.messages = []

        # connect the client's events
        self.client = NicosGuiClient(self)
        for sig in self.client.siglist:
            self.connect(self.client, SIGNAL(sig),
                         getattr(self, 'on_client_'+sig))

        # set-up the initial connection data
        self.connectionData = {
            'host': '', 'port': 0, 'login': '',
            'display': get_display(), 'gzip': False,
        }

        # some UI stuff
        self.queueFrame.hide()
        self.statusLabel.hide()
        self.printPaperBar.hide()
        self.grepPanel.hide()
        self.grepText.scrollWidget = self.outView
        self.customStyleWidgets = [self.traceView, self.queueView,
                                   self.watchView, self.outView,
                                   self.commandInput]
        self.commandInput.scrollWidget = self.outView

        self.actionLabel.hide()
        self.outView.setActionLabel(self.actionLabel)

        # local command queue
        self.scriptQueue = ScriptQueue(self.queueFrame, self.queueView)

        # status indicator
        self.pauseColor = QColor('#ffdddd')

        # load saved settings
        self.sgroup = SettingGroup('MainWindow')
        self.loadSettings()

        # collect all actions that will be disabled if not connected
        self.connectedActions = g = QActionGroup(self)
        g.addAction(self.actionBreak)
        g.addAction(self.actionContinue)
        g.addAction(self.actionStop)
        g.addAction(self.actionEmergencyStop)
        g.addAction(self.actionRunCommand)
        g.addAction(self.actionReload)

        # setup tray icon
        self.trayIcon = QSystemTrayIcon(self)
        self.connect(self.trayIcon,
                     SIGNAL('activated(QSystemTrayIcon::ActivationReason)'),
                     self.on_trayIcon_activated)
        self.trayMenu = QMenu(self)
        nameAction = self.trayMenu.addAction(self.instrument)
        nameAction.setEnabled(False)
        self.trayMenu.addSeparator()
        actionMenu = self.trayMenu.addMenu('Actions')
        for action in [self.actionBreak, self.actionContinue, self.actionStop]:
            actionMenu.addAction(action)
        self.trayMenu.addSeparator()
        toggleAction = self.trayMenu.addAction('Hide main window')
        toggleAction.setCheckable(True)
        self.connect(toggleAction, SIGNAL('triggered(bool)'), self.hideorshow)
        self.trayIcon.setContextMenu(self.trayMenu)

        # setup state members
        self.curlineicon = QIcon(':/currentline')
        empty = QPixmap(16, 16)
        empty.fill(Qt.transparent)
        self.otherlineicon = QIcon(empty)
        self.current_request = {}
        self.current_line = -1
        self.current_status = None
        self.watch_items = {}
        self.action_start_time = None
        self.set_status('disconnected')
        self.run_queue = []

        # add user-defined tools
        self.addTools(main_tools, self.menuTools, lambda x: None)

    def show(self):
        QMainWindow.show(self)
        if self.autoconnect:
            self.on_actionConnect_triggered(True)

    def hideorshow(self, hide):
        self.setVisible(not hide)

    def loadSettings(self):
        with self.sgroup as settings:
            # geometry and window appearance
            geometry = settings.value('geometry').toByteArray()
            mainsplitter = settings.value('mainsplitter').toByteArray()
            topsplitter = settings.value('topsplitter').toByteArray()
            font = QFont(settings.value('font'))
            color = QColor(settings.value('color'))

            # state of connection, editor and analysis windows
            editFns = settings.value('editedfiles').toStringList()
            openanalysis = settings.value('openanalysis').toBool()
            cmdhistory = settings.value('cmdhistory').toStringList()
            self.autoconnect = settings.value('autoconnect').toBool()

            # from server dialog
            self.connectionData['host'] = str(settings.value(
                'host', QVariant('localhost')).toString())
            self.connectionData['port'] = settings.value(
                'port', QVariant(1201)).toInt()[0]
            self.connectionData['login'] = str(settings.value(
                'login', QVariant('admin')).toString())
            self.servers = settings.value('servers').toStringList()

            # from preferences dialog
            self.instrument = settings.value('instrument').toString()
            self.tcspath = settings.value('tcspath').toString()
            self.customname = settings.value('customname').toString()
            self.confirmexit = settings.value('confirmexit',
                                              QVariant(True)).toBool()
            self.showtrayicon = settings.value('showtrayicon',
                                               QVariant(True)).toBool()

        self.restoreGeometry(geometry)
        self.mainSplitter.restoreState(mainsplitter)
        self.topSplitter.restoreState(topsplitter)
        self.commandInput.history = map(str, cmdhistory)
        for widget in self.customStyleWidgets:
            widget.setFont(font)
            if color.isValid():
                setBackgroundColor(widget, color)
        self.update()
        if openanalysis:
            self.on_actionAnalysis_triggered()
        for filename in editFns:
            editor = self.on_actionUserEditor_triggered()
            editor.openFile(str(filename))

    def closeEvent(self, event):
        if self.confirmexit and QMessageBox.question(
            self, self.tr('Quit'),
            self.tr('Do you really want to quit?'),
            QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            event.ignore()
            return

        editFns = []
        for window in list(self.editorWindows):
            if window.filename:
                editFns.append(window.filename)
            if not window.close():
                event.ignore()
                return

        with self.sgroup as settings:
            settings.setValue('geometry', QVariant(self.saveGeometry()))
            settings.setValue('mainsplitter',
                              QVariant(self.mainSplitter.saveState()))
            settings.setValue('topsplitter',
                              QVariant(self.topSplitter.saveState()))
            settings.setValue('openanalysis',
                              QVariant(self.analysisWindow is not None))
            settings.setValue('editedfiles',
                              QVariant(QStringList(editFns)))
            # only save 100 entries of the history
            cmdhistory = self.commandInput.history[-100:]
            settings.setValue('cmdhistory',
                              QVariant(QStringList(cmdhistory)))
            settings.setValue('autoconnect',
                              QVariant(self.client.connected))
            servers = sorted(set(map(str, self.servers)))
            settings.setValue('servers',
                              QVariant(QStringList(servers)))

        if self.client.connected:
            self.client.disconnect()

        event.accept()

    def keyPressEvent(self, event):
        if event.type() == QEvent.KeyPress and \
           event.key() == Qt.Key_P:
            mods = event.modifiers()
            if mods & Qt.ControlModifier and \
               (mods & Qt.MetaModifier or mods & Qt.AltModifier):
                if self.printPaperBar.isVisible():
                    self.printPaperBar.hide()
                else:
                    self.printPaperBar.show()
        return QMainWindow.keyPressEvent(self, event)

    def setConnData(self, login, host, port):
        self.connectionData['login'] = login
        self.connectionData['host'] = host
        self.connectionData['port'] = port

    @qtsig('')
    def on_actionFont_triggered(self):
        font, ok = QFontDialog.getFont(self.outView.font(), self)
        if not ok:
            return
        for widget in self.customStyleWidgets:
            widget.setFont(font)
        with self.sgroup as settings:
            settings.setValue('font', QVariant(font))

    @qtsig('')
    def on_actionColor_triggered(self):
        color = QColorDialog.getColor(Qt.white, self)
        if not color.isValid():
            return
        for widget in self.customStyleWidgets:
            setBackgroundColor(widget, color)
        with self.sgroup as settings:
            settings.setValue('color', QVariant(color))

    @qtsig('')
    def on_actionAbout_triggered(self):
        QMessageBox.information(
            self, self.tr('About this application'),
            self.tr('NICOS-NG GUI client version %1, '
                    'written by Georg Brandl.\n\nServer: ').arg(nicos_version)
            + (self.client.connected and self.client.version or
               self.tr('not connected')))

    @qtsig('')
    def on_actionAboutQt_triggered(self):
        QMessageBox.aboutQt(self)

    @qtsig('bool')
    def on_actionConnect_triggered(self, on):
        # connection or disconnection request?
        if not on:
            self.client.disconnect()
            return

        addr = '%s:%s' % (self.connectionData['host'],
                          self.connectionData['port'])

        self.actionConnect.setChecked(False)  # gets set by connection event
        authdlg = dialogFromUi(self, 'auth.ui')
        authdlg.userName.setText(self.connectionData['login'])
        authdlg.serverAddr.addItems(self.servers)
        authdlg.serverAddr.setEditText(addr)
        authdlg.password.setFocus()
        ret = authdlg.exec_()
        if ret != QDialog.Accepted:
            return
        new_addr = str(authdlg.serverAddr.currentText())
        if new_addr != addr:
            try:
                host, port = new_addr.split(':')
                port = int(port)
            except ValueError:
                host = new_addr
                port = 1201
            self.connectionData['host'] = host
            self.connectionData['port'] = port
            self.servers.append('%s:%s' % (host, port))
        self.connectionData['login'] = str(authdlg.userName.text())
        self.client.connect(self.connectionData,
                            str(authdlg.password.text()))
        self.commandInput.setFocus()

    @qtsig('')
    def on_actionConnectionData_triggered(self):
        dlg = dialogFromUi(self, 'server.ui')
        dlg.host.setEditText(self.connectionData['host'])
        dlg.port.setText(str(self.connectionData['port']))
        dlg.port.setValidator(QIntValidator(1, 65536, dlg))
        dlg.login.setEditText(self.connectionData['login'])
        dlg.display.setText(self.connectionData['display'])
        ret = dlg.exec_()
        if ret != QDialog.Accepted:
            return
        self.connectionData['host'] = str(dlg.host.currentText())
        self.connectionData['port'] = int(dlg.port.text())
        self.connectionData['login'] = str(dlg.login.currentText())
        self.connectionData['display'] = str(dlg.display.text())
        with self.sgroup as settings:
            settings.setValue('host',
                              QVariant(self.connectionData['host']))
            settings.setValue('port',
                              QVariant(self.connectionData['port']))
            settings.setValue('login',
                              QVariant(self.connectionData['login']))

    @qtsig('')
    def on_actionPreferences_triggered(self):
        dlg = dialogFromUi(self, 'prefs.ui')
        dlg.instrument.setText(self.instrument)
        dlg.tcspath.setText(self.tcspath)
        dlg.customname.addItems(sorted(list_customizations()))
        dlg.customname.setEditText(self.customname)
        dlg.confirmExit.setChecked(self.confirmexit)
        dlg.horzLayout.setChecked(self.mainSplitter.orientation()
                                  == Qt.Horizontal)
        dlg.showTrayIcon.setChecked(self.showtrayicon)
        ret = dlg.exec_()
        if ret != QDialog.Accepted:
            return
        self.instrument = dlg.instrument.text()
        self.tcspath = dlg.tcspath.text()
        new_customname = dlg.customname.currentText()
        if self.customname != new_customname:
            if not has_customization(str(new_customname)):
                self.showError('Customization %s does not exist.' %
                               new_customname)
            else:
                self.showInfo('This application has to be restarted for a '
                              'change in customization to take effect.')
                self.customname = new_customname
        self.confirmexit = dlg.confirmExit.isChecked()
        self.showtrayicon = dlg.showTrayIcon.isChecked()
        self.mainSplitter.setOrientation(dlg.horzLayout.isChecked() and
                                         Qt.Horizontal or Qt.Vertical)
        self.topSplitter.setOrientation(dlg.horzLayout.isChecked() and
                                        Qt.Vertical or Qt.Horizontal)
        if self.showtrayicon:
            self.trayIcon.show()
        else:
            self.trayIcon.hide()
        with self.sgroup as settings:
            settings.setValue('instrument', QVariant(self.instrument))
            settings.setValue('tcspath', QVariant(self.tcspath))
            settings.setValue('customname', QVariant(self.customname))
            settings.setValue('confirmexit', QVariant(self.confirmexit))
            settings.setValue('showtrayicon', QVariant(self.showtrayicon))

    @qtsig('')
    def on_actionUserEditor_triggered(self):
        editor = EditorWindow(self)
        editor.show()
        self.connect(editor, SIGNAL('closed'), self.editorWindowClosed)
        self.editorWindows.add(editor)
        return editor

    def editorWindowClosed(self, window):
        self.editorWindows.remove(window)

    @qtsig('')
    def on_actionAnalysis_triggered(self):
        if not AnalysisWindow:
            QMessageBox.warning(self, self.tr('Analysis Error'),
                self.tr('Qwt5 is not available, analysis window '
                        'cannot be opened.'))
            return
        if self.analysisWindow:
            self.analysisWindow.activateWindow()
            self.analysisWindow.raise_()
        else:
            self.analysisWindow = AnalysisWindow(self)
            self.analysisWindow.show()
            self.connect(self.analysisWindow, SIGNAL('closed'),
                         self.analysisWindowClosed)

    def analysisWindowClosed(self, window):
        self.analysisWindow = None

    @qtsig('')
    def on_actionErrorWindow_triggered(self):
        self.outView.openErrorWindow()

    @qtsig('')
    def on_actionBreak_triggered(self):
        self.client.send_command('break_prg', True)
        self.action_start_time = time.time()

    @qtsig('')
    def on_actionContinue_triggered(self):
        self.client.send_command('cont_prg', True)
        self.action_start_time = time.time()

    @qtsig('')
    def on_actionStop_triggered(self):
        self.client.send_command('stop_prg', True)
        self.action_start_time = time.time()

    @qtsig('')
    def on_actionEmergencyStop_triggered(self):
        self.client.send_command('emergency_stop', True)
        self.action_start_time = time.time()

    @qtsig('')
    def on_actionReload_triggered(self):
        if self.client.send_command('reload_nicos', True):
            QMessageBox.information(self, self.tr('Reload'),
                                    self.tr('NICOS system reloaded on server.'))

    def on_trayIcon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.activateWindow()

    # -------- client event handlers -------------------------------------------

    def on_client_disconnected(self):
        self.set_status('disconnected')

    def on_client_connected(self):
        self.set_status('idle')

        # get all server status info
        allstatus = self.client.unserialize(
            self.client.send_command('get_all_status'))
        status, script, messages, watch = allstatus

        # handle status, script and watch
        self.set_script(script)
        self.current_request['script'] = script
        self.current_request['reqno'] = None
        self.on_client_new_status(status)
        self.on_client_new_values(watch)

        # handle output (i.e. messages)
        self.outView.clear()
        total = len(messages) // 2500 + 1
        for i, batch in enumerateWithProgress(chunks(messages, 2500),
                            text='Synchronizing...', parent=self, total=total):
            self.outView.addMessages(batch)
        self.outView.scrollToBottom()

        # retrieve datasets and put them into the analysis window
        return
        pd = QProgressDialog(self)
        pd.setLabelText('Transferring datasets, please wait...')
        pd.setRange(0, 1)
        pd.setCancelButton(None)
        pd.show()
        QApplication.processEvents()
        raw = self.client.send_command('get_datasets')
        datasets = self.client.unserialize(raw)
        if self.analysisWindow:
            self.analysisWindow.bulk_adding = True
        for dataset in datasets:
            self.on_client_new_dataset(dataset)
        if self.analysisWindow:
            self.analysisWindow.bulk_adding = False
        pd.setValue(1)
        pd.close()

    def on_client_error(self, problem, exc=None):
        if exc is not None:
            print 'Exception:', exc
        if self.errorWindow is None:
            self.errorWindow = QDialog(self)
            def reset_errorWindow():
                self.errorWindow = None
            self.errorWindow.connect(self.errorWindow, SIGNAL('accepted()'),
                                     reset_errorWindow)
            loadUi(self.errorWindow, 'error.ui')
            self.errorWindow.setWindowTitle(self.tr('Connection error'))
            self.errorWindow.errorText.setText(problem)
            self.errorWindow.iconLabel.setPixmap(
                self.style().standardIcon(QStyle.SP_MessageBoxWarning).
                pixmap(32, 32))
            self.errorWindow.show()
        else:
            self.errorWindow.errorText.setText(
                self.errorWindow.errorText.text() + '\n' + problem)

    def on_client_message(self, message):
        #print 'message:', message
        self.outView.addMessage(message)

    def on_client_new_request(self, request):
        if 'script' not in request:
            return
        self.scriptQueue.append(request)

    def on_client_processing_request(self, request):
        if 'script' not in request:
            return
        new_current_line = -1
        if self.current_request['reqno'] == request['reqno']:
            # on update, set the current line to the same as before
            # (this may be WRONG, but should not in most cases, and it's
            # better than no line indicator at all)
            new_current_line = self.current_line
        self.scriptQueue.remove(request['reqno'])
        self.set_script(request['script'])
        self.current_request = request
        self.set_current_line(new_current_line)

    def set_script(self, script):
        self.traceView.clear()
        for line in script.splitlines():
            item = QListWidgetItem(self.otherlineicon, line, self.traceView)
            self.traceView.addItem(item)
        self.current_line = -1

    def set_current_line(self, line):
        if self.current_line != -1:
            item = self.traceView.item(self.current_line - 1)
            if item: item.setIcon(self.otherlineicon)
        if 0 < line <= self.traceView.count():
            self.traceView.item(line - 1).setIcon(self.curlineicon)
        self.current_line = line

    def on_client_new_script(self, script):
        # deprecated event...
        pass

    def set_status(self, status):
        if status == self.current_status:
            return
        if self.action_start_time and self.current_status == 'running' and \
           status in ('idle', 'interrupted') and \
           time.time() - self.action_start_time > 20:
            # show a visual indication of what happened
            ss = {'idle': 'finished', 'interrupted': 'interrupted'}[status]
            self.trayIcon.showMessage(self.instrument, 'Script is now %s.' % ss)
            self.action_start_time = None
        self.current_status = status
        isconnected = status != 'disconnected'
        self.actionConnect.setChecked(isconnected)
        if isconnected:
            self.actionConnect.setText(self.tr('Disconnect'))
        else:
            self.actionConnect.setText(self.tr('Connect to server...'))
        # new status icon
        newicon = QIcon()
        newicon.addPixmap(QPixmap(':/' + status), QIcon.Disabled)
        self.actionStatus.setIcon(newicon)
        self.actionStatus.setText(self.tr('Script status: %1').arg(status))
        self.trayIcon.setIcon(newicon)
        self.trayIcon.setToolTip(self.tr('%1 status: %2').
                                 arg(self.instrument).arg(status))
        if self.showtrayicon:
            self.trayIcon.show()
        # red if interrupted
        if status == 'interrupted':
            self.statusLabel.setText(self.tr('Script is interrupted.'))
            self.statusLabel.show()
            setBackgroundColor(self.traceView, self.pauseColor)
        else:
            self.statusLabel.hide()
            setBackgroundColor(self.traceView,
                               self.outView.palette().color(QPalette.Base))
        if status != 'idle':
            setBackgroundColor(self.commandInput, self.pauseColor)
        else:
            setBackgroundColor(self.commandInput,
                               self.outView.palette().color(QPalette.Base))
        self.traceView.update()
        self.commandInput.update()
        # title bar change
        self.setWindowTitle((str(self.instrument) or 'NICOS') + ' - ' +
                            (status == 'disconnected' and
                             self.tr('disconnected') or
                             self.tr('connected to %1:%2').
                             arg(self.client.host).arg(self.client.port)))
        # set action buttons
        self.actionBreak.setEnabled(status != 'idle')
        self.actionBreak.setVisible(status != 'interrupted')
        self.actionContinue.setVisible(status == 'interrupted')
        self.actionStop.setEnabled(status != 'idle')
        # all other actions
        self.connectedActions.setEnabled(isconnected)
        self.commandInput.setEnabled(isconnected)
        self.addWatch.setEnabled(isconnected)
        self.deleteWatch.setEnabled(isconnected)
        self.oneShotEval.setEnabled(isconnected)

    def on_client_new_status(self, data):
        status, line = data
        if status == STATUS_IDLE:
            self.set_status('idle')
        elif status != STATUS_INBREAK:
            self.set_status('running')
        else:
            self.set_status('interrupted')
        if line != self.current_line:
            self.set_current_line(line)

    def on_client_new_output(self, data):
        # fabricate a message out of the new output
        message = ['nicos', time.time(), 20, ''.join(data), None]
        self.outView.addMessage(message)

    def on_client_new_values(self, data):
        # XXX implement name:group scheme
        values = data
        names = set()
        for name, val in values.iteritems():
            name = name[:name.find(':')]
            if name in self.watch_items:
                self.watch_items[name].setText(1, str(val))
            else:
                newitem = QTreeWidgetItem(self.watchView,
                                          [str(name), str(val)])
                self.watchView.addTopLevelItem(newitem)
                self.watch_items[name] = newitem
            names.add(name)
        removed = set(self.watch_items) - names
        for itemname in removed:
            self.watchView.takeTopLevelItem(
                self.watchView.indexOfTopLevelItem(
                    self.watch_items[itemname]))
            del self.watch_items[itemname]

    def on_client_new_dataset(self, dataset):
        try:
            self.data.new_dataset(dataset[0])
        except DataError, err:
            print 'Data error:', err
        else:
            for curve in dataset[1:]:
                try:
                    self.data.add_curve(curve)
                except DataError, err:
                    print 'DataError:', err

    def on_client_new_curve(self, curve):
        try:
            self.data.add_curve(curve)
        except DataError, err:
            print 'Data error:', err

    def on_client_new_point(self, (index, point)):
        try:
            self.data.add_point(index, point)
        except DataError, err:
            print 'Data error:', err

    def on_client_new_points(self, (index, points)):
        try:
            self.data.add_points(index, points)
        except DataError, err:
            print 'Data error:', err

    def on_commandInput_textChanged(self, text):
        try:
            script = str(self.commandInput.text())
            if not script:
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
        try:
            compile(script+'\n', 'script', 'single')
        except SyntaxError, err:
            QMessageBox.information(
                self, self.tr('Command'),
                self.tr('Syntax error in command: %1').arg(err.msg))
            self.commandInput.setCursorPosition(err.offset)
            return
        if self.current_status != 'idle':
            if QMessageBox.question(
                self, self.tr('Queue?'),
                self.tr('A script is currently running, do you want '
                        'to queue this command?'),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) \
                == QMessageBox.No:
                return
        self.run_script('None', script)
        self.commandInput.setText('')

    def run_script(self, name, script):
        """Called from editor window and command box."""
        if not self.client.send_commands('queue_named_prg', name, script):
            return
        self.action_start_time = time.time()

    @qtsig('')
    def on_actionPrint_triggered(self):
        printer = QPrinter()
        printdlg = QPrintDialog(printer, self)
        printdlg.addEnabledOption(QAbstractPrintDialog.PrintSelection)
        if printdlg.exec_() == QDialog.Accepted:
            self.outView.print_(printer)

    @qtsig('')
    def on_actionSave_triggered(self):
        fn = QFileDialog.getSaveFileName(self, self.tr('Save log'),
                                         '', self.tr('All files (*.*)'))
        if fn.isEmpty():
            return
        try:
            with codecs.open(str(fn), 'w', 'utf-8') as f:
                f.write(unicode(self.outView.getOutputString()))
        except Exception, err:
            QMessageBox.warning(self, self.tr('Error'),
                                self.tr('Writing file failed: %1').arg(str(err)))

    @qtsig('')
    def on_actionRunCommand_triggered(self):
        command, ok = QInputDialog.getText(
            self, self.tr('Run command'),
            self.tr('Warning: In most cases it is advisable to at least break '
                    'the script before using this function!\n'
                    'Command to run in script namespace:'))
        if not ok:
            return
        self.client.send_commands('exec_cmd', str(command))

    @qtsig('')
    def on_addWatch_clicked(self):
        expr, ok = QInputDialog.getText(
            self, self.tr('Add watch expression'),
            self.tr('New expression to watch:'))
        if not ok:
            return
        newexpr = self.client.serialize([str(expr) + ':default'])
        self.client.send_commands('add_values', newexpr)

    @qtsig('')
    def on_deleteWatch_clicked(self):
        item = self.watchView.currentItem()
        if not item:
            return
        expr = item.text(0)
        delexpr = self.client.serialize([str(expr) + ':default'])
        self.client.send_commands('del_values', delexpr)

    @qtsig('')
    def on_oneShotEval_clicked(self):
        expr, ok = QInputDialog.getText(
            self, self.tr('Evaluate an expression'),
            self.tr('Expression to evaluate:'))
        if not ok:
            return
        self.client.send_command('get_value', True)
        expr = str(expr) + ':default'
        ret = self.client.unserialize(self.client.send_command(expr))
        QMessageBox.information(self, self.tr('Result'), ret)

    def on_outView_anchorClicked(self, url):
        """Called when the user clicks a link in the out view."""
        url = str(url.toString())
        if url.startswith('exec:'):
            self.run_script('None', url[5:])
        elif url.startswith('edit:'):
            # XXX check if file is already open
            editor = self.on_actionUserEditor_triggered()
            editor.openFile(url[5:])
        elif url.startswith('trace:'):
            self.showTraceback(url[6:])
        else:
            print 'Strange anchor in outView: ' + url

    def showTraceback(self, tb):
        assert tb.startswith('Traceback')
        # split into frames and message
        frames = []
        message = ''
        for line in tb.splitlines():
            if line.startswith('        '):
                name, v = line.split('=', 1)
                curframe[2][name.strip()] = v.strip()
            elif line.startswith('    '):
                curframe[1] = line.strip()
            elif line.startswith('  '):
                curframe = [line.strip(), '', {}]
                frames.append(curframe)
            elif not line.startswith('Traceback'):
                message += line
        # show traceback window
        dlg = dialogFromUi(self, 'traceback.ui')
        button = QPushButton('To clipboard', dlg)
        dlg.buttonBox.addButton(button, QDialogButtonBox.ActionRole)
        def copy():
            QApplication.clipboard().setText(tb+'\n', QClipboard.Selection)
            QApplication.clipboard().setText(tb+'\n', QClipboard.Clipboard)
        self.connect(button, SIGNAL('clicked()'), copy)
        dlg.message.setText(message)
        dlg.tree.setFont(self.outView.font())
        boldfont = QFont(self.outView.font())
        boldfont.setBold(True)
        for file, line, bindings in frames:
            item = QTreeWidgetItem(dlg.tree, [file])
            item.setFirstColumnSpanned(True)
            item = QTreeWidgetItem(dlg.tree, [line])
            item.setFirstColumnSpanned(True)
            item.setFont(0, boldfont)
            for var, value in bindings.iteritems():
                bitem = QTreeWidgetItem(item, ['', var, value])
        dlg.show()

    @qtsig('')
    def on_actionPrintPaper_triggered(self):
        dlg = dialogFromUi(self, 'progress.ui')
        dlg.label.setText('Writing paper...')
        dlg.show()
        QApplication.processEvents()
        try:
            authors = ['--author', 'Robert Georgii\\\\{ZWE FRM-II, TU M\\"unchen}']
            sysname = ['--sysname', 'MIRA']
            try:
                # get username and sample info from last entered proposal
                settings = QSettings('nicostools')
                settings.beginGroup('proposalinput')
                user = str(settings.value('presets/user').toString()).strip()
                sample = str(settings.value('presets/sampleinfo').toString()).strip()
                settings.endGroup()

                if user and user != 'test':
                    authors += ['--author', user]
                if sample:
                    sysname = ['--sysname', sample]
            except Exception:
                authors += ['--author', 'Georg Brandl\\\\{Physik Department '
                            'E21, TU M\\"unchen}']
            dlg.progress.setValue(20)
            QApplication.processEvents()

            import subprocess
            scigendir = path.join(path.dirname(__file__), '..', '..', 'scigen')
            cwd = os.getcwd()
            try:
                os.chdir(scigendir)
                p = subprocess.Popen([path.join(scigendir, 'make-latex.pl')]
                                     + authors + sysname +
                                     ['--file', '/tmp/paper.ps'],
                                     stdin=subprocess.PIPE)
                p.communicate()
            finally:
                os.chdir(cwd)
            dlg.label.setText('Generating plots...')
            dlg.progress.setValue(70)
            QApplication.processEvents()
            subprocess.Popen(['ps2pdf', '/tmp/paper.ps', '/tmp/paper.pdf']).wait()
            dlg.label.setText('Calling PDF viewer...')
            dlg.progress.setValue(85)
            QApplication.processEvents()
            subprocess.Popen(['acroread', '/tmp/paper.pdf'])
            time.sleep(5)
            dlg.progress.setValue(100)
            QApplication.processEvents()
            time.sleep(0.5)
        except Exception, err:
            print 'Error:', err
        finally:
            dlg.destroy()

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
                    QMessageBox.information(self, self.tr('Error'),
                                            self.tr('Not a valid regex.'))
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

    @qtsig('')
    def on_clearQueue_clicked(self):
        if self.client.send_commands('unqueue_all_prgs'):
            self.scriptQueue.clear()

    @qtsig('')
    def on_deleteQueueItem_clicked(self):
        item = self.queueView.currentItem()
        if not item:
            return
        reqno = item.data(Qt.UserRole).toInt()
        if self.client.send_commands('unqueue_prg', str(reqno[0])):
            self.scriptQueue.remove(reqno[0])


class ScriptQueue(object):
    def __init__(self, frame, view):
        self._no2item = {}   # mapping from request number to list widget item
        self._frame = frame
        self._view = view
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.connect(self._timer, SIGNAL('timeout()'), self._timeout)

    def _format_item(self, request):
        script = request['script']
        if len(script) > 100:
            return script[:100] + '...'
        return script

    def _timeout(self):
        self._frame.show()

    def append(self, request):
        item = QListWidgetItem(self._format_item(request))
        item.setData(Qt.UserRole, QVariant(request['reqno']))
        self._no2item[request['reqno']] = item
        self._view.addItem(item)
        # delay showing the frame for 20 msecs, so that it doesn't flicker in
        # and out if the script is immediately taken out of the queue again
        self._timer.start(20)

    def remove(self, reqno):
        item = self._no2item.pop(reqno, None)
        if item is None:
            return
        item = self._view.takeItem(self._view.row(item))
        if not self._no2item:
            self._timer.stop()
            self._frame.hide()
        return item

    def clear(self):
        self._frame.hide()
        self._view.clear()
        self._no2item.clear()

    def __nonzero__(self):
        return bool(self._no2item)


def main(argv):
    # Import the compiled resource file to register resources
    import nicos.gui.gui_rc

    app = QApplication(argv)
    app.setOrganizationName('frm2')
    app.setApplicationName('nicos-ng')

    mainwindow = MainWindow()

    if len(argv) > 1:
        cdata = parse_conndata(argv[1])
        if cdata:
            mainwindow.setConnData(*cdata)
    mainwindow.show()

    return app.exec_()
