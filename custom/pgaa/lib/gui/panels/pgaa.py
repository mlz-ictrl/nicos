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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI PGAA panel components."""

import time
from os import path

from PyQt4.QtGui import QStyle, QColor, QDialogButtonBox, QPushButton
from PyQt4.QtCore import SIGNAL

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, dialogFromUi

my_uipath = path.dirname(__file__)


class TomographyPanel(Panel):
    panelName = 'Tomography'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'tomography.ui', my_uipath)

        self.current_status = None
        self.run_color = QColor('#ffdddd')
        self.idle_color = parent.user_color

        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('message'), self.on_client_message)
        self.connect(client, SIGNAL('initstatus'), self.on_client_initstatus)
        self.connect(client, SIGNAL('mode'), self.on_client_mode)

    def loadSettings(self, settings):
#       self.hasinput = not settings.value('noinput').toBool()
#       self.cmdhistory = list(settings.value('cmdhistory').toStringList())
        pass

    def saveSettings(self, settings):
#       settings.setValue('noinput', not self.hasinput)
        # only save 100 entries of the history
#       cmdhistory = self.commandInput.history[-100:]
#       settings.setValue('cmdhistory', QVariant(QStringList(cmdhistory)))
        pass

    def getMenus(self):
#       menu = QMenu('&Output', self)
#       menu.addAction(self.actionGrep)
#       menu.addSeparator()
#       menu.addAction(self.actionSave)
#       menu.addAction(self.actionPrint)
#       return [menu]
        return []

    def updateStatus(self, status, exception=False):
        self.current_status = status

    def on_client_connected(self):
#       self.outView._currentuser = self.client.login
        pass

    def on_client_mode(self, mode):
#       if mode == 'slave':
#           self.label.setText('slave >>')
#       elif mode == SIMULATION:
#           self.label.setText('SIM >>')
#       elif mode == MAINTENANCE:
#           self.label.setText('maint >>')
#       else:
#           self.label.setText('>>')
        pass

    def on_client_initstatus(self, state):
        self.on_client_mode(state[2])
#        messages = self.client.ask('getmessages', '10000')
#       self.outView.clear()
#       total = len(messages) // 2500 + 1
#       for _, batch in enumerateWithProgress(chunks(messages, 2500),
#                           text='Synchronizing...', parent=self, total=total):
#           self.outView.addMessages(batch)
#       self.outView.scrollToBottom()

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
        code = 'move(x, %r)\nmove(y, %r)\nmove(z, %r)\nmove(phi, %r)\nwait()\n'\
                % (x, y, z, phi)
        self.execScript(code)

    def on_getPositions_clicked(self):
        ret = self.client.eval('[x.read(), y.read(), z.read(), phi.read()]', None)
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
            qwindow = dialogFromUi(self, 'question.ui', 'panels')
            qwindow.questionText.setText('A script is currently running.  What '
                                         'do you want to do?')
            icon = qwindow.style().standardIcon
            qwindow.iconLabel.setPixmap(
                icon(QStyle.SP_MessageBoxQuestion).pixmap(32, 32))
            b0 = QPushButton(icon(QStyle.SP_DialogCancelButton), 'Cancel')
            b1 = QPushButton(icon(QStyle.SP_DialogOkButton), 'Queue script')
            b2 = QPushButton(icon(QStyle.SP_MessageBoxWarning), 'Execute now!')
            qwindow.buttonBox.addButton(b0, QDialogButtonBox.ApplyRole)
            qwindow.buttonBox.addButton(b1, QDialogButtonBox.ApplyRole)
            qwindow.buttonBox.addButton(b2, QDialogButtonBox.ApplyRole)
            qwindow.buttonBox.setFocus()
            result = [0]
            def pushed(btn):
                if btn is b1:
                    result[0] = 1
                elif btn is b2:
                    result[0] = 2
                qwindow.accept()
            self.connect(qwindow.buttonBox, SIGNAL('clicked(QAbstractButton*)'),
                         pushed)
            qwindow.exec_()
            if result[0] == 0:
                return
            elif result[0] == 2:
                action = 'execute'
        if action == 'queue':
            self.client.run(script)
            self.mainwindow.action_start_time = time.time()
        else:
            self.client.tell('exec', script)
