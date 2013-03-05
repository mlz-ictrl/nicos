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

"""NICOS GUI main window and application startup."""

from __future__ import with_statement

__version__ = "$Revision$"

import time
import subprocess
from os import path
import cPickle as pickle

from PyQt4.QtGui import QApplication, QMainWindow, QDialog, QMessageBox, \
     QLabel, QSystemTrayIcon, QStyle, QPixmap, QMenu, QIcon, QAction, \
     QFontDialog, QColorDialog, QDialogButtonBox, QWidget, QFrame, QVBoxLayout
from PyQt4.QtCore import Qt, QObject, QTimer, QSize, QVariant, QStringList, \
     SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig

from nicos import nicos_version
from nicos.utils import parseConnectionString, importString
from nicos.clients.base import NicosClient
from nicos.clients.gui.data import DataHandler
from nicos.clients.gui.utils import DlgUtils, SettingGroup, loadBasicWindowSettings, \
     getXDisplay, dialogFromUi, loadUi
from nicos.clients.gui.config import window, panel
from nicos.clients.gui.panels import AuxiliaryWindow, createWindowItem
from nicos.clients.gui.panels.console import ConsolePanel
from nicos.clients.gui.helpwin import HelpWindow
from nicos.clients.gui.settings import SettingsDialog
from nicos.protocols.cache import cache_load
from nicos.protocols.daemon import DAEMON_EVENTS, DEFAULT_PORT, \
     STATUS_INBREAK, STATUS_IDLE, STATUS_IDLEEXC


class NicosGuiClient(NicosClient, QObject):
    siglist = ['connected', 'disconnected', 'broken', 'failed', 'error'] + \
              DAEMON_EVENTS.keys()

    def __init__(self, parent):
        QObject.__init__(self, parent)
        NicosClient.__init__(self)

    def signal(self, name, *args):
        self.emit(SIGNAL(name), *args)


