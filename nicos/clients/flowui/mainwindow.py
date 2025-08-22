# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Christian Felder <c.felder@fz-juelich.de>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""NICOS GUI main window."""
from os import path
from time import time as current_time

from nicos.clients.flowui import uipath
from nicos.clients.flowui.panels import get_icon, root_path
from nicos.clients.gui.mainwindow import MainWindow as DefaultMainWindow
from nicos.clients.flowui.panels.status import ScriptStatusPanel
from nicos.guisupport.qt import QIcon, QLabel, QMenu, QPixmap, QPoint, \
    QSizePolicy, Qt, QWidget, pyqtSlot
from nicos.utils import findResource


def decolor_logo(pixmap, color):
    ret_pix = QPixmap(pixmap.size())
    ret_pix.fill(color)
    ret_pix.setMask(pixmap.createMaskFromColor(Qt.GlobalColor.transparent))
    return ret_pix


class Spacer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Preferred)


class MainWindow(DefaultMainWindow):
    ui = path.join(uipath, 'main.ui')
    default_facility_logo = ':/ess-logo-auth'

    def __init__(self, log, gui_conf, viewonly=False, tunnel=''):
        DefaultMainWindow.__init__(self, log, gui_conf, viewonly, tunnel)
        self.client.experiment.connect(self._update_toolbar_info)
        self.add_logo()
        self.set_icons()

        self.editor_wintype = self.gui_conf.find_panel(
            ('editor.EditorPanel',
             'nicos.clients.flowui.panels.editor.EditorPanel'))
        self.history_wintype = self.gui_conf.find_panel(
            ('history.HistoryPanel',
             'nicos.clients.flowui.panels.history.HistoryPanel'))

        # Cheeseburger menu
        dropdown = QMenu('')
        dropdown.addAction(self.actionConnect)
        dropdown.addAction(self.actionViewOnly)
        dropdown.addAction(self.actionPreferences)
        dropdown.addAction(self.actionExpert)
        dropdown.addSeparator()
        dropdown.addAction(self.actionExit)
        self.actionUser.setIconVisibleInMenu(True)
        self.dropdown = dropdown
        self.actionExpert.setEnabled(self.client.isconnected)

        self._init_instrument_name()
        self._init_experiment_name()
        self.on_client_disconnected()

    def defaultStylefiles(self):
        return [findResource('nicos/clients/flowui/guiconfig.qss')]

    def _init_toolbar(self):
        self.status_label = QLabel()
        self.status_label.setStyleSheet('font-size: 17pt; font-weight: bold')
        self.status_text = QLabel()
        self.status_text.setStyleSheet('font-size: 17pt')

        self.toolbar = self.toolBarRight

        for panel in self.panels:
            if isinstance(panel, ScriptStatusPanel):
                self.toolbar.addAction(panel.actionEmergencyStop)
                break

        self.toolbar.addWidget(self.status_text)
        self.toolbar.addWidget(self.status_label)

    def _init_experiment_name(self):
        self.experiment_label = QLabel()
        self.experiment_label.setSizePolicy(QSizePolicy.Policy.Expanding,
                                            QSizePolicy.Policy.Preferred)
        self.experiment_label.setStyleSheet('font-size: 17pt; '
                                            'font-weight: bold')
        self.toolBarMain.addWidget(self.experiment_label)

        self.experiment_text = QLabel()
        self.experiment_text.setSizePolicy(QSizePolicy.Policy.Expanding,
                                           QSizePolicy.Policy.Preferred)
        self.experiment_text.setStyleSheet('font-size: 17pt')
        self.toolBarMain.addWidget(self.experiment_text)

    def _init_instrument_name(self):
        self.instrument_label = QLabel()
        self.instrument_label.setSizePolicy(QSizePolicy.Policy.Expanding,
                                            QSizePolicy.Policy.Preferred)
        self.instrument_label.setStyleSheet('font-size: 17pt; '
                                            'font-weight: bold')
        self.toolBarMain.addWidget(self.instrument_label)

        self.instrument_text = QLabel()
        self.instrument_text.setSizePolicy(QSizePolicy.Policy.Expanding,
                                           QSizePolicy.Policy.Preferred)
        self.instrument_text.setStyleSheet('font-size: 17pt')
        self.toolBarMain.addWidget(self.instrument_text)

    def set_icons(self):
        self.actionUser.setIcon(get_icon('settings_applications-24px.svg'))
        self.actionConnect.setIcon(get_icon('power-24px.svg'))
        self.actionExit.setIcon(get_icon('exit_to_app-24px.svg'))
        self.actionViewOnly.setIcon(get_icon('lock-24px.svg'))
        self.actionPreferences.setIcon(get_icon('tune-24px.svg'))
        self.actionExpert.setIcon(get_icon('fingerprint-24px.svg'))

    def add_logo(self):
        spacer = QWidget()
        spacer.setMinimumWidth(20)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Expanding)
        self.toolBarMain.insertWidget(self.toolBarMain.actions()[0], spacer)

        nicos_label = QLabel()
        pxr = decolor_logo(QPixmap(path.join(root_path, 'resources',
                                             'nicos-logo-high.svg')),
                           Qt.GlobalColor.white)
        nicos_label.setPixmap(pxr.scaledToHeight(
            self.toolBarMain.height(),
            Qt.TransformationMode.SmoothTransformation))
        self.toolBarMain.insertWidget(self.toolBarMain.actions()[1],
                                      nicos_label)

    def update_instrument_text(self):
        instrument = self.client.eval('session.instrument', None)
        self.instrument_label.setText('Instrument:')
        if instrument:
            logo = decolor_logo(QPixmap(path.join(root_path,
                                'resources', f'{instrument}-logo.svg')),
                                Qt.GlobalColor.white)
            if logo.isNull():
                self.instrument_text.setText(instrument.upper())
                return
            self.instrument_text.setPixmap(logo.scaledToHeight(
                self.toolBarMain.height(),
                Qt.TransformationMode.SmoothTransformation))
        else:
            self.instrument_text.setText('UNKNOWN')

    def update_experiment_text(self):
        max_text_length = 50
        experiment = self.client.eval('session.experiment.title', None)
        if experiment is not None:
            self.experiment_label.setText('     Experiment:')
            self.experiment_text.setText(experiment[0:max_text_length])

    def setStatus(self, status, exception=False):
        if status == self.current_status:
            return
        if self.client.last_action_at and \
           self.current_status == 'running' and \
           status in ('idle', 'paused') and \
           current_time() - self.client.last_action_at > 20:
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
        self._update_toolbar_info()
        self._update_status_text()
        # new status icon
        pixmap = QPixmap(':/' + status + ('exc' if exception else ''))
        new_icon = QIcon()
        new_icon.addPixmap(pixmap, QIcon.Mode.Disabled)
        self.trayIcon.setIcon(new_icon)
        self.trayIcon.setToolTip('%s status: %s' % (self.instrument, status))
        if self.showtrayicon:
            self.trayIcon.show()
        if self.promptWindow and status != 'paused':
            # when script continues, any prompts are useless
            self.promptWindow.close()
            self.promptWindow = None
        # propagate to panels
        for panel in self.panels:
            panel.updateStatus(status, exception)
        for window in self.windows.values():
            for panel in window.panels:
                panel.updateStatus(status, exception)

    def _update_toolbar_info(self):
        if self.current_status != 'disconnected':
            self.update_instrument_text()
            self.update_experiment_text()
        else:
            self.clear_experiment_text()
            self.clear_instrument_text()

    def _update_status_text(self):
        if self.current_status == 'disconnected':
            self.status_label.setText(self.current_status.upper())
            self.status_text.setText('')
        else:
            self.status_label.setText('     Status: ')
            self.status_text.setText(self.current_status.upper())

    def clear_instrument_text(self):
        self.instrument_label.clear()
        self.instrument_text.clear()

    def clear_experiment_text(self):
        self.experiment_label.clear()
        self.experiment_text.clear()

    def on_client_connected(self):
        DefaultMainWindow.on_client_connected(self)
        self.actionConnect.setIcon(get_icon('power_off-24px.svg'))
        self.actionExpert.setEnabled(True)
        self.actionViewOnly.setEnabled(True)
        self.actionConnect.setText('Disconnect')

    def on_client_disconnected(self):
        DefaultMainWindow.on_client_disconnected(self)
        self.actionConnect.setIcon(get_icon('power-24px.svg'))
        self.actionConnect.setText('Connect to server...')
        self.actionExpert.setEnabled(False)
        self.actionViewOnly.setEnabled(False)
        self.setTitlebar(False)

    @pyqtSlot(bool)
    def on_actionConnect_triggered(self, _):
        # connection or disconnection request?
        connection_req = self.current_status == 'disconnected'
        super().on_actionConnect_triggered(connection_req)

    @pyqtSlot()
    def on_actionUser_triggered(self):
        w = self.toolBarRight.widgetForAction(self.actionUser)
        self.dropdown.popup(w.mapToGlobal(QPoint(0, w.height())))
