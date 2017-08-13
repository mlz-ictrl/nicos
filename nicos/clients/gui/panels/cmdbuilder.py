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

"""NICOS GUI single cmdlet command input."""

from PyQt4.QtCore import Qt, pyqtSignature as qtsig
from PyQt4.QtGui import QApplication, QAction, QKeyEvent, QMenu

from nicos.clients.gui.cmdlets import all_categories, all_cmdlets
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, modePrompt
from nicos.guisupport.utils import setBackgroundColor
from nicos.utils import importString


class CommandPanel(Panel):
    """Provides a panel where the user can click-and-choose a NICOS command.

    The command can be generated with the help of GUI elements known as
    "cmdlets".

    Options:

    * ``modules`` (default ``[]``) -- list of additional Python modules that
      contain cmdlets and should be loaded.
    """

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

        self.commandInput.history = self.cmdhistory
        self.commandInput.completion_callback = self.completeInput
        self.console = None

        client.initstatus.connect(self.on_client_initstatus)
        client.mode.connect(self.on_client_mode)
        client.simresult.connect(self.on_client_simresult)

    def postInit(self):
        self.console = self.window.getPanel('Console')
        if self.console:
            self.console.outView.anchorClicked.connect(
                self.on_consoleView_anchorClicked)

    def setViewOnly(self, viewonly):
        self.inputFrame.setVisible(not viewonly)

    def setOptions(self, options):
        Panel.setOptions(self, options)
        modules = options.get('modules', [])
        for module in modules:
            importString(module)  # should register cmdlets

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
        self.commandInput.setStatus(status)

    def setCustomStyle(self, font, back):
        self.commandInput.idle_color = back
        self.commandInput.setFont(font)
        setBackgroundColor(self.commandInput, back)

    def getMenus(self):
        menus = []
        for category in all_categories[::]:
            if category not in self.mapping:
                continue
            menu = QMenu('&' + category + ' commands', self)
            menu.addActions(self.mapping[category])
            menus.append(menu)
        return menus

    def completeInput(self, fullstring, lastword):
        try:
            return self.client.ask('complete', fullstring, lastword,
                                   default=[])
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

    def clearCmdlet(self):
        self.value_collection.update(self.current_cmdlet.getValues())
        self.current_cmdlet.removeSelf()
        self.current_cmdlet = None

    def selectCmdlet(self, cmdlet):
        if self.current_cmdlet:
            self.clearCmdlet()
        inst = cmdlet(self.frame, self.client)
        inst.setValues(self.value_collection)
        inst.buttons.upBtn.setVisible(False)
        inst.buttons.downBtn.setVisible(False)
        inst.cmdletRemove.connect(self.clearCmdlet)
        inst.line.setVisible(False)
        self.frame.layout().insertWidget(0, inst)
        self.current_cmdlet = inst
        inst.dataChanged.connect(self.updateCommand)
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
        self.simBtn.setEnabled(False)
        self.client.tell('simulate', '', script, '0')

    def on_client_simresult(self, data):
        self.simBtn.setEnabled(True)

    @qtsig('')
    def on_runBtn_clicked(self):
        # Make sure we add the command to the history.
        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier)
        QApplication.postEvent(self.commandInput, event)

    def on_commandInput_execRequested(self, script, action):
        if action == 'queue':
            self.client.run(script)
        else:
            self.client.tell('exec', script)
        self.commandInput.selectAll()
        self.commandInput.setFocus()
