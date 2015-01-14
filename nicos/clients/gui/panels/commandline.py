#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI command line input component."""

import time

from PyQt4.QtGui import QColor, QMessageBox
from PyQt4.QtCore import SIGNAL

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, ScriptExecQuestion, \
     setBackgroundColor, setForegroundColor
from nicos.core import SIMULATION, SLAVE, MAINTENANCE


class CommandLinePanel(Panel):
    panelName = 'CommandLinePanel'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'commandline.ui', 'panels')

        self.current_status = None
        self.run_color = QColor('#ffdddd')
        self.idle_color = parent.user_color
        self.commandInput.history = self.cmdhistory
        self.commandInput.completion_callback = self.completeInput

        self.connect(client, SIGNAL('initstatus'), self.on_client_initstatus)
        self.connect(client, SIGNAL('mode'), self.on_client_mode)
        self.connect(client, SIGNAL('experiment'), self.on_client_experiment)

    def setOptions(self, options):
        pass

    def loadSettings(self, settings):
        self.cmdhistory = settings.value('cmdhistory') or []

    def saveSettings(self, settings):
        # only save 100 entries of the history
        cmdhistory = self.commandInput.history[-100:]
        settings.setValue('cmdhistory', cmdhistory)

    def getMenus(self):
        return []

    def setCustomStyle(self, font, back):
        self.idle_color = back
        self.commandInput.setFont(font)
        self.label.setFont(font)
        setBackgroundColor(self.commandInput, back)

    def updateStatus(self, status, exception=False):
        self.current_status = status
        if status != 'idle':
            setBackgroundColor(self.commandInput, self.run_color)
        else:
            setBackgroundColor(self.commandInput, self.idle_color)
        self.commandInput.update()
        self.commandInput.setEnabled(status != 'disconnected')

    def completeInput(self, fullstring, lastword):
        try:
            return self.client.ask('complete', fullstring, lastword)
        except Exception:
            return []

    def on_client_mode(self, mode):
        if mode == SLAVE:
            self.label.setText('slave >>')
        elif mode == SIMULATION:
            self.label.setText('SIM >>')
        elif mode == MAINTENANCE:
            self.label.setText('maint >>')
        else:
            self.label.setText('>>')

    def on_client_initstatus(self, state):
        self.on_client_mode(state['mode'])

    def on_client_experiment(self, data):
        (_, proptype) = data
        if proptype == 'user':
            # only clear when switching TO a user experiment
            self.commandInput.history = []

    def on_commandInput_textChanged(self, text):
        try:
            script = self.commandInput.text()
            if not script or script.strip().startswith('#'):
                return
            compile(script+'\n', 'script', 'single')
        except Exception:
            setForegroundColor(self.commandInput, QColor("#ff0000"))
        else:
            setForegroundColor(self.commandInput, QColor("#000000"))

    def on_commandInput_returnPressed(self):
        script = self.commandInput.text()
        if not script:
            return
        # XXX: this does not apply in SPM mode
        # sscript = script.strip()
        # if not (sscript.startswith(('#', '?', '.', ':')) or sscript.endswith('?')):
        #     try:
        #         compile(script+'\n', 'script', 'single')
        #     except SyntaxError as err:
        #         QMessageBox.information(
        #             self, 'Command', 'Syntax error in command: %s' % err.msg)
        #         self.commandInput.setCursorPosition(err.offset)
        #         return
        action = 'queue'
        if self.current_status != 'idle':
            qwindow = ScriptExecQuestion()
            result = qwindow.exec_()
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Apply:
                action = 'execute'
        if action == 'queue':
            self.mainwindow.action_start_time = time.time()
            self.client.tell('queue', '', script)
        else:
            self.client.tell('exec', script)
        self.commandInput.setText('')
