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
#
# *****************************************************************************

"""Graphical maintenance command runner."""

import time
import subprocess
from select import select
from threading import Thread
from os import path

from nicos.guisupport.qt import pyqtSignal, pyqtSlot, QDialog, QPushButton, \
    QMessageBox

from nicos.clients.gui.utils import loadUi
from nicos.utils import createSubprocess


class CommandsTool(QDialog):
    """The dialog displays a list of buttons that start shell commands.

    This can be used for maintenance commands that the user should be able to
    start without knowing the command.

    Options:

    * ``commands`` -- a list of tuples ``(text, shellcommand)``.  For each of
      them a button is created in the dialog.
    """

    def __init__(self, parent, client, **settings):
        QDialog.__init__(self, parent)
        loadUi(self, 'commands.ui', 'tools')

        self.closeBtn.clicked.connect(self.close)

        commands = settings.get('commands', [])
        ncmds = len(commands)
        collen = min(ncmds, 8)

        for i, (text, cmd) in enumerate(commands):
            btn = QPushButton(text, self)
            self.buttonLayout.addWidget(btn, i % collen, i // collen)
            btn.clicked.connect(lambda btncmd=cmd: self.execute(btncmd))

    def execute(self, cmd):
        self.outputBox.setPlainText('[%s] Executing %s...\n' %
                                    (time.strftime('%H:%M:%S'), cmd))
        proc = createSubprocess(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        out = proc.communicate()[0].decode()
        self.outputBox.appendPlainText(out)

    def closeEvent(self, event):
        self.deleteLater()
        self.accept()


class AsyncCommandsTool(CommandsTool):
    """ A tool to run a long-running process in a background thread

    The output is captured and displayed in the widget.
    """

    newText = pyqtSignal(str, name='newText')

    def __init__(self, parent, client, **settings):
        CommandsTool.__init__(self, parent, client, **settings)
        self.setModal(False)
        self.newText.connect(self.appendText)
        self.proc = None
        self.thread = None
        self.client = client

    def execute(self, cmd):
        if self.proc and self.proc.poll() is None:
            self.outputBox.appendPlainText('Tool is already running,'
                                           ' not starting a new one.')
        self.outputBox.setPlainText('[%s] Executing %s...\n' %
                                    (time.strftime('%H:%M:%S'), cmd))

        datapath = self.client.eval('session.experiment.datapath', '')
        if not datapath or not path.isdir(datapath):
            datapath = None
        self.proc = createSubprocess(cmd, shell=False, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, bufsize=0,
                                     cwd=datapath)
        self.thread = Thread(target=self._pollOutput)
        self.thread.start()

    def _pollOutput(self):
        while 1:
            if self.proc and self.proc.poll() is not None:
                self.proc = None
                return
            if self.proc is None:
                return
            (rl, _wl, _xl) = select([self.proc.stdout], [],
                                    [self.proc.stdout], 1.)
            if rl:
                line = self.proc.stdout.readline()
                while line:
                    self.newText.emit(line)
                    line = self.proc.stdout.readline()

    @pyqtSlot(str)
    def appendText(self, line):
        self.outputBox.appendPlainText(line.strip('\n').decode())
        sb = self.outputBox.verticalScrollBar()
        sb.setValue(sb.maximum())

    def closeEvent(self, event):
        if not self.checkClose():
            event.ignore()
            return
        self.deleteLater()
        self.accept()

    def checkClose(self):
        if ((self.thread and self.thread.is_alive()) or
                (self.proc and self.proc.poll is None)):
            res = QMessageBox.question(self, 'Message',
                                       'Close window and kill program?',
                                       QMessageBox.Yes, QMessageBox.No)
            if res == QMessageBox.No:
                return False
            else:
                if self.proc:
                    self.proc.kill()
                    self.proc = None
        return True

    def close(self):
        if not self.checkClose():
            return
        CommandsTool.close(self)
