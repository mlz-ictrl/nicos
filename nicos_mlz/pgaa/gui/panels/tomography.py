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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI PGAA panel components."""

from os import path

from nicos.guisupport.qt import QColor, QMessageBox, QMenu

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, ScriptExecQuestion

my_uipath = path.dirname(__file__)


class TomographyPanel(Panel):
    panelName = 'Tomography'
    menu = None

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'tomography.ui', my_uipath)

        self.current_status = None
        self.run_color = QColor('#ffdddd')
        self.idle_color = parent.user_color

        client.connected.connect(self.on_client_connected)
        client.message.connect(self.on_client_message)
        client.initstatus.connect(self.on_client_initstatus)
        client.mode.connect(self.on_client_mode)

    def loadSettings(self, settings):
        # self.hasinput = not settings.value('noinput', False, bool)
        # self.cmdhistory = settings.value('cmdhistory') or []
        pass

    def saveSettings(self, settings):
        # settings.setValue('noinput', not self.hasinput)
        # only save 100 entries of the history
        # cmdhistory = self.commandInput.history[-100:]
        # settings.setValue('cmdhistory', QVariant(QStringList(cmdhistory)))
        pass

    def getMenus(self):
        if not self.menu:
            menu = QMenu('&Output', self)
        #   menu.addAction(self.actionGrep)
        #   menu.addSeparator()
        #   menu.addAction(self.actionSave)
        #   menu.addAction(self.actionPrint)
            self.menu = menu
        return [self.menu]

    def updateStatus(self, status, exception=False):
        self.current_status = status

    def on_client_connected(self):
        # self.outView._currentuser = self.client.login
        pass

    def on_client_mode(self, mode):
        # if mode == 'slave':
        #     self.label.setText('slave >>')
        # elif mode == SIMULATION:
        #     self.label.setText('SIM >>')
        # elif mode == MAINTENANCE:
        #     self.label.setText('maint >>')
        # else:
        #     self.label.setText('>>')
        pass

    def on_client_initstatus(self, state):
        self.on_client_mode(state['mode'])
        # messages = self.client.ask('getmessages', '10000')
        # self.outView.clear()
        # total = len(messages) // 2500 + 1
        # for _, batch in enumerateWithProgress(chunks(messages, 2500),
        #                                       text='Synchronizing...',
        #                                       parent=self, total=total):
        #     self.outView.addMessages(batch)
        # self.outView.scrollToBottom()

    def on_client_message(self, message):
        if message[-1] == '(sim) ':
            return

    def on_takeOpenBeam_clicked(self):
        pass

    def on_takeDarkImages_clicked(self):
        pass

    def on_takeSeries_clicked(self):
        pass

    def on_takeTomography_clicked(self):
        pass

    def on_takeImage_clicked(self):
        pass

    def on_setButton_clicked(self):
        x = self.xValue.value()
        y = self.yValue.value()
        z = self.zValue.value()
        phi = self.phiValue.value()
        code = 'move(x, %r)\nmove(y, %r)\nmove(z, %r)\nmove(phi, %r)\n' \
               'wait()\n' % (x, y, z, phi)
        self.execScript(code)

    def on_getPositions_clicked(self):
        ret = self.client.eval('[x.read(), y.read(), z.read(), phi.read()]',
                               None)
        if ret:
            self.xValue.setValue(float(ret[0]))
            self.yValue.setValue(float(ret[1]))
            self.zValue.setValue(float(ret[2]))
            self.phiValue.setValue(float(ret[3]))

    def execScript(self, script):
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
            self.client.run(script)
        else:
            self.client.tell('exec', script)
