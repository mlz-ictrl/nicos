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

"""NICOS GUI main window and application startup."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time
import cPickle as pickle

from PyQt4.QtCore import Qt, QObject, QTimer, QSize, QVariant, QStringList, SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig
from PyQt4.QtGui import QApplication, QMainWindow, QDialog, QMessageBox, \
     QLabel, QSystemTrayIcon, QStyle, QPixmap, QMenu, QIcon, QAction, \
     QFontDialog, QColorDialog, QFont, QColor

from nicos import __version__ as nicos_version
from nicos.gui.data import DataHandler
from nicos.gui.utils import DlgUtils, SettingGroup, \
     parseConnectionData, getXDisplay, dialogFromUi, loadUi
from nicos.gui.client import NicosDaemon, NicosClient, DEFAULT_PORT, \
     STATUS_INBREAK, STATUS_IDLE, STATUS_IDLEEXC
from nicos.gui.panels import hsplit, vsplit, panel, window, AuxiliaryWindow, \
     createWindowItem
from nicos.gui.panels.console import ConsolePanel
from nicos.gui.settings import SettingsDialog
from nicos.cache.utils import cache_load


class NicosGuiClient(NicosClient, QObject):
    siglist = ['connected', 'disconnected', 'broken', 'failed', 'error'] + \
              NicosDaemon.daemon_events.keys()

    def __init__(self, parent):
        QObject.__init__(self, parent)
        NicosClient.__init__(self)

    def signal(self, type, *args):
        self.emit(SIGNAL(type), *args)


class MainWindow(QMainWindow, DlgUtils):
    def __init__(self):
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

        # connect the client's events
        self.client = NicosGuiClient(self)
        self.connect(self.client, SIGNAL('error'), self.on_client_error)
        self.connect(self.client, SIGNAL('broken'), self.on_client_broken)
        self.connect(self.client, SIGNAL('failed'), self.on_client_failed)
        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)
        self.connect(self.client, SIGNAL('disconnected'), self.on_client_disconnected)
        self.connect(self.client, SIGNAL('status'), self.on_client_status)

        # data handling setup
        self.data = DataHandler(self.client)

        default_profile_uid = '07139e62-d244-11e0-b94b-00199991c246'
        default_profile_config = ('Default', [
            vsplit(
                hsplit(
                    panel('nicos.gui.panels.status.ScriptStatusPanel'),
                    panel('nicos.gui.panels.watch.WatchPanel')),
                panel('nicos.gui.panels.console.ConsolePanel'),
                ),
            window('Errors/warnings', 'errors', True,
                   panel('nicos.gui.panels.errors.ErrorPanel')),
            window('Editor', 'editor', False,
                   panel('nicos.gui.panels.editor.EditorPanel')),
            window('Live data', 'live', True,
                   panel('nicos.gui.panels.live.LiveDataPanel')),
            ])

        # load profiles and current profile
        self.pgroup = SettingGroup('Application')
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

        config = self.profiles[self.curprofile][1]
        createWindowItem(config[0], self, self.centralLayout)

        if len(self.splitstate) == len(self.splitters):
            for sp, st in zip(self.splitters, self.splitstate):
                sp.restoreState(st.toByteArray())

        for i, wconfig in enumerate(config[1:]):
            action = QAction(QIcon(':/' + wconfig[1]), wconfig[0], self)
            self.toolBarWindows.addAction(action)
            self.menuWindows.addAction(action)
            def callback(on, i=i):
                self.createWindow(i)
            self.connect(action, SIGNAL('triggered(bool)'), callback)

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

        # setup state members
        self.current_status = None
        self.action_start_time = None
        self.setStatus('disconnected')

    def createWindow(self, type):
        wconfig = self.profiles[self.curprofile][1][type+1]
        if wconfig[2] and self.windows.get(type):
            return
        window = AuxiliaryWindow(self, type, wconfig, self.curprofile)
        window.setWindowIcon(QIcon(':/' + wconfig[1]))
        self.windows.setdefault(type, set()).add(window)
        self.connect(window, SIGNAL('closed'), self.on_auxWindow_closed)
        window.show()

    def on_auxWindow_closed(self, window):
        self.windows[window.type].discard(window)

    def setConnData(self, login, host, port):
        self.connectionData['login'] = login
        self.connectionData['host'] = host
        self.connectionData['port'] = port

    def _reconnect(self):
        self.client.connect(self.connectionData, self.lastpasswd)

    def show(self):
        QMainWindow.show(self)
        if self.autoconnect:
            self.on_actionConnect_triggered(True)

    def loadSettings(self, settings):
        # geometry and window appearance
        geometry = settings.value('geometry').toByteArray()
        self.restoreGeometry(geometry)
        windowstate = settings.value('windowstate').toByteArray()
        self.restoreState(windowstate)
        self.splitstate = settings.value('splitstate').toList()
        self.user_font = QFont(settings.value('font'))
        color = QColor(settings.value('color'))
        if color.isValid():
            self.user_color = color
        else:
            self.user_color = Qt.white

        # state of connection, editor and analysis windows
        self.autoconnect = settings.value('autoconnect').toBool()

        self.connectionData['host'] = str(settings.value(
            'host', QVariant('localhost')).toString())
        self.connectionData['port'] = settings.value(
            'port', QVariant(DEFAULT_PORT)).toInt()[0]
        self.connectionData['login'] = str(settings.value(
            'login', QVariant('guest')).toString())
        self.servers = settings.value('servers').toStringList()

        self.instrument = settings.value('instrument').toString()
        self.scriptpath = settings.value('scriptpath').toString()
        self.confirmexit = settings.value('confirmexit',
                                          QVariant(True)).toBool()
        self.showtrayicon = settings.value('showtrayicon',
                                           QVariant(True)).toBool()
        self.autoreconnect = settings.value('autoreconnect',
                                            QVariant(True)).toBool()

        self.update()

        auxstate = settings.value('auxwindows').toList()
        for type in [x.toInt()[0] for x in auxstate]:
            self.createWindow(type)
        # XXX restore e.g. last edited files

    def saveSettings(self, settings):
        settings.setValue('geometry', QVariant(self.saveGeometry()))
        settings.setValue('windowstate', QVariant(self.saveState()))
        settings.setValue('splitstate',
                          QVariant([sp.saveState() for sp in self.splitters]))
        auxstate = []
        for type, windows in self.windows.iteritems():
            for window in windows:
                auxstate.append(type)
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

        for wtype, windows in self.windows.items():
            for window in list(windows):
                if not window.close():
                    event.ignore()
                    return

        if self.client.connected:
            self.client.disconnect()

        event.accept()

    def setTitlebar(self, connected, setups=[]):
        inststr = str(self.instrument) or 'NICOS'
        if connected:
            hoststr = '%s at %s:%s' % (self.connectionData['login'],
                                       self.client.host, self.client.port)
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
                msg = 'Script is not interrupted.'
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
        # propagate info to all components
        self.client.signal('initstatus', initstatus)

        # set focus to command input, if present
        for panel in self.panels:
            if isinstance(panel, ConsolePanel) and panel.hasinput:
                panel.commandInput.setFocus()

    def on_client_status(self, data):
        status, line = data
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

    def on_client_cache(self, (time, key, op, value)):
        if key == 'session/mastersetupexplicit':
            self.setTitlebar(True, cache_load(value))

    def on_trayIcon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.activateWindow()

    @qtsig('')
    def on_actionAbout_triggered(self):
        QMessageBox.information(
            self, 'About this application', 'NICOS-NG GUI client version %s, '
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
                port = DEFAULT_PORT
            self.connectionData['host'] = host
            self.connectionData['port'] = port
            self.servers.append('%s:%s' % (host, port))
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
    import nicos.gui.gui_rc

    app = QApplication(argv)
    app.setOrganizationName('nicos')
    app.setApplicationName('gui')

    mainwindow = MainWindow()

    if len(argv) > 1:
        cdata = parseConnectionData(argv[1])
        if cdata:
            mainwindow.setConnData(*cdata)
    mainwindow.show()

    return app.exec_()
