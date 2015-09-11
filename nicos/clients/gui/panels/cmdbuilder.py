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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI single cmdlet command input."""

import time

from PyQt4.QtCore import SIGNAL, pyqtSignature as qtsig
from PyQt4.QtGui import QAction, QMenu

from nicos.clients.gui.cmdlets import all_categories, all_cmdlets
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, modePrompt
from nicos.guisupport.utils import setBackgroundColor
from nicos.utils import importString


class CommandPanel(Panel):
    panelName = 'Command'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'cmdbuilder.ui', 'panels')

        self.window = parent
        self.mapping = {}
        self.current_cmdlet = None

        # collect values of all cmdlets that have been added
        # so that the common fields carry over to the next cmdlet
        self.value_collection = {}

        self.current_status = None
        self.commandInput.history = self.cmdhistory
        self.commandInput.completion_callback = self.completeInput
        self.console = None

        self.connect(client, SIGNAL('initstatus'), self.on_client_initstatus)
        self.connect(client, SIGNAL('mode'), self.on_client_mode)

    def postInit(self):
        self.console = self.window.getPanel('Console')
        if self.console:
            self.console.outView.anchorClicked.connect(
                self.on_consoleView_anchorClicked)

    def setOptions(self, options):
        Panel.setOptions(self, options)
        modules = options.get('modules', [])
        for module in modules:
            importString(module, ('nicos.',))  # should register cmdlets

        for cmdlet in all_cmdlets:
            action = QAction(cmdlet.name, self)

            def callback(on, cmdlet=cmdlet):
                self.selectCmdlet(cmdlet)
            action.triggered.connect(callback)
            self.mapping.setdefault(cmdlet.category, []).append(action)

    def loadSettings(self, settings):
        self.cmdhistory = settings.value('cmdhistory') or []

    def saveSettings(self, settings):
        # only save 100 entries of the history
        cmdhistory = self.commandInput.history[-100:]
        settings.setValue('cmdhistory', cmdhistory)

    def updateStatus(self, status, exception=False):
        self.current_status = status
        self.commandInput.setStatus(status)

    def setCustomStyle(self, font, back):
        self.commandInput.idle_color = back
        self.commandInput.setFont(font)
        setBackgroundColor(self.commandInput, back)

    def getMenus(self):
        menus = []
        for category in all_categories[::]:
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

    def on_client_initstatus(self, state):
        self.on_client_mode(state['mode'])

    def on_client_mode(self, mode):
        self.label.setText(modePrompt(mode))

    def on_consoleView_anchorClicked(self, url):
        """Called when the user clicks a link in the out view."""
        url = url.toString()
        if url.startswith('exec:'):
            self.commandInput.setText(url[5:])
            self.commandInput.setFocus()

    def selectCmdlet(self, cmdlet):
        if self.current_cmdlet:
            self.value_collection.update(self.current_cmdlet.getValues())
            self.current_cmdlet.removeSelf()
        inst = cmdlet(self.frame, self.client)
        inst.setValues(self.value_collection)
        inst.buttons.setVisible(False)
        inst.line.setVisible(False)
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
        script = self.commandInput.text()
        if not script:
            return
        self.client.tell('simulate', '', script, 'sim')

    @qtsig('')
    def on_runBtn_clicked(self):
        self.commandInput.on_returnPressed()

    def on_commandInput_execRequested(self, script, action):
        if action == 'queue':
            self.mainwindow.action_start_time = time.time()
            self.client.run(script)
        else:
            self.client.tell('exec', script)
        self.commandInput.selectAll()
        self.commandInput.setFocus()
