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

from __future__ import print_function

from os import path

from PyQt4.QtGui import QColor, QButtonGroup, QMessageBox
from PyQt4.QtCore import pyqtSlot, SIGNAL, QTimer

from nicos.utils import chunks
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, enumerateWithProgress, \
    ScriptExecQuestion

my_uipath = path.dirname(__file__)


class PGAAPanel(Panel):

    panelName = 'PGAA'

    positions = [4, 74, 144, 214, 284, 354]

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'pgaaposition.ui', my_uipath)

        self.timer = QTimer()
#       self.lab_act_status.setText(str(sampleholder.read()))
        self.lab_RefSearchDone.setText("Not yet!")

        # Connect the buttons and fields
        self.gotoPosition.clicked.connect(self.on_gotoPosition)
        self.submitPosition.clicked.connect(self.on_submitPosition)
#       self.btn_ManReadyOn.clicked.connect(self.startDetector)
#       self.btn_ManReadyOff.clicked.connect(self.stopDetector)
        self.refSearch.clicked.connect(self.on_refSearch)
        self.startBatch.clicked.connect(self.on_startBatch)
        self.line_ManPos.valueChanged.connect(self.manPosChanged)
        self.timer.timeout.connect(self.update)

        self.timer.start(500)
        # Regularly update the interface
        self.update()
        self.on_clearBatch_clicked()

        self.current_status = None
        self.run_color = QColor('#ffdddd')
        self.idle_color = parent.user_color

        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('message'), self.on_client_message)
        self.connect(client, SIGNAL('initstatus'), self.on_client_initstatus)
        self.connect(client, SIGNAL('mode'), self.on_client_mode)

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.addButton(self.rad_Man, -2)
        self.buttonGroup.addButton(self.rad_Pos0, 0)
        self.buttonGroup.addButton(self.rad_Pos1, 1)
        self.buttonGroup.addButton(self.rad_Pos2, 2)
        self.buttonGroup.addButton(self.rad_Pos3, 3)
        self.buttonGroup.addButton(self.rad_Pos4, 4)
        self.buttonGroup.addButton(self.rad_Pos5, 5)

        self.connect(self.buttonGroup, SIGNAL('buttonClicked(int)'),
                     self.on_buttonClicked)

    def loadSettings(self, settings):
        pass
        # self.hasinput = not settings.value('noinput', False, bool)
        # self.cmdhistory = settings.value('cmdhistory') or []

    def saveSettings(self, settings):
        # settings.setValue('noinput', not self.hasinput)
        # only save 100 entries of the history
        # cmdhistory = self.commandInput.history[-100:]
        # settings.setValue('cmdhistory', QVariant(QStringList(cmdhistory)))
        pass

    def getMenus(self):
        # menu = QMenu('&Output', self)
        # menu.addAction(self.actionGrep)
        # menu.addSeparator()
        # menu.addAction(self.actionSave)
        # menu.addAction(self.actionPrint)
        # return [menu]
        return []

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
        messages = self.client.ask('getmessages', '2000')
        self.browser_log.clear()
        total = len(messages) // 2500 + 1
        for _, batch in enumerateWithProgress(chunks(messages, 2500),
                                              text='Synchronizing...',
                                              parent=self, total=total):
            self.browser_log.addMessages(batch)
        self.browser_log.scrollToBottom()

    def on_client_message(self, message):
        if message[-1] == '(sim) ':
            return
        try:
            self.browser_log.addMessage(message)
        except Exception as e:
            print(e)
            print(message)

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

    @pyqtSlot(str)
    def manPosChanged(self, text):
        self.rad_Man.setChecked(True)

    @pyqtSlot()
    def on_startBatch(self):
        # Read the postitions from the interface
        text_in_queue = self.txted_queue.toPlainText()
        # Split the positions of the list
        list_of_positions = text_in_queue.split("\n")
        if len(list_of_positions):
            script = ["maw(shutter, 'open')"]
            script.append('read(shutter)')
            script.append('shutter.read(0)')
            script.append('scan(sample_motor, [%s])' %
                          ', '.join(list_of_positions))
            script.append("maw(shutter, 'closed')")
            script.append('')
            self.execScript('\n'.join(script))

    @pyqtSlot()
    def on_refSearch(self):
        script = 'reference(sample_motor)'
        self.execScript(script)

    def on_clearBatch_clicked(self):
        self.txted_queue.setPlainText('')
        self.startBatch.setDisabled(True)

    def on_detOn_clicked(self):
        # detector.start()
        self.update()

    def on_detOff_clicked(self):
        # detector.finish()
        self.update()

    @pyqtSlot()
    def on_submitPosition(self):
        """Appends the queued positions to the text field"""
        if self.buttonGroup.checkedId() != -1:
            text = str(self.txted_queue.toPlainText())
            text += '%r\n' % self.check_selected_button()
            self.txted_queue.setPlainText(text)
            self.startBatch.setEnabled(True)

    def update(self):
        """Used for the timer to start automatically and that it does not get
        garbage collected"""
        try:
            pass
#           detstatus = detector.status()
#           self.detOn.setEnabled(not detstatus)
#           self.detOff.setEnabled(detstatus)
#           self.lab_act_status.setText(str(sampleholder.read()))
#           self.stat_motor.setText(str(sampleholder.deviceState()))
#           self.stat_dspec.setText(str(detector.get_ready.read()))
        finally:
            pass

    def on_gotoPosition(self):
        script = 'maw(sample_motor, %s)' % self.check_selected_button()
        self.execScript(script)

    def on_buttonClicked(self, index):
        pass

    def check_selected_button(self):
        index = self.buttonGroup.checkedId()
        if index == -2:
            return self.line_ManPos.value()
        elif index == -1:
            # self.log('No Button selected! Please select a button first!')
            return False
        else:
            return self.positions[index]
