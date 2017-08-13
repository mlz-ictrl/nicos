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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI main window."""

import sys
import traceback
from time import strftime, time as currenttime

from nicos.guisupport.qt import pyqtSignal, pyqtSlot, Qt, QTimer, QSize, \
    QApplication, QMainWindow, QMessageBox, QDialog, QLabel, QSystemTrayIcon, \
    QPixmap, QMenu, QIcon, QAction, QFontDialog, QColorDialog, QWebView

try:
    from sshtunnel import BaseSSHTunnelForwarderError, SSHTunnelForwarder
except ImportError:
    SSHTunnelForwarder = None

from nicos import nicos_version
from nicos.utils import importString
from nicos.core.utils import ADMIN
from nicos.clients.base import ConnectionData
from nicos.clients.gui.data import DataHandler
from nicos.clients.gui.client import NicosGuiClient
from nicos.clients.gui.utils import DlgUtils, SettingGroup, loadUi, \
    loadBasicWindowSettings, loadUserStyle, splitTunnelString
from nicos.clients.gui.panels import AuxiliaryWindow, createWindowItem
from nicos.clients.gui.panels.console import ConsolePanel
from nicos.clients.gui.tools import createToolMenu, startStartupTools
from nicos.clients.gui.dialogs.auth import ConnectionDialog
from nicos.clients.gui.dialogs.error import ErrorDialog
from nicos.clients.gui.dialogs.pnp import PnPSetupQuestion
from nicos.clients.gui.dialogs.help import HelpWindow
from nicos.clients.gui.dialogs.debug import DebugConsole
from nicos.clients.gui.dialogs.settings import SettingsDialog
from nicos.clients.gui.dialogs.watchdog import WatchdogDialog
from nicos.protocols.daemon import STATUS_INBREAK, STATUS_IDLE, \
    STATUS_IDLEEXC, BREAK_NOW
from nicos.pycompat import iteritems, listvalues, text_type

from nicos.clients.gui.config import tabbed


class MainWindow(DlgUtils, QMainWindow):

    # Emitted when a panel generates code that an editor panel should add.
    codeGenerated = pyqtSignal(object)

    def __init__(self, log, gui_conf, viewonly=False, tunnel=''):
        QMainWindow.__init__(self)
        DlgUtils.__init__(self, 'NICOS')
        loadUi(self, 'main.ui')

        # set app icon in multiple sizes
        icon = QIcon()
        icon.addFile(':/appicon')
        icon.addFile(':/appicon-16')
        icon.addFile(':/appicon-48')
        self.setWindowIcon(icon)

        if tunnel and SSHTunnelForwarder is None:
            self.showError('You want to establish a connection to NICOS via '
                           "a SSH tunnel, but the 'sshtunnel' module is not "
                           'installed. The tunneling feature will disabled.')
        self.tunnel = tunnel if SSHTunnelForwarder is not None else ''
        self.tunnelServer = None

        # hide admin label until we are connected as admin
        self.adminLabel.hide()

        # our logger instance
        self.log = log

        # window for displaying errors
        self.errorWindow = None

        # window for "prompt" event confirmation
        self.promptWindow = None

        # debug console window, if opened
        self.debugConsole = None

        # log messages sent by the server
        self.messages = []

        # are we in expert mode?  (always false on startup)
        self.expertmode = False

        # no wrapping at startup
        self.allowoutputlinewrap = False

        # set-up the initial connection data
        self.conndata = ConnectionData(host='localhost', port=1301,
                                       user='guest', password=None,
                                       viewonly=viewonly)

        # state members
        self.current_status = None

        # connect the client's events
        self.client = NicosGuiClient(self, self.log)
        self.client.error.connect(self.on_client_error)
        self.client.broken.connect(self.on_client_broken)
        self.client.failed.connect(self.on_client_failed)
        self.client.connected.connect(self.on_client_connected)
        self.client.disconnected.connect(self.on_client_disconnected)
        self.client.status.connect(self.on_client_status)
        self.client.showhelp.connect(self.on_client_showhelp)
        self.client.clientexec.connect(self.on_client_clientexec)
        self.client.plugplay.connect(self.on_client_plugplay)
        self.client.watchdog.connect(self.on_client_watchdog)
        self.client.prompt.connect(self.on_client_prompt)

        # data handling setup
        self.data = DataHandler(self.client)

        # panel configuration
        self.gui_conf = gui_conf
        self.initDataReaders()
        self.mainwindow = self

        # determine if there is an editor window type, because we would like to
        # have a way to open files from a console panel later
        self.editor_wintype = self.gui_conf.find_panel(
            ('editor.EditorPanel',
             'nicos.clients.gui.panels.editor.EditorPanel'))
        self.history_wintype = self.gui_conf.find_panel(
            ('history.HistoryPanel',
             'nicos.clients.gui.panels.history.HistoryPanel'))

        # additional panels
        self.panels = []
        self.splitters = []
        self.windowtypes = []
        self.windows = {}

        # setting presets
        self.instrument = self.gui_conf.name

        self.createWindowContent()

        # timer for reconnecting
        self.reconnectTimer = QTimer(singleShot=True, timeout=self._reconnect)
        self._reconnect_count = 0
        self._reconnect_time = 0

        # setup tray icon
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.activated.connect(self.on_trayIcon_activated)
        self.trayMenu = QMenu(self)
        nameAction = self.trayMenu.addAction(self.instrument)
        nameAction.setEnabled(False)
        self.trayMenu.addSeparator()
        toggleAction = self.trayMenu.addAction('Hide main window')
        toggleAction.setCheckable(True)
        toggleAction.triggered[bool].connect(
            lambda hide: self.setVisible(not hide))
        self.trayIcon.setContextMenu(self.trayMenu)

        self.statusLabel = QLabel('', self, pixmap=QPixmap(':/disconnected'),
                                  margin=5, minimumSize=QSize(30, 10))
        self.toolBarMain.addWidget(self.statusLabel)

        # help window
        self.helpWindow = None
        # watchdog window
        self.watchdogWindow = None
        # plug-n-play notification windows
        self.pnpWindows = {}

        # create initial state
        self.setStatus('disconnected')

    def createWindowContent(self):
        self.sgroup = SettingGroup('MainWindow')
        with self.sgroup as settings:
            loadUserStyle(self, settings)
            # load saved settings and stored layout for panel config
            self.loadSettings(settings)

        # create panels in the main window
        widget = createWindowItem(self.gui_conf.main_window, self, self, self,
                                  self.log)
        if widget:
            self.centralLayout.addWidget(widget)
        self.centralLayout.setContentsMargins(0, 0, 0, 0)

        # call postInit after creation of all panels
        for panel in self.panels:
            panel.postInit()

        with self.sgroup as settings:
            # geometry and window appearance
            loadBasicWindowSettings(self, settings)
            self.update()
            # load auxiliary windows state
            self.loadAuxWindows(settings)
        if len(self.splitstate) == len(self.splitters):
            for sp, st in zip(self.splitters, self.splitstate):
                sp.restoreState(st)

        if not self.gui_conf.windows:
            self.menuBar().removeAction(self.menuWindows.menuAction())
        for i, wconfig in enumerate(self.gui_conf.windows):
            action = QAction(QIcon(':/' + wconfig.icon), wconfig.name, self)
            self.toolBarWindows.addAction(action)
            self.menuWindows.addAction(action)

            def window_callback(on, i=i):
                self.createWindow(i)
            action.triggered[bool].connect(window_callback)
        if not self.gui_conf.windows:
            self.toolBarWindows.hide()
        else:
            self.toolBarWindows.show()

        createToolMenu(self, self.gui_conf.tools, self.menuTools)
        if isinstance(self.gui_conf.main_window, tabbed) and widget:
            widget.tabChangedTab(0)

    def createWindow(self, wtype):
        # for the history_wintype or editor_wintype
        if wtype == -1:
            return self
        try:
            wconfig = self.gui_conf.windows[wtype]
        except IndexError:
            # config outdated, window type doesn't exist
            return
        if wtype in self.windows:
            window = self.windows[wtype]
            window.activateWindow()
            return window
        window = AuxiliaryWindow(self, wtype, wconfig)
        if window.centralLayout.count():
            window.setWindowIcon(QIcon(':/' + wconfig.icon))
            self.windows[wtype] = window
            window.closed.connect(self.on_auxWindow_closed)
            for panel in window.panels:
                panel.updateStatus(self.current_status)
            window.show()
            return window
        else:
            del window
            return None

    def getPanel(self, panelName):
        for panelobj in self.panels:
            if panelobj.panelName == panelName:
                return panelobj

    def initDataReaders(self):
        try:
            # just import to register all default readers
            # pylint: disable=unused-import, unused-variable
            import nicos.devices.datasinks
        except ImportError:
            pass
        classes = self.gui_conf.options.get('reader_classes', [])
        for clsname in classes:
            try:
                importString(clsname)
            except ImportError:
                pass

    def on_auxWindow_closed(self, window):
        del self.windows[window.type]
        window.deleteLater()

    def setConnData(self, data):
        self.conndata = data

    def _reconnect(self):
        if self._reconnect_count and self.conndata.password is not None:
            self._reconnect_count -= 1
            if self._reconnect_count <= self.client.RECONNECT_TRIES_LONG:
                self._reconnect_time = self.client.RECONNECT_INTERVAL_LONG
            self.client.connect(self.conndata)

    def show(self):
        QMainWindow.show(self)
        if self.autoconnect and not self.client.isconnected:
            self.on_actionConnect_triggered(True)

    def startup(self):
        self.show()
        startStartupTools(self, self.gui_conf.tools)

    def loadSettings(self, settings):
        self.autoconnect = settings.value('autoconnect', True, bool)

        self.connpresets = {}
        # new setting key, with dictionary values
        for (k, v) in iteritems(settings.value('connpresets_new', {})):
            self.connpresets[k] = ConnectionData(**v)
        # if it was empty, try old setting key with list values
        if not self.connpresets:
            for (k, v) in iteritems(settings.value('connpresets', {})):
                self.connpresets[k] = ConnectionData(
                    host=v[0], port=int(v[1]), user=v[2], password=None)
        self.lastpreset = settings.value('lastpreset', '')
        if self.lastpreset in self.connpresets:
            self.conndata = self.connpresets[self.lastpreset].copy()

        self.instrument = settings.value('instrument', self.gui_conf.name)
        self.confirmexit = settings.value('confirmexit', True, bool)
        self.warnwhenadmin = settings.value('warnwhenadmin', True, bool)
        self.showtrayicon = settings.value('showtrayicon', True, bool)
        self.autoreconnect = settings.value('autoreconnect', True, bool)
        self.autosavelayout = settings.value('autosavelayout', True, bool)
        self.allowoutputlinewrap = settings.value('allowoutputlinewrap', False, bool)

        self.update()

    def loadAuxWindows(self, settings):
        open_wintypes = settings.value('auxwindows') or []
        if isinstance(open_wintypes, text_type):
            open_wintypes = [int(w) for w in open_wintypes.split(',')]

        for wtype in open_wintypes:
            if isinstance(wtype, text_type):
                wtype = int(wtype)
            self.createWindow(wtype)

    def saveWindowLayout(self):
        with self.sgroup as settings:
            settings.setValue('geometry', self.saveGeometry())
            settings.setValue('windowstate', self.saveState())
            settings.setValue('splitstate',
                              [sp.saveState() for sp in self.splitters])
            open_wintypes = list(self.windows)
            settings.setValue('auxwindows', open_wintypes)

    def saveSettings(self, settings):
        settings.setValue('autoconnect', self.client.isconnected)
        settings.setValue('connpresets_new', dict((k, v.serialize()) for (k, v)
                                                  in self.connpresets.items()))
        settings.setValue('lastpreset', self.lastpreset)
        settings.setValue('font', self.user_font)
        settings.setValue('color', self.user_color)

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

        if self.autosavelayout:
            self.saveWindowLayout()
        with self.sgroup as settings:
            self.saveSettings(settings)
        for panel in self.panels:
            with panel.sgroup as settings:
                panel.saveSettings(settings)

        for window in listvalues(self.windows):
            if not window.close():
                event.ignore()
                return

        if self.helpWindow:
            self.helpWindow.close()

        self.on_actionConnect_triggered(False)

        event.accept()
        QApplication.instance().quit()

    def setTitlebar(self, connected):
        inststr = str(self.instrument) or 'NICOS'
        if connected:
            hoststr = '%s at %s:%s' % (self.client.login, self.client.host,
                                       self.client.port)
            self.setWindowTitle('%s - %s' % (inststr, hoststr))
        else:
            self.setWindowTitle('%s - disconnected' % inststr)

    def setStatus(self, status, exception=False):
        if status == self.current_status:
            return
        if self.client.last_action_at and \
           self.current_status == 'running' and \
           status in ('idle', 'paused') and \
           currenttime() - self.client.last_action_at > 20:
            # show a visual indication of what happened
            if status == 'paused':
                msg = 'Script is now paused.'
            elif exception:
                msg = 'Script has exited with an error.'
            else:
                msg = 'Script has finished.'
            self.trayIcon.showMessage(self.instrument, msg)
            self.client.last_action_at = 0
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
        if self.promptWindow and status != 'paused':
            self.promptWindow.close()
        # propagate to panels
        for panel in self.panels:
            panel.updateStatus(status, exception)
        for window in self.windows.values():
            for panel in window.panels:
                panel.updateStatus(status, exception)

    def on_client_error(self, problem, exc=None):
        if exc is not None:
            self.log.error('Error from daemon', exc=exc)
        problem = strftime('[%m-%d %H:%M:%S] ') + problem
        if self.errorWindow is None:
            def reset_errorWindow():
                self.errorWindow = None
            self.errorWindow = ErrorDialog(self, windowTitle='Daemon error')
            self.errorWindow.accepted.connect(reset_errorWindow)
            self.errorWindow.addMessage(problem)
            self.errorWindow.show()
        else:
            self.errorWindow.addMessage(problem)

    def on_client_broken(self, problem):
        self.on_client_error(problem)
        if self.autoreconnect:
            self._reconnect_count = self.client.RECONNECT_TRIES
            self._reconnect_time = self.client.RECONNECT_INTERVAL_SHORT
            self.reconnectTimer.start(self._reconnect_time)

    def on_client_failed(self, problem):
        if self._reconnect_count:
            self.reconnectTimer.start(self._reconnect_time)
        else:
            self.on_client_error(problem)

    def on_client_connected(self):
        self.setStatus('idle')
        self._reconnect_count = 0

        self.setTitlebar(True)
        # get all server status info
        initstatus = self.client.ask('getstatus')
        if initstatus:
            # handle initial status
            self.on_client_status(initstatus['status'])
            # propagate info to all components
            self.client.signal('initstatus', initstatus)

        # show warning label for admin users
        self.adminLabel.setVisible(
            self.warnwhenadmin and
            self.client.user_level is not None and
            self.client.user_level >= ADMIN)

        self.actionViewOnly.setChecked(self.client.viewonly)

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
            self.setStatus('paused')

    def on_client_disconnected(self):
        self.adminLabel.setVisible(False)
        self.setStatus('disconnected')

    def on_client_showhelp(self, data):
        if self.helpWindow is None:
            self.helpWindow = HelpWindow(self, self.client)
        self.helpWindow.showHelp(data)
        self.helpWindow.activateWindow()

    def on_client_clientexec(self, data):
        # currently used for client-side plot using matplotlib; data is
        # (funcname, args, ...)
        plot_func_path = data[0]
        try:
            modname, funcname = plot_func_path.rsplit('.', 1)
            func = getattr(__import__(modname, None, None, [funcname]),
                           funcname)
            func(*data[1:])
        except Exception:
            self.log.exception('Error during clientexec:\n%s',
                               '\n'.join(traceback.format_tb(sys.exc_info()[2])))

    def on_client_plugplay(self, data):
        windowkey = data[0:2]  # (mode, setupname)
        if windowkey in self.pnpWindows:
            self.pnpWindows[windowkey].activateWindow()
        else:
            window = PnPSetupQuestion(self, self.client, data)
            self.pnpWindows[windowkey] = window
            window.closed.connect(self.on_pnpWindow_closed)
            window.show()

    def on_pnpWindow_closed(self, window):
        self.pnpWindows.pop(window.data[0:2], None)

    def on_client_watchdog(self, data):
        if self.watchdogWindow is None:
            self.watchdogWindow = WatchdogDialog(self)
        self.watchdogWindow.addEvent(data)
        self.watchdogWindow.show()

    def on_client_prompt(self, data):
        if self.promptWindow:
            self.promptWindow.close()

        # show non-modal dialog box that prompts the user to continue or abort
        prompt_text = data[0]
        dlg = self.promptWindow = QMessageBox(
            QMessageBox.Information, 'Confirmation required',
            prompt_text, QMessageBox.Ok | QMessageBox.Cancel, self)
        dlg.setWindowModality(Qt.NonModal)

        # give the buttons better descriptions
        btn = dlg.button(QMessageBox.Cancel)
        btn.setText('Abort script')
        btn.clicked.connect(lambda: self.client.tell_action('stop', BREAK_NOW))
        btn = dlg.button(QMessageBox.Ok)
        btn.setText('Continue script')
        btn.clicked.connect(lambda: self.client.tell_action('continue'))
        btn.setFocus()

        dlg.show()

    def on_trayIcon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.activateWindow()

    def on_actionExpert_toggled(self, on):
        self.expertmode = on
        for panel in self.panels:
            panel.setExpertMode(on)
        for window in self.windows.values():
            for panel in window.panels:
                panel.setExpertMode(on)

    def on_actionViewOnly_toggled(self, on):
        # also triggered when the action is checked by on_client_connected
        self.client.viewonly = on
        for panel in self.panels:
            panel.setViewOnly(on)
        for window in self.windows.values():
            for panel in window.panels:
                panel.setViewOnly(on)

    @pyqtSlot()
    def on_actionNicosHelp_triggered(self):
        if not QWebView:
            self.showError('Cannot open help window: Qt web extension is not '
                           'available on your system.')
            return
        self.client.eval('session.showHelp("index")')

    @pyqtSlot()
    def on_actionNicosDocu_triggered(self):
        if not QWebView:
            self.showError('Cannot open documentation window: Qt web extension'
                           ' is not available on your system.')
            return
        from nicos.clients.gui.tools.website import WebsiteTool
        # XXX: change URL to current release version
        dlg = WebsiteTool(
            self, self.client,
            url='http://forge.frm2.tum.de/nicos/doc/nicos-3.0/')
        dlg.setWindowModality(Qt.NonModal)
        dlg.show()

    @pyqtSlot()
    def on_actionDebugConsole_triggered(self):
        if self.debugConsole is None:
            self.debugConsole = DebugConsole(self)
        self.debugConsole.show()

    @pyqtSlot()
    def on_actionAbout_triggered(self):
        info = {'version': nicos_version,
                'server_host': 'not connected',
                'server_version': '',
                'custom_version': '',
                'nicos_root': '',
                'custom_path': ''}
        if self.client.isconnected:
            dinfo = self.client.daemon_info
            info['server_host'] = self.conndata.host
            info['server_version'] = dinfo.get('daemon_version', 'unknown')
            info['custom_version'] = dinfo.get('custom_version', 'unknown')
            info['nicos_root'] = dinfo.get('nicos_root', 'unknown')
            info['custom_path'] = dinfo.get('custom_path', 'unknown')
        QMessageBox.information(
            self, 'About this application', 'NICOS GUI client version '
            '%(version)s.\n\nServer info (from %(server_host)s):\n'
            'NICOS path: %(nicos_root)s\nNICOS version: %(server_version)s\n'
            'Custom path: %(custom_path)s\nCustom version: %(custom_version)s'
            % info)

    @pyqtSlot()
    def on_actionAboutQt_triggered(self):
        QMessageBox.aboutQt(self)

    @pyqtSlot(bool)
    def on_actionConnect_triggered(self, on):
        # connection or disconnection request?
        if not on:
            self.client.disconnect()
            if self.tunnelServer:
                self.tunnelServer.stop()
                self.tunnelServer = None
            return

        self.actionConnect.setChecked(False)  # gets set by connection event
        ret = ConnectionDialog.getConnectionData(self, self.connpresets,
                                                 self.lastpreset,
                                                 self.conndata, self.tunnel)
        new_name, new_data, save, tunnel = ret

        if new_data is None:
            return
        if save:
            self.lastpreset = save
            self.connpresets[save] = new_data
        else:
            self.lastpreset = new_name
        self.conndata = new_data
        if tunnel:
            try:
                host, username, password = splitTunnelString(tunnel)
                self.tunnelServer = SSHTunnelForwarder(
                    host, ssh_username=username, ssh_password=password,
                    remote_bind_address=(self.conndata.host,
                                         self.conndata.port),
                    compression=True)
                self.tunnelServer.start()
                tunnel_port = self.tunnelServer.local_bind_port

                # corresponding ssh command line (debug)
                # print 'ssh -f %s -L %d:%s:%d -N' % (host, tunnel_port,
                #                                     self.conndata.host,
                #                                     self.conndata.port)

                # store the established tunnel information host, user, and
                # password for the next connection try to avoid typing password
                # for every (re)connection via the GUI
                self.tunnel = tunnel
                self.conndata.host = 'localhost'
                self.conndata.port = tunnel_port
            except ValueError as e:
                self.showError(e.message)
                self.tunnelServer = None
            except BaseSSHTunnelForwarderError as e:
                self.showError(e.message)
                self.tunnelServer = None
        self.client.connect(self.conndata)

    @pyqtSlot()
    def on_actionPreferences_triggered(self):
        dlg = SettingsDialog(self)
        ret = dlg.exec_()
        if ret == QDialog.Accepted:
            dlg.saveSettings()

    @pyqtSlot()
    def on_actionFont_triggered(self):
        font, ok = QFontDialog.getFont(self.user_font, self)
        if not ok:
            return
        for panel in self.panels:
            panel.setCustomStyle(font, self.user_color)
        self.user_font = font

    @pyqtSlot()
    def on_actionColor_triggered(self):
        color = QColorDialog.getColor(self.user_color, self)
        if not color.isValid():
            return
        for panel in self.panels:
            panel.setCustomStyle(self.user_font, color)
        self.user_color = color