class MainWindow(QMainWindow, DlgUtils):
    def __init__(self, configfile):
        QMainWindow.__init__(self)
        DlgUtils.__init__(self, 'NICOS')
        loadUi(self, 'main.ui')

        # window for displaying errors
        self.errorWindow = None

        # log messages sent by the server
        self.messages = []

        # set-up the initial connection data
        self.connectionData = dict(
            host    = '',
            port    = 1301,
            login   = '',
            display = getXDisplay(),
        )

        # state members
        self.current_status = None
        self.action_start_time = None

        # connect the client's events
        self.client = NicosGuiClient(self)
        self.connect(self.client, SIGNAL('error'), self.on_client_error)
        self.connect(self.client, SIGNAL('broken'), self.on_client_broken)
        self.connect(self.client, SIGNAL('failed'), self.on_client_failed)
        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)
        self.connect(self.client, SIGNAL('disconnected'),
                     self.on_client_disconnected)
        self.connect(self.client, SIGNAL('status'), self.on_client_status)
        self.connect(self.client, SIGNAL('showhelp'), self.on_client_showhelp)
        self.connect(self.client, SIGNAL('clientexec'), self.on_client_clientexec)
        self.connect(self.client, SIGNAL('plugplay'), self.on_client_plugplay)
        self.connect(self.client, SIGNAL('watchdog'), self.on_client_watchdog)

        # data handling setup
        self.data = DataHandler(self.client)

        # load profiles and current profile
        self.pgroup = SettingGroup('Application')

        with open(configfile, 'rb') as fp:
            configcode = fp.read()
        ns = {}
        exec configcode in ns
        default_profile_uid = ns['default_profile_uid']
        default_profile_config = ns['default_profile_config']

        with self.pgroup as settings:
            profiles = str(settings.value('profiles').toString())
            if not profiles:
                profiles = {}
            else:
                profiles = pickle.loads(profiles)
            if default_profile_uid not in profiles:
                profiles[default_profile_uid] = default_profile_config
            self.profiles = profiles
            curprofile = str(settings.value('curprofile').toString())
            if not curprofile or curprofile not in self.profiles:
                curprofile = default_profile_uid
            self.curprofile = curprofile

        # determine if there is an editor window type, because we would like to
        # have a way to open files from a console panel later
        self.editor_wintype = None
        for i, winconfig in enumerate(self.profiles[self.curprofile][1]):
            if isinstance(winconfig, window) and \
               isinstance(winconfig[3], panel) and \
               winconfig[3][0] == 'nicos.clients.gui.panels.editor.EditorPanel':
                self.editor_wintype = i - 1

        # additional panels
        self.panels = []
        self.splitters = []
        self.windowtypes = []
        self.windows = {}
        self.mainwindow = self

        # load saved settings for current profile
        self.sgroup = SettingGroup('MainWindow-' + self.curprofile)
        with self.sgroup as settings:
            self.loadSettings(settings)

        windowconfig = self.profiles[self.curprofile][1]
        widget = createWindowItem(windowconfig[0], self)
        self.centralLayout.addWidget(widget)

        if len(self.splitstate) == len(self.splitters):
            for sp, st in zip(self.splitters, self.splitstate):
                sp.restoreState(st.toByteArray())

        for i, wconfig in enumerate(windowconfig[1:]):
            action = QAction(QIcon(':/' + wconfig[1]), wconfig[0], self)
            self.toolBarWindows.addAction(action)
            self.menuWindows.addAction(action)
            def window_callback(on, i=i):
                self.createWindow(i)
            self.connect(action, SIGNAL('triggered(bool)'), window_callback)

        # load tools menu
        toolconfig = self.profiles[self.curprofile][2]
        for i, tconfig in enumerate(toolconfig):
            action = QAction(tconfig[0], self)
            self.menuTools.addAction(action)
            def tool_callback(on, i=i):
                self.runTool(i)
            self.connect(action, SIGNAL('triggered(bool)'), tool_callback)

        # timer for reconnecting
        self.reconnectTimer = QTimer()
        self.reconnectTimer.setSingleShot(True)
        self.connect(self.reconnectTimer, SIGNAL('timeout()'), self._reconnect)
        self._reconnecting = False

        # setup tray icon
        self.trayIcon = QSystemTrayIcon(self)
        self.connect(self.trayIcon,
                     SIGNAL('activated(QSystemTrayIcon::ActivationReason)'),
                     self.on_trayIcon_activated)
        self.trayMenu = QMenu(self)
        nameAction = self.trayMenu.addAction(self.instrument)
        nameAction.setEnabled(False)
        self.trayMenu.addSeparator()
        toggleAction = self.trayMenu.addAction('Hide main window')
        toggleAction.setCheckable(True)
        self.connect(toggleAction, SIGNAL('triggered(bool)'),
                     lambda hide: self.setVisible(not hide))
        self.trayIcon.setContextMenu(self.trayMenu)

        self.statusLabel = QLabel('', self)
        self.statusLabel.setPixmap(QPixmap(':/disconnected'))
        self.statusLabel.setMargin(5)
        self.statusLabel.setMinimumSize(QSize(30, 10))
        self.toolBarMain.addWidget(self.statusLabel)

        # help window
        self.helpWindow = None
        # watchdog window
        self.watchdogWindow = None

        # create initial state
        self.setStatus('disconnected')

    def createWindow(self, wtype):
        wconfig = self.profiles[self.curprofile][1][wtype+1]
        #if wconfig[2] and self.windows.get(wtype):  # we don't support
                                                     # multi-instance anymore
        if self.windows.get(wtype):
            iter(self.windows[wtype]).next().activateWindow()
            return
        window = AuxiliaryWindow(self, wtype, wconfig, self.curprofile)
        window.setWindowIcon(QIcon(':/' + wconfig[1]))
        self.windows.setdefault(wtype, set()).add(window)
        self.connect(window, SIGNAL('closed'), self.on_auxWindow_closed)
        for panel in window.panels:
            panel.updateStatus(self.current_status)
        window.show()
        return window

    def on_auxWindow_closed(self, window):
        self.windows[window.type].discard(window)

    def runTool(self, ttype):
        tconfig = self.profiles[self.curprofile][2][ttype]
        try:
            # either it's a class name
            toolclass = importString(tconfig[1])
        except ImportError:
            # or it's a system command
            subprocess.Popen(tconfig[1], shell=True)
        else:
            dialog = toolclass(self, **tconfig[2])
            dialog.setWindowModality(Qt.NonModal)
            dialog.show()

    def setConnData(self, login, passwd, host, port):
        self.connectionData['login'] = login
        self.connectionData['host'] = host
        self.connectionData['port'] = port

    def _reconnect(self):
        self.client.connect(self.connectionData, self.lastpasswd)

    def show(self):
        QMainWindow.show(self)
        if self.autoconnect and not self.client.connected:
            self.on_actionConnect_triggered(True)

    def loadSettings(self, settings):
        # geometry and window appearance
        loadBasicWindowSettings(self, settings)

        self.autoconnect = settings.value('autoconnect').toBool()

        self.connectionData['host'] = str(settings.value(
            'host', QVariant('localhost')).toString())
        self.connectionData['port'] = settings.value(
            'port', QVariant(DEFAULT_PORT)).toInt()[0]
        self.connectionData['login'] = str(settings.value(
            'login', QVariant('guest')).toString())
        self.servers = settings.value('servers').toStringList()

        self.instrument = settings.value('instrument').toString()
        self.confirmexit = settings.value('confirmexit',
                                          QVariant(True)).toBool()
        self.showtrayicon = settings.value('showtrayicon',
                                           QVariant(True)).toBool()
        self.autoreconnect = settings.value('autoreconnect',
                                            QVariant(True)).toBool()

        self.update()

        auxstate = settings.value('auxwindows').toList()
        for wtype in [x.toInt()[0] for x in auxstate]:
            self.createWindow(wtype)

    def saveSettings(self, settings):
        settings.setValue('geometry', QVariant(self.saveGeometry()))
        settings.setValue('windowstate', QVariant(self.saveState()))
        settings.setValue('splitstate',
                          QVariant([sp.saveState() for sp in self.splitters]))
        auxstate = []
        for wtype, windows in self.windows.iteritems():
            for _win in windows:
                auxstate.append(wtype)
        settings.setValue('auxwindows', QVariant(auxstate))
        settings.setValue('autoconnect', QVariant(self.client.connected))
        servers = sorted(set(map(str, self.servers)))
        settings.setValue('servers', QVariant(QStringList(servers)))
        settings.setValue('font', QVariant(self.user_font))
        settings.setValue('color', QVariant(self.user_color))

    def closeEvent(self, event):
        if self.confirmexit and QMessageBox.question(
            self, 'Quit', 'Do you really want to quit?',
            QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            event.ignore()
            return

        for panel in self.panels:
            if not panel.requestClose():
                event.ignore()
                return

        with self.sgroup as settings:
            self.saveSettings(settings)
        for panel in self.panels:
            with panel.sgroup as settings:
                panel.saveSettings(settings)

        for windows in self.windows.values():
            for window in list(windows):
                if not window.close():
                    event.ignore()
                    return

        if self.helpWindow:
            self.helpWindow.close()

        if self.client.connected:
            self.client.disconnect()

        event.accept()

    def setTitlebar(self, connected, setups=()):
        inststr = str(self.instrument) or 'NICOS'
        if connected:
            hoststr = '%s at %s:%s' % (self.client.login, self.client.host,
                                       self.client.port)
            self.setWindowTitle('%s [%s] - %s' % (inststr, ', '.join(setups),
                                                  hoststr))
        else:
            self.setWindowTitle('%s - disconnected' % inststr)

    def setStatus(self, status, exception=False):
        if status == self.current_status:
            return
        if self.action_start_time and self.current_status == 'running' and \
           status in ('idle', 'interrupted') and \
           time.time() - self.action_start_time > 20:
            # show a visual indication of what happened
            if status == 'interrupted':
                msg = 'Script is now interrupted.'
            elif exception:
                msg = 'Script has exited with an error.'
            else:
                msg = 'Script has finished.'
            self.trayIcon.showMessage(self.instrument, msg)
            self.action_start_time = None
        self.current_status = status
        isconnected = status != 'disconnected'
        self.actionConnect.setChecked(isconnected)
        if isconnected:
            self.actionConnect.setText('Disconnect')
        else:
            self.actionConnect.setText('Connect to server...')
            self.setTitlebar(False)
        # new status icon
        pixmap = QPixmap(':/' + status + ('exc' if exception else ''))
        self.statusLabel.setPixmap(pixmap)
        self.statusLabel.setToolTip('Script status: %s' % status)
        newicon = QIcon()
        newicon.addPixmap(pixmap, QIcon.Disabled)
        self.trayIcon.setIcon(newicon)
        self.trayIcon.setToolTip('%s status: %s' % (self.instrument, status))
        if self.showtrayicon:
            self.trayIcon.show()
        # propagate to panels
        for panel in self.panels:
            panel.updateStatus(status, exception)
        for wlist in self.windows.itervalues():
            for win in wlist:
                for panel in win.panels:
                    panel.updateStatus(status, exception)

    def on_client_error(self, problem, exc=None):
        if exc is not None:
            print 'Exception:', exc
        problem = time.strftime('[%m-%d %H:%M:%S] ') + problem
        if self.errorWindow is None:
            self.errorWindow = QDialog(self)
            def reset_errorWindow():
                self.errorWindow = None
            self.errorWindow.connect(self.errorWindow, SIGNAL('accepted()'),
                                     reset_errorWindow)
            loadUi(self.errorWindow, 'error.ui')
            self.errorWindow.setWindowTitle('Connection error')
            self.errorWindow.errorText.setText(problem)
            self.errorWindow.iconLabel.setPixmap(
                self.style().standardIcon(QStyle.SP_MessageBoxWarning).
                pixmap(32, 32))
            self.errorWindow.show()
        else:
            self.errorWindow.errorText.setText(
                self.errorWindow.errorText.text() + '\n' + problem)

    def on_client_broken(self, problem):
        self.on_client_error(problem)
        if self.autoreconnect:
            self._reconnecting = True
            self.reconnectTimer.start(500)  # half a second

    def on_client_failed(self, problem):
        if not self._reconnecting:
            self.on_client_error(problem)
        elif self.autoreconnect:
            self.reconnectTimer.start(500)

    def on_client_connected(self):
        self.setStatus('idle')
        self._reconnecting = False

        # get all server status info
        initstatus = self.client.ask('getstatus')
        # handle setups
        self.setTitlebar(True, initstatus[4])
        # handle initial status
        self.on_client_status(initstatus[0])
        # propagate info to all components
        self.client.signal('initstatus', initstatus)

        # set focus to command input, if present
        for panel in self.panels:
            if isinstance(panel, ConsolePanel) and panel.hasinput:
                panel.commandInput.setFocus()

    def on_client_status(self, data):
        status = data[0]
        if status == STATUS_IDLE:
            self.setStatus('idle')
        elif status == STATUS_IDLEEXC:
            self.setStatus('idle', exception=True)
        elif status != STATUS_INBREAK:
            self.setStatus('running')
        else:
            self.setStatus('interrupted')

    def on_client_disconnected(self):
        self.setStatus('disconnected')

    def on_client_showhelp(self, data):
        if self.helpWindow is None:
            self.helpWindow = HelpWindow(self, self.client)
        self.helpWindow.showHelp(data)

    def on_client_clientexec(self, data):
        # currently used for client-side plot using matplotlib; data is
        # (funcname, args, ...)
        plot_func_path = data[0]
        try:
            modname, funcname = plot_func_path.rsplit('.', 1)
            func = getattr(__import__(modname, None, None, [funcname]),
                           funcname)
            func(*data[1:])
        except Exception, err:
            print 'Error during clientexec:', err

    def on_client_plugplay(self, data):
        if data[0] == 'added':
            window = dialogFromUi(self, 'plugplay.ui')
            window.titlestring.setText('New sample environment detected')
            window.message.setText(
                'A new sample environment %shas been detected.  '
                'Click Apply to load the corresponding setup (%s).'
                % (data[2] and '(%s) ' % data[2] or '', data[1]))
            def react(btn):
                if btn is window.buttonBox.button(QDialogButtonBox.Ignore):
                    window.reject()
                else:
                    self.client.tell('queue', '', 'AddSetup(%r)' % data[1])
                    window.accept()
            window.connect(window.buttonBox,
                           SIGNAL('clicked(QAbstractButton*)'), react)
            window.show()

    def on_client_watchdog(self, data):
        if self.watchdogWindow is None:
            dlg = self.watchdogWindow = dialogFromUi(self, 'watchdog.ui')
            dlg.frame = QFrame(dlg)
            dlg.scrollArea.setWidget(dlg.frame)
            dlg.frame.setLayout(QVBoxLayout())
            dlg.frame.layout().setContentsMargins(0, 0, 10, 0)
            dlg.frame.layout().addStretch()
            def btn(button):
                if dlg.buttonBox.buttonRole(button) == QDialogButtonBox.ResetRole:
                    for w in dlg.frame.children():
                        if isinstance(w, QWidget):
                            w.hide()
                else:
                    dlg.close()
            dlg.connect(dlg.buttonBox, SIGNAL('clicked(QAbstractButton*)'), btn)
        else:
            dlg = self.watchdogWindow
        w = QWidget(dlg.frame)
        loadUi(w, 'watchdog_item.ui')
        dlg.frame.layout().insertWidget(dlg.frame.layout().count()-1, w)
        if data[0] == 'warning':
            w.datelabel.setText('Watchdog alert - %s' %
                time.strftime('%Y-%m-%d %H:%S', time.localtime(data[1])))
            w.messagelabel.setText(data[2])
        elif data[0] == 'action':
            w.datelabel.setText('Watchdog action - %s' %
                time.strftime('%Y-%m-%d %H:%S', time.localtime(data[1])))
            w.messagelabel.setText('Executing action:\n' + data[2])
        dlg.show()

    def on_client_cache(self, (time, key, op, value)):
        if key == 'session/mastersetupexplicit':
            self.setTitlebar(True, cache_load(value))

    def on_trayIcon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.activateWindow()

    @qtsig('')
    def on_actionNicosHelp_triggered(self):
        self.client.eval('session.showHelp("index")', None)

    @qtsig('')
    def on_actionAbout_triggered(self):
        QMessageBox.information(
            self, 'About this application', 'NICOS GUI client version %s, '
            'written by Georg Brandl.\n\nServer: ' % nicos_version
            + (self.client.connected and self.client.version or
               'not connected'))

    @qtsig('')
    def on_actionAboutQt_triggered(self):
        QMessageBox.aboutQt(self)

    @qtsig('bool')
    def on_actionConnect_triggered(self, on):
        # connection or disconnection request?
        if not on:
            self.client.disconnect()
            return

        addr = self.connectionData['host']
        if self.connectionData['port'] != DEFAULT_PORT:
            addr += ':%s' % self.connectionData['port']

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
                port = DEFAULT_PORT
            self.connectionData['host'] = host
            self.connectionData['port'] = port
            self.servers.append('%s:%s' % (host, port))
        if authdlg.saveDefault.isChecked():
            with self.sgroup as settings:
                settings.setValue('host', QVariant(self.connectionData['host']))
                settings.setValue('port', QVariant(self.connectionData['port']))
                settings.setValue('login',
                                  QVariant(self.connectionData['login']))
        self.connectionData['login'] = str(authdlg.userName.text())
        passwd = str(authdlg.password.text())
        self.client.connect(self.connectionData, passwd)
        self.lastpasswd = passwd

    @qtsig('')
    def on_actionPreferences_triggered(self):
        dlg = SettingsDialog(self)
        ret = dlg.exec_()
        if ret == QDialog.Accepted:
            dlg.saveSettings()

    @qtsig('')
    def on_actionFont_triggered(self):
        font, ok = QFontDialog.getFont(self.user_font, self)
        if not ok:
            return
        for panel in self.panels:
            panel.setCustomStyle(font, self.user_color)
        self.user_font = font

    @qtsig('')
    def on_actionColor_triggered(self):
        color = QColorDialog.getColor(self.user_color, self)
        if not color.isValid():
            return
        for panel in self.panels:
            panel.setCustomStyle(self.user_font, color)
        self.user_color = color


def main(argv):
    # Import the compiled resource file to register resources
    import nicos.clients.gui.gui_rc #pylint: disable=W0612

    app = QApplication(argv)
    app.setOrganizationName('nicos')
    app.setApplicationName('gui')

    # XXX implement proper argument parsing
    configfile = path.join(path.dirname(__file__), 'defconfig.py')
    if '-c' in argv:
        idx = argv.index('-c')
        configfile = argv[idx+1]
        del argv[idx:idx+2]

    mainwindow = MainWindow(configfile)

    if len(argv) > 1:
        cdata = parseConnectionString(argv[1], DEFAULT_PORT)
        if cdata:
            mainwindow.setConnData(*cdata)
            if len(argv) > 2:
                mainwindow.client.connect(mainwindow.connectionData, argv[2])
    mainwindow.show()

    return app.exec_()
