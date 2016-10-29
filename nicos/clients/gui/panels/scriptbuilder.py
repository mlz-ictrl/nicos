#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI multiple cmdlet script-builder input."""

from PyQt4.QtCore import SIGNAL, pyqtSignature as qtsig
from PyQt4.QtGui import QAction, QMenu, QToolButton

from nicos.clients.gui.cmdlets import all_categories, all_cmdlets
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.utils import importString


class CommandsPanel(Panel):
    """Provides a panel to create via click-and-choose multiple NICOS commands.

    This panel allows the user to create a series of NICOS commands with
    cmdlets (similar to the `.cmdbuilder.CommandPanel` but for multiple
    commands).

    Options:

    * ``modules`` (default [ ]) -- list of additional Python modules that
      contain cmdlets and should be loaded.
    """
    panelName = 'Commands'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'scriptbuilder.ui', 'panels')

        self.window = parent
        self.runBtn.setVisible(False)
        self.mapping = {}

    def setOptions(self, options):
        Panel.setOptions(self, options)

        modules = options.get('modules', [])
        for module in modules:
            importString(module, ('nicos.',))  # should register cmdlets

        for cmdlet in all_cmdlets:
            action = QAction(cmdlet.name, self)
            def callback(on, cmdlet=cmdlet):
                inst = cmdlet(self.frame, self.client)
                inst.cmdletUp.connect(self.on_cmdletUp)
                inst.cmdletDown.connect(self.on_cmdletDown)
                inst.cmdletRemove.connect(self.on_cmdletRemove)
                self.runBtn.setVisible(True)
                self.frame.layout().insertWidget(
                    self.frame.layout().count() - 2, inst)
            action.triggered.connect(callback)
            self.mapping.setdefault(cmdlet.category, []).append(action)

        for category in all_categories[::-1]:
            if category not in self.mapping:
                return
            toolbtn = QToolButton(self)
            toolbtn.setText(category)
            toolbtn.setPopupMode(QToolButton.InstantPopup)
            menu = QMenu(self)
            menu.addActions(self.mapping[category])
            toolbtn.setMenu(menu)
            self.btnLayout.insertWidget(1, toolbtn)

    def on_cmdletRemove(self):
        cmdlet = self.sender()
        layout = self.frame.layout()

        layout.removeWidget(cmdlet)
        cmdlet.hide()

        if layout.count() < 3:
            self.runBtn.setVisible(False)

    def on_cmdletUp(self):
        cmdlet = self.sender()
        layout = self.frame.layout()

        index = layout.indexOf(cmdlet)

        if not index:
            return

        layout.removeWidget(cmdlet)
        layout.insertWidget(index - 1, cmdlet)

    def on_cmdletDown(self):
        cmdlet = self.sender()
        layout = self.frame.layout()

        index = layout.indexOf(cmdlet)

        if index >= (layout.count() - 3):
            return

        layout.removeWidget(cmdlet)
        layout.insertWidget(index + 1, cmdlet)

    @qtsig('')
    def on_runBtn_clicked(self):
        code = ''
        valid = True
        mode = 'python'
        if self.client.eval('session.spMode', False):
            mode = 'simple'
        for i in range(self.frame.layout().count() - 2):
            cmdlet = self.frame.layout().itemAt(i).widget()
            valid = valid and cmdlet.isValid()
            generated = cmdlet.generate(mode)
            if not generated.endswith('\n'):
                generated += '\n'
            code += generated
        if not valid:
            return
        self.window.emit(SIGNAL('codeGenerated'), code)
