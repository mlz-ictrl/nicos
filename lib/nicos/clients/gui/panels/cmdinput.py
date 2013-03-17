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

"""NICOS GUI command input widgets."""

__version__ = "$Revision$"

from PyQt4.QtCore import SIGNAL, pyqtSignature as qtsig
from PyQt4.QtGui import QMenu, QAction

from nicos.clients.gui.utils import loadUi
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.panels.cmdlets import all_cmdlets


class CommandsPanel(Panel):
    panelName = 'Script status'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'cmdinput.ui', 'panels')

        self.window = parent
        self.menu_devices = QMenu(self)
        self.menu_scan = QMenu(self)

        self.deviceCmds.setMenu(self.menu_devices)
        self.scanCmds.setMenu(self.menu_scan)

        self.runBtn.setVisible(False)

        for cmdlet in all_cmdlets:
            action = QAction(cmdlet.name, self)
            if cmdlet.category == 'device':
                self.menu_devices.addAction(action)
            else:
                self.menu_scan.addAction(action)
            def callback(on, cmdlet=cmdlet):
                inst = cmdlet(self.frame, self.client)
                self.connect(inst, SIGNAL('cmdletRemoved'),
                             self.on_cmdletRemoved)
                self.runBtn.setVisible(True)
                self.frame.layout().insertWidget(
                    self.frame.layout().count() - 2, inst)
            action.triggered.connect(callback)

    def on_cmdletRemoved(self, cmdlet):
        if self.frame.layout().count() < 3:
            self.runBtn.setVisible(False)

    @qtsig('')
    def on_runBtn_clicked(self):
        code = ''
        for i in range(self.frame.layout().count() - 2):
            cmdlet = self.frame.layout().itemAt(i).widget()
            code += cmdlet.generate()
        self.window.emit(SIGNAL('codeGenerated'), code)
