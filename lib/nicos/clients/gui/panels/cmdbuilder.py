#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI single cmdlet command input."""

import time

from PyQt4.QtCore import SIGNAL, pyqtSignature as qtsig, QVariant, QStringList
from PyQt4.QtGui import QMenu, QAction, QMessageBox, QColor

from nicos.clients.gui.utils import loadUi, setBackgroundColor, \
     ScriptExecQuestion
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.cmdlets import all_cmdlets, all_categories


class CommandPanel(Panel):
    panelName = 'Command'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'cmdbuilder.ui', 'panels')

        self.window = parent
        self.mapping = {}
        self.current_cmdlet = None

        self.current_status = None
        self.run_color = QColor('#ffdddd')
        self.idle_color = parent.user_color
        self.commandInput.history = self.cmdhistory
        self.commandInput.completion_callback = self.completeInput

        for cmdlet in all_cmdlets:
            action = QAction(cmdlet.name, self)
            def callback(on, cmdlet=cmdlet):
                self.selectCmdlet(cmdlet)
            action.triggered.connect(callback)
            self.mapping.setdefault(cmdlet.category, []).append(action)

    def loadSettings(self, settings):
        self.cmdhistory = list(settings.value('cmdhistory').toStringList())

    def saveSettings(self, settings):
        # only save 100 entries of the history
        cmdhistory = self.commandInput.history[-100:]
        settings.setValue('cmdhistory', QVariant(QStringList(cmdhistory)))

    def updateStatus(self, status, exception=False):
        self.current_status = status
        if status != 'idle':
            setBackgroundColor(self.commandInput, self.run_color)
        else:
            setBackgroundColor(self.commandInput, self.idle_color)
        self.commandInput.update()
        self.commandInput.setEnabled(status != 'disconnected')

    def setCustomStyle(self, font, back):
        self.idle_color = back
        self.commandInput.setFont(font)
        setBackgroundColor(self.commandInput, back)

    def getMenus(self):
        menus = []
        for category in all_categories[::-1]:
            if category not in self.mapping:
                return
            menu = QMenu('&' + category + ' commands', self)
            menu.addActions(self.mapping[category])
            menus.append(menu)
        return menus

    def completeInput(self, fullstring, lastword):
        try:
            return self.client.ask('complete', fullstring, lastword)
        except Exception:
            return []

    def selectCmdlet(self, cmdlet):
        if self.current_cmdlet:
            self.current_cmdlet.removeSelf()
        inst = cmdlet(self.frame, self.client)
        inst.delBtn.setVisible(False)
        self.frame.layout().insertWidget(0, inst)
        self.current_cmdlet = inst
        self.connect(inst, SIGNAL('dataChanged'), self.updateCommand)
        self.updateCommand()

    def _generate(self):
        mode = 'python'
        if self.current_cmdlet is None:
            return
        if self.client.eval('session.spMode', False):
            mode = 'simple'
        if not self.current_cmdlet.isValid():
            return
        return self.current_cmdlet.generate(mode).rstrip()

    def updateCommand(self):
        code = self._generate()
        if code is not None:
            self.commandInput.setText(code)
        else:
            self.commandInput.setText('')

    @qtsig('')
    def on_simBtn_clicked(self):
        script = str(self.commandInput.text().toUtf8())
        if not script:
            return
        self.client.tell('simulate', '', script, 'sim')

    def on_commandInput_returnPressed(self):
        self.on_runBtn_clicked()

    @qtsig('')
    def on_runBtn_clicked(self):
        script = str(self.commandInput.text().toUtf8())
        if not script:
            return
        action = 'queue'
        if self.current_status != 'idle':
            qwindow = ScriptExecQuestion()
            result = qwindow.exec_()
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Apply:
                action = 'execute'
        if action == 'queue':
            self.client.tell('queue', '', script)
            self.mainwindow.action_start_time = time.time()
        else:
            self.client.tell('exec', script)
        self.commandInput.selectAll()
        self.commandInput.setFocus()
